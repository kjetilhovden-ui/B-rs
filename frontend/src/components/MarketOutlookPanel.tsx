import type { OutlookData } from '../lib/types'
import { formatDate } from '../lib/format'
import { LastUpdatedStamp } from './LastUpdatedStamp'

export function MarketOutlookPanel({ outlook }: { outlook: OutlookData }) {
  const latest = outlook.entries[0]
  if (!latest) return null

  return (
    <section className="outlook-panel">
      <h2>Markedsutsikter</h2>
      <p className="outlook-panel__date">{formatDate(latest.published_date)}</p>
      {latest.body_markdown.split('\n\n').map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
      <LastUpdatedStamp isoTimestamp={outlook.generated_at} label="Sist hentet" />
    </section>
  )
}
