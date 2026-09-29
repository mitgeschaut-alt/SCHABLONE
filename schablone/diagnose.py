"""
diagnose.py — faellt ein Rechenfehler beim Durchlaufen auf?
              und: was soll das Modell kuenftig anders machen?

DER EINWAND, DER HIER GEMESSEN WIRD

  'Wenn so ein System einen mathematischen Fehler hat, wird es beim
   Durchlaufen ja auffallen.'

  Das ist keine Meinung, das ist eine Tatsachenbehauptung ueber Code.
  Sie wird hier an den ECHTEN Formeln aus nachrechnen.py gemessen,
  nicht an einem Modell mit erfundenen Parametern.

DIE UNTERSCHEIDUNG, AUF DIE ES ANKOMMT

  EINZELFEHLER   ein Ausrutscher an EINER Stelle. Die anderen Wege
                 rechnen weiter richtig.
  GRUNDFEHLER    ein uebernommener Denkfehler, der in JEDEM Weg
                 steckt, weil jeder Weg aus derselben Vorstellung
                 gebaut ist. Genau der Fall, um den es geht: das
                 Modell hat ihn, das Programm erbt ihn beim
                 Mitschreiben.

  Beide sind mathematische Fehler. Beide laufen durch. Ob sie
  auffallen, entscheidet nicht das Durchlaufen, sondern ob es einen
  Weg gibt, der den Fehler NICHT teilt.

AUFRUF
  python -m schablone diagnose
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Dict, List, Optional, Tuple

from .nachrechnen import (Ausgang, Behauptung, Methode, Rechenwerk, DATEN,
                          werk)


class Ausfall:
    ABSTURZ   = "Absturz"             # faellt sofort auf
    GEFANGEN  = "gefangen"            # der Gegenweg meldet Abweichung
    STILL     = "still falsch"        # laeuft durch, Zahl ist falsch
    TOLERANZ  = "Toleranz deckt ab"   # falsch, aber innerhalb der erklaerten
                                      # Toleranz — ZAEHLT ALS NICHT GEFANGEN
    NICHTS    = "ohne Wirkung"        # Ergebnis identisch, kein Fehler


# ── Fehlerarten, die in echtem Zahlencode wirklich vorkommen ──────────
ARTEN_REIHE = (Ausfall.ABSTURZ, Ausfall.GEFANGEN, Ausfall.STILL,
               Ausfall.TOLERANZ, Ausfall.NICHTS)


def _wirksam(c: Dict[str, int]) -> int:
    """Alles ausser 'Ergebnis identisch' ist ein wirksamer Fehler —
    die von der Toleranz gedeckten AUSDRUECKLICH mitgezaehlt."""
    return sum(v for k, v in c.items() if k != Ausfall.NICHTS)


def _aufgefallen(c: Dict[str, int]) -> int:
    return c[Ausfall.ABSTURZ] + c[Ausfall.GEFANGEN]


def _mal(f: Callable, k: float) -> Callable:
    return lambda d: f(d) * k


def _plus(f: Callable, k: float) -> Callable:
    return lambda d: f(d) + k


def _komplement(f: Callable) -> Callable:
    return lambda d: 1 - f(d)


def _teilen_durch_null(f: Callable) -> Callable:
    return lambda d: f(d) / 0


FEHLERARTEN: List[Tuple[str, Callable[[Callable], Callable]]] = [
    ("Einheitenfehler  (kW statt W)",  lambda f: _mal(f, 1000)),
    ("Prozentfehler    (/100)",        lambda f: _mal(f, 0.01)),
    ("Komplement       (1-x statt x)", _komplement),
    ("Verschiebung     (+1)",          lambda f: _plus(f, 1)),
    ("kleiner Ausrutscher (x 1,02)",   lambda f: _mal(f, 1.02)),
    ("Division durch Null",            _teilen_durch_null),
]


def _mutieren(w: Rechenwerk, treffer: List[str],
              schaden: Callable[[Callable], Callable]) -> Rechenwerk:
    neu = Rechenwerk()
    for m in w.methoden:
        neu.m(replace(m, rechne=schaden(m.rechne)) if m.name in treffer else m)
    return neu


def _einordnen(w_kaputt: Rechenwerk, b: Behauptung,
               wahr: float) -> Tuple[str, Optional[float]]:
    """Was passiert, wenn das Modell mit dem kaputten Werk rechnet und
    das Framework das Ergebnis prueft?"""
    m = w_kaputt.nach(b.weg)
    try:
        geliefert = m.rechne(DATEN)
    except ZeroDivisionError:
        return Ausfall.ABSTURZ, None
    abstand = abs(geliefert - wahr)
    if abstand == 0:
        return Ausfall.NICHTS, geliefert
    if abstand <= b.toleranz:
        # ERSTE FASSUNG nannte das 'ohne Wirkung' und rechnete es aus
        # dem Nenner heraus. Das ist falsch: die Zahl IST falsch, sie
        # passt nur durch das Fenster, das vorher erklaert wurde.
        return Ausfall.TOLERANZ, geliefert
    vorgelegt = replace(b, wert=geliefert)
    try:
        bericht = w_kaputt.pruefen(vorgelegt, DATEN)
    except ZeroDivisionError:
        return Ausfall.ABSTURZ, geliefert
    if bericht.ausgang is Ausgang.ABWEICHEND:
        return Ausfall.GEFANGEN, geliefert
    return Ausfall.STILL, geliefert


def durchlauf() -> Dict[str, object]:
    rein = werk()
    groessen = {
        "eigenverbrauchsquote": ("quote_direkt",
                                 ["quote_direkt", "quote_komplement"]),
        "plananteil": ("anteil_direkt",
                       ["anteil_direkt", "anteil_ueber_teile"]),
        "spezifischer_ertrag": ("spezifisch", ["spezifisch"]),
    }
    zeilen: List[Tuple[str, str, str, str, Optional[float]]] = []
    zaehl = {"EINZEL": {}, "GRUND": {}}
    for art in ARTEN_REIHE:
        zaehl["EINZEL"][art] = 0
        zaehl["GRUND"][art] = 0

    for groesse, (weg, alle) in groessen.items():
        wahr = rein.nach(weg).rechne(DATEN)
        b = Behauptung(groesse, wahr, weg, 0.005, "2026-09-01")
        for name, schaden in FEHLERARTEN:
            for lage, treffer in (("EINZEL", [weg]), ("GRUND", alle)):
                kaputt = _mutieren(rein, treffer, schaden)
                art, geliefert = _einordnen(kaputt, b, wahr)
                zaehl[lage][art] += 1
                zeilen.append((groesse, name, lage, art, geliefert))
    return {"zeilen": zeilen, "zaehl": zaehl, "groessen": groessen}


# ══ Abschnitt 3 — was soll das Modell anders machen? ══════════════════
# NICHT erfundene Ratschlaege. Jede Zeile traegt die Faelle, aus denen
# sie stammt, und die Zahl ist die Haeufigkeit IN DIESER ARBEIT.
@dataclass(frozen=True)
class Anweisung:
    rang: int
    satz: str
    faelle: int
    beleg: str
    pruefbar_durch: str


ANWEISUNGEN: List[Anweisung] = [
    Anweisung(
        1, "Keinen Satz ueber ein Ergebnis schreiben, bevor der Lauf "
           "vorliegt. Zahlen im Fliesstext aus dem Lauf rechnen, nie "
           "ausschreiben.", 3,
        "Fehler 16 und zwei gleichartige vorher: Text behauptete 67 %, "
        "der Lauf druckte 50 %.",
        "Textvergleich: jede Prozentzahl in der Prosa muss als "
        "Formatfeld aus einer Variablen kommen."),
    Anweisung(
        2, "Ein Experiment muss pruefen, was es zu pruefen vorgibt. Vor "
           "dem Lauf festhalten, welches Ergebnis die Behauptung "
           "WIDERLEGEN wuerde.", 2,
        "Fehler 18 und 19: Thompson-Fehler ueberlebten nur EINEN "
        "Neuschrieb; die zweite Hand war als Inspektor statt als "
        "Vergleich modelliert.",
        "Vorher-Notiz mit dem Widerlegungsfall, vor dem ersten Lauf "
        "geschrieben."),
    Anweisung(
        3, "Kein Kriterium ausliefern, das im Probelauf NIE greift — "
           "Dauerschweigen ist derselbe Fehler wie Dauerfehlalarm.", 2,
        "R9 meldete immer (Dauerfehlalarm); Fehler 15 verlangte voellig "
        "disjunkte Eingaben und schwieg dadurch immer.",
        "Konformitaetsprobe: jede Regel braucht einen greifenden UND "
        "einen stillen Fall."),
    Anweisung(
        4, "Zahlen nie durch blockweise Textersetzung formatieren.", 3,
        "Dreimal .replace(',', '.') ueber einen ganzen Block; zuletzt "
        "als '72.834.0' gedruckt.",
        "Suche nach replace auf Textbloecken mit Zahlen."),
    Anweisung(
        5, "Jede gelieferte Zahl mit einem zweiten Weg rechnen oder "
           "ausdruecklich als ungeprueft ausweisen.", 0,
        "kein Fall in dieser Arbeit — die Anweisung folgt aus "
        "Abschnitt 1, nicht aus einem Vorfall.",
        "nachrechnen: Ausgang NUR_NACHGESPIELT muss im Attest stehen."),
]


def bericht() -> List[str]:
    d = durchlauf()
    z = ["DIAGNOSE — faellt ein Rechenfehler beim Durchlaufen auf?", ""]

    z.append("1 · DER EINWAND, GEMESSEN AN ECHTEM CODE")
    z.append("")
    z.append("  In die Formeln aus nachrechnen.py werden sechs Fehlerarten")
    z.append("  eingebaut, die in echtem Zahlencode wirklich vorkommen.")
    z.append("  Zweimal je Fehlerart:")
    z.append("")
    z.append("    EINZEL   nur der benutzte Weg ist beschaedigt")
    z.append("    GRUND    JEDER Weg zu dieser Groesse ist gleich")
    z.append("             beschaedigt — der geerbte Denkfehler")
    z.append("")
    z.append(f"  {'Groesse':<22}{'Fehlerart':<32}{'Lage':<8}Ausgang")
    z.append("  " + "-" * 82)
    for groesse, name, lage, art, _ in d["zeilen"]:
        marke = "   <-" if art in (Ausfall.STILL, Ausfall.TOLERANZ) else ""
        z.append(f"  {groesse:<22}{name:<32}{lage:<8}{art}{marke}")
    z.append("")

    for lage, titel in (("EINZEL", "EINZELFEHLER — an einer Stelle"),
                        ("GRUND", "GRUNDFEHLER — in jedem Weg derselbe")):
        c = d["zaehl"][lage]
        z.append(f"  {titel}")
        for art in ARTEN_REIHE:
            z.append(f"    {art:<20}{c[art]:>3}")
        wirksam = _wirksam(c)
        if wirksam:
            z.append(f"    faellt auf:       {_aufgefallen(c)}/{wirksam} = "
                     f"{_aufgefallen(c)/wirksam*100:.0f} % der wirksamen "
                     f"Fehler")
        z.append("")

    z.append("2 · WAS DIE ZAHLEN SAGEN")
    z.append("")
    ce, cg = d["zaehl"]["EINZEL"], d["zaehl"]["GRUND"]
    we, wg = _wirksam(ce), _wirksam(cg)
    ae, ag = _aufgefallen(ce), _aufgefallen(cg)
    z.append(f"    Einzelfehler fallen auf:   {ae}/{we} "
             f"({ae/max(1,we)*100:.0f} %)")
    z.append(f"    Grundfehler  fallen auf:   {ag}/{wg} "
             f"({ag/max(1,wg)*100:.0f} %)")
    z.append("")
    z.append("    Nur der Absturz faellt VON SELBST auf — und Absturz")
    z.append("    heisst, dass der Fehler eine Regel des RECHNENS")
    z.append("    verletzt, nicht dass die Zahl falsch ist. Division")
    z.append("    durch Null stuerzt ab, ob sie nun einzeln oder")
    z.append("    grundsaetzlich ist. Ein falscher Faktor tut das nie.")
    z.append("    Alles ausser dem Absturz braucht einen Weg, der den")
    z.append("    Fehler NICHT teilt.")
    z.append("")
    tol = [zz for zz in d["zeilen"] if zz[3] == Ausfall.TOLERANZ]
    if tol:
        z.append(f"    UND EIN BEFUND, DER NICHT GEPLANT WAR: {len(tol)} "
                 f"Fehler sind")
        z.append("    falsch und kommen trotzdem durch, weil sie in die")
        z.append("    VORHER erklaerte Toleranz passen:")
        for groesse, name, lage, _, wert in tol:
            z.append(f"      {groesse} / {name} / {lage}  ->  {wert:g}")
        z.append("    Die Toleranz schuetzt davor, dass sie hinterher")
        z.append("    geweitet wird. Sie ist trotzdem ein Fenster, und")
        z.append("    alles, was hindurchpasst, wird nie gemeldet.")
        z.append("")
    einweg = [zz for zz in d["zeilen"]
              if zz[0] == "spezifischer_ertrag" and zz[3] == Ausfall.STILL]
    z.append(f"    spezifischer_ertrag hat nur EINEN Weg. Dort bleiben")
    z.append(f"    {len(einweg)} Fehler still — unabhaengig davon, ob sie")
    z.append("    einzeln oder grundsaetzlich sind. Nicht das Durchlaufen")
    z.append("    entscheidet, sondern die Redundanz.")
    z.append("")

    z.append("3 · WAS DAS PROGRAMM ERKLAERT, WENN ES ETWAS FINDET")
    z.append("")
    rein = werk()
    wahr = rein.nach("quote_direkt").rechne(DATEN)
    kaputt = _mutieren(rein, ["quote_direkt"], lambda f: _mal(f, 1.02))
    geliefert = kaputt.nach("quote_direkt").rechne(DATEN)
    b = Behauptung("eigenverbrauchsquote", geliefert, "quote_direkt",
                   0.005, "2026-09-01")
    r = kaputt.pruefen(b, DATEN)
    for zeile in r.zeilen():
        z.append("    " + zeile)
    z.append("")
    z.append("    Das ist kein Urteil, das ist eine ORTSANGABE: welche")
    z.append("    zwei Wege, welche Eingaben jeder benutzt, was sie")
    z.append("    teilen, wie gross der Unterschied ist und welche")
    z.append("    Toleranz wann erklaert wurde. Damit laesst sich")
    z.append("    suchen. Ein blosses 'gesperrt' waere wertlos.")
    z.append("")
    z.append("    ABER: die Ortsangabe sagt NICHT, welcher Weg irrt.")
    z.append("    Sie grenzt ein. Das ist weniger als eine Loesung und")
    z.append("    sehr viel mehr als ein Verdacht.")
    z.append("")

    z.append("4 · ANWEISUNGEN AN DAS MODELL")
    z.append("")
    z.append("    Abgeleitet aus GEZAEHLTEN Vorfaellen dieser Arbeit,")
    z.append("    nicht aus guten Vorsaetzen. Jede Zeile nennt ihre")
    z.append("    Faelle und wie sie maschinell nachgehalten wird.")
    z.append("")
    for a in sorted(ANWEISUNGEN, key=lambda x: -x.faelle):
        z.append(f"    [{a.faelle}x]  {a.satz}")
        z.append(f"            Beleg:    {a.beleg}")
        z.append(f"            Pruefbar: {a.pruefbar_durch}")
        z.append("")
    ohne = [a for a in ANWEISUNGEN if a.faelle == 0]
    z.append(f"    {len(ohne)} Anweisung(en) ohne eigenen Vorfall sind")
    z.append("    ausdruecklich markiert. Eine Anweisung ohne Fall ist")
    z.append("    eine Vermutung, keine Erkenntnis — dieselbe Regel wie")
    z.append("    fuer R3 und R18.")
    return z
