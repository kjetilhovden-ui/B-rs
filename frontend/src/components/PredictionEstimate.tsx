import type { PricePrediction } from '../lib/types'
import { formatPrice } from '../lib/format'

// Always labeled as an uncertain, rough estimate - never framed as a
// guaranteed target. See etl/etl/scoring/prediction.py for the (simple)
// method behind it.
export function PredictionEstimate({ prediction, compact }: { prediction: PricePrediction | null; compact?: boolean }) {
  if (!prediction) {
    return <span className="prediction-estimate prediction-estimate--unavailable">Ikke nok historikk</span>
  }

  if (compact) {
    return (
      <span className="prediction-estimate" title="Usikkert estimat basert på nylig kursutvikling og svingning - ingen garanti">
        {formatPrice(prediction.week.low)}–{formatPrice(prediction.week.high)} kr
      </span>
    )
  }

  return (
    <div className="prediction-estimate-block">
      <PredictionRow label="Om 1 uke" range={prediction.week} />
      <PredictionRow label="Om 1 måned" range={prediction.month} />
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
      </span>
    </div>
  )
}
