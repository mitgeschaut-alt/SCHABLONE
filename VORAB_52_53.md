# Vorab, vor dem Umbau — Fehler 52 und 53

Beide von Laeufen gefunden, die das Werkzeug benutzt haben, beide
nachgestellt. Jetzt repariert. Was ich erwarte, steht hier, bevor
gemessen wird.

## Fehler 52 — `annahmen` fehlt im Luegenmenue

`mindestluege()` meldet bei jedem P6-Befund „mit bis zu 3 Zuegen nicht
raeumbar". Das liest sich wie Robustheit und heisst: das Menue kennt
das Feld nicht.

**V1** Nach dem Einbau gibt `mindestluege` fuer einen reinen
P6-Fall eine Zahl statt `None`.
**V2** Die Mindestluege bei angriff_2 (zwei Zeugen, eine Wurzel) kann
sinken. Das waere kein Schaden, sondern eine Korrektur: die Zahl war
vorher zu hoch.
**Widerlegt**, wenn `mindestluege` weiterhin `None` liefert.

## Fehler 53 — P1 ist ein ODER ueber die Zweige

`boden()` sammelt alle Kettenenden; EIN gemessenes Blatt darunter macht
BODENLOS fuer alle uebrigen Zweige stumm. Nachgestellt: ein unbelegtes
Berichtsblatt allein -> BODENLOS. Dasselbe Blatt plus einer echten
Messung -> kein Befund. **Der vollstaendigere Bogen erzeugt weniger
Beanstandung.**

Umbau: BODENLOS bleibt, wie es ist (keine einzige Wurzel traegt). Dazu
kommt **P1b UNGETRAGENER_ZWEIG**: ein einzelner Zweig, der weder bei
einer Messung noch bei einem benannten Urheber endet, wird benannt —
auch wenn andere Zweige tragen.

**V3** Fehlalarm bleibt 0/40. Der saubere Korpus haengt nur an
Messungen, also darf nichts feuern.
**V4** Auf den sechs modellgefuellten Boegen feuert P1b auf V1 und G1 —
den beiden Berichten ohne eigene Messung und ohne Rueckhalt. Das ist
der Kern jenes Falls und damit richtig, kein Fehlalarm.
**V5** Erkennung bleibt 44/44, proben bleibt 47/47.

**Widerlegt**, wenn Fehlalarm ueber 0/40 steigt. Dann ist die Regel zu
scharf und muss eine Auskunft werden statt eines Widerspruchs.

## Die Gefahr, vorab benannt

P1b koennte auf jedem ehrlichen Bogen feuern, der irgendeine
Hintergrundunterlage als Grundlage fuehrt. Falls das eintritt, ist die
richtige Antwort nicht, die Regel zu entschaerfen, sondern sie aus den
Widerspruechen in die Negativliste zu verschieben — melden statt
sperren, wie bei P8.
