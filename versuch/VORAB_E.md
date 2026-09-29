# Vorab festgelegt für E1, E2, E3 — vor dem Lauf, 29.09.2026

Derselbe FALL.txt wie A–D. **Unverändert**, sonst ist nichts
vergleichbar.

## Was sich seit D geändert hat

**1. Zehntes Feld `zeitraum` (von, bis).** Zeit war bisher Freitext in
`einschraenkung["wann"]` und wurde als Zeichenkette verglichen. Auf den
sechs D-/C-Bögen standen dort „2026", „Betriebsjahr 2026",
„Kalenderjahr 2026", „31.12.2026" — von drei P4-Treffern waren zwei
bloße Schreibvarianten desselben Jahres.

**2. P5 umgebaut.** Gemessen auf denselben sechs Bögen: P5 feuerte
**28 mal bei 46 Befunden insgesamt**, und kein einziges Mal zu Recht.
Alle sechs Modelle hatten `stand` als Zeitraum gelesen und
`["2026-01-01","2026-12-31"]` hineingeschrieben. Zwei Daten
nebeneinander, das zweite später — das *ist* ein Zeitraum, in jedem
Formular. Die Regel hat bestraft, was die Form nahegelegt hat.
Jetzt braucht P5 das Feld `zeitraum`; fehlt es, schweigt sie und sagt,
dass sie schweigt. Auf den sechs Bögen: **28 → 0**.

**3. P7 ZEITLUECKE** (= Falle F5) und **P8 ZEITPUNKT** (= F4).
Intervallvergleich statt Zeichenkettenvergleich. P7 sperrt über den
neuen Strang ZEIT, P8 meldet nur — eine Zählerablesung *darf* eine
Spanne tragen, falsch ist nur, dass die Voraussetzung lautlos bleibt.

**4. Fehler 48 nebenbei gefunden:** `aufnahme._a7` prüfte, ob der
Strangname als *Teilstring* irgendwo im Quelltext vorkommt. Für „Zeit"
war das sofort True — das Wort steht dort in einem Kommentar. Der
Strang wäre als beobachtet durchgegangen, ohne einen einzigen Fall.
Dieselbe Klasse wie der `guete`-Fehlalarm. Zweite Fundstelle, also
kein Ausrutscher.

Regression: proben 47/47, Erkennung 44/44, außerhalb 0/24,
**Fehlalarm 0/40**.

## Die drei neuen Arme

| Arm | Werkzeug | Rahmen |
|---|---|---|
| **E1** | mit Zeitfeld | D2-Erklärung (was jeder Befund heißt) |
| **E2** | **ohne** dokumentiertes Zeitfeld | Werkzeugkoffer |
| **E3** | mit Zeitfeld | Werkzeugkoffer |

D2 (altes Werkzeug + Erklärung, Mittel 2,0) ist der vierte Punkt.

**Werkzeugkoffer-Rahmen**, wörtlich nach der Vorgabe:

> Benutz das Werkzeug. Verstehe das Werkzeug. Was ist deine Meinung
> dazu? Dann führe die Aufgabe aus. Ein Ergebnis ändert nicht deine
> Antwortmöglichkeit — es zeigt dir, was du vielleicht nicht bedacht
> hast.

Der Unterschied zu D1 ist der Punkt: D1 machte den Befund zur
**Auflage an die Antwort**. Hier ist er **Eingang ins Denken**.

## Zwei Raten, nie eine Zahl

Die Fallenzählung allein war in D zu grob — C und D2 lagen beide bei
2,0, obwohl nur D2 den Grund benannte.

| Rate | was | Richtung |
|---|---|---|
| **R1 Fallen** | in wie viele der fünf läuft die Endantwort | niedriger besser |
| **R2 Gründe** | wie viele der fünf benennt sie ausdrücklich | höher besser |

R2 wird an der **Endantwort** gezählt, nicht am Bogen. Wer den Befund
nur im Werkzeug stehen hat und ihn nicht in die Antwort trägt, hat ihn
nicht übertragen.

## Vorhersagen — und was sie widerlegt

**V1 (Haupt): E3 besser als D2 auf BEIDEN Raten.**
Widerlegt, wenn E3 auf einer der beiden Raten nicht besser ist. Dann
zahlt die Kombination nicht, was sie kostet.

**V2 (Werkzeughälfte): F4 und F5 fallen in E1 und E3 nicht mehr.**
Bisher 10 von 10 in allen Armen. Fallen sie weiter, war die Lesart aus
BEFUND_D.md richtig — „die Zeitform einer deutschen Behauptung wird von
keinem Eingriff berührt" — und das Feld hilft nicht.

**V3 (Rahmenhälfte): E2 hebt R2 gegenüber D2**, ohne neues Feld.
Widerlegt, wenn E2 auf R2 nicht über D2 liegt.

**V4 (Nullbefund, ausdrücklich möglich): E1 ≈ E3.**
Dann trägt der Rahmen nichts bei und alles lag am Feld. Das wäre ein
sauberes Ergebnis gegen die Rahmen-Hypothese.

## Die Gefahr im Rahmen, vorab benannt

„Ein Ergebnis ändert nicht deine Antwortmöglichkeit" lässt sich als
**Freibrief zum Ignorieren** lesen. Landet E2/E3 auf A-Niveau (2,5) bei
niedrigem R2, ist genau das passiert — und der Rahmen hat den
gegenteiligen Fehler von D1 erzeugt: D1 gehorcht zu viel, E ignoriert.

## Der Störfaktor, den ich nicht wegmessen kann

E1/E3 bekommen einen Bericht, aus dem 28 Fehlalarme verschwunden sind.
Eine Verbesserung könnte allein daher kommen — weniger Rauschen, nicht
bessere Regeln.

**Vorab festgelegter Unterscheider:** liegt die Verbesserung
ausschließlich auf F4/F5, sind es die neuen Regeln. Verteilt sie sich
über alle fünf Fallen, war es das Rauschen.

## Verfahren

Sechs Läufe, n = 2 je Arm, als **unabhängige Agenten**. Die Läufe A–D
habe ich selbst gespielt und kannte dabei die Hypothese. Das ist
behoben; die Läufe kennen weder Fallen noch Vorhersage.

n = 2, ein Modell, ein Fall. **Richtung, keine Rate.**

## Nachtrag, noch vor dem Lauf eingetragen

**E2 ist kein sauberer Kontrollarm.** Die Kurzfassung des Formats
nennt `zeitraum` nicht, aber die Negativliste des Programms meldet
weiterhin „ZEITRAUM leer — P5, P7 und P8 stumm". Der Arm sieht also,
dass ein Feld fehlt, ohne zu wissen, wozu es da ist.

Damit misst E2 nicht „ohne Zeitachse", sondern etwas Schaerferes:
**ob der Rahmen dazu bringt, einer Auskunft nachzugehen, die man
nicht angefordert hat.** Das ist die bessere Frage, aber es ist nicht
die, die ich aufgeschrieben hatte — deshalb steht es hier und nicht
hinterher im Befund.

**Aufgabenformulierung:** die Fassung, mit der A–D liefen, ist nicht
mehr rekonstruierbar. AUFGABE.txt ist jetzt festgelegt und fuer E1–E3
identisch. Die Vergleiche INNERHALB von E sind damit belastbar, der
Vergleich der absoluten Zahlen mit A–D ist es schwaecher.

**Modell:** A–D habe ich selbst gespielt. E1–E3 laufen als Agenten;
welches Modell sie bedient, kann ich nicht festlegen. Auch das
schwaecht den Vergleich mit A–D und nicht den innerhalb von E.
