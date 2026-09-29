"""
verdacht.py — der dritte Ausgabetyp.

WAS GEFEHLT HAT

  Das Programm konnte bisher zweierlei sagen:

    WIDERSPRUCH   zwei Felder passen nicht zusammen   -> sperrt
    AUSKUNFT      das wurde nicht geprueft            -> meldet

  Keines von beiden FORDERT ARBEIT AN. Und gemessen am 28.09.2026:
  von 22 Modulen erreichen genau vier eine Entscheidung (kern, regeln,
  leitung, tor). Achtzehn berichten nur — darunter guete mit fuenf
  Abwertungsgruenden, die nirgends ankommen.

  Dazu kam: ein Widerspruch hat die Felder art, betrifft, warum. Er
  sagt, was falsch ist, und nie, was es ausraeumen wuerde.

DER VERDACHT

  Aus dem Strafverfahren uebernommen, weil es dort ausgearbeitet ist:
  ein Verdacht rechtfertigt ERMITTLUNG, nicht Strafe. Er sperrt nichts.
  Er lenkt Aufwand.

    ANFANGSVERDACHT    etwas an der Form ist auffaellig
    HINREICHEND        eine Regel hat gegriffen, der Fall ist auf der
                       Form allein nicht entscheidbar

DIE ASYMMETRIE — die eigentliche Regel

  Ein Verdacht darf nur durch eine URTEILSFREIE Pruefung ausgeraeumt
  werden: Einsetzen, Dimensionspruefung, zweiter Rechenweg mit anderer
  Praemisse. Eine Pruefung, deren Ausgang an der Einschaetzung des
  Pruefers haengt, kann ihn bestaerken, aber nie ausraeumen.

  Belegt an den vier Rechenfehlern dieser Sitzung: drei wurden durch
  Einsetzen erledigt (Fragmentradius, Dimensionen, Bisektion) — die
  Gleichung ging auf oder nicht. Der vierte, die Ausgasung, wurde nur
  von meiner Erwartung ausgeraeumt, und er ist der schwaechste.

    geprueft und nicht entkraeftet  !=  entkraeftet
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .schablone import Art_W, Satz, abgleichen, negativliste, waisen


class Stufe_V(Enum):
    ANFANGS = ("Anfangsverdacht", 1)
    HINREICHEND = ("hinreichender Verdacht", 2)

    @property
    def text(self) -> str:
        return self.value[0]

    @property
    def gewicht(self) -> int:
        return self.value[1]


class Stand(Enum):
    ERHOBEN = "erhoben"
    ENTKRAEFTET = "entkraeftet"
    OFFEN = "geprueft, nicht entkraeftet"


@dataclass(frozen=True)
class Verdacht:
    kennung: str
    betrifft: Tuple[str, ...]
    worauf: str
    stufe: Stufe_V
    klaerungsschritt: str
    urteilsfrei: bool          # haengt der Ausgang am Urteil des Pruefers?
    aufwand: str
    stand: Stand = Stand.ERHOBEN
    befund: str = ""

    def entkraeften(self, befund: str) -> "Verdacht":
        """Ein Verdacht faellt nur durch eine urteilsfreie Pruefung.

        Sonst bleibt er OFFEN — das ist nicht dasselbe wie erledigt."""
        if not self.urteilsfrei:
            return replace(self, stand=Stand.OFFEN,
                           befund=f"{befund} (Pruefung nicht urteilsfrei)")
        return replace(self, stand=Stand.ENTKRAEFTET, befund=befund)

    def bestaerken(self, befund: str) -> "Verdacht":
        """Bestaerken darf jede Pruefung — auch eine mit Urteil.
        Die Asymmetrie ist Absicht."""
        return replace(self, stufe=Stufe_V.HINREICHEND, befund=befund)


# ══════════════════════════════════════════════════════════════════════
# Je Widerspruchsart: was wuerde ihn ausraeumen, und haengt das am
# Urteil des Pruefers?
# ══════════════════════════════════════════════════════════════════════

KLAERUNG: Dict[Art_W, Tuple[str, bool, str, Stufe_V]] = {
    Art_W.BODENLOS: (
        "die Kette bis zu einer Messung oder einem benannten Urheber "
        "weiterverfolgen", True,
        "eine Quellenrecherche", Stufe_V.HINREICHEND),
    Art_W.EIN_ZEUGE: (
        "pruefen, ob die beiden Blaetter getrennte Vorgaenge haben",
        True, "ein Blick in beide Unterlagen", Stufe_V.HINREICHEND),
    Art_W.GETEILTE_ANNAHME: (
        "die gemeinsame Praemisse auf einem dritten Weg rechnen, der "
        "sie nicht voraussetzt", True,
        "eine Nachrechnung", Stufe_V.HINREICHEND),
    Art_W.BRUECKE_OHNE_RUECKHALT: (
        "das Dokument benennen, das die Bruecke traegt", True,
        "eine Quellenangabe", Stufe_V.ANFANGS),
    Art_W.GETEILTE_BRUECKE: (
        "pruefen, ob der Schritt in beiden Faellen derselbe ist",
        False, "eine Einschaetzung", Stufe_V.ANFANGS),
    Art_W.UEBERDEHNUNG: (
        "den Geltungsbereich der Behauptung an die Grundlage angleichen",
        True, "eine Umformulierung", Stufe_V.HINREICHEND),
    Art_W.NACHTRAEGLICH: (
        "das Datum der Festlegung belegen", True,
        "ein Blick in die Vorgeschichte", Stufe_V.HINREICHEND),
}


def erheben(s: Satz, ziel: str) -> List[Verdacht]:
    """Aus jedem Befund einen Verdacht mit Klaerungsschritt.

    Das schliesst die Luecke: ein Widerspruch sagte bisher, was falsch
    ist, und nie, was es ausraeumen wuerde."""
    aus: List[Verdacht] = []
    n = 0
    for w in abgleichen(s, ziel):
        k = KLAERUNG.get(w.art)
        if k is None:
            continue
        schritt, urteilsfrei, aufwand, stufe = k
        n += 1
        aus.append(Verdacht(
            kennung=f"V{n}", betrifft=w.betrifft,
            worauf=f"{w.art.paar} {w.art.name}: {w.warum[:60]}",
            stufe=stufe, klaerungsschritt=schritt,
            urteilsfrei=urteilsfrei, aufwand=aufwand))
    for k in sorted(waisen(s, ziel)):
        n += 1
        aus.append(Verdacht(
            kennung=f"V{n}", betrifft=(k,),
            worauf=f"{k} traegt nichts bei",
            stufe=Stufe_V.ANFANGS,
            klaerungsschritt=f"pruefen, ob {k} die Behauptung stuetzen "
                             f"sollte und die Kante fehlt",
            urteilsfrei=False, aufwand="eine Einschaetzung"))
    return aus


def aufwandsstufe(vs: List[Verdacht]) -> int:
    """Wieviel Arbeit fordert dieser Bogen an? Kein Urteil ueber die
    Behauptung — eine Zahl ueber den noetigen Aufwand."""
    return sum(v.stufe.gewicht for v in vs if v.stand is not Stand.ENTKRAEFTET)


def bericht(s: Optional[Satz] = None, ziel: str = "Z") -> List[str]:
    from .schablone import angriff_3
    if s is None:
        _, s, ziel = angriff_3()
    z: List[str] = []
    a = z.append
    a("=" * 74)
    a("VERDACHT — der dritte Ausgabetyp")
    a("=" * 74)
    a("")
    a("  Ein Verdacht sperrt nichts. Er fordert Arbeit an.")
    a("")
    vs = erheben(s, ziel)
    if not vs:
        a("  kein Verdacht")
        return z
    for v in vs:
        a(f"  {v.kennung}  {v.stufe.text.upper()}   "
          f"betrifft {', '.join(v.betrifft)}")
        a(f"      {v.worauf}")
        a(f"      klaert sich durch: {v.klaerungsschritt}")
        a(f"      Aufwand: {v.aufwand}")
        uf = ("JA" if v.urteilsfrei else
              "NEIN — kann nur bestaerkt, nie ausgeraeumt werden")
        a(f"      urteilsfrei: {uf}")
        a("")
    a(f"  ANGEFORDERTER AUFWAND: {aufwandsstufe(vs)}")
    a("")
    a("  Probe der Asymmetrie:")
    for v in vs[:2]:
        neu = v.entkraeften("nachgesehen, alles in Ordnung")
        a(f"    {v.kennung} nach Pruefung -> {neu.stand.value}")
    a("")
    a("  Ein Verdacht, den nur jemandes Einschaetzung ausgeraeumt hat,")
    a("  bleibt stehen. geprueft und nicht entkraeftet != entkraeftet.")
    return z
