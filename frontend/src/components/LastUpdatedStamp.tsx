import { formatDateTime } from '../lib/format'

// Each panel shows its OWN "last updated" timestamp rather than one global
// clock, since ranking.json (updated every weekday morning) and
// outlook.json (updated sporadically by hand) must never be conflated.
export function LastUpdatedStamp({ isoTimestamp, label }: { isoTimestamp: string; label?: string }) {
  return (
    <p className="last-updated">
      {label ?? 'Sist oppdatert'}: {formatDateTime(isoTimestamp)}
    </p>
  )
}
