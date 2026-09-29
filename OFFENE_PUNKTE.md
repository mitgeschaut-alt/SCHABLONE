# FrameNetwork 2.3 — was zu verbessern ist

Stand 28.09.2026. Geordnet nach dem, was es einbringt, nicht nach
Aufwand. Was bereits behoben ist, steht am Ende, damit es nicht
verlorengeht.

---

## 1  Der Korpus kann den echten Defekt nicht darstellen

**Der wichtigste Punkt, und er blockiert alles andere.**

Die Quellblätter der 100 Erkennungstests tragen keine Zahlen:

```
M1  behauptung: 'Zaehler BHKW'
M2  behauptung: 'Wechselrichterprotokoll BHKW'
Z   behauptung: 'Der Ertrag 2025 liegt 4,2 % ueber Plan.'
```

Der Defekt des Fernwärme-Falls — zwei Blätter nennen dieselbe Zahl,
keine Kante verbindet sie — ist darin **nicht konstruierbar**. Ebenso
wenig die Klasse „gleiche Zahl, andere Größe" aus dem 2.2-Entwurf
(18 % Verbrauch gegen 18 % Kosten).

Solange das so ist, kann der Korpus keine Architekturfrage
entscheiden. Er hat in dieser Sitzung bereits einmal fast eine
falsche entschieden: die Regression „32/36 statt 36/36" sah aus wie
ein Argument gegen die relationale Fassung von P2 und war in
Wahrheit ein Argument dafür, dass Klasse B in der Form von P2 gebaut
wurde.

**Zu tun:** Zahlen auf die Quellblätter, und zwar vor der nächsten
Regeländerung.

---

## 2  Fehler 42 — der Prüfstand vergleicht die falsche Hälfte

`pruefstand` vergleicht Blätter **nach Kennung**. Im Fernwärme-Lauf
zählte das Zielblatt dadurch bei allen vier Modellen als „fehlt Z"
plus „zusätzlich Z1" — und genau das Blatt, auf das es ankommt, wurde
nie verglichen.

Der Vergleich muss nach **Rolle** laufen: `ziel` gegen `ziel`.

Die Verlustzahlen des ersten Laufs (6–7 von 24) enthalten sechs
Pseudo-Verluste und sind bis dahin nicht belastbar.

---

## 3  Zwei Regeln sind eingebaut und ungeprüft

| Regel | Lage |
|---|---|
| P3b GETEILTE_BRUECKE | überlebt die Mutationsprobe, wird von den 100 Tests nie berührt |
| P6 GETEILTE_ANNAHME | feuert 0 von 100, weil `annahmen` überall leer ist |

Beide brauchen eine **eigene, vorab festgelegte Defektklasse** — keine
Nachrüstung an den bestehenden Zahlen. Eine Regel, die nie anschlägt,
ist nicht bewiesen sicher, sie ist unbeobachtet.

---

## 4  P6 erreicht das Tor nicht

Derselbe Bruch wie Fehler 46, an einer anderen Naht. Der Strang
`Reichweite` trägt nur ÜBERDEHNUNG. Der Strang `2. Hand` zählt Pfade
über `unabhaengige_pfade()`, und das kennt nur Quellen, keine
Prämissen von Ableitungen.

Eine geteilte Annahme wird also gemeldet und ändert nichts.

**Aber nicht auf Verdacht einbauen.** Gemessen wurde heute: eine
einzelne Verbindung bringt keine neue Erkennung, sondern eine neue
Unterscheidungsachse — und *alle* Schichten zu verbinden sperrt
46 von 46 geprüften Bögen, echte wie saubere. Jede Verbindung einzeln,
begründet, und mit der Messung bezahlt, wieviel Redundanz sie
zerstört.

---

## 5  Der eigentliche Hebel: `grundlage` darf leer bleiben

Aus dem Fernwärme-Lauf: die Kante `G1 ← V1` stand in keinem Feld, und
**beide** P2-Varianten waren darauf blind. Text gegen Relation ist
nicht die Achse. Der Hebel ist, dass ein Feld leer bleiben kann, ohne
dass es jemandem auffällt.

Zwei Wege, beide ungetestet:

- **Dritter Zustand:** `null` = nicht beantwortet, `[]` = „dieses Blatt
  steht für sich". Dieselbe Nicht-Gleichung wie Fehler 32, 34, 43 —
  das Muster hat dreimal getragen. Kosten: ein Formzustand mehr, und
  der erste Lauf zeigte, dass die Form schon jetzt überfordert.
- **Formfrage:** *herkunftsart ≠ gemessen und grundlage leer → fragen.*
  Ein bis zwei Fragen je Bogen, trifft G1 in vier von vier. Billig,
  keine neue Regel.

---

## 6  Die Stufe wird nicht aufgezeichnet

S0 sperrt nichts — der Gedankenspiel-Modus ist seit der ersten Fassung
da. Was fehlt, ist der **Weg**: dass ein Einfall am Montag S0 war, am
Dienstag eine rechenbare Frage wurde und am Mittwoch ein angreifbares
Kippkriterium.

Die Zustandsmaschine (`KANDIDAT → VERMERK → BESTÄTIGT`) zeichnet den
Status auf, nicht die Stufe. Der Weg durch die Stufen ist genau die
Pipeline, um die es geht, und nichts hält ihn fest.

**Dazu eine Regel ohne Code:** die Stufe muss erklärt werden, nicht
erraten. In dieser Sitzung habe ich sie geraten und alles auf S3
behandelt, was Vermerk war.

---

## 7  `mindestluege` kennt `grundlage` nicht

Zugmenü: `herkunftsart, kippkriterium, bruecke, rueckhalt,
einschraenkung, stand`. Relationen fehlen. Deshalb kann das beste
Fragewerkzeug des Programms nicht nach der einen Kante fragen, auf die
es ankam — fünf von fünf Bögen, keine erzeugte Frage zeigte darauf.

Vor dem Einbau die Laufzeit messen: die Suche wird kombinatorisch
größer.

---

## 8  Was das System grundsätzlich nicht prüft

Klassen J–O: Zahlendreher, falsche Einheit, erfundene Quelle,
unzulässige Brücke, Vorzeichen, verwechselte Größe. **0 von 24**,
vorab so erwartet.

In dieser Sitzung wurde das eindrucksvoll bestätigt: das Tor hat
meinen Kometenbogen gesperrt und saß dabei auf **vier falschen
Zahlen**, die es nicht sehen konnte — Ausgasung um Faktor 1,7,
Jarkowski um acht Größenordnungen, Fragmentradius invertiert,
Bisektion verkehrt herum.

Das ist keine Lücke, die man mit einer Regel schließt. Was hilft, ist
Auffindbarkeit: Einheiten mitschleppen, Ergebnisse einsetzen und
prüfen ob die Gleichung aufgeht. Alle vier Fehler wären an einer
Dimensionsprüfung oder einer Rückprobe gescheitert.

---

## 9  Methodisch: zwei Bögen, eine Hand

Fernwärme und Komet — beide Bögen von mir. Nach der eigenen Regel des
Systems ist das **eine Stimme**. Die vier Modellbögen sind fremd, aber
die Referenz, gegen die sie gemessen wurden, ist meine.

Was das löst: ein Bogen, den der Nutzer schreibt, zu einem Fall, den
ich nicht kenne.

Und die seit langem wichtigste ungemachte Messung: **zehn eigene Bögen
mit der Stoppuhr.** Ohne sie ist unbekannt, was das Ausfüllen einen
Menschen kostet.

---

## 10  Offen am Kometenfall

- **Lösungsgeschichte:** `orbit_id 19` heißt, es gab achtzehn frühere.
  Ist q über die Versionen monoton gewandert, während der Bogen wuchs,
  ist das verdächtig. JPL liefert nur die aktuelle Lösung; die
  früheren stehen in MPEC-Rundschreiben des MPC, für mich nicht
  abrufbar.
- **Residuen je Sternwarte und je Nacht** — braucht die
  Beobachtungsdatei des MPC.
- **Teilbögen getrennt anpassen**, die beiden q vergleichen. Der
  schärfste Test mit vorhandenen Daten.
- **3. Dezember 2026:** erste prüfbare Vorhersage, Elongation 60 Grad,
  mag 17,6.
- **Archivsuche:** RA 12h21m bis 12h57m, Dek +10 bis +19 Grad,
  Pan-STARRS ab 2023, DECam ab 2019.

---

## Behoben in dieser Sitzung

| Nr | Was | Gefunden durch |
|---|---|---|
| 43 | zwei leere Kippkriterien galten als zwei Zeugen | fremder Modellbogen |
| 44 | Negativliste las nur das Zielblatt | Kandidatenprüfung |
| 45 | Waisenblätter fielen lautlos heraus | Prüfung eines anderen Kandidaten |
| 46 | Schablone gab ihre Befunde nie ans Tor | die Eichung |
| 47 | mein eigener Einbau war invertiert | die Tabelle sah verkehrt aus |

Regression nach allen fünf: 47/47, 36/36, 0/24, 0/40.

**Und das Muster darin:** kein einziger dieser Funde kam daher, dass
etwas funktionierte. Alle fünf kamen daher, dass etwas brach.

---

## Nachtrag 29.09.2026 — nach dem Zeitfeld

**Fehler 51, belegt, nicht repariert.** `nach_netz()` fuellt `zahlen`
nie. Der Strang Rechnung meldet auf jedem aus einem Bogen gebauten
Eintrag "keine abgeleitete Zahl enthalten" — auch dort, wo die
Behauptung aus nichts als einer abgeleiteten Zahl besteht. In allen
sechs E-Laeufen hat die 3,29 der Mensch gerechnet, nie das Programm.
Dritte Fundstelle derselben Naht wie Fehler 46 und 49: eine Schicht
findet etwas (oder koennte es), die andere erfaehrt nie davon.

Nicht mit einer Zeile zu reparieren: das Bogenformat hat ueberhaupt
kein Feld fuer Zahlen. Das ist derselbe offene Punkt wie Nummer 1
(der Korpus kann den echten Defekt nicht ausdruecken), eine Ebene
tiefer.

**Widerspruch zwischen den Schichten, belegt.** Das Tor schreibt
"[ok] Inhalt — empirisch mehrfach gestuetzt", waehrend die Schablone
im selben Lauf EIN_ZEUGE meldet. Zwei Laeufe haben das unabhaengig
gefunden. `s_inhalt` zaehlt Quellen, `versagenspunkte()` zaehlt
Versagenspunkte — und niemand haelt die beiden gegeneinander.

**R2 fuer A-D fehlt.** Die zweite Rate (Gruende benannt) gibt es erst
seit E. Damit sind die Hauptvorhersagen V1 und V3 nicht entscheidbar.
Wer die Reihe fortsetzt, muss A-D nachzaehlen — die Antworten liegen
allerdings nicht als Dateien vor, also waere es ein Neulauf.

**Kontamination.** Ein Lauf hat die Vorabregistrierung mitgelesen und
es gemeldet. Bei den uebrigen fuenf kann ich es nicht ausschliessen.
Kuenftig gehoert der Fall in ein eigenes Verzeichnis, das nichts
anderes enthaelt — so wie `lauf_rein/`.

**Fehler 52, belegt, nicht repariert.** `annahmen` fehlt im Luegenmenue
(`MENUE`). Sobald P6 GETEILTE_ANNAHME feuert, meldet `mindestluege()`
"mit bis zu 3 Zuegen nicht raeumbar". Das liest sich wie Robustheit und
heisst in Wahrheit: das Menue kennt das Feld nicht. Nachgestellt:
ein Bogen mit genau einem P6-Befund -> `mindestluege` = None.
Betrifft eine Zahl, die das System UEBER SICH SELBST ausgibt.

**Fehler 53, belegt, nicht repariert.** P1 ist ein ODER ueber die
Zweige: `boden()` sammelt alle Kettenenden, und EIN gemessenes Blatt
darunter macht BODENLOS fuer alle uebrigen Zweige stumm. Nachgestellt:
Bogen mit einem unbelegten Berichtsblatt V1 -> BODENLOS. Derselbe Bogen
plus einer echten Messung -> kein Befund. Der vollstaendigere,
ehrlichere Bogen erzeugt WENIGER Beanstandung als der reduzierte. Das
ist ein Anreiz in die falsche Richtung und dieselbe Klasse wie
Fehler 50.

**Woher 49 bis 53 kamen.** Alle fuenf aus Laeufen, die das Werkzeug
BENUTZT haben, keiner aus dem Bauen. Und alle fuenf aus den Armen, die
die Frage "was ist deine Meinung dazu" bekommen hatten — die beiden
Laeufe ohne diese Frage (E1) haben die Aufgabe am besten geloest und
ueber das Werkzeug nichts gesagt.

**52 und 53 repariert am 29.09.2026.** Vorab in `VORAB_52_53.md`.
Gemessen danach: proben 47/47, Erkennung 44/44, ausserhalb 0/24,
Fehlalarm 0/40. `mindestluege` auf einem reinen P6-Fall: 1 Zug statt
`None`. Der vollstaendigere Bogen erzeugt jetzt MEHR Beanstandung als
der reduzierte, nicht weniger.

V4 nur teilweise bestaetigt: P1b feuert auf den sechs Modellboegen nur
in einem auf V1/G1, in zweien auf die Planungsunterlage, in dreien gar
nicht. Grund: mehrere Modelle hatten V1/G1 einen `rueckhalt`
eingetragen. Ob dieser Rueckhalt traegt oder selbstbedienend ist, kann
P1b nicht sehen — das ist die naechste offene Stelle derselben Naht.

**Gemessen am 29.09.2026, gegen die eigene Darstellung.** Beim
Nachrechnen jeder Zahl einer oeffentlichen Seite kamen fuenf Fehler
heraus, einer davon schwer:

    P2 auf den sechs echten Waermepumpenboegen
      trifft V1/G1 (die abgeschriebene Zahl)     2 von 6
      trifft M1/M2 (zwei getrennte Zaehler)      4 von 6

Der Fehlalarm war HAEUFIGER als der Treffer. Ursache: die Modelle
gaben beiden Zaehlern dasselbe Kippkriterium — der bekannte Fall
"fauler Ausfueller", aber auf echtem Material mit einer Rate, die der
Korpus nicht erahnen liess (dort 2 von 12 Faellen).

Offen: haelt das Verhaeltnis, wenn die Blaetter sorgfaeltig ausgefuellt
werden? Gemessen ist nur, dass es bei nachlaessigem Ausfuellen kippt.
Das waere die naechste Messung, und sie braucht Boegen von jemandem,
der die Felder verstanden hat.
