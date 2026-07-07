import { useEffect, useState } from 'react'
import type { OutlookData, RankingData, StatusData } from './types'

interface DailyData {
  ranking: RankingData | null
  status: StatusData | null
  outlook: OutlookData | null
  loading: boolean
  error: string | null
}

// Fetches the static JSON files the daily GitHub Actions job writes into
// public/data/. No backend server involved - this is just fetch() against
// files served alongside the rest of the static site.
export function useDailyData(): DailyData {
  const [ranking, setRanking] = useState<RankingData | null>(null)
  const [status, setStatus] = useState<StatusData | null>(null)
  const [outlook, setOutlook] = useState<OutlookData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const base = import.meta.env.BASE_URL

    async function load() {
      try {
        const [rankingRes, statusRes] = await Promise.all([
          fetch(`${base}data/ranking.json`),
          fetch(`${base}data/status.json`),
        ])
        if (!rankingRes.ok) throw new Error('Fant ikke ranking.json')
        setRanking(await rankingRes.json())
        if (statusRes.ok) setStatus(await statusRes.json())

        // Outlook is optional - not having it yet shouldn't break the page.
        try {
          const outlookRes = await fetch(`${base}data/outlook.json`)
          if (outlookRes.ok) setOutlook(await outlookRes.json())
        } catch {
          // ignore - outlook panel just won't render
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ukjent feil ved lasting av data')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  return { ranking, status, outlook, loading, error }
}
