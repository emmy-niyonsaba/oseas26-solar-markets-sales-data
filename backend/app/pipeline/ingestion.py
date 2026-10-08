"""Load raw layers. In demo mode these are synthetic; otherwise they come from data/raw/<CODE>/."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.enums import Resampling
from shapely.geometry import Polygon

from ..config import Settings
from ..countries import Country
from .cleaning import validate_columns
from .spatial_processing import GridSpec, assign_cells, raster_to_grid, values_at_cells

logger = logging.getLogger(__name__)

# Files expected in backend/data/raw/<CODE>/ when DEMO_MODE=false
REQUIRED_FILES = {
    "population.tif": "WorldPop / Meta HRSL population raster (people per pixel)",
    "night_lights.tif": "NASA Black Marble (VNP46A4 or similar) annual radiance raster",
    "solar_resource.tif": "Global Solar Atlas GHI raster (kWh/m2/day)",
    "relative_wealth.csv": "Meta Relative Wealth Index CSV with columns latitude, longitude, rwi",
    "grid.geojson": "Gridfinder / OSM / EAE grid lines",
    "surveys.csv": "DHS / MICS / MTF clusters: latitude, longitude, solar_ownership[, electricity_access, n_households]",
}
OPTIONAL_FILES = {
    "minigrids.geojson": "Existing or planned minigrids (points or lines)",
    "boundary.geojson": "Country boundary polygon (otherwise the bbox is used)",
    "gogla.csv": "GOGLA national sales: country, reported_sales, product_category, year",
}


@dataclass
class RawLayers:
    population_density: np.ndarray       # people / km2, aligned to grid rows
    nighttime_radiance: np.ndarray
    relative_wealth: np.ndarray
    solar_resource: np.ndarray
    grid_lines: gpd.GeoDataFrame
    minigrids: gpd.GeoDataFrame
    surveys: pd.DataFrame
    gogla: pd.DataFrame | None = None
    is_demo: bool = False
    sources: dict[str, str] = field(default_factory=dict)


def empty_gdf() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:4326")


def load_boundary(country: Country, raw_dir: Path, use_demo_outline: bool) -> Polygon | None:
    path = raw_dir / "boundary.geojson"
    if not use_demo_outline and path.exists():
        gdf = gpd.read_file(path).to_crs(epsg=4326)
        return gdf.geometry.union_all() if hasattr(gdf.geometry, "union_all") else gdf.geometry.unary_union
    if country.boundary:
        return Polygon(country.boundary)
    return None


def _read_vector(path: Path) -> gpd.GeoDataFrame:
    if not path.exists():
        return empty_gdf()
    gdf = gpd.read_file(path)
    return gdf.to_crs(epsg=4326) if gdf.crs else gdf.set_crs(epsg=4326)


def _load_real(settings: Settings, country: Country, grid: gpd.GeoDataFrame, spec: GridSpec) -> RawLayers:
    raw_dir = settings.raw_path(country.code)
    missing = [f for f in REQUIRED_FILES if not (raw_dir / f).exists()]
    if missing:
        listing = "\n".join(f"  - {f}: {REQUIRED_FILES[f]}" for f in missing)
        raise FileNotFoundError(
            f"DEMO_MODE=false but required files are missing in {raw_dir}:\n{listing}\n"
            "Add them or set DEMO_MODE=true."
        )
    logger.info("Loading real datasets from %s", raw_dir)
    pop_total = values_at_cells(raster_to_grid(raw_dir / "population.tif", spec, Resampling.sum), grid)
    night = values_at_cells(raster_to_grid(raw_dir / "night_lights.tif", spec, Resampling.average), grid)
    solar = values_at_cells(raster_to_grid(raw_dir / "solar_resource.tif", spec, Resampling.average), grid)

    rwi = pd.read_csv(raw_dir / "relative_wealth.csv")
    validate_columns(rwi, ["latitude", "longitude", "rwi"], "relative_wealth.csv")
    rwi = assign_cells(rwi, grid, spec).groupby("cell_id")["rwi"].mean()
    wealth = grid["cell_id"].map(rwi).to_numpy(dtype=float)

    gogla = pd.read_csv(raw_dir / "gogla.csv") if (raw_dir / "gogla.csv").exists() else None
    return RawLayers(
        population_density=pop_total / spec.res_km**2,
        nighttime_radiance=night,
        relative_wealth=wealth,
        solar_resource=solar,
        grid_lines=_read_vector(raw_dir / "grid.geojson"),
        minigrids=_read_vector(raw_dir / "minigrids.geojson"),
        surveys=pd.read_csv(raw_dir / "surveys.csv"),
        gogla=gogla,
        is_demo=False,
        sources={f: REQUIRED_FILES.get(f, OPTIONAL_FILES.get(f, "")) for f in REQUIRED_FILES},
    )


def load_raw_layers(settings: Settings, country: Country, grid: gpd.GeoDataFrame, spec: GridSpec) -> RawLayers:
    if settings.demo_mode:
        from .demo_generator import generate_demo

        return generate_demo(settings, country, grid, spec)
    return _load_real(settings, country, grid, spec)
