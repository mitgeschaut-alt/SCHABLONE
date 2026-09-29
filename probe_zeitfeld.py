"""
probe_zeitfeld.py — VORBEFUND, vor jedem Umbau.

FRAGE

  F4 und F5 sind in 10 von 10 Laeufen gefallen. Die Erklaerung in
  BEFUND_D.md war: "die Zeitform einer deutschen Behauptung wird von
  keinem Eingriff beruehrt". Das ist eine Vermutung ueber Sprache.

  Es gibt eine zweite, langweiligere Erklaerung, und die ist vorher
  auszuschliessen: DAS ZEITFELD WIRD FALSCH BENUTZT.

  stand = [Daten ab, Kriterium festgelegt am]

  Wer es als [von, bis] liest, schreibt bei ehrlicher Arbeit
  ['2026-01-01', '2026-12-31'] hinein — und P5 feuert, weil
  kipp_am > daten_ab. Das waere ein Fehlalarm in jedem einzelnen
  Blatt, und keine einzige meiner 40 sauberen Faelle haette ihn je
  gesehen: die habe ICH ausgefuellt, und ich kenne die Bedeutung.

GEMESSEN WIRD

  1  Wie oft feuert P5 auf den sechs modellgefuellten Boegen?
  2  Wie viele dieser Blaetter haben ueberhaupt ein Kippkriterium?
     (Ein "Kriterium festgelegt am" ohne Kriterium ist sinnlos.)
  3  Wie oft feuert P4 auf dem Schluessel "wann", und wie viele davon
     sind blosse Schreibvarianten desselben Zeitraums?

  Punkt 3 entscheidet, ob F5 eine fehlende Regel ist oder eine
  vorhandene Regel auf Freitext.
"""
from __future__ import annotations

import glob
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schablone.schablone import Art_W, abgleichen, laden

JAHR = re.compile(r"(19|20)\d{2}")


def jahre(text: str) -> frozenset:
    """Die Jahreszahlen in einem Freitextfeld. Bewusst stumpf:
    wenn zwei Werte dieselben Jahre nennen, sind sie als ZEITRAUM
    gleich, auch wenn die Zeichenketten verschieden sind."""
    return frozenset(m.group(0) for m in JAHR.finditer(text or ""))


def main() -> int:
    a = print
    a("=" * 74)
    a("VORBEFUND ZEITFELD — feuern P4 und P5 aus dem richtigen Grund?")
    a("=" * 74)
    a("")

    p5_gesamt = 0
    p5_ohne_kriterium = 0
    p4_wann = 0
    p4_wann_gleiche_jahre = 0
    p4_wann_leer = 0
    arten: Counter = Counter()
    zeilen = []

    hier = Path(__file__).resolve().parent
    pfade = (sorted(glob.glob(str(hier / "boegen" / "bogen_[cd]*.json")))
             or sorted(glob.glob(str(hier / "bogen_[cd]*.json"))))
    if not pfade:
        a("  KEINE BOEGEN GEFUNDEN — erwartet in ./boegen/ oder hier.")
        a("  Ohne sie misst diese Probe nichts, statt null zu melden.")
        return 1
    for p in pfade:
        b = laden(p)
        s, ziel = b.satz, b.ziel
        ws = abgleichen(s, ziel)
        for w in ws:
            arten[w.art.name] += 1

        # ── 1 und 2: P5 ──────────────────────────────────────────────
        for w in ws:
            if w.art is not Art_W.NACHTRAEGLICH:
                continue
            p5_gesamt += 1
            k = w.betrifft[0]
            blatt = s.blaetter[k]
            if not blatt.kippkriterium.strip():
                p5_ohne_kriterium += 1
                zeilen.append(
                    f"    {Path(p).stem:<12} {k:<14} P5 feuert, "
                    f"KIPPKRITERIUM ist leer  stand={blatt.stand}")
            else:
                zeilen.append(
                    f"    {Path(p).stem:<12} {k:<14} P5 feuert, Kriterium "
                    f"da  stand={blatt.stand}")

        # ── 3: P4 auf dem Schluessel "wann" ──────────────────────────
        z = s.blaetter[ziel]
        unten = {}
        for g in z.grundlage:
            if g in s.blaetter:
                for kk, vv in s.blaetter[g].einschraenkung.items():
                    unten.setdefault(kk, set()).add(vv)
        for kk, werte in unten.items():
            if kk.lower() not in ("wann", "zeit", "zeitraum"):
                continue
            meiner = z.einschraenkung.get(kk)
            if meiner is None:
                p4_wann += 1
                p4_wann_leer += 1
                zeilen.append(f"    {Path(p).stem:<12} {ziel:<14} P4 'wann' "
                              f"fehlt im Ziel — echte Ueberdehnung")
            elif meiner not in werte:
                p4_wann += 1
                gleich = any(jahre(meiner) == jahre(v) and jahre(meiner)
                             for v in werte)
                if gleich:
                    p4_wann_gleiche_jahre += 1
                    zeilen.append(
                        f"    {Path(p).stem:<12} {ziel:<14} P4 'wann' "
                        f"{meiner!r} vs {sorted(werte)!r}")
                    zeilen.append(
                        f"    {'':<12} {'':<14}    -> GLEICHE JAHRE, "
                        f"nur andere Schreibweise")

    a("  ARTEN DER BEFUNDE AUF SECHS MODELLGEFUELLTEN BOEGEN")
    for k, v in arten.most_common():
        a(f"    {k:<26}{v:>4}")
    a("")
    a("  EINZELN")
    for zl in zeilen:
        a(zl)
    a("")
    a("  " + "=" * 68)
    a(f"  P5 NACHTRAEGLICH feuert {p5_gesamt} mal")
    a(f"     davon auf Blaettern OHNE Kippkriterium: {p5_ohne_kriterium}")
    a(f"  P4 auf Schluessel 'wann': {p4_wann} mal")
    a(f"     davon blosse Schreibvariante desselben Jahres: "
      f"{p4_wann_gleiche_jahre}")
    a(f"     davon echte Luecke (Ziel nennt 'wann' nicht): {p4_wann_leer}")
    a("")
    a("  LESART")
    a("  Ein P5, das auf einem Blatt ohne Kippkriterium feuert, sagt")
    a("  'das Kriterium wurde nachtraeglich festgelegt' ueber ein")
    a("  Kriterium, das es nicht gibt. Das ist kein Befund, das ist")
    a("  ein Formfehler des Feldes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
