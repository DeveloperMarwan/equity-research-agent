export function fmtMarketCap(val: number | null | undefined): string {
  if (val == null) return "N/A";
  if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
  if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
  if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
  return `$${val.toLocaleString()}`;
}

export function fmtNumber(val: number | null | undefined, decimals = 2): string {
  if (val == null) return "N/A";
  return val.toFixed(decimals);
}

export function fmtPercent(val: number | null | undefined): string {
  if (val == null) return "N/A";
  return `${(val * 100).toFixed(2)}%`;
}

export function fmtPrice(val: number | null | undefined): string {
  if (val == null) return "N/A";
  return `$${val.toFixed(2)}`;
}

export function fmtMultiple(val: number | null | undefined): string {
  if (val == null) return "N/A";
  return `${val.toFixed(1)}x`;
}
