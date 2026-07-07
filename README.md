# Oslo Børs Case-finner

En personlig app som rangerer aksjer og fond fra Oslo Børs etter antatt
fremtidig potensiale, som beslutningsstøtte for videre research — **ikke**
investeringsrådgivning eller automatisert trading.

## Hvordan bruke appen

Nettsiden ligger på GitHub Pages og oppdateres av en daglig automatisk jobb
(se under). Du åpner den bare i Safari på iPad-en din som en vanlig
nettside — ingenting å installere.

## Hvordan oppdatere dataene selv

Alle disse filene kan redigeres direkte i nettleseren via GitHub (fungerer
fint fra iPad Safari — trykk på blyant-ikonet på filen):

- `data/manual/assets.yaml` — hvilke aksjer/fond som er med i rangeringen
- `data/manual/report_dates.yaml` — kommende kvartalsrapport-datoer
- `data/manual/market_outlook.md` — markedskommentaren din, legg nyeste øverst

Etter en endring: gå til **Actions**-fanen → **Daglig oppdatering** → **Run
workflow** for å oppdatere siden med det nye med en gang (ellers skjer det
automatisk neste virkedag morgen når automatikken er skrudd på).

## Repo-struktur

```
data/manual/     Filene du redigerer selv (aksjeliste, rapportdatoer, markedsutsikter)
data/history.db  SQLite-database, oppdateres automatisk av den daglige jobben
etl/             Python: henter kursdata, regner ut score, eksporterer JSON
frontend/        React-nettsiden (Vite), leser JSON-filene og viser rangeringen
docs/            Notater/research, bl.a. om datakilder
```

## Byggerekkefølge

Prosjektet bygges i faser — se den fulle planen i
`/root/.claude/plans/prosjekt-oslo-b-rs-case-finner-valiant-pie.md` for
detaljer om hver fase og hvorfor de tekniske valgene ble tatt som de ble.

## For utvikling lokalt (valgfritt)

Du trenger ikke dette for å bruke appen — det er bare til referanse hvis du
(eller en fremtidig Claude Code-økt) vil kjøre ting lokalt:

```
# ETL
cd etl
pip install -r requirements.txt
python -m etl.run_daily     # henter data, regner score, skriver JSON
python -m pytest            # kjører scoring-testene

# Frontend
cd frontend
npm install
npm run dev                 # http://localhost:5173
npm run build                # bygger til frontend/dist
```
