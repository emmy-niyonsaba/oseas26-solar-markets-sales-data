import { fmtCompact, fmtInt, fmtNum, fmtPct } from "../utils/format";

function Card({ label, value, sub }) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
      {sub && <span className="stat-sub">{sub}</span>}
    </div>
  );
}

export default function StatCards({ s }) {
  return (
    <section className="stats" aria-label="Statistics">
      <Card label="Average solar penetration" value={fmtPct(s.avg_predicted_penetration)}
            sub={`${fmtPct(s.population_weighted_penetration)} population-weighted`} />
      <Card label="Potentially underserved areas" value={fmtInt(s.potentially_underserved_cells)}
            sub={`cells of ${fmtInt(s.n_cells)} (gap ≥ ${fmtPct(s.threshold)})`} />
      <Card label="Population in potential gap areas" value={fmtCompact(s.population_in_gap_areas)}
            sub={`of ${fmtCompact(s.total_population)} total`} />
      <Card label="Model R² (spatial CV)" value={fmtNum(s.model_r2_spatial, 2)}
            sub={`random CV: ${fmtNum(s.model_r2_random, 2)}`} />
      <Card label="High / low penetration cells" value={`${fmtInt(s.high_penetration_cells)} / ${fmtInt(s.low_penetration_cells)}`}
            sub={`${fmtInt(s.total_area_km2)} km² covered`} />
    </section>
  );
}
