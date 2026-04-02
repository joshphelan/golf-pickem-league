/**
 * Parse a date-only ISO string (YYYY-MM-DD) as local time.
 *
 * JavaScript's `new Date("2025-04-09")` treats date-only strings as UTC
 * midnight per spec, which in US timezones (e.g. ET = UTC-4) shifts the
 * displayed date back to the prior day. Appending T12:00:00 interprets
 * the value as local noon, safely away from any day-boundary or DST edge.
 */
export function parseLocalDate(dateStr: string): Date {
  return new Date(dateStr + 'T12:00:00');
}
