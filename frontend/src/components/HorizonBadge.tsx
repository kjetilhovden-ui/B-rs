const HORIZON_CLASS: Record<string, string> = {
  'Kort sikt (uker)': 'horizon-badge--short',
  'Middels sikt (6–12 mnd)': 'horizon-badge--medium',
  'Lang sikt (1–3 år)': 'horizon-badge--long',
  'Usikker horisont': 'horizon-badge--uncertain',
}

export function HorizonBadge({ horizon, explanation }: { horizon: string; explanation: string }) {
  return (
    <span className={`horizon-badge ${HORIZON_CLASS[horizon] ?? ''}`} title={explanation}>
      {horizon}
    </span>
  )
}
