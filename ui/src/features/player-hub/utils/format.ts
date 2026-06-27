export function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(", ") : "—";
  }
  if (typeof value === "number") {
    if (Number.isInteger(value)) {
      return value.toLocaleString();
    }
    return value.toLocaleString(undefined, { maximumFractionDigits: 3 });
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  return String(value);
}

export function formatStat(value: unknown, suffix = ""): string {
  const formatted = formatValue(value);
  return formatted === "—" ? formatted : `${formatted}${suffix}`;
}

export function seasonLabel(seasonEndYear: number): string {
  const start = seasonEndYear - 1;
  return `${start}-${String(seasonEndYear).slice(-2)}`;
}

export function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

export function seasonEndYearFromLabel(value: unknown): number | null {
  if (typeof value !== "string") {
    return null;
  }
  const match = /^(\d{4})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }
  const start = Number(match[1]);
  let end = Math.floor(start / 100) * 100 + Number(match[2]);
  if (end <= start) {
    end += 100;
  }
  return end;
}
