// Sequential single-hue ramps. Deliberately no red/green "traffic light" colours,
// so the map does not imply certainty.
export const PALETTES = {
  solar_penetration: ["#f1f6f5", "#b9dcd6", "#6fb8ae", "#2f8c84", "#0b5550"],
  market_gap: ["#fbf3dc", "#f4d98a", "#e8b04a", "#c97d1f", "#8a4a0c"],
  population: ["#f4f1f8", "#cfc3e3", "#a28ac6", "#7152a3", "#43276f"],
  night_lights: ["#0f1b2e", "#2d3f66", "#6a7fa6", "#c9c28a", "#f6e7a1"],
  grid: ["#eef2f6", "#c3cfdc", "#8ea1b8", "#56708f", "#2a3f5c"],
  solar_resource: ["#fff6d8", "#fbe08a", "#f6c244", "#eb9b1d", "#c96a0b"],
};

const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

export function rampColor(stops, t) {
  if (t == null || Number.isNaN(t)) return "#c9d1da";
  const x = Math.min(1, Math.max(0, t)) * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(x));
  const f = x - i;
  const a = rgb(stops[i]);
  const b = rgb(stops[i + 1]);
  return "#" + a.map((v, k) => Math.round(v + (b[k] - v) * f).toString(16).padStart(2, "0")).join("");
}

export const gradientCss = (stops) => `linear-gradient(to right, ${stops.join(",")})`;
