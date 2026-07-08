export function formatPercent(value: number | null, decimals = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  const pct = value * 100
  const sign = pct > 0 ? '+' : ''
  return `${sign}${pct.toFixed(decimals)} %`
}

export function formatPrice(value: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  return new Intl.NumberFormat('nb-NO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
}

export function formatDate(iso: string | null): string {
  if (!iso) return '–'
  const d = new Date(iso + 'T00:00:00')
  return new Intl.DateTimeFormat('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' }).format(d)
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso)
  return new Intl.DateTimeFormat('nb-NO', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d)
}

// Deliberately computed client-side (never baked into the JSON export) so
// the countdown - and the red "under 14 days" warning - never goes stale
// between the days the site happens to be opened.
export function daysUntil(iso: string | null): number | null {
  if (!iso) return null
  const target = new Date(iso + 'T00:00:00')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diffMs = target.getTime() - today.getTime()
  return Math.round(diffMs / (1000 * 60 * 60 * 24))
}
