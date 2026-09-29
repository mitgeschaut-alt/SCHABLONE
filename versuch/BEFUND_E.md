# Zeitfeld und Werkzeugkoffer — was gehalten hat und was nicht

Vorab festgelegt in `VORAB_E.md`, vor dem Lauf. Sechs Läufe als
unabhängige Agenten, die weder die Fallen noch die Vorhersagen kannten.
Ausgezählt hat ein siebter, der nur die sechs Texte unter neutralen
Namen in gemischter Reihenfolge gesehen hat und **zu jeder Wertung ein
wörtliches Zitat liefern musste**.

## Verworfen, bevor gezählt wurde

**E2b ist gefallen.** Der Lauf hat beim ersten Blick ins Verzeichnis
`VORAB_E.md` mitgelesen und kannte damit F1–F5 und die Vorhersagen. Er
hat das von sich aus gemeldet. Wiederholt als **E2b2** in einem
Verzeichnis, das nur FALL, AUFGABE und FORMAT enthält.

Für die übrigen fünf kann ich Kontamination nicht ausschließen — keiner
hat sie gemeldet, aber ich kann es nicht nachprüfen. Das ist eine echte
Schwäche dieses Durchgangs.

## Ergebnis

| Arm | Lauf | R1 Fallen ↓ | R2 Gründe ↑ |
|---|---|---|---|
| **E1** Zeitfeld + Erklärung | e1a | 0 | 5 |
| | e1b | 0 | 5 |
| **E2** ohne Zeitfeld + Werkzeugkoffer | e2a | 0 | 5 |
| | e2b2 | **1** | 4 |
| **E3** Zeitfeld + Werkzeugkoffer | e3a | 0 | 4 |
| | e3b | 0 | 4 |

```
                              R1     R2
E1  Zeitfeld + Erklaerung     0,0    5,0
E2  ohne Zeitfeld + Koffer    0,5    4,5
E3  Zeitfeld + Koffer         0,0    4,0

zum Vergleich, nur R1:
A 2,5   B 2,5   C 2,0   D1 3,0   D2 2,0
```

## V2 hält — und zwar deutlich

**F4 und F5 sind in E1 und E3 kein einziges Mal gefallen: 0 von 8.**
In A–D waren es 10 von 10, in jedem Arm.

Der einzige Fallentreffer im ganzen E-Block ist F4 in **e2b2** — dem
Arm **ohne** Zeitfeld. Das ist das sauberste Signal des Versuchs: die
Falle, die vorher ausnahmslos zuschnappte, schnappt jetzt nur noch dort
zu, wo das Feld fehlt.

Die Läufe sagen auch, woran es liegt. e1b:

> „aus einem Zeitpunkt wird hier ein Jahr"

e2a, das den Punkt über eine Auskunft fand, die niemand angefordert
hatte:

> „das Programm meldete auf jedem Blatt `ZEITRAUM leer` — ein Feld, das
> mein Formatblatt gar nicht nennt. Als ich es nachtrug, feuerten P7
> und P8."

Das war im Nachtrag zur Vorabregistrierung als Möglichkeit benannt und
ist eingetreten.

## V4 hält auch — gegen die Rahmen-Hypothese

**E1 ist nicht schlechter als E3, sondern besser.** Gleiches Werkzeug,
einziger Unterschied der Rahmen: R2 5,0 gegen 4,0.

Der Werkzeugkoffer-Rahmen hat auf beiden Raten **nichts gewonnen**. Bei
n = 2 und einem Punkt Abstand ist das Rauschen — aber die Richtung ist
gegen die Hypothese, nicht dafür. Was an den beiden fehlenden Punkten
hängt, ist konkret: e3a hat den Wartungsvertrag in der Endantwort gar
nicht erwähnt, e3b die zeitliche Eingrenzung nicht ausgesprochen.

Beide E3-Läufe haben stattdessen viel Aufwand in eine **Kritik am
Werkzeug** gesteckt — die Frage „was ist deine Meinung dazu" hat
gearbeitet, aber am Werkzeug statt am Fall. Das ist nicht wertlos (siehe
unten, es hat zwei echte Fehler gefunden), aber es ist nicht das, wofür
der Rahmen gedacht war.

## V1 und V3 sind nicht entscheidbar

Beide vergleichen gegen D2 auf R2. **R2 wurde für D2 nie erhoben** — in
D gab es die zweite Rate noch nicht, und die D-Antworten liegen nicht
als Dateien vor. Auf R1 ist E3 besser als D2 (0 gegen 2,0), auf R2 weiß
ich es nicht. Die Hauptvorhersage ist damit halb offen, und das ist mein
Fehler in der Versuchsanlage, nicht ein Ergebnis.

## Der Störfaktor, vorab benannt — und er greift

Vorab festgelegt: *liegt die Verbesserung ausschließlich auf F4/F5, sind
es die neuen Regeln; verteilt sie sich, war es das Rauschen.*

Sie verteilt sich. **F2 fiel in A–D 3 von 10 mal, in E 0 von 6.** Das
kann das Zeitfeld nicht bewirkt haben. Wahrscheinlicher: die 28
P5-Fehlalarme sind weg, das Formatblatt ist neu und viel besser, und
die Läufe sind Agenten statt meiner selbst.

**Ich kann den Anteil des Zeitfelds nicht sauber abtrennen.** Was
bleibt, ist der eine saubere Punkt: der einzige F4-Treffer sitzt im
einzigen Arm ohne das Feld.

## Was die Läufe an meinem Werkzeug gefunden haben

Drei von ihnen, unabhängig voneinander, am selben Tag, an dem ich den
Strang gebaut habe. Beide Vorwürfe habe ich nachgestellt — durch
Einsetzen, nicht durch Einschätzung.

**Fehler 49 — der grüne Haken aus dem Nichts.** `s_zeit` meldete
`[ok] Zeit — die Behauptung bleibt im belegten Zeitraum` genau dann,
wenn gar kein Zeitraum dastand. Acht Zeilen über der Auskunft „P5, P7
und P8 stumm", im selben Bericht. e2a:

> „Ein grüner Haken, der aus dem Hinsehen-auf-nichts entsteht, verletzt
> die eigene Regel des Programms, ‚nicht geprüft ≠ in Ordnung' — und er
> ist schlimmer als gar kein Haken."

Das ist die Nicht-Gleichung, auf der das ganze System steht, gebrochen
von dem Strang, der sie durchsetzen sollte. Repariert: ohne lesbaren
Zeitraum meldet der Strang `NICHT PRUEFBAR` und sperrt auf S2/S3.

**Fehler 50 — ein unbelegtes Dokument entfernt einen Befund.** P7 nahm
min/max über *alle* Stützen. e3a:

> „P7 blieb still, weil V1 und G1, die beiden unbelegten Behauptungen,
> die Spanne 2026-01-01..2026-12-31 tragen und die Lücke in P7s
> min/max-Arithmetik schließen."

Nachgestellt: zwei Punktablesungen am 31.12. → `ZEITLUECKE`. Ein
Berichtsblatt ohne jede Messung dazu → **still**. Mehr Papier, weniger
Beanstandung — die falsche Richtung. Repariert: eine Stütze trägt den
Zeitraum nur, wenn sie selbst unten bei einer Messung oder einem
benannten Urheber ankommt. Dieselbe Prüfung wie P1, wiederverwendet.

**Fehler 51 — nicht repariert, aufgeschrieben.** `nach_netz()` füllt
`zahlen` nie. Der Strang Rechnung meldet deshalb auf jedem Bogen
„keine abgeleitete Zahl enthalten", auch wenn die Behauptung aus nichts
als einer abgeleiteten Zahl besteht. Die 3,29 hat in allen sechs Läufen
der Mensch gerechnet, nie das Programm. Dritte Fundstelle derselben
Naht wie Fehler 46.

Dazu ein Befund, der älter ist als heute (e2b, e3b): das Tor schreibt
`[ok] Inhalt — empirisch mehrfach gestützt`, während zwei Zeilen höher
`EIN_ZEUGE` steht. Die beiden Schichten widersprechen sich im selben
Lauf.

## Regression nach beiden Reparaturen

```
proben                47/47
Erkennung             44/44   (zwei neue Klassen P, Q)
ausserhalb             0/24
Fehlalarm              0/40
P5 auf sechs echten Boegen   28 -> 0
```

## Fazit

**Das Feld hat gewirkt, der Rahmen nicht.**

Zeit war nie ein Sprachproblem. Die Deutung aus `BEFUND_D.md` — „die
Zeitform einer deutschen Behauptung wird von keinem Eingriff berührt" —
war falsch, und sie war falsch, weil ich die einfachere Erklärung nicht
geprüft hatte: **es gab kein Feld.** Sobald Zeit ein Intervall ist statt
einer Zeichenkette in einem Freitextwörterbuch, fällt die Falle, die
vorher zehn von zehn mal zuschnappte, null von acht mal.

Der Werkzeugkoffer-Rahmen hat auf dieser Messung nichts hinzugefügt.
Er hat die Läufe dazu gebracht, das Werkzeug zu prüfen statt nur zu
benutzen — und dabei zwei echte Fehler in meinem Code gefunden. Für die
Aufgabe selbst hat er nichts gebracht. Das ist kein Argument gegen ihn,
aber es ist auch kein Beleg für ihn.

n = 2 je Arm, ein Fall, Agenten unbekannten Modells, ein verworfener
Lauf, ein nicht abtrennbarer Störfaktor. **Richtung, keine Rate.**
