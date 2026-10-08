export const fmtInt = (n) => (n == null ? "-" : Math.round(n).toLocaleString("en-US"));
export const fmtNum = (n, d = 2) => (n == null ? "-" : Number(n).toFixed(d));
export const fmtPct = (n, d = 0) => (n == null ? "-" : `${(n * 100).toFixed(d)}%`);
export const fmtCompact = (n) =>
  n == null ? "-" : Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(n);
