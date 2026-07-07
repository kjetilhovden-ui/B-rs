# Euronext API for rapportdatoer — foreløpige funn

Status: konkret forsøk gjort (juli 2026) — konklusjon: **ikke brukbart uten
betalt/lisensiert avtale**. Se "Oppdatering" nederst.

## Bakgrunn

Rapportdatoer (`data/manual/report_dates.yaml`) er MVP-løsningen: en
manuelt vedlikeholdt liste. Brukeren foreslo å undersøke Euronexts
"Web Services" / Data Shop som en mulig automatisk kilde:
https://www.euronext.com/en/data/how-access-market-data/web-services

## Funn så langt

- Både `euronext.com/en/data/how-access-market-data/web-services` og
  `live.euronext.com/en/datashop/delayed-data` returnerte HTTP 403 på
  direkte automatisert henting (bot-blokkering), så innholdet kunne ikke
  leses direkte.
- Websøk tyder på at Euronext skiller mellom:
  - **Gratis, forsinket markedsdata** ("delayed data"), tilgjengelig for
    individuelle investorer i tråd med MiFIR-krav — dette er kursdata, ikke
    rapportdatoer.
  - **"Corporate Actions Data"** — en kommersiell/lisensiert
    datastrøm som dekker utbytte, fusjoner, noteringer/strykninger. Dette er
    trolig IKKE det samme som en kvartalsrapport-kalender.
  - **"Web Services"** — generell markedsdata-API, ser ut til å være rettet
    mot kommersielle/lisensierte kunder, ikke en enkel gratis
    selv-registrering for hobbyprosjekter.
- Konklusjon foreløpig: usikkert om Euronext faktisk har en gratis,
  enkelt-tilgjengelig kilde spesifikt for kvartalsrapport-datoer. Det kan
  hende det ikke finnes uten en betalt/lisensiert avtale.

## Neste steg (Fase 3)

1. Prøve konkret registrering for gratis "delayed data"-tilgang og se hva
   som faktisk er tilgjengelig i praksis (krever en Euronext-brukerkonto).
2. Undersøke alternative gratis kilder til rapportkalendere, f.eks.
   selskapenes egne IR-sider (kan scrapes per selskap, men skjørt og
   krever vedlikehold per ticker), eller aggregatorer som gir ut en enkel
   RSS/kalenderfeed.
3. Uansett utfall: `data/manual/report_dates.yaml` forblir en fungerende
   fallback som aldri fjernes, siden den ikke er avhengig av at noen
   ekstern kilde fortsetter å virke.

## Oppdatering (konkret forsøk)

Prøvde direkte å hente en konkret produktside for en enkeltaksje
(`live.euronext.com/en/product/equities/...` for Equinor) i tillegg til de
generelle API-sidene. Samme resultat: **HTTP 403 på all automatisert
henting**, også for vanlige produktsider — ikke bare API-endepunktene. Dette
bekrefter bot-beskyttelse (sannsynligvis Cloudflare) som blokkerer
ikke-nettleser-klienter generelt, ikke bare "premium"-endepunkter.

Viktig: dette ville blokkert *uansett* om forsøket kjørte fra en
utviklingsøkt eller fra selve GitHub Actions-jobben — begge er
automatiserte klienter uten ekte nettleser, så konklusjonen gjelder
produksjonsmiljøet også, ikke bare en lokal begrensning.

**Konklusjon: Euronext scraping/API droppes som datakilde** for dette
prosjektet, både for kurs- og rapportdata. `report_dates.yaml` er den
varige løsningen for rapportdatoer, ikke en midlertidig fallback.

For vekst-/verdsettelsestallene som egentlig var det underliggende
problemet (Yahoo sine "info"-felt var tomme for de fleste Oslo Børs-
tickerne): løst uten Euronext, ved å hente rådata fra yfinance sitt
resultatregnskap (`Ticker.income_stmt`) og regne ut vekst/EPS selv i stedet
for å stole på Yahoos ferdigberegnede sammendragsfelt. Se
`etl/etl/sources/yfinance_source.py`.
