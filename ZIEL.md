# FRAME-NETWORK — Ziel, festgelegt am 26.09.2026

## Wofür

**FrameNetwork ist ein Messinstrument für Modellausgaben.**

Gemessen wird nicht, ob ein Modell klug ist, sondern: wie viel eines
extern vorgegebenen Kontrollsystems trägt es, wenn es dieselben
Rohdaten bekommt wie jedes andere.

## Warum diese Wahl und keine andere

Nicht aus Eleganz, sondern wegen eines Defekts im Testkorpus:

    selbst gebaut   168 von 178 Fällen   94,4 %
    extern           10 von 178           5,6 %   (CDC/ACIP, GRADE)

Die Fehlalarmquote von 0 auf 40 Fällen misst die eigene
Vorstellungskraft. Modellantworten sind die erste Datenquelle in
diesem Projekt, die **weder der Auftraggeber noch der Entwickler
geschrieben hat**.

## Die methodische Falle und ihre Umgehung

Das Programm frisst einen Bogen, ein Modell liefert Prosa. Wer
übersetzt, konstruiert — dann wäre wieder alles selbst gebaut.

**Ausweg: das geprüfte Modell füllt den Bogen selbst.** Es bekommt die
Rohdaten und das Bogenformat, sonst nichts. Was ankommt, ist eine
Datei, kein Text, den jemand interpretiert.

Ehrlich benannt verschiebt das, was gemessen wird: nicht „wie gut denkt
das Modell", sondern „wie gut füllt es eine extern vorgegebene Struktur
aus". Das ist die Forschungsfrage des Benchmarks und nicht weniger wert.

## Was das Instrument kann, gemessen

    maschinell vergleichbar   4 von 8 Feldern = 50,0 %
      herkunftsart, grundlage, einschraenkung, stand
    nur mit Kodierern         4 von 8 Feldern = 50,0 %
      behauptung, bruecke, rueckhalt, kippkriterium

**Die Hälfte des Benchmarks läuft ohne Menschen.** Für die andere
Hälfte braucht es zwei unabhängige Kodierer und ein berichtetes Kappa.
Ohne das wäre es ein Urteil, das sich als Messung ausgibt.

## Trockenlauf des Instruments (nicht Messung von Modellen)

Drei konstruierte Bögen zu Testfall B, gegen einen Referenzbogen:

    Antwort                   Verlust            epist. Fehler
    A sorgfältig         4/28 [4–33 %]           0/24 [0–14 %]
    B schlampig          2/28 [1–24 %]           4/28 [4–33 %]
    C kaputt          Bogen abgewiesen                       —

Die Trennung funktioniert: A verliert Information und behauptet nichts
Falsches, B behauptet mehr als belegt und verliert wenig. Genau diese
zwei Profile sollten unterscheidbar sein.

## Was der Trockenlauf an Mängeln gefunden hat

**FEHLER 40 (im Instrument, behoben):** Der Widerspruchsvergleich
benutzte Mengen. Zwei UEBERDEHNUNG fielen auf eine zusammen, der
Bericht meldete „gleich". Vielfachheit ist hier Information.

**Testentwurfsfehler (meiner, offen):** Die Schlampigkeit in Bogen B
saß in Blättern, die das Zielblatt gar nicht stützen. Deshalb gab das
Tor beide Male FREIGABE — der Torvergleich wurde nicht geprüft. Beim
ersten echten Lauf muss der Defekt in der Stützkette liegen.

## Was als Nächstes zu tun ist, in dieser Reihenfolge

1. **Einen Referenzbogen vorab schreiben und datieren**, bevor
   irgendein Modell antwortet. Nach dem Sehen ist kein Kriterium.
2. **Eine Vorlage bauen**, die an jedes Modell identisch geht:
   Rohdaten + Bogenformat + nichts sonst. Kein Wort über
   Fehlerklassen, Bewertung oder erwartete Einsicht.
3. **Zehn bis zwanzig Fälle**, nicht drei. Bei den jetzigen
   Fallzahlen trennen die Intervalle nichts.
4. Erst dann messen.

## Was ausdrücklich nicht das Ziel ist

- Kein Gesamtscore. Pro Metrik ein Wert mit Nenner.
- Keine Aussage darüber, welches Modell besser ist. Nur: wie viel
  Struktur trägt es.
- Keine weiteren Regeln in den Kern. Zwei blinde Klassen
  (erfundene Quelle, falsche Brücke) sind prinzipiell unlösbar,
  vier weitere wären es über Einheitenalgebra und Nachrechnen —
  aber das ist ein anderes Ziel als dieses.
