"""
mutanten.py — die Loesung fuer die Haelfte, die eine Maschine loesen kann.

DAS PROBLEM

  Die Faelle der Konformitaetsprobe stammen von derselben Hand wie die
  Regeln. 47 von 47 ist deshalb keine Guetezahl, sondern eine erfuellte
  Mindestanforderung. Was fehlt, ist ein ANGREIFER, der nicht aus
  meinem Urteil kommt.

DIE LOESUNG FUER DEN TECHNISCHEN TEIL

  Nicht mehr Faelle schreiben, sondern die REGELN beschaedigen und
  nachsehen, ob die Probe es merkt. Das Verfahren heisst
  Mutationstest und ist seit den siebziger Jahren bekannt.

      < wird zu <=        Schwelle um eins verschoben
      and wird zu or      Bedingung aufgeweicht
      True wird zu False  Urteil umgedreht
      == wird zu !=       Vergleich umgedreht
      n wird zu n+1       Konstante verschoben

  Jede Beschaedigung ergibt eine eigene Fassung der Regeldatei. Faellt
  die Probe darueber, ist der Mutant ERLEGT. Laeuft die Probe durch,
  hat sie diese Stelle nicht geprueft — und das ist eine Luecke, die
  niemand nach Gefuehl ausgewaehlt hat.

  Die Mutationsquote je Regel ist damit genau die Zahl, die ich nach
  eigener Aussage nicht selbst herstellen kann: ein Mass fuer die
  Probe, das nicht von dem stammt, der die Probe geschrieben hat.

WAS ES NICHT LOEST

  Ob die Regeln die RICHTIGE Epistemik kodieren. Ein Mutationstest
  zeigt, dass die Probe den Code prueft. Er kann nicht sagen, ob
  'zwei disjunkte Wurzeln' das richtige Kriterium ist. Dafuer braucht
  es Faelle von Menschen.

AUFRUF
  python -m schablone mutanten
"""

from __future__ import annotations

import ast
import sys
import types
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import proben

QUELLE = Path(__file__).resolve().parent / "regeln.py"

VERGLEICH = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt,
    ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot, ast.IsNot: ast.Is,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
}


@dataclass
class Mutant:
    nummer: int
    regel: str
    art: str
    zeile: int
    beschreibung: str
    erlegt: bool = False
    fehler: Optional[str] = None

    @property
    def gelaufen(self) -> bool:
        """Ein Mutant, der gar nicht laedt, ist KEIN Beleg dafuer, dass
        die Probe etwas merkt. Er wird getrennt gezaehlt."""
        return self.fehler is None


class Sammler(ast.NodeVisitor):
    """Findet die Stellen, an denen mutiert werden kann, und merkt sich,
    in welcher Funktion sie liegen."""

    def __init__(self) -> None:
        self.stellen: List[Tuple[int, str, str, str]] = []
        self.funktion = "?"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        alt, self.funktion = self.funktion, node.name
        self.generic_visit(node)
        self.funktion = alt

    def visit_Compare(self, node: ast.Compare) -> None:
        for i, op in enumerate(node.ops):
            if type(op) in VERGLEICH:
                self.stellen.append(
                    (id(node), self.funktion, f"vergleich:{i}",
                     f"{type(op).__name__} -> "
                     f"{VERGLEICH[type(op)].__name__}"))
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.stellen.append(
            (id(node), self.funktion, "boolop",
             "and <-> or"))
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool):
            self.stellen.append(
                (id(node), self.funktion, "bool",
                 f"{node.value} -> {not node.value}"))
        elif isinstance(node.value, int) and not isinstance(node.value, bool):
            self.stellen.append(
                (id(node), self.funktion, "int",
                 f"{node.value} -> {node.value + 1}"))
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.Not):
            self.stellen.append(
                (id(node), self.funktion, "not", "not entfernt"))
        self.generic_visit(node)


class Aendern(ast.NodeTransformer):
    def __init__(self, ziel: int, art: str) -> None:
        self.ziel, self.art = ziel, art
        self.getroffen = False

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        if id(node) == self.ziel and self.art.startswith("vergleich:"):
            i = int(self.art.split(":")[1])
            node.ops[i] = VERGLEICH[type(node.ops[i])]()
            self.getroffen = True
        return self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        if id(node) == self.ziel and self.art == "boolop":
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
            self.getroffen = True
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if id(node) == self.ziel:
            if self.art == "bool":
                node.value = not node.value
                self.getroffen = True
            elif self.art == "int":
                node.value = node.value + 1
                self.getroffen = True
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        if id(node) == self.ziel and self.art == "not":
            self.getroffen = True
            return self.generic_visit(node.operand)
        return self.generic_visit(node)


def regel_von(funktion: str) -> str:
    """r1_unabhaengig -> R1"""
    if funktion.startswith("r") and "_" in funktion:
        return "R" + funktion[1:].split("_")[0]
    return funktion


def laden_als_modul(baum: ast.AST, name: str) -> types.ModuleType:
    """Der Mutant muss in sys.modules stehen, BEVOR er ausgefuehrt wird —
    sonst scheitert schon der @dataclass-Dekorator, und zwar bei jedem
    einzelnen Mutanten. Genau das ist beim ersten Lauf passiert: alle
    96 Mutanten stuerzten beim Laden ab, wurden als 'erlegt' gezaehlt,
    und der Bericht meldete eine Mutationsquote von 100 Prozent.

    Ein Instrument, das alles erlegt, misst so wenig wie eines, das
    nichts erlegt."""
    voll = f"framenetwork.{name}"
    quelltext = compile(baum, filename=f"<mutant {name}>", mode="exec")
    modul = types.ModuleType(voll)
    modul.__package__ = "framenetwork"
    modul.__name__ = voll
    sys.modules[voll] = modul
    try:
        exec(quelltext, modul.__dict__)
    except BaseException:
        sys.modules.pop(voll, None)
        raise
    return modul


def laufen(grenze: Optional[int] = None) -> List[Mutant]:
    text = QUELLE.read_text(encoding="utf-8")
    original = ast.parse(text)
    s = Sammler()
    s.visit(original)
    stellen = s.stellen
    if grenze:
        stellen = stellen[:grenze]

    echt = proben.R
    ergebnisse: List[Mutant] = []
    for i, (ziel, funktion, art, wie) in enumerate(stellen, start=1):
        baum = ast.parse(text)
        # ids stimmen nach dem Neuparsen nicht mehr — also erneut sammeln
        s2 = Sammler()
        s2.visit(baum)
        if i - 1 >= len(s2.stellen):
            continue
        ziel2, funktion2, art2, wie2 = s2.stellen[i - 1]
        m = Mutant(i, regel_von(funktion2), art2, 0, wie2)
        try:
            neu = Aendern(ziel2, art2).visit(baum)
            ast.fix_missing_locations(neu)
            modul = laden_als_modul(neu, f"regeln_m{i}")
            proben.R = modul
            ok, ges, _ = proben.lauf(False, True)
            m.erlegt = ok < ges
        except Exception as x:
            m.erlegt = False            # NICHT als Treffer zaehlen
            m.fehler = f"{type(x).__name__}"
        finally:
            proben.R = echt
            sys.modules.pop(f"framenetwork.regeln_m{i}", None)
        ergebnisse.append(m)
    return ergebnisse


def bericht(grenze: Optional[int] = None) -> List[str]:
    erg = laufen(grenze)
    gesamt = len(erg)
    gelaufen = [m for m in erg if m.gelaufen]
    kaputt = [m for m in erg if not m.gelaufen]
    erlegt = sum(1 for m in gelaufen if m.erlegt)
    je_regel: Dict[str, List[Mutant]] = {}
    for m in gelaufen:
        je_regel.setdefault(m.regel, []).append(m)

    z = ["MUTATIONSTEST — der Angreifer, der nicht aus meinem Urteil kommt", ""]
    z.append(f"  Mutanten erzeugt              {gesamt:>5}")
    z.append(f"  davon lauffaehig              {len(gelaufen):>5}")
    z.append(f"  davon beim Laden gescheitert  {len(kaputt):>5}"
             "   (kein Beleg, getrennt gezaehlt)")
    z.append(f"  erlegt                        {erlegt:>5}")
    if gelaufen:
        z.append(f"  Mutationsquote                {erlegt/len(gelaufen)*100:>5.1f} %"
                 "   nur ueber die lauffaehigen")
    z.append("")
    z.append(f"  {'Regel':<8}{'Mutanten':>10}{'erlegt':>9}{'Quote':>9}"
             "   ueberlebt")
    z.append("  " + "-" * 68)
    if not je_regel:
        z.append("  KEIN EINZIGER MUTANT LIEF. Die Quote oben ist keine.")
        return z
    for regel in sorted(je_regel, key=lambda r: (len(r), r)):
        ms = je_regel[regel]
        k = sum(1 for m in ms if m.erlegt)
        rest = [m.beschreibung for m in ms if not m.erlegt][:2]
        z.append(f"  {regel:<8}{len(ms):>10}{k:>9}{k/len(ms)*100:>8.0f} %"
                 f"   {', '.join(rest)}")
    z.append("")
    schwach = [r for r, ms in je_regel.items()
               if sum(1 for m in ms if m.erlegt) / len(ms) < 0.6]
    if schwach:
        z.append(f"  SCHWACH GEPRUEFT (unter 60 %): {', '.join(sorted(schwach))}")
        z.append("  Dort faellt die Probe ueber eine beschaedigte Regel nicht.")
    z.append("")
    z.append("  Was diese Quote NICHT sagt: ob die Regeln die richtige")
    z.append("  Epistemik kodieren. Sie sagt, ob die Probe den Code prueft.")
    return z
