export function toFiniteNumber(value, fallback = 0) {
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue : fallback;
}

export function clampNumber(value, min, max) {
  return Math.min(Math.max(toFiniteNumber(value, min), min), max);
}

export function formatNumber(value, digits = 2) {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return "—";
  }
  const rounded = Number(numericValue.toFixed(digits));
  return Object.is(rounded, -0) ? "0" : String(rounded);
}

export function formatMm(value, digits = 2) {
  const text = formatNumber(value, digits);
  return text === "—" ? text : `${text} mm`;
}

export function formatXyz(point, digits = 2) {
  if (!Array.isArray(point) || point.length < 3) {
    return "—";
  }
  return `(${formatNumber(point[0], digits)}, ${formatNumber(point[1], digits)}, ${formatNumber(point[2], digits)})`;
}

export function shallowObjectValuesEqual(left, right) {
  const leftKeys = Object.keys(left || {});
  const rightKeys = Object.keys(right || {});
  if (leftKeys.length !== rightKeys.length) {
    return false;
  }
  return leftKeys.every((key) => Object.hasOwn(right || {}, key) && left?.[key] === right?.[key]);
}
