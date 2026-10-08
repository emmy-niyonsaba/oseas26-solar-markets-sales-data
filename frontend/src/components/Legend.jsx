import { PALETTES, gradientCss } from "../utils/colors";
import { fmtNum } from "../utils/format";

export default function Legend({ meta }) {
  if (!meta) return null;
  const stops = PALETTES[meta.layer];
  return (
    <div className="legend" aria-label={`Legend for ${meta.name}`}>
      <strong>{meta.name}</strong>
      <div className="legend-bar" style={{ background: gradientCss(stops) }} />
      <div className="legend-labels">
        <span>{meta.legend.low}</span>
        <span>{meta.legend.mid}</span>
        <span>{meta.legend.high}</span>
      </div>
      {meta.layer === "solar_penetration" ? (
        <div className="legend-labels legend-numbers"><span>0.0</span><span>0.5</span><span>1.0</span></div>
      ) : (
        <small>
          {fmtNum(meta.min, 2)} to {fmtNum(meta.max, 2)}
          {meta.unit !== "0-1" && ` ${meta.unit}`}
          {meta.layer === "market_gap" ? " (2nd to 98th percentile of this country)" : " (2nd to 98th percentile)"}
        </small>
      )}
    </div>
  );
}
