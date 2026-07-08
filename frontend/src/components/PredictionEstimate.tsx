import type { PricePrediction } from '../lib/types'
import { formatPercent, formatPrice } from '../lib/format'

// Always labeled as an uncertain, rough estimate - never framed as a
// guaranteed target. See etl/etl/scoring/prediction.py for the (simple)
// method behind it.
export function PredictionEstimate({ prediction }: { prediction: PricePrediction | null }) {
  if (!prediction) {
    return <span className="prediction-estimate prediction-estimate--unavailable">Ikke nok historikk</span>
  }

  return (
    <div className="prediction-estimate-block">
      <PredictionRow label="Om 7 dager" range={prediction.week} />
      <PredictionRow label="Om 31 dager" range={prediction.month} />
      <p className="prediction-disclaimer">Usikkert estimat basert på nylig kursutvikling og svingning - ingen garanti.</p>
    </div>
  )
}

function PredictionRow({ label, range }: { label: string; range: PricePrediction['week'] }) {
  return (
    <div className="prediction-row">
      <span className="prediction-row__label">{label}</span>
      <span className="prediction-row__range">
        {formatPrice(range.low)}–{formatPrice(range.high)} kr
        <span
          className={
            range.projected_return_pct < 0
              ? 'prediction-row__pct prediction-row__pct--negative'
              : 'prediction-row__pct prediction-row__pct--positive'
          }
        >
          ({formatPercent(range.projected_return_pct)})
        </span>
      </span>
    </div>
  )
}
