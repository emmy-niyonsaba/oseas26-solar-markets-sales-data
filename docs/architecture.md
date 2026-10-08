# Architecture

```
Raw data / DEMO generator
  -> pipeline/ingestion.py          load layers (demo or data/raw/<CODE>/)
  -> pipeline/cleaning.py           validate, fill gaps, clip
  -> pipeline/spatial_processing.py common grid, reprojection, raster resampling
  -> pipeline/feature_engineering.py distances, presence flags, settlement density
  -> pipeline/build.py              writes data/processed/<CODE>/ (cells_features.csv, training.csv, ...)
  -> ml/validation.py + train.py    random CV, spatial blocked CV, RF + XGBoost, model selection
  -> ml/predict.py                  clamp 0-1 predictions, need score, market gap score
  -> outputs/<CODE>/                cells.csv, solar_penetration.tif, market_gap.tif, *.geojson
  -> services/ + api/               FastAPI (read-only REST)
  -> frontend/                      React + Leaflet dashboard
```

* **Country-agnostic.** Everything is keyed by a country code. Add an entry to `app/countries.py`
  (bbox, UTM EPSG, demo cities) and set the files in `data/raw/<CODE>/`.
* **One grid.** Cells are regular lat/lon squares of `GRID_RESOLUTION_KM`. Cell `row`/`col` align
  exactly with the output GeoTIFF, so raster and vector outputs always match.
* **Artefacts on disk, cache in memory.** The API never trains per request. On first start (or when
  artefacts are missing) `DataService.ensure()` runs the pipeline once.
* **EAE-ready.** Read-only JSON/GeoJSON/GeoTIFF endpoints; no coupling to the frontend.
