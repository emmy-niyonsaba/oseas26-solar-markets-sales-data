"""End-to-end data pipeline: load -> validate -> clean -> grid -> features -> ML dataset."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import geopandas as gpd
import pandas as pd

from ..config import Settings
from ..countries import get_country
from .cleaning import aggregate_labels, clean_cells, clean_surveys
from .feature_engineering import build_feature_frame
from .ingestion import load_boundary, load_raw_layers
from .spatial_processing import build_grid

logger = logging.getLogger(__name__)


def build_dataset(settings: Settings, country_code: str) -> dict:
    country = get_country(country_code)
    out_dir = settings.processed_path(country.code)
    res = settings.grid_resolution_km

    boundary = load_boundary(country, settings.raw_path(country.code), settings.demo_mode)
    grid, spec = build_grid(country, res, boundary)
    raw = load_raw_layers(settings, country, grid, spec)

    cells = clean_cells(build_feature_frame(grid, raw, country, res))
    labels = aggregate_labels(clean_surveys(raw.surveys), grid, spec)
    training = cells.merge(labels, on="cell_id", how="inner")
    if len(training) < settings.min_training_cells:
        raise ValueError(
            f"Only {len(training)} labelled cells; need at least {settings.min_training_cells} to train."
        )

    cells.to_csv(out_dir / "cells_features.csv", index=False)
    training.to_csv(out_dir / "training.csv", index=False)
    if raw.gogla is not None:
        raw.gogla.to_csv(out_dir / "gogla.csv", index=False)

    infra = []
    if not raw.grid_lines.empty:
        infra.append(raw.grid_lines[["geometry"]].assign(kind="grid_line"))
    if not raw.minigrids.empty:
        infra.append(raw.minigrids[["geometry"]].assign(kind="minigrid"))
    infra_json = (
        gpd.GeoDataFrame(pd.concat(infra, ignore_index=True), crs="EPSG:4326").to_json()
        if infra else json.dumps({"type": "FeatureCollection", "features": []})
    )
    (out_dir / "infrastructure.geojson").write_text(infra_json)

    meta = {
        "country": country.code,
        "country_name": country.name,
        "is_demo": raw.is_demo,
        "grid_spec": spec.to_dict(),
        "n_cells": len(cells),
        "n_labelled_cells": len(training),
        "bounds": [
            float(cells["lon"].min() - spec.deg / 2), float(cells["lat"].min() - spec.deg / 2),
            float(cells["lon"].max() + spec.deg / 2), float(cells["lat"].max() + spec.deg / 2),
        ],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "sources": raw.sources,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    logger.info("Dataset built: %d cells, %d labelled", len(cells), len(training))
    return meta
