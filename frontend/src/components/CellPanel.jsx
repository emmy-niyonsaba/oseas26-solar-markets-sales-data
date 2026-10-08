import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { fmtInt, fmtNum, fmtPct } from "../utils/format";
import AsyncView from "./AsyncView";

const Row = ({ label, value }) => (
  <div className="kv">
    <dt>{label}</dt>
    <dd>{value}</dd>
  </div>
);

export default function CellPanel({ cellId, threshold }) {
  const state = useApi(() => (cellId ? api.cell(cellId, threshold) : Promise.resolve(null)), [cellId, threshold]);

  return (
    <aside className="panel cellpanel" aria-live="polite">
      <h2>Area details</h2>
      {!cellId ? (
        <p className="muted">Click a cell on the map to see its details.</p>
      ) : (
        <AsyncView state={state} label="Loading cell..." isEmpty={(d) => !d || d.cell_id !== cellId} empty="Loading cell...">
          {(c) => (
            <>
              <p className="cell-id">{c.cell_id}{c.is_demo && " (demo data)"}</p>
              <dl>
                <Row label="Population" value={fmtInt(c.population)} />
                <Row label="Predicted solar penetration" value={fmtPct(c.predicted_solar_penetration)} />
                {c.observed_solar_penetration != null && (
                  <Row label="Survey-observed (this cell)" value={fmtPct(c.observed_solar_penetration)} />
                )}
                <Row label="Distance to grid" value={`${fmtNum(c.distance_to_grid_km, 1)} km`} />
                <Row label="Solar resource" value={`${fmtNum(c.solar_resource, 1)} kWh/m²/day`} />
                <Row label="Relative wealth" value={fmtNum(c.relative_wealth, 2)} />
                <Row label="Nighttime radiance" value={fmtNum(c.nighttime_radiance, 2)} />
                <Row label="Potential market gap" value={fmtPct(c.market_gap_score)} />
              </dl>
              <div className={`interpretation ${c.potentially_underserved ? "flag" : ""}`}>
                <strong>Interpretation</strong>
                <p>{c.interpretation}</p>
              </div>
            </>
          )}
        </AsyncView>
      )}
    </aside>
  );
}
