# Dreiarm-Lauf: was das Zusammenspiel verhindert

Fünf Fallen, vorab festgelegt (VORAB.md). Gezählt wird, in wie viele
die **Endantwort** hineinläuft. Modell: haiku, je zwei Läufe.

## Ergebnis

| Falle | A1 | A2 | B1 | B2 | C1 | C2 |
|---|---|---|---|---|---|---|
| F1 Zahl falsch (3,5 statt 3,29) | – | – | – | – | – | – |
| F2 G1 schreibt von V1 ab | **X** | – | **X** | – | – | – |
| F3 K1 trägt nichts bei | – | – | – | – | – | – |
| F4 Laufzeit unbekannt | **X** | **X** | **X** | **X** | **X** | **X** |
| F5 zeitlich überdehnt | **X** | **X** | **X** | **X** | **X** | **X** |
| **Summe** | **3** | **2** | **3** | **2** | **2** | **2** |

```
A  ohne alles          3, 2     Mittel 2,5
B  Selbstpruefung      3, 2     Mittel 2,5
C  mit FrameNetwork    2, 2     Mittel 2,0
```

## Was gehalten hat

**F1 fällt in keinem Arm.** Alle sechs Läufe haben nachgerechnet und
3,29 gefunden. Damit ist die Rechenfalle in dieser Aufgabenform
wirkungslos — anders als im Verdachtsexperiment, wo dieselbe Art
Fehler bei „fasse zusammen" 2 von 2 durchrutschte. **Die Aufgabenform
entscheidet mehr als der Arm.**

**F2 ist die einzige Falle, die zwischen den Armen trennt.** A1 und B1
behandeln V1 und G1 als zwei Bestätigungen. Beide C-Läufe nicht.

Und B1 ist der schärfste Einzelbefund des ganzen Laufs: die
Selbstprüfung hat sich **aktiv hineingeredet** —

> „V1 und G1 nennen beide 3,5, ohne Begründung – aber das sind
> immerhin zwei unabhängige Quellen."

Kritisches Nachlesen hat die Falle hier nicht entschärft, sondern
zugeschnappt. B2 dagegen kam von selbst auf „sie berufen sich
möglicherweise gegenseitig". Selbstprüfung ist unzuverlässig, nicht
wirkungslos.

## Was nicht gehalten hat

**F4 und F5 fallen in 6 von 6.** Kein Arm, auch C nicht, bindet die
Aussage zeitlich ein. „Die Anlage arbeitet suboptimal" steht in der
Gegenwart, unbegrenzt — genau die ÜBERDEHNUNG, die das Programm im
Bogen meldet und die in der Prosa danach wieder auftaucht.

**Das ist der wichtigste Befund gegen das Werkzeug:** FrameNetwork
korrigiert den Bogen, nicht den Satz, der daraus geschrieben wird.
Der Befund wird gelesen und dann nicht in die Sprache übernommen.

F4 halte ich außerdem für schlecht gebaut: die Unterlagen sagen
„Betriebsjahr 2026" und liefern Jahreszähler. Ganzjährigen Betrieb
anzunehmen ist nicht unvernünftig. Die Falle zählt, aber ich würde
sie beim nächsten Mal streichen.

## Der Unterschied, ehrlich beziffert

```
A gegen C    2,5 -> 2,0     eine halbe Falle weniger
B gegen C    2,5 -> 2,0     eine halbe Falle weniger
A gegen B    2,5 -> 2,5     kein Unterschied
```

Bei n = 2 je Arm ist das **kein Ergebnis, sondern eine Richtung**. Was
belastbar ist: der Unterschied entsteht an genau einer Falle (F2), und
das ist die Falle zur Quellenunabhängigkeit — also genau die Achse, auf
der das Programm gebaut ist. Nicht an der Rechenfalle, nicht an der
Überdehnung.

## Kosten

Arm C brauchte 5 bis 10 Werkzeugaufrufe und rund 43.000 Token je Lauf
gegen 30.000 in A. Rund 40 Prozent mehr Aufwand für eine halbe Falle.
