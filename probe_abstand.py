"""
probe_abstand.py — wie knapp sind die 40 sauberen Faelle vorbeigegangen?

"0 von 40 Fehlalarm" ist eine Zaehlung an einem Punkt. Sie sagt nicht,
ob die 40 weit weg lagen oder um Haaresbreite.

GEMESSEN WIRD DER ABSTAND: wie viele Felder muesste ein ehrlicher
Ausfueller LEER lassen, damit der Fall anschlaegt? Nicht luegen —
weglassen. Das ist der Fehler, den ein Mensch wirklich macht.

  Abstand 1  ein einziges leeres Feld genuegt        -> zerbrechlich
  Abstand 2  zwei muessten zusammenkommen
  Abstand 3+ auch mit drei Luecken bleibt es still   -> robust

VORAB FESTGELEGT

  V1  Die Verteilung ist NICHT gleichmaessig. Es gibt Faelle bei
      Abstand 1 und Faelle bei 3+.
  V2  Faelle bei Abstand 1 haengen ueberwiegend am Zielblatt, nicht
      an den Stuetzen — weil P4 das Zielblatt gegen seine Grundlage
      haelt.
  V3  GEFAHR: liegt der Median bei 1, ist "0 von 40" keine Aussage
      ueber das Regelwerk, sondern ueber die Sorgfalt dessen, der die
      40 Faelle gebaut hat. Das waere ein Befund gegen den Korpus.
"""
from __future__ import annotations

import sys
from collections import Counter
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schablone import erkennung
from schablone.schablone import Blatt, Satz, abgleichen

LEER = {"bruecke": "", "rueckhalt": (), "einschraenkung": {},
        "kippkriterium": "", "stand": (None, None), "annahmen": ()}


def leeren(s: Satz, zuege: Tuple[Tuple[str, str], ...]) -> Satz:
    neu = Satz(dict(s.blaetter))
    for k, feld in zuege:
        if k in neu.blaetter:
            neu.blaetter[k] = replace(neu.blaetter[k], **{feld: LEER[feld]})
    return neu


def abstand(s: Satz, ziel: str, tiefe: int = 3
            ) -> Tuple[Optional[int], Tuple[Tuple[str, str], ...]]:
    if abgleichen(s, ziel):
        return (0, ())
    kand = [(k, f) for k in sorted(s.traeger(ziel)) if k in s.blaetter
            for f in LEER]
    for n in range(1, tiefe + 1):
        for zug in combinations(kand, n):
            if abgleichen(leeren(s, zug), ziel):
                return (n, zug)
    return (None, ())


def main() -> int:
    a = print
    a("=" * 74)
    a("ABSTAND ZUR SCHWELLE — wie knapp gingen die sauberen Faelle vorbei?")
    a("=" * 74)
    a("\n  Gezaehlt wird, wie viele Felder LEER bleiben muessten, damit")
    a("  der Fall anschlaegt. Nicht gelogen — weggelassen.\n")

    verteilung: Counter = Counter()
    wo: Counter = Counter()
    beispiele: List[str] = []
    sauber = [f for f in erkennung.faelle() if not f.defekt]
    for f in sauber:
        n, zug = abstand(f.satz, f.ziel)
        verteilung[n if n is not None else "3+"] += 1
        if n == 1:
            k, feld = zug[0]
            wo[("Zielblatt" if k == f.ziel else "Stuetze") + f" . {feld}"] += 1
            if len(beispiele) < 4:
                beispiele.append(f"Fall {f.nr}: {k}.{feld} leer genuegt")

    a(f"  {'Abstand':<12}{'Faelle':>8}   was das heisst")
    a("  " + "-" * 62)
    for k in (0, 1, 2, 3, "3+"):
        if verteilung[k]:
            txt = {0: "schlaegt schon an (duerfte nicht sein)",
                   1: "ein leeres Feld genuegt — zerbrechlich",
                   2: "zwei muessten zusammenkommen",
                   3: "drei",
                   "3+": "auch mit drei Luecken still — robust"}[k]
            a(f"  {str(k):<12}{verteilung[k]:>8}   {txt}")

    n1 = verteilung[1]
    a(f"\n  V1 Verteilung ungleichmaessig: "
      f"{'JA' if len([k for k in verteilung if verteilung[k]]) > 1 else 'NEIN'}")
    a(f"  V3 Median bei 1: "
      f"{'JA — Befund gegen den Korpus' if n1 > len(sauber)/2 else 'nein'}")

    if wo:
        a(f"\n  WO die zerbrechlichen Faelle haengen ({n1} Faelle):")
        for k, v in wo.most_common():
            a(f"    {k:<28}{v:>3}")
        a("")
        for b in beispiele:
            a(f"    {b}")

    a("\n" + "=" * 74)
    a("  WAS DARAUS FOLGT")
    a("  '0 von 40' bleibt richtig. Aber es ist eine Zahl AN EINEM PUNKT.")
    a("  Die Verteilung daneben sagt, wie weit man diesen Punkt")
    a("  verschieben muesste, damit aus 0 etwas anderes wird —")
    a("  und das ist die Auskunft, die man beim Skalieren braucht.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
