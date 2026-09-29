"""
lebenszyklus.py — Paragraph als Bündel, Revalidierung statt Dauerschleife.

DIE VORGESCHLAGENE ARCHITEKTUR

  ENTWURF -> IN_PRUEFUNG -> BESTAETIGT_UNTER_PROFIL -> AKTIV
          -> FAELLIG -> IN_REVALIDIERUNG -> ABGELOEST / AKTIV

  Der Kerngedanke ist richtig und er ist eine Verbesserung: kein
  dauerlaufender Agent, sondern ein Zustand, der gilt, bis ein Anlass
  eine neue Pruefung rechtfertigt. 'Was macht der Agent ohne neue
  Information? Nichts.'

WAS DAVON SCHON IM CODE STEHT

  Netz.neue_fassung()   Abhaengigkeitsaenderung -> VERALTET, rueckwaerts
  buch.faellige()       was seit n Tagen offen ist
  Eintrag.fassung       Versionierung

  Der Ausloeser 'dependency_changed' ist also implementiert. Neu sind
  nur der ZEITLICHE Ausloeser und das Profil je Paragraphenart.

WAS DER ENTWURF VERLIERT — und das ist ein Rueckschritt

  In der Liste ENTWURF..ABGELOESE fehlt WIDERLEGT.

  ABGELOEST ist VERALTET: etwas Neues ist an die Stelle getreten.
  WIDERLEGT ist etwas anderes: ein Gegenbeleg liegt vor. Zwei der
  fuenf Nicht-Gleichungen haengen daran:

      geprueft und nicht bestaetigt   !=   widerlegt
      widerlegt                       !=   wertlos

  Ohne eigenen Endzustand kann ein widerlegter Paragraph ueber
  REVALIDIERUNG wieder nach AKTIV laufen. Genau das verbietet
  kern.py heute: WIDERLEGT hat eine LEERE Nachfolgemenge und filtert
  den Zulauf.

WAS AM NAMEN NICHT STIMMT

  'VERIFIED_UNDER_PROFILE' traegt das Wort verified im Zustandsnamen.
  Wer den Zustand abliest, liest 'verified' und nicht den Nachsatz —
  dasselbe Problem wie bei einem Feld namens hallucination_resistance,
  das 100 % meldet. BESTAETIGT_UNTER_PROFIL sagt dasselbe und laesst
  sich nicht auf 'bestaetigt' verkuerzen, ohne dass es auffaellt.

DER VERSTECKTE LOOP IN DER AUSLOESERLISTE

  review_trigger: time OR source_changed OR dependency_changed
                  OR contradiction_detected OR ruleset_changed
                  OR new_evidence

  'contradiction_detected' ist kein Ereignis, das von selbst eintritt.
  Jemand muss suchen. Damit ist die Dauerschleife nicht verschwunden,
  sie ist in den Ausloeser gewandert. Loesbar, aber nur so: Konflikte
  werden BEIM SCHREIBEN geprueft, gegen die Paragraphen, die dieselbe
  Groesse beruehren — nicht laufend gegen alles.

DIE EINZIGE BEHAUPTUNG, DIE HIER GEMESSEN WIRD

  'Muessen wir 100 Millionen Paragraphen bei jeder Aenderung
   vollstaendig ueberpruefen? Die Antwort sollte nein sein.'

  'Sollte' ist keine Messung. Die Kaskade haengt daran, wie die
  Wurzeln verteilt sind — und ausgerechnet die Quellwurzelrechnung
  sagt, dass sie NICHT gleichverteilt sind. Wenige Wurzeln tragen
  viele Aussagen. Dann invalidiert eine einzige Aenderung sehr viel.

AUFRUF
  python -m schablone lebenszyklus
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Tuple


# ══ 1 · Der Lebenszyklus, mit wiederhergestelltem Endzustand ══════════
class Zustand(Enum):
    ENTWURF        = "entwurf"
    IN_PRUEFUNG    = "in pruefung"
    BESTAETIGT     = "bestaetigt unter profil"
    AKTIV          = "aktiv"
    FAELLIG        = "faellig"
    REVALIDIERUNG  = "in revalidierung"
    ABGELOEST      = "abgeloest"
    WIDERLEGT      = "widerlegt"        # fehlte im Vorschlag


ZYKLUS: Dict[Zustand, FrozenSet[Zustand]] = {
    Zustand.ENTWURF:       frozenset({Zustand.IN_PRUEFUNG,
                                      Zustand.WIDERLEGT}),
    Zustand.IN_PRUEFUNG:   frozenset({Zustand.BESTAETIGT, Zustand.ENTWURF,
                                      Zustand.WIDERLEGT}),
    Zustand.BESTAETIGT:    frozenset({Zustand.AKTIV, Zustand.WIDERLEGT}),
    Zustand.AKTIV:         frozenset({Zustand.FAELLIG, Zustand.ABGELOEST,
                                      Zustand.WIDERLEGT}),
    Zustand.FAELLIG:       frozenset({Zustand.REVALIDIERUNG,
                                      Zustand.ABGELOEST, Zustand.WIDERLEGT}),
    Zustand.REVALIDIERUNG: frozenset({Zustand.AKTIV, Zustand.ABGELOEST,
                                      Zustand.WIDERLEGT}),
    Zustand.ABGELOEST:     frozenset({Zustand.REVALIDIERUNG,
                                      Zustand.WIDERLEGT}),
    Zustand.WIDERLEGT:     frozenset(),          # terminal, wie im Kern
}

# Eine gescheiterte Revalidierung fuehrt NICHT nach WIDERLEGT, sondern
# nach FAELLIG zurueck — geprueft und nicht bestaetigt != widerlegt.
BRAUCHT_GEGENBELEG = Zustand.WIDERLEGT


# ══ 2 · Die getrennten Achsen ═════════════════════════════════════════
# Der stichhaltigste Teil des Vorschlags: vier verschiedene Fragen, die
# regelmaessig zu einer verschmolzen werden.
ACHSEN: List[Tuple[str, str, Tuple[str, ...]]] = [
    ("anerkennung", "wird in der Fachwelt getragen",
     ("hoch", "geteilt", "randstaendig", "unbekannt")),
    ("belegguete", "wie stark ist die Evidenz",
     ("hoch", "mittel", "gering", "unbekannt")),
    ("beweisstand", "formal ableitbar",
     ("bewiesen", "erwartet", "teilweise", "unbekannt")),
    ("maschinenpruefbar", "auf eigenem Weg nachrechenbar",
     ("ja", "teilweise", "nein", "unbekannt")),
    ("aktualitaet", "gilt der Stand noch",
     ("gueltig", "faellig", "ueberholt", "unbekannt")),
]


# ══ 3 · Die Messung: wie gross ist die Kaskade? ═══════════════════════
@dataclass
class Kaskade:
    verteilung: str
    getroffen_direkt: float
    getroffen_gesamt: float
    groesste: float


def _zipf_wurzel(r: random.Random, anzahl: int, s: float) -> int:
    """Wurzel ziehen. s=0 gleichverteilt, s>0 wenige Wurzeln dominieren."""
    if s <= 0:
        return r.randrange(anzahl)
    # Inverse Transformation auf einer abgeschnittenen Zipf-Verteilung
    u = r.random()
    return min(anzahl - 1, int(anzahl ** (u ** (1 / (1 - s) if s < 1 else 3))))


def kaskade(n_paragraphen: int = 100_000, n_wurzeln: int = 2_000,
            wurzeln_je: int = 3, kanten_je: float = 2.0,
            s: float = 0.0, keim: int = 11) -> Kaskade:
    r = random.Random(keim)
    # Jeder Paragraph haengt an Wurzeln und an frueheren Paragraphen.
    an_wurzel: Dict[int, List[int]] = {w: [] for w in range(n_wurzeln)}
    kinder: List[List[int]] = [[] for _ in range(n_paragraphen)]
    for p in range(n_paragraphen):
        for _ in range(wurzeln_je):
            an_wurzel[_zipf_wurzel(r, n_wurzeln, s)].append(p)
        ganz, rest = int(kanten_je), kanten_je - int(kanten_je)
        for _ in range(ganz + (1 if r.random() < rest else 0)):
            if p:
                kinder[r.randrange(p)].append(p)

    # Eine Wurzel aendert sich. Wen trifft es, direkt und weitergereicht?
    direkt, gesamt, groesste = [], [], 0
    for _ in range(40):
        w = _zipf_wurzel(r, n_wurzeln, s)
        start = set(an_wurzel[w])
        direkt.append(len(start))
        rand, gesehen = list(start), set(start)
        while rand:
            p = rand.pop()
            for k in kinder[p]:
                if k not in gesehen:
                    gesehen.add(k)
                    rand.append(k)
        gesamt.append(len(gesehen))
        groesste = max(groesste, len(gesehen))
    m = len(direkt)
    return Kaskade(
        "gleichverteilt" if s <= 0 else f"Zipf s={s:g}",
        sum(direkt) / m / n_paragraphen * 100,
        sum(gesamt) / m / n_paragraphen * 100,
        groesste / n_paragraphen * 100)


def bericht() -> List[str]:
    z = ["LEBENSZYKLUS — Paragraph als Buendel, Revalidierung statt "
         "Dauerschleife", ""]

    z.append("1 · DER ZYKLUS, MIT DEM FEHLENDEN ENDZUSTAND")
    z.append("")
    for zu, nach in ZYKLUS.items():
        ziel = ", ".join(sorted(x.name for x in nach)) or "— terminal —"
        mk = "  <- fehlte im Vorschlag" if zu is Zustand.WIDERLEGT else ""
        z.append(f"    {zu.name:<16}-> {ziel}{mk}")
    z.append("")
    z.append("    ABGELOEST ist VERALTET: etwas Neues ist an die Stelle")
    z.append("    getreten. WIDERLEGT ist etwas anderes: ein Gegenbeleg")
    z.append("    liegt vor. Ohne eigenen Endzustand laeuft ein")
    z.append("    widerlegter Paragraph ueber REVALIDIERUNG wieder nach")
    z.append("    AKTIV. Das verbietet kern.py heute schon.")
    z.append("")

    z.append("2 · DIE GETRENNTEN ACHSEN — der stichhaltigste Teil")
    z.append("")
    for name, frage, werte in ACHSEN:
        z.append(f"    {name:<20}{frage}")
        z.append(f"    {'':<20}{' / '.join(werte)}")
    z.append("")
    z.append("    'Wissenschaftlich anerkannt' ist nicht 'formal")
    z.append("    beweisbar' ist nicht 'maschinell nachrechenbar'. Das")
    z.append("    ist eine sechste Nicht-Gleichung, und sie fehlte.")
    z.append("")

    z.append("3 · DIE KASKADE — die einzige gemessene Behauptung")
    z.append("")
    z.append("    100.000 Paragraphen, 2.000 Wurzeln, je 3 Wurzeln und")
    z.append("    2 Abhaengigkeiten. EINE Wurzel aendert sich. Wie viel")
    z.append("    Prozent des Bestandes muss neu geprueft werden?")
    z.append("")
    z.append(f"    {'Wurzelverteilung':<22}{'direkt':>9}{'mit Weitergabe':>17}"
             f"{'schlimmster':>13}")
    z.append("    " + "-" * 61)
    for s in (0.0, 0.5, 0.8, 0.95):
        k = kaskade(s=s)
        z.append(f"    {k.verteilung:<22}{k.getroffen_direkt:>8.2f}%"
                 f"{k.getroffen_gesamt:>16.1f}%{k.groesste:>12.1f}%")
    z.append("")
    z.append("    Auch GLEICHVERTEILT kaskadiert es auf ueber die Haelfte.")
    z.append("    Die Wurzelverteilung ist also nicht der Knopf. Der")
    z.append("    naechste Abschnitt sucht den richtigen.")
    z.append("")

    z.append("4 · DER KNOPF, AN DEM ES WIRKLICH HAENGT")
    z.append("")
    z.append("    Gleichverteilte Wurzeln, damit nur eine Groesse wirkt:")
    z.append("    wie viele Paragraphen haengen im Mittel an einem?")
    z.append("")
    z.append(f"    {'Abhaengige je Paragraph':<26}{'direkt':>9}"
             f"{'mit Weitergabe':>17}{'schlimmster':>13}")
    z.append("    " + "-" * 65)
    for g in (0.0, 0.5, 0.9, 1.0, 1.1, 1.5, 2.0):
        r = kaskade(kanten_je=g, s=0.0)
        z.append(f"    {g:<26.1f}{r.getroffen_direkt:>8.2f}%"
                 f"{r.getroffen_gesamt:>16.2f}%{r.groesste:>12.1f}%")
    z.append("")
    z.append("    Der Umschlag liegt zwischen 1,0 und 1,1 — und er ist")
    z.append("    scharf: bei 0,9 bleibt der schlimmste Fall unter 3 %,")
    z.append("    bei 1,1 springt er auf ueber 60 %. Das ist kein")
    z.append("    Zufall, das ist der Perkolationsschwellwert eines")
    z.append("    Verzweigungsprozesses: bis zu einem Nachfolger im")
    z.append("    Mittel sterben Kaskaden aus, darueber erreichen sie")
    z.append("    fast alles.")
    z.append("")
    z.append("    FOLGE FUER DEN ENTWURF: Die Frage 'zeitlicher oder")
    z.append("    ereignisgesteuerter Ausloeser' entscheidet gar nichts.")
    z.append("    Entscheidend ist, wie viele Paragraphen im Mittel auf")
    z.append("    einem anderen aufbauen. Ueber eins ist die")
    z.append("    Revalidierung unbeschraenkt — egal wie klug der")
    z.append("    Ausloeser ist.")
    z.append("")
    z.append("    Was daraus folgt und im Vorschlag fehlt: die")
    z.append("    Abhaengigkeitszahl muss eine GEMESSENE UND GEDECKELTE")
    z.append("    Groesse des Systems sein, so wie der Schuldendeckel")
    z.append("    aus R18. Nicht 'wir haben Abhaengigkeiten', sondern")
    z.append("    'im Mittel 0,8, Obergrenze 1,0, sonst Aufnahmestopp'.")
    return z
