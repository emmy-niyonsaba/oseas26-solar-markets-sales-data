# Data sources

The same content is served by `GET /api/data-sources` (see `backend/app/data_sources.py`).
Expected files for `DEMO_MODE=false` in `backend/data/raw/<CODE>/`:

| File | Content | Required |
|---|---|---|
| `surveys.csv` | `latitude, longitude, solar_ownership[, electricity_access, n_households]` | yes |
| `population.tif` | WorldPop / Meta HRSL, people per pixel | yes |
| `night_lights.tif` | Black Marble annual radiance | yes |
| `solar_resource.tif` | Global Solar Atlas GHI (kWh/m2/day) | yes |
| `relative_wealth.csv` | `latitude, longitude, rwi` | yes |
| `grid.geojson` | Gridfinder / OSM / EAE lines | yes |
| `minigrids.geojson` | minigrid points or lines | no |
| `boundary.geojson` | country polygon | no (bbox is used) |
| `gogla.csv` | `country, reported_sales, product_category, year` | no |

Rasters may be in any CRS and resolution; they are reprojected onto the common grid
(sum for population, average for the others).
