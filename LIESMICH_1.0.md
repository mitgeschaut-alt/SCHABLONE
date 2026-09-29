# FRAME-NETWORK 1.0

Kontrollierte epistemische Buchhaltung. Ein Aufsatz, der Aussagen nach
**Inhalt** prüft, ihre **Herkunft vermerkt** statt sie zu filtern, Buch
führt über das, was ungeprüft wartet, und zu jeder Freigabe ein Attest
ausgibt, das auch nennt, **was nicht geprüft wurde**.

## Aufruf

```
python -m framenetwork pruefen [datei.json]   Kette und Attest je Aussage
python -m framenetwork bilanz  [datei.json]   was ungeprüft wartet
python -m framenetwork proben                 Konformitätsprobe
python -m framenetwork mutanten               Regeln beschädigen, Probe messen
python -m framenetwork metamorph              zufällige Eingaben, feste Beziehungen
python -m framenetwork ka                     Kontrollinstanz für die Wissensausweitung
python -m framenetwork suche                  wo das Ableiten scheitert und was geht
python -m framenetwork nachrechnen            ein Ergebnis auf eigenem Weg erreichen
python -m framenetwork eigenstaendig          kann das Werk seinen Ursprung überholen
python -m framenetwork diagnose               fällt ein Rechenfehler beim Laufen auf
python -m framenetwork zweihand               wie unabhängig sind zwei Modelle wirklich
python -m framenetwork guete                  Abwertungsgründe, geschlossener Katalog
```

Ohne Dateiangabe läuft `beispiel_neuwied.json`. Kein Fremdpaket, Python 3.9+.

## Aufbau

| Datei | Inhalt |
|---|---|
| `kern.py` | Datenmodell und **Übergangstabelle** — die fünf Nicht-Gleichungen als Code |
| `regeln.py` | R1–R18, jede aufrufbar, jede mit Einstufung |
| `tor.py` | Kette, Stufen S0–S3, fünf Stränge, Attest |
| `buch.py` | Bilanz, Alter, Schuldendeckel, zwei Raten |
| `proben.py` | 47 Fälle in vier Klassen, plus Strohmann |
| `mutanten.py` | Mutationstest — beschädigt die Regeln, misst die Probe |
| `metamorph.py` | metamorphe Probe — zufällige Eingaben, feste Beziehungen |
| `ka.py` | K\|A — Untersuchungsaufträge statt Sperren, Konfliktkerne |
| `suche.py` | vier Hebel für die Konsequenzsuche, ohne Interessantheitsmaß |
| `nachrechnen.py` | ein **vorgelegtes** Ergebnis auf eigenem Weg erreichen |
| `eigenstaendig.py` | kann ein LLM-gebautes System sein Erbe überholen — gemessen |
| `guete.py` | **geschlossener Katalog von fünf Abwertungsgründen** — schließt die gemessene Hauptlücke |
| `zweihand.py` | misst, statt zu behaupten, wie unabhängig zwei Modelle sind |
| `diagnose.py` | fällt ein Rechenfehler beim Laufen auf — an echtem Code gemessen; **Anweisungen an das Modell** |

## Die fünf Nicht-Gleichungen — erzwungen, nicht kommentiert

```
unbekannt                     != falsch
ungeprüft                     != vorläufig bestätigt
Prüfung offen                 != Bestätigung wahrscheinlich
geprüft und nicht bestätigt   != widerlegt
widerlegt                     != wertlos
```

`Eintrag.wechseln()` wirft einen Fehler statt stillschweigend zu
erlauben. `WIDERLEGT` ohne Gegenbeleg ist unmöglich. `WIDERLEGT`
filtert den Zulauf — eine Wiedervorlage wird abgewiesen, nicht erneut
geprüft.

## Die Kette

```
Quelle -> Inhalt -> Zerlegung -> Graph
       -> prüfbar?  --nein--> VERMERK (nicht prüfbar, Grund)
            |ja
       -> geprüft?  --nein--> VERMERK (prüfbar, die Uhr läuft)
            |ja
       -> Evidenzstufe -> Status
```

`prüfbar` ist eine Eigenschaft der **Aussage**, `geprüft` eine der
**Buchhaltung**. Nur die zweite darf in die Evidenzstufe.

Den Rückweg erledigt `Netz.neue_fassung()`: ändert sich eine
Abhängigkeit, fällt jeder Eintrag auf dieser Kante nach `VERALTET`.

## Was das Beispiel zeigt

| | Aussage | S0 | S1 | S2 | S3 |
|---|---|---|---|---|---|
| A1 | Eigenverbrauch 61,0 %, nachgerechnet | frei | frei | frei | **sperr** |
| A2 | Projektbericht mit Briefkopf, „hauptsächlich durch PV" | merk | **sperr** | sperr | sperr |
| A3 | Blog + Projektbericht, dieselbe Zahl | frei | **sperr** | sperr | sperr |
| A4 | 250 kWp, zwei echte Wurzeln, benannter Prüfer | frei | frei | frei | **frei** |
| A5 | YouTube rechnet korrekt vor | frei | frei | **frei** | sperr |
| A6 | gesperrter Sender, korrekte Rechnung | frei | **frei** | sperr | sperr |
| A7 | „exakt" ohne Modellform | merk | **sperr** | sperr | sperr |

- **A5 gegen A2** ist der Kern: das YouTube-Video kommt bis S2, der
  Briefkopf bleibt auf S0. Gesperrt wird nach Inhalt, nie nach Quelle.
- **A3** sind drei Dokumente mit einer Wurzel. Ohne Wurzelrechnung sähe
  das nach dreifacher Bestätigung aus.
- **A6** zeigt, was eine Sperrliste darf: die Rechnung wird geprüft und
  ist richtig, die Sperre deckelt die **Stufe**, nie den Wahrheitswert
  — und nur, solange kein zweiter Weg existiert.
- **A7** ist mein eigener Fehler aus dieser Arbeit: eine Kostenidentität,
  „gilt exakt" genannt, ohne den Grundpreis zu nennen.

## Konformitätsprobe

47 Fälle in vier Klassen:

```
A  muss blockieren      10
B  muss durchlassen     18
C  muss unterscheiden   16
D  muss unzuständig     3

echte Regeln  nur greift                     47 / 47
echte Regeln  streng (greift + Einstufung)   47 / 47
Strohmann     nur greift                     47 / 47
Strohmann     streng (greift + Einstufung)   39 / 47
```

Der **Strohmann** gibt bei jedem Fall die richtige Ja/Nein-Antwort und
nennt immer die vorsichtigste Begründung. Er besteht eine reine
`greift/still`-Probe vollständig. `greift` ist ein Bit; mehrere Regeln
haben drei oder vier Ausgänge — die C-Klasse misst die Differenz.

Die Probe meldet ihre eigenen Lücken: **R3 und R18 haben keinen
auslösenden Fall** und gelten damit als ungeprüft.

## Wer prüft die Prüfung

Die 47 Fälle stammen von derselben Hand wie die Regeln. Zwei Verfahren
nehmen mir je eine Hälfte dieser Auswahl ab.

**Mutationstest** beschädigt die Regeln mechanisch — `<` wird `<=`,
`and` wird `or`, `True` wird `False` — und misst, ob die Probe es
merkt. Die Angriffe kommen damit aus einem Verfahren, nicht aus meinem
Urteil.

```
Mutanten erzeugt                 96
davon lauffähig                  84
davon beim Laden gescheitert     12   (kein Beleg, getrennt gezählt)
erlegt                           73
Mutationsquote                 86,9 %

schwach geprüft: R18 (33 %), R3 (67 %), R5 (71 %), R16 (75 %)
```

R18 hatte die Konformitätsprobe schon als „ohne Scheiterfall" gemeldet.
Zwei unabhängige Instrumente zeigen auf dieselbe Lücke.

**Metamorphe Probe** erzeugt zufällige Netze und prüft fünf Beziehungen,
die ohne Orakel gelten müssen: die Stufenleiter ist monoton, eine
zusätzliche disjunkte Wurzel senkt nie, Umbenennen ändert nichts, ein
Sperrlisteneintrag hebt nie, ein unbeteiligter Eintrag wirkt nicht.
1500 Netze, 0 Verletzungen.

**Was beide nicht können:** sagen, ob die Regeln die *richtige*
Epistemik kodieren. Der Mutationstest zeigt, dass die Probe den Code
prüft. Die metamorphe Probe zeigt, dass fünf Invarianten halten. Ob
„zwei disjunkte Wurzeln" das richtige Kriterium für empirische Stützung
ist, kann keine Maschine beantworten. Dafür braucht es Fälle von
Menschen — das bleibt offen.

## K|A — Kontrollinstanz für die Wissensausweitung

K|A ist **keine Regel**. Regeln sperren. K|A erzeugt einen
**Untersuchungsauftrag**:

```
Ergebnis -> Befund -> K|A -> Untersuchungsauftrag
und NICHT
Ergebnis -> Regeländerung
```

K|A **setzt keinen Status**. Dürfte sie es, könnte sie ihre eigenen
Befunde zu Paragraphen machen und sich selbst bestätigen — genau das,
was sie verhindern soll. Der Regress endet dort, wo die Instanz nur
Aufträge erzeugt und nie Zustände.

**Die Zahl, die Naturkonstante und Zirkel trennt.** Beide „kommen immer
richtig heraus", beide werden von fünf Paragraphen gestützt, keiner
widerspricht. Die Stützungszahl unterscheidet sie nicht. Nur diese
Frage tut es: *auf wie vielen unabhängigen Wegen hätte es schiefgehen
können?*

```
Naturkonstante §C    5 unabhängige Wege
Selbstbestätigung §P 0 unabhängige Wege
```

Ein Verbot von „kommt immer richtig heraus" würde die Naturkonstante
mitsperren. Deshalb: Untersuchung, keine Regel.

**Und K|A liefert den Weg, nicht das Bit:**

```
UNTERSUCHUNGSAUFTRAG zu §P
  Trag-Anteil ohne Selbstbezug  0 %
  WEGE MIT SELBSTBEZUG
    §P -> §A -> §P
    §P -> §B -> §A -> §P
    §P -> §C2 -> §B -> §A -> §P
    ...
  FRAGE AN DEN MENSCHEN
    Gibt es einen Beleg für §P, der NICHT über §P läuft?
    Wenn nein: VERMERK, nicht widerlegt.
```

**Konfliktkerne statt Paarlisten.** Fünf Folgerungen ergeben sieben
paarweise Meldungen mit fast demselben Ursprung — bei hundert sind es
Hunderte. Brauchbar ist eine Meldung je Größe: welche Folgerungen haben
zusammen keinen gemeinsamen Punkt, und welche größte Teilmenge hätte
noch einen. Ein Konfliktkandidat heißt **nicht**, dass die Theorie
falsch ist; er nennt vier mögliche Erklärungen und erzeugt einen
Auftrag.

## Nachrechnen — die Frage, die tatsächlich lösbar ist

Nicht „welche Konsequenzen hat die Theorie?" (unendlich), sondern „kann
ich **dieses eine** Ergebnis selbst erreichen?" — das Ziel ist gegeben,
gesucht ist ein Weg dorthin. Genau deshalb sofort umsetzbar.

```
NACHVOLLZIEHEN  den vorgelegten Rechenweg noch einmal gehen  -> prüft nichts
NACHRECHNEN     dasselbe Ergebnis mit ANDEREN EINGABEN       -> prüft
```

Vier Ausgänge, nicht zwei:

| Ausgang | Bedeutung |
|---|---|
| `REPRODUZIERT` | anderer Weg, gleiches Ergebnis in **vorher** erklärter Toleranz |
| `ABWEICHEND` | anderer Weg, anderes Ergebnis — Konflikt, **kein Urteil** |
| `NUR_NACHGESPIELT` | es gibt nur den vorgelegten Weg — geprüft ist nichts |
| `NICHT_ERREICHBAR` | kein Weg gefunden — und das ist **keine Widerlegung** |

Am Beispiel: das LLM rechnet `E_eigen / E_ges`, das Framework rechnet
`1 - E_einsp / E_ges`. Andere Eingabe, gleiches Ergebnis. Der geteilte
Nenner `E_ges` wird im Bericht **benannt**, denn ein Fehler dort fällt
beiden Wegen nicht auf.

Statt zu blockieren, bietet `NICHT_ERREICHBAR` an, was mit den
vorhandenen Eingaben überhaupt erreichbar ist.

**Die Zahl, ohne die `nicht erreichbar` nichts bedeutet:**

```
ABDECKUNG       50 %   von 4 nachweislich richtigen Ergebnissen selbst erreicht
TREFFERQUOTE    67 %   von 3 falschen Ergebnissen als abweichend erkannt
```

„Nicht herleitbar" heißt zweierlei — *das Ergebnis ist falsch* oder
*mein Methodenvorrat ist unvollständig* — und beide sehen gleich aus.
Nur die Abdeckung trennt sie. Bei 50 % ist der Ausgang fast wertlos:
jedes zweite richtige Ergebnis fällt genauso heraus. **Der Wert des
Systems ist diese Zahl**, und sie steigt mit dem Methodenvorrat, nicht
mit besserem Code.

## Güte — der geschlossene Katalog (neu in 1.0)

Der an zehn Fremdfällen gemessene Hauptmangel: **keine Sprache für
Schätzgüte.** Fünf Gründe, hergeleitet aus dem eigenen Aufbau, danach
mit GRADE verglichen:

| Grund | Frage | GRADE-Gegenstück |
|---|---|---|
| `STREUBREITE` | deckt das Intervall verschiedene Entscheidungen ab? | imprecision |
| `UNEINIGKEIT` | widersprechen sich die Quellen stärker als erwartbar? | inconsistency |
| `ABSTAND` | wurde gemessen, was gefragt war? | indirectness |
| `AUSWAHL` | ist das Vorliegende eine Auswahl aus dem Vorhandenen? | publication bias |
| `SCHEINEINIGKEIT` | **teilen die übereinstimmenden Quellen ihre Wurzel?** | **keins** |

`SCHEINEINIGKEIT` ist die Wurzelrechnung, auf die Schätzgüteseite
gebracht: Übereinstimmung unter Abschriften ist keine Übereinstimmung.

**Der Unterschied zu GRADE, der aus den eigenen Axiomen folgt.** GRADE
kennt „not serious". Das vermischt zwei Zustände:

```
geprüft und unbedenklich   !=   nicht bewertet
```

Eine nicht bewertete Domäne kostet deshalb **keine** Stufe
(*unbekannt ≠ falsch*), erscheint aber im Ergebnis. Das Ergebnis ist
nie eine Zahl allein, sondern **Stufe plus Anzahl offener Domänen**.

### Praktischer Test — dieselben zehn Fremdfälle

Eingaben nur aus Rohangaben, GRADE-Stufe zurückgehalten, Schwellen im
Modulkopf **vor** dem Lauf festgelegt.

```
                        vorher (0.9)     nachher (1.0)
verschiedene Werte      1 von 4          4 von 4
Übereinstimmung         4 von 10         4 von 10
Cohens Kappa            0,00             +0,20
```

Die **Trefferzahl hat sich nicht bewegt, der Informationsgehalt schon.**
Ein konstanter Rater hat Kappa 0 per Definition, egal wie oft er
zufällig richtig liegt. Abweichung: 4 zu hoch, 2 zu niedrig, mittlere
Verschiebung +0,5 Stufen — das System ist milder als die Fachleute.

### Was der Lauf aufgedeckt hat

**F01 bekommt High, GRADE sagt Very Low.** Das Intervall 0,05–0,77
spannt den Faktor 15, enthält aber nicht 1,0 — und meine vorab
festgelegte Regel prüft die Weite nur, wenn das Intervall 1,0 enthält.
Das ist falsch: ein sehr weites Intervall ist auch dann unpräzise, wenn
es ganz auf einer Seite liegt.

**Nicht nachträglich korrigiert.** Eine Schwelle nach Blick auf die
Antwort zu ändern, ist Anpassung ans Ergebnis — was R5 und R16
verbieten. Die nächste Fassung legt vorher fest: Weite unabhängig von
der Lage, Faktor > 10 ernst, > 25 sehr ernst. Dann ein neuer Lauf.

**Was dieser Korpus nicht zeigen kann:** drei der fünf Domänen sind bei
allen zehn Fällen *nicht bewertet* — lauter Einzelstudien ohne
Registerangabe. Vor allem `SCHEINEINIGKEIT`, der einzige Grund ohne
GRADE-Gegenstück, konnte in keinem Fall greifen. **Der eigene Beitrag
bleibt auf diesem Korpus ungeprüft.**

## Fällt ein Rechenfehler beim Laufen auf?

Gemessen an den **echten** Formeln aus `nachrechnen.py`, nicht an einem
Modell. Sechs Fehlerarten, die in Zahlencode wirklich vorkommen, je
zweimal eingebaut:

```
EINZEL   nur der benutzte Weg ist beschädigt   — ein Ausrutscher
GRUND    JEDER Weg ist gleich beschädigt       — der geerbte Denkfehler
```

| | Absturz | gefangen | still falsch | Toleranz deckt ab | fällt auf |
|---|---|---|---|---|---|
| **EINZEL** | 3 | 9 | 5 | 1 | **12/18 = 67 %** |
| **GRUND** | 3 | 0 | 14 | 1 | **3/18 = 17 %** |

Beim Grundfehler wird **kein einziger** durch Prüfung gefangen — die
drei sind Abstürze. Und ein Absturz heißt, dass eine Regel des
*Rechnens* verletzt wurde, nicht dass die Zahl falsch ist. Division
durch Null stürzt immer ab; ein falscher Faktor nie.

`spezifischer_ertrag` hat nur **einen** Weg. Dort bleiben 10 von 10
Fehlern still, egal ob einzeln oder grundsätzlich. **Nicht das
Durchlaufen entscheidet, sondern die Redundanz.**

**Ungeplanter Befund:** zwei Fehler sind falsch und kommen durch, weil
sie in die *vorher* erklärte Toleranz passen (`plananteil`, Komplement,
0,5025 statt 0,4975). Die Toleranz schützt davor, hinterher geweitet zu
werden — sie bleibt trotzdem ein Fenster, und alles, was hindurchpasst,
wird nie gemeldet.

**Was das Programm liefert, wenn es etwas findet**, ist kein Urteil,
sondern eine **Ortsangabe**:

```
AUSGANG   ABWEICHEND
  eigener Weg   quote_komplement
  ergibt        0.61
  neue Eingabe  E_einsp
  geteilt       E_ges   <- ein Fehler dort fällt beiden nicht auf
  Unterschied 0.0122 > Toleranz 0.005 — Konflikt, kein Urteil
```

Welche zwei Wege, welche Eingaben, was sie teilen, wie groß der
Unterschied, wann die Toleranz erklärt wurde. Damit lässt sich suchen.
Ein bloßes „gesperrt" wäre wertlos. **Aber:** die Ortsangabe sagt nicht,
welcher Weg irrt. Sie grenzt ein — weniger als eine Lösung, sehr viel
mehr als ein Verdacht.

## Anweisungen an das Modell

Aus **gezählten Vorfällen** dieser Arbeit abgeleitet, nicht aus guten
Vorsätzen. Jede trägt ihre Fälle und wie sie maschinell nachgehalten
wird.

| Fälle | Anweisung | prüfbar durch |
|---|---|---|
| 3× | Keinen Satz über ein Ergebnis schreiben, bevor der Lauf vorliegt; Zahlen im Fließtext aus dem Lauf rechnen | jede Prozentzahl in der Prosa muss Formatfeld einer Variablen sein |
| 3× | Zahlen nie durch blockweise Textersetzung formatieren | Suche nach `replace` auf Textblöcken mit Zahlen |
| 2× | Ein Experiment muss prüfen, was es zu prüfen vorgibt — vorher festhalten, welches Ergebnis die Behauptung **widerlegen** würde | Vorher-Notiz mit dem Widerlegungsfall |
| 2× | Kein Kriterium ausliefern, das im Probelauf nie greift — Dauerschweigen ist derselbe Fehler wie Dauerfehlalarm | jede Regel braucht einen greifenden **und** einen stillen Fall |
| 0× | Jede gelieferte Zahl mit einem zweiten Weg rechnen oder als ungeprüft ausweisen | `NUR_NACHGESPIELT` muss im Attest stehen |

Die letzte hat **keinen** eigenen Vorfall und ist deshalb markiert. Eine
Anweisung ohne Fall ist eine Vermutung, keine Erkenntnis — dieselbe
Regel wie für R3 und R18.

## Eigenständig — überholt das Werk seinen Ursprung?

Die Frage: *Es ist egal, ob ein LLM das System baut — wenn die Struktur
selbstlernend ist, entfernt sie sich vom Ursprung.* Herkunft ist kein
Wahrheitsargument; das ist der Grundsatz dieses Systems, auf das System
selbst angewandt. Aber die Behauptung hat eine messbare Konsequenz.

**Selbstlernen allein senkt die Fehlerzahl nicht — es sortiert die
Fehler nach Unsichtbarkeit.**

```
gemeldete Fehler je Runde   1,2  ->   1,6      unverändert gesund
Bestand im System           1,8  ->  88,5
Anteil im blinden Fleck    77 %  ->  99,6 %
```

Die gemeldete Zahl ist ein **Zufluss**, der Bestand ein **Lager**. Der
Zufluss bleibt ruhig, während das Lager wächst — und was am Ende darin
liegt, ist fast ausschließlich das, was die Probe nie sehen konnte.
Eine fallende Fehlerrate heißt nicht „wird richtiger", sondern „die
verbleibenden Fehler sind die, die mein Test nicht sieht".

**Der harte Gegenfall** ist Ken Thompsons *Reflections on Trusting
Trust* (1984): ein Fehler, der sich in jede Neufassung mitkopiert und
im Quelltext nicht steht. Ein kompletter Neuschrieb räumt viel weg und
trifft genau das nicht:

```
Runde 31, alles neu geschrieben:  45,9 -> 5,4   davon Thompson-Art 5,4
```

Das einzige bekannte Gegenmittel ist **Diverse Double-Compiling**
(Wheeler 2005/2009): ein zweiter, **unabhängig entstandener** Prüfer —
nicht mehr Iteration. Der Fehler wird nicht durch Hinsehen gefunden,
sondern durch **Vergleich**, und ein Unterschied fällt nur auf, wenn
die zweite Hand den Fehler nicht teilt. Ihr Wert ist genau ihre
Unabhängigkeit:

| Kopplung der blinden Flecke | Bestand | davon Thompson-Art | besser |
|---|---|---|---|
| keine zweite Hand | 88,5 | 27,2 | — |
| **1,0 — dieselbe Hand** | **88,5** | **27,1** | **0 %** |
| 0,9 | 63,4 | 5,8 | 28 % |
| 0,6 | 48,2 | 1,0 | 45 % |
| 0,3 | 36,6 | 0,3 | 59 % |
| **0,0 — unabhängig** | **24,6** | **0,1** | **72 %** |

Nicht die **Anzahl** der Prüfer entscheidet, sondern ihre
**Unabhängigkeit** — dieselbe Rechnung wie bei disjunkten
Quellwurzeln, nur auf das Prüfsystem selbst angewandt. Bemerkenswert:
schon 10 % Unabhängigkeit, über viele Runden angewandt, senken den
Thompson-Anteil von 27 auf 6.

**Und wo sitzt das Erbe wirklich?** `eigenstaendig` prüft die eigenen
Bausteine mit der K|A-Zahl — auf wie vielen unabhängigen Wegen hätte
der Baustein scheitern können?

```
definitorisch mit 0 Wegen   unbedenklich — eine Definition kann nicht
                            falsch sein, nur unbrauchbar
empirisch mit 0 Wegen       3 von 10 Bausteinen:
                              Kriterium "zwei disjunkte Wurzeln"
                              Abdeckungszahl
                              Trag-Anteil / K|A
```

Die Liste ist **kurz und benennbar**. Das ist der Teil der Behauptung,
der sich hält: das Erbe verschwindet nicht durch Iteration, aber es
lässt sich einkreisen — und dann gezielt angreifen.

> Das Modell ist ein Modell. Es beweist nichts über das echte System.
> Es macht die Behauptung *präzise und widerlegbar*: wenn Prüfer einen
> festen blinden Fleck haben, dann folgt das Obige. Die Parameter
> stehen oben in der Datei und sind angreifbar.

## Grenzen — ausdrücklich

- **Keine Richtigkeitsgarantie.** Alle Regeln prüfen die *Beziehung*
  zwischen Aussage und Quelle. Keine prüft die Quelle. Gegen einen
  unehrlichen Vorverarbeiter hilft nur ein zweiter Datenstrom aus
  anderer Hand — deshalb verlangt S3 ihn.
- **Alter ist eine Eigenschaft der Buchhaltung, nie der Aussage.**
  `faellige()` sagt nicht „verdächtig", sondern „seit n Tagen nicht
  entschieden".
- **Die Fälle der Probe stammen von derselben Hand wie die Regeln.**
  47/47 ist eine erfüllte Mindestanforderung, keine Gütezahl.
- **Der Engpass ist nicht die Rechenzeit, sondern die Fragestellung.**
  „Interessant" ist keine Eigenschaft eines Satzes, sondern eine
  Beziehung zwischen Satz und offener Frage. Statt „welche Konsequenz
  von T ist wertvoll?" fragt `suche` „welche Konsequenz entscheidet
  etwas, das im Buch offen ist?" — endlich, zählbar, ohne Wertmaß.
  Was damit **nicht** gelöst ist: keiner der vier Hebel erfindet einen
  neuen Begriff.
- **Konsequenzen suchen ist nicht machbar, prüfen schon.** Die
  Literatur ist eindeutig: das Erzeugen aller ableitbaren Sätze ist
  „theoretisch vollständig, aber rechnerisch unbeherrschbar — der
  Suchraum wächst exponentiell mit der Ableitungstiefe", und die
  Auswahl der *interessanten* Konsequenzen ist ausdrücklich ungelöst.
  Was geht: eine vorgelegte Ableitung prüfen und über einer endlichen
  Menge Widersprüche finden.
- **Nie eine Zahl allein.** `zwei_raten()` liefert Erfindungsrate *und*
  Übervorsichtsrate. Ein System, das auf alles nein sagt, erreicht bei
  der ersten 0 % und ist wertlos.
- **Ein zweiter Rechenweg ist keine zweite Wurzel.** `E_eigen` und
  `E_einsp` kommen aus demselben Zähler. Der *Weg* ist verschieden, die
  *Quelle* nicht. Gegen einen Fehler im Zähler hilft nur die zweite Hand
  aus S3.
- **Eigene Fehlerzählung: 17 in dieser Arbeit, 16 davon selbst gefunden
  und gemeldet.** Die auffälligste Klasse — Prosa, die ein Ergebnis
  behauptet, bevor der Lauf es zeigt — trat dreimal auf. Behoben wurde
  sie nicht durch Vorsatz, sondern dadurch, dass der Text die Zahl jetzt
  *aus dem Lauf rechnet*. Ein System, das Fehlerraten verlangt, muss
  seine eigene nennen.

## Was als Nächstes fehlt

1. Fälle von außen, gemischt mit solchen, bei denen die bequeme Antwort
   die richtige ist. **Nur dieser Punkt braucht Menschen** — die beiden
   Prüfverfahren oben decken den technischen Teil ab.
2. Scheiterfälle für R3 und R18 — von Mutationstest und
   Konformitätsprobe unabhängig voneinander angezeigt.
3. Die zwei Raten an echten Aufgaben messen: rund 110 Fälle für die
   Frage *ob*, rund 250 für die Frage *wie stark*.
4. Das Attest gegen bestehende Aufzeichnungspflichten ausrichten statt
   gegen ein eigenes Format.

---

## schablone.py — die Vorstufe (neu in 1.2)

Acht Felder, alle aus geprueftem Fremdverfahren uebernommen (Toulmin,
Admiralty Code / ICD 206, GRADE, AsPredicted/OSF). Fuenf Abgleichregeln,
jede ein Mengenvergleich zwischen ZWEI Feldern. Kein Statusfeld.

    P1  Herkunftsart x Grundlage      -> BODENLOS
    P2  Grundlage x Kippkriterium     -> EIN_ZEUGE
    P3  Bruecke x Rueckhalt           -> BRUECKE_OHNE_RUECKHALT / GETEILTE_BRUECKE
    P4  Einschraenkung x Grundlage    -> UEBERDEHNUNG
    P5  Stand x Stand der Grundlage   -> NACHTRAEGLICH

Gemessen (22.09.2026):

    Angriff 2 (ging im Tor auf S3 durch)
      von Hand              Wurzeln F1,H1  -> S3 FREIGABE
      ueber die Schablone   Wurzeln M1     -> S3 GESPERRT (r17, unveraendert)
      entschlossen gelogen  Wurzeln F1,M1  -> S3 FREIGABE, 4 abgestimmte
                                              Aenderungen, 2 davon aussen
                                              nachpruefbar
      ehrliche Arbeit       Wurzeln M4,M5  -> S3 FREIGABE, 0 Widersprueche

    Zwei Raten, 12 vorab beschriftete Faelle
      Erfindungsrate       20,0 %   (sorgfaeltiger Luegner)
      Uebervorsichtsrate   28,6 %   (fauler Ausfueller)

Ergebnis: nicht die ZAHL der noetigen Luegen steigt, sondern ihr ORT
verschiebt sich nach aussen. uebernommen_aus behauptete nichts ueber die
Welt und konnte deshalb nirgends scheitern.

Nicht geloest: P2 und P3 stehen auf Freitext.

    python -m framenetwork schablone

FEHLER 22: erste Fassung von P1 prueste nur GERECHNET. Ein Zug
("sag berichtet") raeumte den Widerspruch, ohne dass ein Urheber
genannt werden musste. Symmetrisch korrigiert.

---

## Zeit (neu in 1.3)

Gemessen vorher: **kein Datum loeste im ganzen Programm einen
Statuswechsel aus.** Der Teil davon, der Absicht ist, bleibt — eine Uhr,
die von allein einen Status aendert, hiesse 'alt = wahrscheinlich
falsch'. Drei Loecher, die keine Absicht waren, sind zu:

    FEHLER 23  neue_fassung() sah nur in e.stand. Wer die Variable unter
               e.variablen fuehrt, aber keine Fassung notiert, blieb
               BESTAETIGT — der Rueckweg war ueber ein setzbares Feld
               abschaltbar. Jetzt: wer die Variable nennt, ist betroffen.
               Rueckgabe sind ZWEI Listen (notiert / ungeklaert), damit
               der Preis sichtbar bleibt.

    FEHLER 24  faellige() sah nur offene_vermerke(). Ein VERALTETER
               Eintrag fiel aus der Buchhaltung — keine Wiedervorlage,
               kein Alter. Jetzt: Netz.offen() = VERMERK + VERALTET, und
               die Uhr laeuft ueber wartet() ab dem letzten
               Statuswechsel, nicht ueber alter() ab dem Eingang.

    FEHLER 25  deckt() trennte an '-'. 'ab 2020' und 'bis 2024' fielen
               still auf 'nicht bewertet'. Von der Probe gefunden.

NEU: GELTUNG — kein sechster Strang

  Die fuenf Straenge pruefen die Aussage gegen ihre Quellen. Die Geltung
  prueft die VERWENDUNG gegen die Aussage.

      der Satz bleibt BESTAETIGT   !=   der Satz gilt fuer heute

  tor(..., verwendet_am="2030-09-22") vergleicht geltungsbereich['wann']
  mit dem Verwendungstag. Ergebnis ist ein eigenes Wort,
  AUSSERHALB DER GELTUNG, nicht GESPERRT: gesperrt ist die Verwendung,
  nicht der Satz. Das ist P4 der Schablone auf der Zeitachse.
  Drei Ausgaenge, nicht zwei: ja / NEIN / nicht bewertet.

DREI GROESSEN, DIE NICHT DASSELBE SIND

    alter(heute)    seit dem EINGANG
    wartet(heute)   seit dem letzten STATUSWECHSEL — die Faelligkeitsuhr
    Zahl.daten_ab   wie alt die DATEN sind (nur R5 liest das)

GEGENPROBE: bestraft die Korrektur korrekte Arbeit?

    Fassung 1 notiert, Revision auf v2    -> VERALTET (notiert)
    Fassung 2 notiert, Revision auf v2    -> BESTAETIGT, unveraendert
    keine Fassung notiert                 -> VERALTET (ungeklaert)

ZUR KASKADE: zwei Messversuche verworfen, beide dokumentiert in
probe_kaskade.py. Die Korrektur vergroessert die Startmenge, fuegt dem
Ausbreitungsgraphen aber keine Kante hinzu. Die Schwelle (mittlerer
Ausgangsgrad 1,0) ist eine Eigenschaft der Ausbreitung und verschiebt
sich nicht. Was die Korrektur wirklich kostet, ist die
ungeklaert-Quote — die haengt an der Mitschreibdisziplin, nicht am
Code, und steht ab jetzt als eigene Liste im Revisionsbericht.

---

## erkennung.py — 100 Erkennungstests (neu in 1.4)

Fuenfzehn Defektklassen, je 4 Faelle, dazu 40 ohne Defekt. Klassen und
erwartete Ausgaenge VOR dem Lauf festgelegt. Beschriftung aus der
Konstruktion, nicht aus einem Urteil.

    Defekte IM Regelwerk   36 von 36 erkannt          [90,3 % ; 100,0 %]
    Defekte AUSSERHALB      0 von 24 erkannt          [ 0,0 % ;  14,2 %]
    Faelle OHNE Defekt      0 von 40 Fehlalarm        [ 0,0 % ;   8,8 %]

Jede Klasse hat genau die Regel ausgeloest, fuer die sie gebaut wurde.
Keine wurde aus einem fremden Grund gefangen.

SECHS BLINDE KLASSEN — absichtlich mitgeprueft
    J Zahlendreher · K Einheit falsch · L Quelle erfunden
    M Bruecke logisch unzulaessig · N Vorzeichen im Rechenweg
    O Groesse verwechselt (Leistung statt Arbeit)

ARBEITSTEILUNG, aus dem Lauf gezaehlt
    nur Schablone 20 · nur Tor 16 · beide 0 · keines 24
    Keine Ueberschneidung. B und F sind das Paar: zwei Abschriften mit
    gleichem Kippkriterium faengt nur P2; eine offen deklarierte
    gemeinsame Wurzel faengt nur r17.

FEHLER 27: clopper_pearson bisektierte beide Grenzen als steigend.
P(X <= k) faellt aber in p. 0 von 24 kam als [0 % ; 100 %] heraus.
Gegen scipy an sieben Stuetzstellen geprueft.

    python -m framenetwork erkennung

---

## Kern-Haertung (1.5) — sieben Behauptungen, vorher gemessen

Alle sechs Code-Behauptungen waren wahr. Gemessen VOR jeder Aenderung,
bei 47/47 bestandenen Konformitaetsproben:

    1  aufnehmen() ersetzte eine belegte Kennung STILL — die
       Uebergangstabelle war umgehbar, indem man sie nicht benutzte.
    2  Ein Zyklus in uebernommen_aus warf RecursionError.
    3  Eine nirgends eingetragene Quellenkennung zaehlte als
       unabhaengige Wurzel. EIN TIPPFEHLER reichte fuer S3-FREIGABE.
    5  wurzeln() nahm bei mehreren Messwurzeln 'mess[0]' — die
       alphabetisch erste. Eine epistemische Entscheidung, versteckt
       in einer Sortierung.
    6  quelle() ueberschrieb still.
    7  unabhaengige_pfade() gab es nicht; die Zaehlung stand inline.

GESCHLOSSEN — Fehler 28 bis 33

  wurzeln() ist jetzt REINE PROVENIENZ: alle Wurzeln, keine Auswahl,
  zyklusfest, #unbekannt und #zyklus als sichtbare Marken.

  Netz.pfade() und Netz.unabhaengige_pfade() machen die epistemische
  Entscheidung AUSDRUECKLICH: #unbekannt raus, #zyklus raus, gleicher
  Vorgang einmal. R1 und R17 benutzen jetzt DIESELBE Definition —
  vorher hatte jede ihre eigene.

  FEHLER 33, von der Probe gefunden (46/47), nicht beim Lesen:
  die erste Haertung liess eine MESSUNG mit eigenem Vorgang ihre
  Wurzeln erben. 'Ablesung Maerz' und 'Ablesung April' wurden dadurch
  ein Zeuge. Grund: uebernommen_aus traegt ZWEI Bedeutungen —
  'abgeschrieben von' und 'gemessen MIT'. Eine MESSUNG mit eigenem
  Vorgang hat selbst hingesehen; ihr Apparat gehoert in den Vermerk,
  nicht in die Wurzelrechnung.

NICHT gemacht, mit Begruendung:
  Art um HYPOTHESE erweitern. Die Schablone RECHNET das heute schon
  aus (P1 BODENLOS). Ein Enum-Wert waere wieder ein SETZBARES Feld —
  genau die Klasse, durch die in dieser Sitzung jeder Angriff lief.
  STOERUNG gehoert ausserdem nicht in Art: wie man etwas weiss und was
  dem Signal zugestossen ist, sind zwei Achsen.

NICHT geschlossen, bewusst:
  Netz.eintraege bleibt ein offenes Verzeichnis. metamorph.py benutzt
  das an sechs Stellen absichtlich. Kapselung waere ein Umbau, keine
  Haertung.

## Die Leiter — leiter.py

    1  definiert, nirgends gerufen                 0
    2  gerufen, aber NICHT vom produktiven Pfad  108
    3  vom produktiven Pfad erreicht (gemessen)   42

  Stufe 1 sah zuerst nach 20 aus — alle zwanzig waren Messartefakt
  (@property und NodeVisitor-Dispatch werden nicht als Aufruf gezaehlt).
  Es gibt KEINEN toten Code. Das Problem ist ausschliesslich Verdrahtung.

  16 von 18 Regeln stehen auf Stufe 2. Produktiv erreicht werden nur
  r7_modellform und r17_zweite_hand — dieselben zwei wie in der
  Laufzeitmessung von vorher, unabhaengig repliziert.

  ka.py: 13 Funktionen, KEINE davon produktiv erreicht.

---

## Die drei Leitungen (1.6) — kette/tor -> ka, buch, guete

Nichts behauptet: fuer jede Leitung wurde VERSUCHT, sie zu legen.
probe_leitung.py.

IMPORTKANTEN, gemessen
    kern    -> —
    regeln  -> kern
    tor     -> kern, regeln
    buch    -> kern
    ka      -> —          KEIN Import aus dem Paket
    guete   -> —          KEIN Import aus dem Paket
  ka und guete werden nur von __main__ importiert, fuer ihren eigenen
  Befehl. Aus der Kette heraus erreicht sie nichts.

ka.py — TYPENBRUCH AUF EINER ACHSE, Leitung aber legbar
    ka.Knoten            kern                       uebersetzbar
    kennung              Quelle.kennung             ja
    text                 Quelle.was                 ja
    stuetzt_sich_auf     Quelle.uebernommen_aus     ja
    wurzel               Netz.pfade()               ja
    art (Aussageart)     kein Gegenstueck           NEIN

  Aussageart {definitorisch, logisch, mathematisch, empirisch} und
  Art {messung, aussage, rechnung} sind ZWEI ACHSEN, nicht zwei Namen.
  Eine Abbildung waere verlustbehaftet und falsch.

  ABER gemessen: wege/wurzel_von/untersuchen/frage_stellen lesen .art
  NICHT. Die Selbstbezugspruefung ist heute anschliessbar. Der Adapter
  ist 14 Zeilen und steht in probe_leitung.py.

  WAS SIE BRINGT, gemessen an drei Lagen:
    Zirkel A->B->A   Tor: GESPERRT (1 Pfad) | ka: nennt den Weg A->B->A
    Angriff 2        Tor: FREIGABE          | ka: findet nichts
    saubere Arbeit   Tor: FREIGABE          | ka: findet nichts
  -> ka liefert die ERKLAERUNG, nicht die Erkennung. Den verschwiegenen
     gemeinsamen Ursprung findet weiterhin nur P2 der Schablone.

  Nebenbefund: Knoten.wurzel ist im Original ein GESPEICHERTES Feld —
  dasselbe setzbare Muster. Der Adapter fuellt es aus Netz.pfade(),
  also berechnet. Das ist die eigentliche Verbesserung am Anschluss.

guete.py — KEINE fehlende Leitung, ein Vorgabewert
  Aus dem produktiven Pfad verfuegbar: 4 von 10 Feldern
      name, wert, quellen, wurzeln
  Die vier reichen fuer zwei der fuenf Domaenen: UNEINIGKEIT und
  SCHEINEINIGKEIT — genau die beiden, die FrameNetworks eigener
  Beitrag sind.
  Es fehlen: unten, oben (Zahl fuehrt kein Intervall), surrogat,
  beobachtung_monate, spaetes_seltenes_ereignis, registriert.

  FEHLER 34, nur beim Anschliessen sichtbar: surrogat hatte den
  Vorgabewert False. Naiv angeschlossen meldete ABSTAND deshalb
  'keine Bedenken — direkt gemessen' ueber Daten, die das Programm nie
  gesehen hat. Das ist die zweite Nicht-Gleichung, von innen gebrochen.
  Korrigiert auf Optional[bool] = None plus NICHT_BEWERTET.
  Die zehn ehrlichen Faelle unveraendert: 4/10, Kappa +0,20.

buch.py — keine fehlende Leitung, getrennte Befehle
  buch importiert kern, bilanz()/faellige() nehmen Netz. Die Sprache
  passt. Erreicht werden sie nur von befehl_bilanz; tor() fragt buch
  nie. Und R18 prueft dieselbe Bedingung wie kern.aufnehmen()
  (regeln.py:338 gegen kern.py:323) — eine Regel, die dupliziert, was
  der Kern ohnehin tut.

---

## Produktive Leitung statt Call-Graph-Leitung (1.7)

Die Frage war: erzeugt ka.untersuchen() einen Befund, den das Tor als
erklaerende Diagnose verwenden kann, OHNE dass ka Statusentscheidungen
uebernimmt — und wird der Befund downstream wirklich VERWENDET.
Gemessen in probe_downstream.py, vier Stufen plus Invarianz plus
Ablation.

    Stufe 1  erreicht        ka: wege, wurzel_von, untersuchen,
                             frage_stellen — vom produktiven Pfad
    Stufe 2  verarbeitet     Rueckgabe liegt als Attest.diagnose
    Stufe 3  ergaenzt        Attest 20 -> 25 Zeilen, mit Weg und Frage
    Stufe 3a INVARIANZ       404 Vergleiche (100 Faelle x 4 Stufen +
                             Zirkel x 4): Ergebnis weicht 0-mal ab
    Stufe 4  Zustand         siehe Ablation

DIE ARBEITSTEILUNG
    ka.py        meldet    'Weg A -> B -> A laeuft durch die Behauptung'
    leitung.py   uebersetzt; rechnet Knoten.wurzel aus Netz.pfade()
                 statt es zu speichern
    tor.py       traegt den Befund, liest ihn NICHT fuer das Ergebnis
    __main__     entscheidet: keine automatische Bestaetigung

  ka.py importiert weiterhin NICHTS aus dem Paket. Es kann keine
  Statusentscheidung treffen, weil es Status, Stufe und Attest nicht
  kennt — nicht aus Zurueckhaltung, sondern aus Unfaehigkeit. Das ist
  die belastbare Form der Trennung.

FEHLER 35, von der Ablation gefunden
  Die erste Messung sagte 'Stufe 4 erfuellt' — zu Unrecht. kette()
  zaehlte weiterhin rohe Wurzelkennungen, waehrend r17 laengst
  unabhaengige_pfade() benutzte. Ein Zirkel A->B->A zaehlte in der
  Kette als eigene Wurzel: Kettenstatus BESTAETIGT, befehl_bilanz
  befoerderte automatisch, waehrend das Tor ueber die 2. Hand sperrte.
  Zwei Definitionen von 'unabhaengig' im selben Durchlauf — derselbe
  Befund wie bei R1/R17, eine Ebene hoeher. kette() benutzt jetzt
  unabhaengige_pfade().

  Folge fuer die Bewertung von ka: die Leitung hatte einen Kernfehler
  kompensiert. Nach der Korrektur steht der Beitrag schmaler, aber echt:

  ABLATION
    Zirkel + EINE Messung      Pfade 1    Kette VERMERK, Tor GESPERRT
       ohne Leitung VERMERK    mit Leitung VERMERK   KEIN Unterschied
    Zirkel + ZWEI Messungen    Pfade 2    Kette BESTAETIGT, Tor FREIGABE
       ohne Leitung BESTAETIGT mit Leitung VERMERK   UNTERSCHIED

  Nur der zweite Fall misst etwas: die Kette ist vollstaendig, das Tor
  gibt frei, alles sieht in Ordnung aus — und ka ist das EINZIGE, was
  meldet, dass eine der angegebenen Stuetzen zirkulaer ist. Die
  Buchhaltung verweigert daraufhin die automatische Bestaetigung.

  Im ersten Fall traegt ka nichts bei. Das ist kein Mangel: der
  gehaertete Kern erledigt den Fall selbst. Eine Leitung, die nur
  Kernfehler zudeckt, waere keine.

---

## Der Bogen-Eingang (1.8)

    python -m framenetwork schablone bogen.json

Ohne Datei laeuft weiterhin der Demolauf mit den vier Angriffen.

FORMAT
    {
      "ziel": "Z",                    Pflicht: welches Blatt behauptet
      "stufe": "S3",                  S0..S3, Vorgabe S1
      "pruefer": "Name",              fuer den Strang MENSCH
      "verwendet_am": "2026-09-23",   fuer die GELTUNG
      "blaetter": [
        {"kennung": "M1",
         "behauptung": "...",
         "herkunftsart": "gemessen",  gemessen | berichtet | gerechnet
         "grundlage": [],
         "bruecke": "",
         "rueckhalt": [],
         "einschraenkung": {"was": "PV", "wann": "2026"},
         "kippkriterium": "...",
         "stand": ["2026-08-31", "2026-01-10"]}
      ]
    }

ABGEWIESEN wird der Bogen bei: doppelter Kennung, unbekannter
Herkunftsart, fehlendem oder unbekanntem ziel, Blatt ohne Kennung.
NUR VERMERKT werden: Grundlage auf ein fehlendes Blatt, Kreise.
Beides steht in den Hinweisen und faellt P1 zur Last — gefiltert
wird nichts.

Ein Bogen laeuft in einem Durchgang durch beide Schichten: Abgleich,
Versagenspunkte, Negativliste, Mindestluege — und danach durch das Tor
bis zum Attest. art und uebernommen_aus werden aus der Form ABGELEITET.

Beispieldateien
    beispiel_bogen.json   sauber, S3 FREIGABE
    bogen_angriff.json    der S3-Angriff: 4 Widersprueche (P2,P3,P4,P5)
    bogen_kaputt.json     Kreis A->B->A plus fehlendes Blatt

FEHLER 36 bis 39 — alle vom ERSTEN echten Eingabebogen gefunden
  36  unbekannt(): ein nur genanntes Blatt wurde in P1 stillschweigend
      weggefiltert, die Meldung sagte 'Kette endet bei —'.
  37  zyklen(): boden() gab bei einem Kreis die leere Menge zurueck.
      Richtiges Ergebnis, unbrauchbare Begruendung.
  38  mindestluege(): KeyError auf einem nur genannten Blatt.
  39  nach_netz(): dieselbe Klasse, zweite Fundstelle.

  Kein Demolauf haette einen davon gezeigt. Das fehlende Blatt bleibt
  jetzt in uebernommen_aus stehen; kern macht daraus von selbst eine
  Wurzel mit der Marke #unbekannt, die nicht mitzaehlt. Beide Ebenen
  behandeln den Fall gleich, ohne eine zweite Regel dafuer.
