import { daysUntil, formatDate } from '../lib/format'

export function ReportCalendarBadge({
  nextReportDate,
  warningDays,
}: {
  nextReportDate: string | null
  warningDays: number
}) {
  if (!nextReportDate) {
    return <span className="report-badge report-badge--unknown">Ingen kjent dato</span>
  }

  const days = daysUntil(nextReportDate)
  const isImminent = days !== null && days <= warningDays && days >= 0
  const isPast = days !== null && days < 0

  return (
    <span
      className={`report-badge ${isImminent ? 'report-badge--warning' : ''}`}
      title={formatDate(nextReportDate)}
    >
      {isPast
        ? `Rapport ${formatDate(nextReportDate)}`
        : days === 0
          ? 'Rapport i dag'
          : `Rapport om ${days} ${days === 1 ? 'dag' : 'dager'}`}
    </span>
  )
}
