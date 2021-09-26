function deepCopy(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Map a value from source range to target range.
 *
 *   Example:
 *     mapRange(0, 100, 10, 20, 50)
 *     >>> 15.0
 *
 *   Based on the rosettacode implementation.
 *
 *   Args:
 *     sourceMin (Number): Lower border of source range
 *     sourceMax (Number): Higher border of source range
 *     targetMin (Number): Lower border of target range
 *     targetMax (Number): Higher border of target range
 *
 *   Returns:
 *     Number: The mapped value
 *
 */
function mapRange(sourceMin, sourceMax, targetMin, targetMax, value) {
  return (
    targetMin + (
      (value - sourceMin) *
      (targetMax - targetMin) /
      (sourceMax - sourceMin)
    )
  );
}
