# Euronext API for rapportdatoer — foreløpige funn

Status: innledende research gjort (juli 2026), konkret implementasjonsforsøk
ikke gjort ennå (planlagt Fase 3). Dette dokumentet oppdateres når forsøket
er gjort.

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
