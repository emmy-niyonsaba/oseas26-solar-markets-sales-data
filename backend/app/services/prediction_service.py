"""Business logic on top of predictions: statistics, cell details, GOGLA sanity check."""
from __future__ import annotations

import pandas as pd

from ..config import Settings
from ..schemas.schemas import CellDetails, GoglaComparison, GoglaRow, Statistics

GOGLA_CAVEAT = (
    "GOGLA reports aggregated national sales, not pixel-level penetration or households currently "
    "using a product. Treat this as a coarse sanity check only."
)


def interpret(pred: float, gap: float, threshold: float) -> str:
    if gap >= threshold:
        return "Potentially underserved area. Further field validation is recommended."
    if pred >= 0.66:
        return "High predicted solar penetration. Market may already be well served; verify locally."
    if pred <= 0.33:
        return "Low predicted solar penetration, but energy need is limited relative to other areas. Area requiring further investigation."
    return "Moderate predicted solar penetration. Area requiring further investigation."


def cell_details(row: pd.Series, code: str, is_demo: bool, threshold: float) -> CellDetails:
    obs = row.get("observed_solar_penetration")
    return CellDetails(
        cell_id=row["cell_id"], country=code, latitude=row["lat"], longitude=row["lon"],
        population=row["population_total"], population_density=row["population_density"],
        nighttime_radiance=row["nighttime_radiance"], relative_wealth=row["relative_wealth"],
        distance_to_grid_km=row["distance_to_grid_km"], distance_to_minigrid_km=row["distance_to_minigrid_km"],
        grid_presence=int(row["grid_presence"]), solar_resource=row["solar_resource"],
        observed_solar_penetration=None if pd.isna(obs) else float(obs),
        predicted_solar_penetration=row["predicted_solar_penetration"],
        energy_need_score=row["energy_need_score"], market_gap_score=row["market_gap_score"],
        potentially_underserved=bool(row["market_gap_score"] >= threshold),
        interpretation=interpret(row["predicted_solar_penetration"], row["market_gap_score"], threshold),
        is_demo=is_demo,
    )


def statistics(cells: pd.DataFrame, metrics: dict, settings: Settings, code: str,
               is_demo: bool, threshold: float) -> Statistics:
    gap = cells["market_gap_score"] >= threshold
    pred = cells["predicted_solar_penetration"]
    pop = cells["population_total"]
    return Statistics(
        country=code, is_demo=is_demo, threshold=threshold,
        total_area_km2=float(len(cells) * settings.grid_resolution_km**2),
        total_population=float(pop.sum()), n_cells=len(cells),
        avg_predicted_penetration=float(pred.mean()),
        population_weighted_penetration=float((pred * pop).sum() / pop.sum()) if pop.sum() > 0 else 0.0,
        potentially_underserved_cells=int(gap.sum()),
        population_in_gap_areas=float(pop[gap].sum()),
        high_penetration_cells=int((pred >= settings.high_penetration_threshold).sum()),
        low_penetration_cells=int((pred <= settings.low_penetration_threshold).sum()),
        model_r2_random=metrics["random_cv"]["r2"], model_r2_spatial=metrics["spatial_cv"]["r2"],
    )


def gogla_comparison(cells: pd.DataFrame, gogla: pd.DataFrame | None, settings: Settings,
                     is_demo: bool) -> GoglaComparison:
    if gogla is None or gogla.empty:
        return GoglaComparison(available=False, is_demo=is_demo, caveat=GOGLA_CAVEAT +
                               " No gogla.csv found for this country.")
    est = float((cells["predicted_solar_penetration"] * cells["population_total"]).sum()
                / settings.avg_household_size)
    total = float(gogla["reported_sales"].sum())
    return GoglaComparison(
        available=True, is_demo=is_demo,
        rows=[GoglaRow(product_category=r.product_category, year=int(r.year), reported_sales=float(r.reported_sales))
              for r in gogla.itertuples()],
        total_reported_sales=total, model_estimated_solar_households=est,
        ratio_model_to_reported=est / total if total else None, caveat=GOGLA_CAVEAT,
    )
