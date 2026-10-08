"""Loads (and lazily builds) per-country artefacts and caches them in memory."""
from __future__ import annotations

import json
import logging
import threading
from functools import lru_cache

import pandas as pd

from ..config import Settings, get_settings
from ..pipeline.spatial_processing import GridSpec

logger = logging.getLogger(__name__)


class DataNotReadyError(RuntimeError):
    pass


class DataService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._cache: dict[str, dict] = {}
        self._lock = threading.Lock()

    def is_ready(self, code: str) -> bool:
        return (self.settings.outputs_path(code) / "cells.csv").exists() and \
               (self.settings.models_path(code) / "metrics.json").exists()

    def ensure(self, code: str) -> None:
        """Build dataset + train if artefacts are missing (first start)."""
        if self.is_ready(code):
            return
        with self._lock:
            if self.is_ready(code):
                return
            from ..ml.train import build_and_train

            logger.info("No artefacts for %s - running pipeline and training", code)
            try:
                build_and_train(self.settings, code)
            except Exception as exc:
                raise DataNotReadyError(str(exc)) from exc

    def reload(self, code: str) -> None:
        self._cache.pop(code, None)

    def _load(self, code: str) -> dict:
        code = code.upper()
        if code not in self._cache:
            self.ensure(code)
            pdir, mdir, odir = (self.settings.processed_path(code), self.settings.models_path(code),
                                self.settings.outputs_path(code))
            meta = json.loads((pdir / "meta.json").read_text())
            gogla = pd.read_csv(pdir / "gogla.csv") if (pdir / "gogla.csv").exists() else None
            self._cache[code] = {
                "cells": pd.read_csv(odir / "cells.csv"),
                "meta": meta,
                "spec": GridSpec(**meta["grid_spec"]),
                "metrics": json.loads((mdir / "metrics.json").read_text()),
                "importance": json.loads((mdir / "feature_importance.json").read_text()),
                "infrastructure": json.loads((pdir / "infrastructure.geojson").read_text()),
                "gogla": gogla,
            }
        return self._cache[code]

    def cells(self, code: str) -> pd.DataFrame:
        return self._load(code)["cells"]

    def meta(self, code: str) -> dict:
        return self._load(code)["meta"]

    def spec(self, code: str) -> GridSpec:
        return self._load(code)["spec"]

    def metrics(self, code: str) -> dict:
        return self._load(code)["metrics"]

    def importance(self, code: str) -> dict:
        return self._load(code)["importance"]

    def infrastructure(self, code: str) -> dict:
        return self._load(code)["infrastructure"]

    def gogla(self, code: str) -> pd.DataFrame | None:
        return self._load(code)["gogla"]


@lru_cache
def get_data_service() -> DataService:
    return DataService(get_settings())
