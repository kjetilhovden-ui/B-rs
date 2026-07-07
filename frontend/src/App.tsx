import './App.css'
import { DisclaimerBanner } from './components/DisclaimerBanner'
import { LastUpdatedStamp } from './components/LastUpdatedStamp'
import { MarketOutlookPanel } from './components/MarketOutlookPanel'
import { RankingTable } from './components/RankingTable'
import { useDailyData } from './lib/useDailyData'

function App() {
  const { ranking, status, outlook, loading, error } = useDailyData()

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Oslo Børs Case-finner</h1>
        <p className="app-subtitle">Rangering av aksjer og fond etter antatt fremtidig potensiale</p>
      </header>

      <DisclaimerBanner />

      {loading && <p className="state-message">Laster data ...</p>}

      {error && (
        <p className="state-message state-message--error">
          Klarte ikke laste data: {error}. Prøv å laste siden på nytt om litt.
        </p>
      )}

      {status && status.warnings.length > 0 && (
        <details className="warnings-box">
          <summary>{status.warnings.length} advarsel(er) fra siste oppdatering</summary>
          <ul>
            {status.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </details>
      )}

      {ranking && (
        <section>
          <LastUpdatedStamp isoTimestamp={ranking.generated_at} />
          <RankingTable assets={ranking.assets} reportWarningDays={ranking.report_warning_days} />
        </section>
      )}

      {outlook && <MarketOutlookPanel outlook={outlook} />}
    </div>
  )
}

export default App
