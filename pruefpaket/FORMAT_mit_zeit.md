# Das Werkzeug — Bogenformat

Du traegst die Unterlagen als **Blaetter** in eine JSON-Datei ein. Ein
Blatt je Unterlage, plus ein Zielblatt `Z` fuer die Aussage, die du
belegen willst. Dann laeuft ein Programm darueber und vergleicht die
Felder miteinander.

```json
{
  "ziel": "Z",
  "stufe": "S2",
  "verwendet_am": "2027-06-01",
  "blaetter": [
    {
      "kennung": "M1",
      "behauptung": "kurz, was auf dem Blatt steht",
      "herkunftsart": "gemessen",
      "grundlage": [],
      "bruecke": "",
      "rueckhalt": [],
      "einschraenkung": {"was": "...", "wo": "..."},
      "kippkriterium": "...",
      "stand": ["2026-12-31", "2026-06-01"],
      "annahmen": [],
      "zeitraum": ["2026-01-01", "2026-12-31"]
    }
  ]
}
```

## Die Felder

| Feld | was hineingehoert |
|---|---|
| `behauptung` | was das Blatt aussagt |
| `herkunftsart` | `gemessen`, `berichtet` oder `gerechnet` |
| `grundlage` | Kennungen der Blaetter, auf denen dieses aufbaut |
| `bruecke` | der gedankliche Schritt von der Grundlage zur Behauptung |
| `rueckhalt` | was diese Bruecke traegt (Norm, Handbuch, Kalibrierschein) |
| `einschraenkung` | wofuer es gilt, als Schluessel-Wert-Paare (`was`, `wo`) |
| `kippkriterium` | woran diese Aussage scheitern wuerde |
| `stand` | **zwei Daten:** [Daten ab, Kriterium festgelegt am] |
| `annahmen` | was diese Ableitung voraussetzt |
| `zeitraum` | **[von, bis]** — welchen Zeitraum die Aussage abdeckt |

### `stand` und `zeitraum` sind NICHT dasselbe

Das ist die haeufigste Verwechslung, und sie war lange ein Fehler des
Formats, nicht der Ausfueller.

- `stand[0]` = **ein** Datum: ab wann Daten vorliegen
- `stand[1]` = **ein** Datum: wann das Kippkriterium festgelegt wurde
  (es muss VOR den Daten festgelegt worden sein, sonst ist es
  nachtraeglich zurechtgelegt)
- `zeitraum` = **zwei** Daten: von wann bis wann die Aussage gilt

**Ein Zeitraum, dessen beide Daten gleich sind, ist ein PUNKT.** Eine
Zaehlerablesung am 31.12. ist ein Punkt: `["2026-12-31","2026-12-31"]`.
Ein Betriebsjahr ist eine Spanne: `["2026-01-01","2026-12-31"]`.

Erlaubte Schreibweisen: `2026`, `2026-03`, `2026-03-15`, `15.03.2026`.
Monatsnamen kann das Programm nicht lesen und sagt das.

## Was das Programm vergleicht

| | vergleicht | meldet |
|---|---|---|
| P1 | Herkunftsart gegen Grundlage | `BODENLOS` — gerechnet, aber unten keine Messung und kein Urheber |
| P2 | Kippkriterien der Stuetzen | `EIN_ZEUGE` — zwei Blaetter, ein Versagenspunkt |
| P3 | Bruecke gegen Rueckhalt | `BRUECKE_OHNE_RUECKHALT`, `GETEILTE_BRUECKE` |
| P4 | Einschraenkung gegen die der Grundlage | `UEBERDEHNUNG` — die Behauptung gilt weiter als ihre Grundlage |
| P5 | Kippkriterium gegen Zeitraum | `NACHTRAEGLICH` — Kriterium nach den Daten festgelegt |
| P6 | Annahmen der Stuetzen | `GETEILTE_ANNAHME` — zwei Wege, eine Praemisse |
| P7 | Zeitraum gegen den der Grundlage | `ZEITLUECKE` — die Behauptung gilt fuer Zeiten, die kein Beleg abdeckt |
| P8 | Punkt gegen Spanne | `ZEITPUNKT` — Punktmessungen tragen eine Spanne |

Dazu drei Auskuenfte, die **nichts** melden, sondern nur berichten:

- **NICHT GEPRUEFT** — welche Felder leer geblieben sind. Ein leeres
  Feld ist kein Fehler. Es heisst nur, dass die zugehoerige Regel
  stumm war. *Nicht geprueft ist nicht dasselbe wie in Ordnung.*
- **NICHT ERREICHT** — Blaetter, die das Zielblatt ueber keine
  `grundlage`-Kette erreicht. Sie tragen nichts bei.
- **MINDESTLUEGE** — wie viele Felder man passend faelschen muesste,
  damit keine Beanstandung mehr uebrig ist.

## Aufruf

```
python3 -m framenetwork schablone DEINE_DATEI.json
```

Das Programm entscheidet nichts. Es vergleicht Felder und schreibt
auf, was dabei herauskommt.
