"""
suche.py — warum das Ableiten nicht geht, und was stattdessen geht.

DIE FRAGE OHNE BERUFUNG AUF LITERATUR

  Wo genau liegt das Problem? Nicht 'es ist schwer'. Die Stelle.

  Es sind DREI verschiedene Dinge, die staendig in einen Topf kommen:

      ERZEUGEN   aus Axiomen ableitbare Saetze herstellen
      PRUEFEN    eine vorgelegte Ableitung nachvollziehen
      AUSWAEHLEN entscheiden, welche davon etwas bedeuten

  PRUEFEN ist billig. ERZEUGEN waechst exponentiell mit der Tiefe.
  AUSWAEHLEN gilt als ungeloest.

  UND GENAU DA STECKT DER DENKFEHLER.

  'Interessant' ist keine Eigenschaft eines Satzes. Es ist eine
  BEZIEHUNG zwischen einem Satz und einer offenen Frage. Ein Satz ist
  interessant, wenn sein Ergebnis etwas aendert, was gerade offen ist.
  Wer Interessantheit absolut definieren will, ohne offene Frage,
  sucht nach einer Eigenschaft, die es nicht gibt.

  Und FRAME-NETWORK hat etwas, was ein allgemeiner Beweissucher nicht
  hat: eine BUCHHALTUNG OFFENER FRAGEN. Konflikte, Vermerke,
  konkurrierende Hypothesen. Das ist eine ENDLICHE Zielmenge.

VIER HEBEL, KEINER BRAUCHT EINEN INTERESSANTHEITSBEGRIFF

  1 · ZIEL STATT AUFZAEHLUNG
      Nicht vorwaerts von den Axiomen, sondern rueckwaerts von den
      offenen Fragen. Gemessen in Teil 1.

  2 · TIEFE DECKELN
      Der wertvolle Fund ist die FLACHE Kombination, die nie gezogen
      wurde — nicht die tiefe, die niemand finden konnte. Teil 2.

  3 · NUR NACH WIDERSPRUECHEN SUCHEN
      Ein Widerspruch braucht kein Wertmass. Er ist per Bauart
      bedeutsam: irgendetwas im Buch muss sich aendern. Teil 3.

  4 · LUECKEN IN DER KO-VORKOMMENS-MATRIX
      Was nie zusammen betrachtet wurde, ist zaehlbar, ohne ueber
      Wert zu urteilen. Teil 4.

AUFRUF
  python -m schablone suche
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

STARTWERT = 20260921


@dataclass(frozen=True)
class Regel:
    praemissen: FrozenSet[str]
    schluss: str

    def __str__(self) -> str:
        return f"{' + '.join(sorted(self.praemissen))} -> {self.schluss}"


def theorie(rng: random.Random, saetze: int = 40,
            regeln: int = 120) -> Tuple[List[str], List[Regel], Set[str]]:
    namen = [f"s{i:02d}" for i in range(saetze)]
    axiome = set(namen[:5])
    rs = []
    for _ in range(regeln):
        k = rng.randint(1, 2)
        p = frozenset(rng.sample(namen, k))
        z = rng.choice(namen)
        if z not in p:
            rs.append(Regel(p, z))
    return namen, rs, axiome


# ══ 1 · Vorwaerts gegen rueckwaerts ═════════════════════════════════════
def vorwaerts(regeln: Sequence[Regel], axiome: Set[str],
              tiefe: int) -> Tuple[Set[str], int]:
    """Alles ableiten, was in 'tiefe' Schritten geht. Zaehlt Versuche."""
    bekannt = set(axiome)
    versuche = 0
    for _ in range(tiefe):
        neu = set()
        for r in regeln:
            versuche += 1
            if r.praemissen <= bekannt and r.schluss not in bekannt:
                neu.add(r.schluss)
        if not neu:
            break
        bekannt |= neu
    return bekannt, versuche


def rueckwaerts(regeln: Sequence[Regel], axiome: Set[str], ziel: str,
                tiefe: int, gesehen: Optional[Set[str]] = None,
                zaehler: Optional[List[int]] = None) -> Tuple[bool, int]:
    """Nur die Regeln ansehen, die auf das Ziel hinauslaufen."""
    zaehler = zaehler if zaehler is not None else [0]
    gesehen = gesehen or set()
    if ziel in axiome:
        return True, zaehler[0]
    if tiefe <= 0 or ziel in gesehen:
        return False, zaehler[0]
    gesehen = gesehen | {ziel}
    for r in regeln:
        if r.schluss != ziel:
            continue
        zaehler[0] += 1
        if all(rueckwaerts(regeln, axiome, p, tiefe - 1, gesehen, zaehler)[0]
               for p in r.praemissen):
            return True, zaehler[0]
    return False, zaehler[0]


def teil1() -> List[str]:
    rng = random.Random(STARTWERT)
    namen, regeln, axiome = theorie(rng)
    z = ["1 · ZIEL STATT AUFZAEHLUNG", ""]
    z.append(f"  {len(namen)} Saetze, {len(regeln)} Regeln, "
             f"{len(axiome)} Axiome.")
    z.append("")
    z.append(f"    {'Tiefe':>6}{'abgeleitet':>13}{'Regelversuche':>16}")
    z.append("    " + "-" * 35)
    for t in (1, 2, 3, 4, 6):
        b, v = vorwaerts(regeln, axiome, t)
        z.append(f"    {t:>6}{len(b):>13}{v:>16}")
    ganz, versuche_vor = vorwaerts(regeln, axiome, 20)
    z.append("")
    z.append(f"  Vorwaerts vollstaendig: {len(ganz)} Saetze, "
             f"{versuche_vor} Regelversuche.")
    z.append("")

    # Rueckwaerts auf drei offene Fragen
    offen = [s for s in namen if s in ganz][-3:]
    gesamt = 0
    for ziel in offen:
        ok, n = rueckwaerts(regeln, axiome, ziel, 6)
        gesamt += n
        z.append(f"  Rueckwaerts auf {ziel}: "
                 f"{'erreichbar' if ok else 'nicht erreichbar'}, "
                 f"{n} Regelversuche")
    z.append("")
    z.append(f"  drei Ziele zusammen: {gesamt} Versuche gegen "
             f"{versuche_vor} vorwaerts.")
    z.append("")
    z.append("  WAS AN DIESEN ZAHLEN NICHT ZAEHLT — zuerst der Einwand:")
    z.append("  der Vorwaertslauf ist naiv gebaut und prueft in jeder Runde")
    z.append("  alle Regeln neu. Ein guter Vorwaertssucher testet nur, was")
    z.append("  sich geaendert hat, und kaeme deutlich billiger weg. Das")
    z.append("  Verhaeltnis 47 zu 585 ist also zum Teil ein Artefakt meiner")
    z.append("  Implementierung, nicht des Verfahrens. Und 38 ableitbare")
    z.append("  Saetze sind zu wenig, um irgendetwas ueber das Wachstum zu")
    z.append("  zeigen.")
    z.append("")
    z.append("  Was BLEIBT, ist strukturell und haengt an keiner Messung:")
    z.append("  vorwaerts muss ALLES ableiten, rueckwaerts nur das, was das")
    z.append("  Ziel braucht. Der Unterschied waechst mit der ableitbaren")
    z.append("  Menge und verschwindet, wenn beide gleich gross sind.")
    z.append("")
    z.append("  DIE BEDINGUNG, unter der das gilt — und sie ist der Punkt:")
    z.append("  Rueckwaerts gewinnt, WENN die Zielmenge klein ist gegenueber")
    z.append("  der ableitbaren Menge. Bei einem Ziel je offener Frage ist")
    z.append("  sie genau so gross wie die Buchhaltung offener Fragen.")
    z.append("  Die Bilanz ist also nicht nur Ordnung — sie ist das,")
    z.append("  was die Suche endlich macht.")
    z.append("")
    z.append("  Und umgekehrt: hat das Buch keine offenen Fragen, gibt es")
    z.append("  nichts zu suchen. Ein System ohne Konflikte ist kein")
    z.append("  fertiges System, sondern ein blindes.")
    return z


# ══ 2 · Die flache, nie gezogene Kombination ════════════════════════════
def teil2() -> List[str]:
    rng = random.Random(STARTWERT)
    namen, regeln, axiome = theorie(rng)
    z = ["", "2 · DIE FLACHE KOMBINATION, DIE NIE GEZOGEN WURDE", ""]

    benutzt: Set[FrozenSet[str]] = set()
    for r in regeln:
        if len(r.praemissen) == 2:
            benutzt.add(r.praemissen)
    ganz, _ = vorwaerts(regeln, axiome, 20)
    moeglich = list(combinations(sorted(ganz), 2))
    nie = [p for p in moeglich if frozenset(p) not in benutzt]

    z.append(f"  ableitbare Saetze            {len(ganz):>6}")
    z.append(f"  moegliche Zweierkombinationen {len(moeglich):>6}")
    z.append(f"  davon je zusammen betrachtet  "
             f"{len(moeglich)-len(nie):>6}")
    z.append(f"  NIE zusammen betrachtet       {len(nie):>6}")
    z.append("")
    z.append("  Das ist die eigentliche Fundgrube, und sie ist ZAEHLBAR.")
    z.append("  Eine tiefe Konsequenz, die niemand gefunden hat, ist meist")
    z.append("  tief, weil ein Schritt fehlt, den niemand formalisiert hat.")
    z.append("  Eine FLACHE Kombination, die nie gezogen wurde, ist ein")
    z.append("  Versehen — und Versehen sind auffindbar.")
    z.append("")
    z.append("  Die Zahl ist gross. Sie ist aber endlich, bekannt und")
    z.append("  abarbeitbar — im Gegensatz zu 'alle Konsequenzen von T'.")
    return z


# ══ 3 · Widersprueche brauchen kein Wertmass ════════════════════════════
def teil3() -> List[str]:
    z = ["", "3 · WIDERSPRUECHE BRAUCHEN KEIN WERTMASS", ""]
    z.append("  Das ganze Problem der Interessantheit entsteht bei der")
    z.append("  Frage: 'ist dieser wahre Satz es wert?'")
    z.append("")
    z.append("  Bei einem Widerspruch stellt sich die Frage nicht.")
    z.append("  Ein Widerspruch ist bedeutsam per Bauart: irgendetwas im")
    z.append("  Buch MUSS sich aendern — eine Folgerung, eine Annahme,")
    z.append("  eine Formalisierung oder die Theorie.")
    z.append("")
    z.append("  Daraus folgt eine Arbeitsteilung, die nichts kostet:")
    z.append("")
    z.append("     erzeugen und bewerten   ungeloest, wird nicht versucht")
    z.append("     erzeugen und auf")
    z.append("     Widerspruch pruefen     entscheidbar ueber endlicher Menge")
    z.append("")
    z.append("  Das System sucht also nicht nach neuen Wahrheiten. Es")
    z.append("  sucht nach Stellen, an denen das Buch mit sich selbst")
    z.append("  nicht auskommt. Jeder Fund ist ein Auftrag, keiner ist")
    z.append("  ein Urteil.")
    z.append("")
    z.append("  DIE GRENZE, ehrlich: ein widerspruchsfreies Buch liefert")
    z.append("  auf diesem Weg nichts. Dann bleibt nur Hebel 2 — die")
    z.append("  ungezogenen flachen Kombinationen.")
    return z


# ══ 4 · Luecken in der Ko-Vorkommens-Matrix ═════════════════════════════
def teil4() -> List[str]:
    rng = random.Random(STARTWERT)
    namen, regeln, axiome = theorie(rng)
    z = ["", "4 · WAS NIE ZUSAMMEN BETRACHTET WURDE", ""]

    ko: Dict[str, Set[str]] = {s: set() for s in namen}
    for r in regeln:
        beteiligte = sorted(r.praemissen | {r.schluss})
        for a, b in combinations(beteiligte, 2):
            ko[a].add(b)
            ko[b].add(a)
    einsam = sorted(namen, key=lambda s: len(ko[s]))[:6]
    dicht = sorted(namen, key=lambda s: -len(ko[s]))[:3]

    z.append(f"  {'Satz':<8}{'Nachbarn':>10}")
    z.append("  " + "-" * 20)
    for s in dicht:
        z.append(f"  {s:<8}{len(ko[s]):>10}   dicht untersucht")
    for s in einsam[:4]:
        z.append(f"  {s:<8}{len(ko[s]):>10}   kaum betrachtet")
    z.append("")
    z.append("  Die Beobachtung, um die es geht: die Forschung sammelt")
    z.append("  sich dort, wo schon Konsequenzen bekannt sind. Was")
    z.append("  daneben liegt, wird weniger untersucht.")
    z.append("")
    z.append("  Diese Ungleichverteilung ist keine Vermutung, sie steht")
    z.append("  im Graphen und laesst sich auszaehlen. Und sie braucht")
    z.append("  kein Urteil darueber, was wertvoll ist — nur die")
    z.append("  Feststellung, was noch nie nebeneinander lag.")
    return z


def schluss() -> List[str]:
    return ["", "═" * 70, "", "  WO DAS PROBLEM WIRKLICH LIEGT", "",
            "  Nicht darin, dass Ableiten zu teuer ist — das laesst sich",
            "  durch ein Ziel und eine Tiefengrenze beherrschen.",
            "",
            "  Sondern darin, dass 'interessant' ohne offene Frage nicht",
            "  definiert ist. Die Loesung ist deshalb keine bessere",
            "  Bewertungsfunktion, sondern eine ANDERE FRAGESTELLUNG:",
            "",
            "     statt  'welche Konsequenz von T ist wertvoll?'",
            "     lieber 'welche Konsequenz entscheidet etwas, das in",
            "            meinem Buch offen ist?'",
            "",
            "  Die zweite Frage ist endlich, zaehlbar und braucht kein",
            "  Wertmass. Die Buchhaltung offener Fragen ist damit nicht",
            "  Beiwerk, sondern der Motor.",
            "",
            "  WAS DAMIT NICHT GELOEST IST — und das ist ehrlich die",
            "  groesste Luecke:",
            "",
            "  Alle vier Hebel rekombinieren, was bereits formalisiert",
            "  ist. Keiner erfindet einen NEUEN BEGRIFF. Genau das tun",
            "  Menschen, wenn eine Theorie wirklich weiterkommt — sie",
            "  fuehren einen Gegenstand ein, den vorher niemand hatte.",
            "  Dafuer habe ich keinen Vorschlag, und ich halte es fuer",
            "  unredlich, so zu tun, als waere es dieselbe Art Problem.",
            ]


def bericht() -> List[str]:
    z = ["DIE SUCHE — wo das Problem liegt und was trotzdem geht", ""]
    z += teil1() + teil2() + teil3() + teil4() + schluss()
    return z
