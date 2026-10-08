from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class CountryInfo(BaseModel):
    code: str
    name: str
    center: tuple[float, float]
    zoom: int
    bbox: tuple[float, float, float, float]
    ready: bool = Field(description="True once predictions exist for this country")


class AppMeta(BaseModel):
    country: str
    country_name: str
    is_demo: bool
    grid_resolution_km: float
    n_cells: int
    n_labelled_cells: int
    bounds: list[float]
    selected_model: str
    features: list[str]
    underserved_threshold: float
    disclaimer: str


class LayerInfo(BaseModel):
    id: str
    name: str
    description: str
    unit: str


class CellDetails(BaseModel):
    cell_id: str
    country: str
    latitude: float
    longitude: float
    population: float
    population_density: float
    nighttime_radiance: float
    relative_wealth: float
    distance_to_grid_km: float
    distance_to_minigrid_km: float
    grid_presence: int
    solar_resource: float
    observed_solar_penetration: float | None = None
    predicted_solar_penetration: float
    energy_need_score: float
    market_gap_score: float
    potentially_underserved: bool
    interpretation: str
    is_demo: bool


class MetricSet(BaseModel):
    mae: float
    rmse: float
    r2: float
    n_folds: int | None = None
    n_evaluated: int | None = None
    n_blocks: int | None = None
    block_km: float | None = None
    buffer_km: float | None = None


class ModelResult(BaseModel):
    random_cv: MetricSet
    spatial_cv: MetricSet


class ModelPerformance(BaseModel):
    country: str
    is_demo: bool
    selected_model: str
    selection_criterion: str
    n_samples: int
    features: list[str]
    trained_at: str
    random_cv: MetricSet
    spatial_cv: MetricSet
    models: dict[str, ModelResult]
    note: str


class FeatureImportanceItem(BaseModel):
    feature: str
    label: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    title: str = "Model feature importance"
    selected_model: str
    is_demo: bool
    importance: list[FeatureImportanceItem]
    by_model: dict[str, list[FeatureImportanceItem]]
    warning: str


class Statistics(BaseModel):
    country: str
    is_demo: bool
    threshold: float
    total_area_km2: float
    total_population: float
    n_cells: int
    avg_predicted_penetration: float
    population_weighted_penetration: float
    potentially_underserved_cells: int
    population_in_gap_areas: float
    high_penetration_cells: int
    low_penetration_cells: int
    model_r2_random: float
    model_r2_spatial: float


class DataSource(BaseModel):
    id: str
    name: str
    description: str
    year: str
    resolution: str
    role: str
    limitations: str
    demo_substitute: str


class GoglaRow(BaseModel):
    product_category: str
    year: int
    reported_sales: float


class GoglaComparison(BaseModel):
    available: bool
    is_demo: bool
    rows: list[GoglaRow] = []
    total_reported_sales: float | None = None
    model_estimated_solar_households: float | None = None
    ratio_model_to_reported: float | None = None
    caveat: str
