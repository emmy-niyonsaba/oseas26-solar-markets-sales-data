# Methodology

**Target.** `solar_penetration` in [0, 1]: household-weighted share of households owning a solar
product in a grid cell, aggregated from survey clusters (`solar_ownership`).

**Features** (configurable with `FEATURES`): population density, nighttime radiance, relative wealth,
solar resource, distance to grid, distance to minigrid, grid presence, minigrid presence and
settlement density (mean density over a ~3x3 neighbourhood). Nighttime radiance is only one predictor:
low light is never interpreted as "no solar".

**Models.** Random Forest and XGBoost regressors. The one with the lowest spatial-CV RMSE is used to
predict every cell; predictions are clamped to [0, 1].

**Validation.**
* *Random CV*: shuffled K-fold. Optimistic when neighbouring cells are similar.
* *Spatial blocked CV*: cells are grouped into `SPATIAL_BLOCK_KM` blocks, whole blocks are held out
  (GroupKFold) and training cells within `SPATIAL_BUFFER_KM` of any test cell are removed.
Reported metrics are pooled out-of-fold MAE, RMSE and R². Nothing is hard-coded.

**Feature importance.** Normalised importance from the fitted model. It describes the model, not causes.

**Potential Market Gap Indicator.**
`energy_need_score` = weighted mean of (scaled log population density, scaled distance to grid,
1 - scaled log radiance), weights `NEED_W_*`; scaling uses the 2nd-98th percentile of the country.
`market_gap_score = energy_need_score * (1 - predicted_solar_penetration)`.
This is a screening heuristic for areas that merit investigation, not an investment model.

**GOGLA.** Used only as a national control total: model-estimated households with solar
(`sum(pred * population / household size)`) is compared with reported sales.
