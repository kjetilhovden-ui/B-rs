import type { AssetRanking } from '../lib/types'
import { formatPercent, formatPrice } from '../lib/format'
import { HorizonBadge } from './HorizonBadge'
import { PredictionEstimate } from './PredictionEstimate'
import { ReportCalendarBadge } from './ReportCalendarBadge'

const TOP_PICKS_COUNT = 3

// The "more intuitive" entry point to the page: instead of making people
// read a dense table to figure out what matters, lead with the handful of
// cases that currently rank highest.
export function TopPicks({ assets, reportWarningDays }: { assets: AssetRanking[]; reportWarningDays: number }) {
  const picks = assets.filter((a) => a.score !== null).slice(0, TOP_PICKS_COUNT)
  if (picks.length === 0) return null

  return (
    <section className="top-picks">
      <h2>Beste case akkurat nå</h2>
      <p className="top-picks__subtitle">
        De høyest rangerte casene ut fra dagens score. Beslutningsstøtte, ikke en kjøpsanbefaling — se alltid på
        helheten før du bestemmer deg.
      </p>
      <div className="top-picks__grid">
        {picks.map((asset, i) => (
          <article className="top-pick-card" key={asset.ticker}>
            <div className="top-pick-card__rank">#{i + 1}</div>
            <div className="top-pick-card__name">{asset.name}</div>
            <div className="top-pick-card__ticker">
              {asset.ticker}
              <span className={`type-badge type-badge--${asset.asset_type}`}>
                {asset.asset_type === 'fond' ? 'Fond' : 'Aksje'}
              </span>
            </div>
            <div className="top-pick-card__price-row">
              <span className="top-pick-card__price-label">Dagens kurs</span>
              <span className="top-pick-card__price-value">{formatPrice(asset.latest_close)} kr</span>
            </div>
            <ChangeRow label="Potensiell økning (7 dager)" pct={asset.prediction?.week.projected_return_pct ?? null} />
            <ChangeRow label="Potensiell økning (31 dager)" pct={asset.prediction?.month.projected_return_pct ?? null} />
            <HorizonBadge horizon={asset.horizon} explanation={asset.horizon_explanation} />
            <p className="top-pick-card__why">
              <strong>Årsak:</strong> {asset.horizon_explanation}
            </p>
            <PredictionEstimate prediction={asset.prediction} />
            <ReportCalendarBadge nextReportDate={asset.next_report_date} warningDays={reportWarningDays} />
          </article>
        ))}
      </div>
    </section>
  )
}

function ChangeRow({ label, pct }: { label: string; pct: number | null }) {
  return (
    <div className="top-pick-card__price-row">
      <span className="top-pick-card__price-label">{label}</span>
      <span
        className={`top-pick-card__change ${
          pct !== null && pct < 0 ? 'top-pick-card__change--negative' : 'top-pick-card__change--positive'
        }`}
      >
        {pct !== null ? formatPercent(pct) : 'Ikke nok historikk'}
      </span>
    </div>
  )
}
