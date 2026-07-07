// Mirrors the JSON shape written by etl/etl/export/export_json.py.
// If you change a field on one side, change it on the other too.

export interface FactorScores {
  momentum: number | null
  growth: number | null
  valuation: number | null
  reaction: number | null
}

export interface RawFactors {
  momentum_pct: number | null
  growth_pct: number | null
  earnings_yield: number | null
  reaction_pct: number | null
}

export type AssetType = 'aksje' | 'fond'
export type DataStatus = 'ok' | 'missing' | 'stale'

export interface AssetRanking {
  ticker: string
  name: string
  asset_type: AssetType
  sector: string | null
  score: number | null
  factor_scores: FactorScores
  raw_factors: RawFactors
  horizon: string
  horizon_explanation: string
  next_report_date: string | null
  latest_close: number | null
  data_status: DataStatus
  data_note: string | null
}

export interface RankingData {
  generated_at: string
  default_weights: Record<string, number>
  report_warning_days: number
  assets: AssetRanking[]
}

export interface StatusData {
  generated_at: string
  last_run_status: 'ok' | 'partial' | 'failed'
  warnings: string[]
  asset_count: number
}

export interface OutlookEntry {
  published_date: string
  body_markdown: string
}

export interface OutlookData {
  generated_at: string
  entries: OutlookEntry[]
}
