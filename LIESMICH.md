# SCHABLONE 3.0

Ein Messinstrument fuer Behauptungen. Es prueft **nicht**, ob eine
Aussage wahr ist. Es vergleicht die Felder, in denen sie begruendet
wird, und meldet, wo diese Felder nicht zusammenpassen.

    10 Felder je Blatt · 9 Abgleichregeln · 7 Straenge am Tor · 4 Stufen

Das Ergebnis darf in keinem Feld stehen. Es entsteht ZWISCHEN zweien —
deshalb kann es niemand hineinschreiben, auch nicht der Ausfueller.

## Sofort ausprobieren

```
python3 -m schablone bogen                     die eingebauten Angriffe
python3 -m schablone bogen datei.json          ein eigener Bogen
python3 -m schablone erkennung              108 Erkennungstests
python3 -m schablone aufnahme               darf aus einer Regel ein
                                               Paragraph werden
python3 -m schablone selbstmass             die eigenen Guetezahlen
                                               als Boegen
python3 -m schablone                        alle Unterbefehle
```

Kein Paket noetig, nur Python 3.

## Die vier Achsen

Alles, was das Programm findet, liegt auf einer davon. Wer wissen will,
ob es fuer einen Fall taugt, fragt zuerst: liegt der vermutete Fehler
auf einer dieser vier?

| Achse | Frage | Regeln |
|---|---|---|
| Herkunft | Endet die Kette bei einer Messung oder einem benannten Urheber? | P1, P1b |
| Unabhaengigkeit | Sind zwei Belege wirklich zwei, oder fallen sie gemeinsam? | P2, P3, P6 |
| Reichweite | Gilt die Behauptung weiter, als ihre Grundlage traegt? | P4 |
| Zeit | Deckt der Beleg den behaupteten Zeitraum ab? | P5, P7, P8 |

## Die eine Regel, die alle anderen traegt

    unbekannt                      != falsch
    nicht bewertet                 != unbedenklich
    kein Kriterium                 != eigener Versagenspunkt
    nicht beantwortet              != steht fuer sich
    geprueft und nicht entkraeftet != entkraeftet

## Stand, gemessen am 29.09.2026

    Defekte im Regelwerk erkannt     44 / 44
    Defekte ausserhalb erkannt        0 / 24   (wie erwartet)
    Fehlalarm auf sauberen Faellen    0 / 40
    Proben                           47 / 47

Reproduzierbar: `python3 -m schablone erkennung`

## Was es NICHT kann

1. **Es rechnet nicht nach.** `nach_netz()` fuellt das Feld `zahlen`
   nie; der Strang Rechnung meldet auf jedem Bogen "keine abgeleitete
   Zahl enthalten". Zahlendreher, falsche Einheit, Vorzeichenfehler
   gehen durch — gemessen: 0 von 24.
2. **Es prueft keine Wahrheit.** Zwei Felder, die zueinander passen und
   beide falsch sind, kommen durch.
3. **Dieselbe Hand fuellt alle Blaetter.** Es verschiebt Aufwand, es
   baut keine Wand. Wie weit, wird gemessen (`mindestluege`): ein bis
   drei passende Aenderungen.
4. **Keine Rate fuer den laufenden Betrieb.** Die 108 Faelle sind
   konstruiert, nicht gezogen.

Ausdruecklich nicht dafuer gedacht: Medizin, Recht, Sicherheit. Und
nicht als Abnahmestempel — `FREIGABE auf S2` heisst "die Felder sind
untereinander stimmig", nicht "die Aussage stimmt".

## Wo was liegt

    schablone/            25 Module, 8.550 Zeilen
      schablone.py        die Vorstufe: 10 Felder, 9 Abgleichregeln
      tor.py              7 Straenge, 4 Stufen, das Attest
      kern.py             Quellen, Netz, Eintraege
      erkennung.py        der Testkorpus, 108 Faelle
      aufnahme.py         wann darf aus einer Regel ein Paragraph werden
      selbstmass.py       die eigenen Guetezahlen als Boegen
      verdacht.py         der dritte Ausgabetyp: fordert Arbeit an
      trigger.py          Halluzinationsausloeser, gepaart und abladiert

    pruefpaket/           Material zum Selbstpruefen — SAUBER
    versuch/              Vorabregistrierungen, Fallen, Antworten
                          NICHT vor einem eigenen Lauf oeffnen

    ZIEL.md               wofuer das Instrument gebaut wurde
    OFFENE_PUNKTE.md      was fehlt, nach Ertrag geordnet
    ZEITANKER.md          woher das Programm weiss, welcher Tag ist
    VORAB_52_53.md        die letzte Vorabregistrierung
    LIESMICH_1.0.md       die alte, ausfuehrliche Fassung (historisch)

## Mitpruefen

Das Nuetzlichste, was jemand beitragen kann, steht als erste Zeile in
`OFFENE_PUNKTE.md`: **ein Fall aus fremder Hand.** Alle 108 Testfaelle
und alle bisherigen Anwendungsfaelle sind von zwei Personen gebaut
worden. Die Fehlalarmquote von 0 auf 40 Faellen misst bis dahin die
eigene Vorstellungskraft.

`pruefpaket/` enthaelt alles, was dafuer noetig ist.

## Fehlerzaehlung

53 nummerierte Fehler. Die letzten fuenf (49 bis 53) haben nicht die
Erbauer gefunden, sondern Laeufe, die das Werkzeug fuer eine echte
Aufgabe benutzt haben — darunter ein Strang, der "geprueft, in Ordnung"
meldete, wenn gar nichts zu pruefen war, und eine Regel, die durch
Hinzufuegen eines UNBELEGTEN Dokuments verstummte.

Das ist die beste bisher gemessene Quelle fuer Fehler in diesem
Programm.
