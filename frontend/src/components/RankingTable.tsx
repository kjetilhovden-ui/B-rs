import type { AssetRanking } from '../lib/types'
import { formatPrice, formatScore } from '../lib/format'
import { HorizonBadge } from './HorizonBadge'
import { ReportCalendarBadge } from './ReportCalendarBadge'

export function RankingTable({
  assets,
  reportWarningDays,
}: {
  assets: AssetRanking[]
  reportWarningDays: number
}) {
  const ranked = assets.filter((a) => a.score !== null)
  const missingData = assets.filter((a) => a.score === null)

  return (
    <div className="table-scroll">
      <table className="ranking-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Navn</th>
            <th>Type</th>
            <th>Score</th>
            <th>Tidshorisont</th>
            <th>Rapportdato</th>
            <th>Siste kurs</th>
          </tr>
        </thead>
        <tbody>
          {ranked.map((asset, i) => (
            <AssetRow key={asset.ticker} asset={asset} rank={i + 1} reportWarningDays={reportWarningDays} />
          ))}
        </tbody>
        {missingData.length > 0 && (
          <>
            <tbody>
              <tr className="ranking-table__section-divider">
                <td colSpan={7}>Mangler data</td>
              </tr>
            </tbody>
            <tbody>
              {missingData.map((asset) => (
                <AssetRow key={asset.ticker} asset={asset} rank={null} reportWarningDays={reportWarningDays} />
              ))}
            </tbody>
          </>
        )}
      </table>
    </div>
  )
}

function AssetRow({
  asset,
  rank,
  reportWarningDays,
}: {
  asset: AssetRanking
  rank: number | null
  reportWarningDays: number
}) {
  return (
    <tr className={asset.data_status !== 'ok' ? 'ranking-table__row--missing' : ''}>
      <td>{rank ?? '–'}</td>
      <td>
        <div className="asset-name">{asset.name}</div>
        <div className="asset-ticker">{asset.ticker}</div>
        {asset.data_status !== 'ok' && (
          <div className="asset-data-note">
            Data ikke tilgjengelig{asset.data_note ? `: ${asset.data_note}` : ''}
          </div>
        )}
      </td>
      <td>
        <span className={`type-badge type-badge--${asset.asset_type}`}>
          {asset.asset_type === 'fond' ? 'Fond' : 'Aksje'}
        </span>
      </td>
      <td className="score-cell">{formatScore(asset.score)}</td>
      <td>
        <HorizonBadge horizon={asset.horizon} explanation={asset.horizon_explanation} />
      </td>
      <td>
        <ReportCalendarBadge nextReportDate={asset.next_report_date} warningDays={reportWarningDays} />
      </td>
      <td>{formatPrice(asset.latest_close)}</td>
    </tr>
  )
}
