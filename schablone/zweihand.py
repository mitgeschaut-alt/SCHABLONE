"""
zweihand.py — wie unabhaengig sind zwei Modelle wirklich?

DIE LAGE

  Die Testfaelle dieser Arbeit stammen von einem zweiten Modell und
  einem Menschen. Damit ist das Zwei-Hand-Verfahren nicht mehr ein
  Vorschlag, sondern laeuft bereits. Nur ist der WERT dieser zweiten
  Hand nie gemessen worden.

  In eigenstaendig.py steht, zwei Modelle haetten 'hoch korrelierte
  blinde Flecke, Kopplung etwa 0,8 bis 0,9'. Das ist eine Behauptung
  ohne Messung, mit einer Wurzel — nach den eigenen Regeln dieses
  Systems GESPERRT ab S1. Dieses Modul ersetzt sie durch ein
  Verfahren.

WARUM FANGZAHLEN HIER NICHT REICHEN

  Der uebliche Weg waere Lincoln-Petersen: zwei Beobachter, Ueberlapp
  messen, Dunkelziffer schaetzen. Das geht hier NICHT, und zwar aus
  einem Grund, der genau hierher gehoert:

      Lincoln-Petersen SETZT VORAUS, dass die beiden Beobachter
      unabhaengig sind. Unabhaengigkeit ist aber das, was gemessen
      werden soll.

  Man kann ein Verfahren nicht benutzen, um das zu messen, was es
  voraussetzt. Deshalb: AUSGESAEHTE Fehler statt gefundener. Bei
  ausgesaehten ist auch bekannt, was BEIDE uebersehen haben — das
  Feld, das sonst leer bleibt.

AUFRUF
  python -m schablone zweihand
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, lgamma, sqrt
from typing import Dict, List, Optional, Tuple


# ══ Der Sitzungsverlauf als erster, sehr kleiner Datenpunkt ═══════════
# Wer hat den Fehler gefunden? Ehrlich, nicht schmeichelhaft.
SELBST   = "selbst beim Lesen des eigenen Laufs"
HAND     = "die zweite Hand (Mensch/anderes Modell) direkt"
VORGABE  = "eine Vorgabe der zweiten Hand hat ihn sichtbar gemacht"

@dataclass(frozen=True)
class Vorfall:
    nr: int
    was: str
    finder: str
    art: str          # 'code' oder 'begriff'


VERLAUF: List[Vorfall] = [
    Vorfall(1,  "replace(',','.') zerlegt Prosa", SELBST, "code"),
    Vorfall(2,  "derselbe Fehler in paragraph.py", SELBST, "code"),
    Vorfall(3,  "sys.exit(0) auf Modulebene", SELBST, "code"),
    Vorfall(4,  "R9 meldete immer (Dauerfehlalarm)", VORGABE, "begriff"),
    Vorfall(5,  "v0.5 sperrte 2 von 3 auf S0", SELBST, "begriff"),
    Vorfall(6,  "Strang ZWEITE_HAND fehlte ganz", VORGABE, "begriff"),
    Vorfall(7,  "nach Quellenart gefiltert statt nach Inhalt", HAND,
                "begriff"),
    Vorfall(8,  "Sperrliste prueft nur Wurzeln", SELBST, "code"),
    Vorfall(9,  "Mutationsquote 100 % weil alle abstuerzten", SELBST, "code"),
    Vorfall(10, "bericht() zaehlt nach Klassenetikett", SELBST, "code"),
    Vorfall(11, "Prosa vor dem Lauf (schlussfolgerung)", SELBST, "begriff"),
    Vorfall(12, "Prosa vor dem Lauf (v05_buchhaltung)", SELBST, "begriff"),
    Vorfall(13, "Prosa vor dem Lauf (nachrechnen)", SELBST, "begriff"),
    Vorfall(14, "veraltete 67 % im Fliesstext", SELBST, "code"),
    Vorfall(15, "voellige Disjunktheit verlangt -> Dauerschweigen", SELBST,
                "begriff"),
    Vorfall(16, "Zahl im Text statt aus dem Lauf", SELBST, "code"),
    Vorfall(17, "replace(',','.') zum dritten Mal", SELBST, "code"),
    Vorfall(18, "Thompson-Fehler ueberlebte nur EINEN Neuschrieb", SELBST,
                "begriff"),
    Vorfall(19, "zweite Hand als Inspektor statt als Vergleich", SELBST,
                "begriff"),
    Vorfall(20, "Toleranz-Treffer als 'ohne Wirkung' etikettiert", SELBST,
                "code"),
]


# ══ Statistik ═════════════════════════════════════════════════════════
def _ibeta(x: float, a: float, b: float, n: int = 20000) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    s = sum(((i + 0.5) * x / n) ** (a - 1) * (1 - (i + 0.5) * x / n) ** (b - 1)
            for i in range(n)) * x / n
    return s / exp(lgamma(a) + lgamma(b) - lgamma(a + b))


def clopper_pearson(k: int, n: int, alpha: float = 0.05
                    ) -> Tuple[float, float]:
    def inv(p: float, a: float, b: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(60):
            m = (lo + hi) / 2
            if _ibeta(m, a, b) < p:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2
    u = 0.0 if k == 0 else inv(alpha / 2, k, n - k + 1)
    o = 1.0 if k == n else inv(1 - alpha / 2, k + 1, n - k)
    return u, o


def _z(p: float) -> float:
    """Inverse Normalverteilung, Acklam-Naeherung, reicht hier."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = sqrt(-2 * __import__("math").log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - pl:
        return -_z(1 - p)
    q, r = p - 0.5, (p - 0.5) ** 2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def umfang(p1: float, p2: float, alpha: float = 0.05,
           macht: float = 0.80) -> int:
    """Wie viele Faelle JE GRUPPE, um p1 von p2 zu unterscheiden."""
    za, zb = _z(1 - alpha / 2), _z(macht)
    pm = (p1 + p2) / 2
    n = (za * sqrt(2 * pm * (1 - pm))
         + zb * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2
    return int(n) + 1


@dataclass
class Vierfeld:
    """Ausgesaehte Fehler, zwei Modelle, alle vier Felder bekannt."""
    beide: int
    nur_a: int
    nur_b: int
    keiner: int

    @property
    def gesamt(self) -> int:
        return self.beide + self.nur_a + self.nur_b + self.keiner

    @property
    def a_findet(self) -> int:
        return self.beide + self.nur_a

    @property
    def b_gegeben_a(self) -> float:
        return self.beide / max(1, self.a_findet)

    @property
    def b_gegeben_nicht_a(self) -> float:
        n = self.nur_b + self.keiner
        return self.nur_b / max(1, n)

    @property
    def kopplung(self) -> float:
        """0 = unabhaengig, 1 = dieselbe Hand. Differenz der bedingten
        Wahrscheinlichkeiten, auf die eigene Spanne bezogen."""
        d = self.b_gegeben_a - self.b_gegeben_nicht_a
        rest = 1 - self.b_gegeben_nicht_a
        return max(0.0, min(1.0, d / rest)) if rest > 0 else 1.0

    def zeilen(self) -> List[str]:
        return [
            f"  {'':<16}{'B findet':>12}{'B uebersieht':>16}",
            f"  {'A findet':<16}{self.beide:>12}{self.nur_a:>16}",
            f"  {'A uebersieht':<16}{self.nur_b:>12}{self.keiner:>16}",
            "",
            f"  P(B findet | A findet)      {self.b_gegeben_a:>6.2f}",
            f"  P(B findet | A uebersieht)  {self.b_gegeben_nicht_a:>6.2f}",
            f"  KOPPLUNG                    {self.kopplung:>6.2f}",
        ]


def bericht() -> List[str]:
    z = ["ZWEIHAND — wie unabhaengig sind zwei Modelle wirklich?", ""]

    z.append("1 · WAS DIE ZWEITE HAND IN DIESER ARBEIT GEFUNDEN HAT")
    z.append("")
    n = len(VERLAUF)
    direkt = [v for v in VERLAUF if v.finder == HAND]
    vorgabe = [v for v in VERLAUF if v.finder == VORGABE]
    selbst = [v for v in VERLAUF if v.finder == SELBST]
    z.append(f"    {len(selbst):>3} von {n}   selbst beim Lesen des Laufs")
    z.append(f"    {len(vorgabe):>3} von {n}   durch eine Vorgabe der zweiten "
             f"Hand sichtbar")
    z.append(f"    {len(direkt):>3} von {n}   von der zweiten Hand DIREKT "
             f"gefunden")
    z.append("")
    u, o = clopper_pearson(len(direkt) + len(vorgabe), n)
    z.append(f"    Anteil der zweiten Hand  "
             f"{(len(direkt)+len(vorgabe))/n*100:.0f} %"
             f"   95%-Intervall [{u*100:.0f} %, {o*100:.0f} %]")
    z.append("")
    z.append("    Das sieht nach wenig aus. Es ist der falsche Blick.")
    z.append("    Entscheidend ist nicht die ZAHL, sondern die ART:")
    z.append("")
    for gruppe, titel in ((selbst, "selbst gefunden"),
                          (vorgabe + direkt, "zweite Hand")):
        code = len([v for v in gruppe if v.art == "code"])
        begr = len([v for v in gruppe if v.art == "begriff"])
        z.append(f"      {titel:<20}Code {code:>3}    Begriff {begr:>3}")
    z.append("")
    for v in direkt + vorgabe:
        z.append(f"      #{v.nr:<3} {v.was}")
    z.append("")
    z.append("    Der Fall, auf den es ankommt, ist #7: nach Quellenart")
    z.append("    filtern statt nach Inhalt. Das war in sich schluessig,")
    z.append("    lief fehlerfrei durch, verletzte keine Invariante — und")
    z.append("    widersprach dem Grundsatz des Systems. Kein Lauf haette")
    z.append("    das gemeldet. Genau die Sorte, die diagnose.py mit 17 %")
    z.append("    ausweist.")
    z.append("")
    z.append("    EIN FALL IST KEINE QUOTE. Aber es ist ein Fall der")
    z.append("    Sorte, die allein nachweislich NICHT auffindbar ist.")
    z.append("")

    z.append("2 · WARUM FANGZAHLEN HIER NICHT GEHEN")
    z.append("")
    z.append("    Lincoln-Petersen schaetzt aus dem Ueberlapp zweier")
    z.append("    Beobachter, was beide uebersehen haben — und SETZT")
    z.append("    dafuer VORAUS, dass die Beobachter unabhaengig sind.")
    z.append("    Unabhaengigkeit ist hier die gesuchte Groesse.")
    z.append("    Ein Verfahren kann nicht messen, was es voraussetzt.")
    z.append("")
    z.append("    Der Ausweg sind AUSGESAEHTE Fehler: dann ist auch")
    z.append("    bekannt, was BEIDE uebersehen haben. Das Feld, das")
    z.append("    sonst leer bleibt, ist das einzige, das die Frage")
    z.append("    beantwortet.")
    z.append("")

    z.append("3 · DAS VERFAHREN, DAS DIE FRAGE BEANTWORTET")
    z.append("")
    z.append("    a  mutanten.py erzeugt die Fehler MECHANISCH (AST-")
    z.append("       Mutation). Sie stammen aus einem Verfahren, nicht")
    z.append("       aus dem Urteil eines der beiden Modelle. 96 liegen")
    z.append("       bereits vor.")
    z.append("    b  Jeder Mutant geht an BEIDE Modelle, getrennt,")
    z.append("       gleicher Wortlaut, KEIN Blick auf die Antwort des")
    z.append("       anderen. Frage: steckt hier ein Fehler, und wo?")
    z.append("    c  Die Zuordnung 'richtig gefunden' steht VORHER fest —")
    z.append("       der Mutationsort ist bekannt. Kein Ermessen.")
    z.append("    d  Vierfeldertafel ausfuellen, Kopplung ausrechnen.")
    z.append("")
    z.append("    Zwei Beispiele, wie das Ergebnis aussieht:")
    z.append("")
    for name, v in (("FAST DIESELBE HAND", Vierfeld(38, 4, 3, 5)),
                    ("WEITGEHEND UNABHAENGIG", Vierfeld(18, 24, 21, 37))):
        z.append(f"    {name}")
        for zeile in v.zeilen():
            z.append("    " + zeile)
        wert = "fast nichts" if v.kopplung > 0.7 else "ein Vielfaches"
        z.append(f"      -> die zweite Hand bringt {wert}")
        z.append("")

    z.append("4 · WIE VIELE MUTANTEN GEBRAUCHT WERDEN")
    z.append("")
    z.append(f"    {'zu unterscheiden':<34}{'je Gruppe':>10}{'gesamt':>10}")
    z.append("    " + "-" * 54)
    for p1, p2, was in ((0.90, 0.50, "Kopplung 0,8 von Kopplung 0,0"),
                        (0.90, 0.70, "Kopplung 0,67 von Kopplung 0,0"),
                        (0.80, 0.70, "feine Abstufungen")):
        je = umfang(p1, p2)
        z.append(f"    {was:<34}{je:>10}{je*2:>10}")
    z.append("")
    z.append("    Die grobe Frage — bringt die zweite Hand ueberhaupt")
    z.append("    etwas — ist mit den 96 vorhandenen Mutanten bereits")
    z.append("    beantwortbar. Dafuer braucht es kein neues Werkzeug,")
    z.append("    nur einen Nachmittag und die Disziplin, die beiden")
    z.append("    Antworten nicht zu vermischen.")
    z.append("")

    z.append("5 · WAS AN DIESER MESSUNG NICHT GEPRUEFT IST")
    z.append("")
    z.append("    - Das Verfahren stammt von EINEM der beiden Modelle,")
    z.append("      also von einer Partei des Vergleichs. Es gehoert vor")
    z.append("      der Durchfuehrung dem anderen Modell und dem Menschen")
    z.append("      vorgelegt. Solange das nicht geschehen ist, steht es")
    z.append("      auf S0.")
    z.append("    - AST-Mutanten sind CODEFEHLER. Der Fall, der zaehlt")
    z.append("      (#7), war ein BEGRIFFSFEHLER. Die Messung beantwortet")
    z.append("      die Frage fuer die Sorte, die sie aussaeht — und die")
    z.append("      ist nicht die gefaehrliche.")
    z.append("    - Fuer Begriffsfehler gibt es kein mechanisches")
    z.append("      Aussaeverfahren. Dort bleibt nur: ein Mensch baut")
    z.append("      Faelle, bei denen die bequeme Antwort die falsche ist,")
    z.append("      und sagt die Loesung nicht.")
    return z
