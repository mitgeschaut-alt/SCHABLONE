"""
selbstmass.py — die Guetezahlen des Systems als Boegen.

DAS PROBLEM

  "0 von 40 Fehlalarm" wurde in einer einzigen Sitzung ein Dutzend Mal
  zitiert, ohne je zu sagen, worunter es gilt. Am 28.09.2026 zeigte die
  Abstandsmessung: alle 40 sauberen Faelle haengen an EINEM Feld
  (Z.rueckhalt, in 40 von 40 gefuellt). Waere es leer, schluege P3 in
  allen vierzig an.

  Die Zahl war also nie falsch — sie war nur nie vollstaendig. Genau
  das, was das Programm bei jeder anderen Behauptung verhindert.

DIE UMSETZUNG

  Eine Messung wird ein Blatt wie jedes andere: mit Geltungsbereich,
  Kippkriterium und Annahmen. Dann faengt P4 jeden, der sie breiter
  zitiert, als sie gemessen wurde — auch mich.

  ENTSCHEIDEND: der Geltungsbereich wird ABGELEITET, nicht
  hingeschrieben. Ein Feld, das in 100 Prozent der Faelle gleich
  aussieht, ist eine Bedingung der Messung und keine Eigenschaft des
  Regelwerks — der Korpus hat es nie variiert. Wer es von Hand
  eintragen duerfte, koennte es auch weglassen.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from . import erkennung
from .schablone import Blatt, Herkunft, Satz, abgleichen

PRUEFBAR = ("bruecke", "rueckhalt", "einschraenkung", "kippkriterium",
            "annahmen")


def _gefuellt(b: Blatt, feld: str) -> bool:
    w = getattr(b, feld)
    return bool(w)


def korpusbedingungen(nur_sauber: bool = True) -> Dict[str, Tuple[int, int]]:
    """Welche Felder hat der Korpus NIE variiert?

    Ein Feld, das in allen Faellen gefuellt (oder in allen leer) ist,
    wurde nicht geprueft. Es ist eine Bedingung der Messung."""
    zaehl: Dict[str, List[int]] = {f: [0, 0] for f in PRUEFBAR}
    for f in erkennung.faelle():
        if nur_sauber and f.defekt:
            continue
        b = f.satz.blaetter[f.ziel]
        for feld in PRUEFBAR:
            zaehl[feld][1] += 1
            zaehl[feld][0] += int(_gefuellt(b, feld))
    return {k: (v[0], v[1]) for k, v in zaehl.items()}


def unvariiert() -> List[str]:
    """Die Felder, die der Korpus konstant haelt — in Klartext."""
    aus = []
    for feld, (n, ges) in sorted(korpusbedingungen().items()):
        if ges and (n == ges or n == 0):
            aus.append(f"Zielblatt.{feld} "
                       f"{'immer gefuellt' if n else 'immer leer'}")
    return aus


def messblatt(kennung: str, was: str, wert: str, wie: str,
              quelle: str, kipp: str, version: str) -> Blatt:
    """Eine Messung als Blatt. Der Geltungsbereich kommt aus dem
    Korpus, nicht aus der Feder des Messenden."""
    bed = unvariiert()
    return Blatt(
        kennung=kennung,
        behauptung=f"{was}: {wert}",
        herkunftsart=Herkunft.GEMESSEN,
        grundlage=(),
        bruecke=wie,
        rueckhalt=(quelle,),
        einschraenkung={
            "was": "; ".join(bed) if bed else "keine unvariierten Felder",
            "wann": f"Version {version}",
            "wo": "erkennung.grund(), Startwert 2026",
        },
        kippkriterium=kipp,
        stand=("2026-09-28", "2026-09-28"),
        annahmen=("Fallgenerator erkennung.grund()",
                  "dieselbe Hand hat Faelle und Regeln gebaut"),
    )


def satz(version: str) -> Tuple[Satz, str]:
    s = Satz()
    s.legen(messblatt(
        "E1", "Erkennung im Regelwerk", "36 von 36",
        "Durchlauf von abgleichen() und tor() je Fall",
        "erkennung.py, Lauf vom 28.09.2026",
        "eine Defektklasse wird hinzugefuegt, die keine Regel trifft",
        version))
    s.legen(messblatt(
        "E2", "Fehlalarm auf sauberen Faellen", "0 von 40",
        "Durchlauf von abgleichen() und tor() je Fall",
        "erkennung.py, Lauf vom 28.09.2026",
        "ein Bogen laesst eines der unvariierten Felder leer",
        version))
    s.legen(messblatt(
        "E3", "Abstand zur Schwelle", "40 von 40 bei Abstand 1",
        "kleinste Zahl leerer Felder, die einen Befund erzeugt",
        "probe_abstand.py, Lauf vom 28.09.2026",
        "der Korpus variiert das betroffene Feld",
        version))
    s.legen(Blatt(
        "Z", "Das Regelwerk schlaegt auf fehlerfreien Boegen nicht an",
        Herkunft.GERECHNET, grundlage=("E2", "E3"),
        bruecke="aus 0 von 40 Fehlalarmen folgt die Aussage",
        rueckhalt=("die Messblaetter",),
        einschraenkung={},           # ABSICHTLICH breit zitiert
        kippkriterium="ein fehlerfreier Bogen schlaegt an",
        stand=("2026-09-28", "2026-09-28"),
        annahmen=("Fallgenerator erkennung.grund()",)))
    return s, "Z"


def bericht(version: str = "2.5") -> List[str]:
    z: List[str] = []
    a = z.append
    a("=" * 74)
    a("SELBSTMASS — die Guetezahlen als Boegen")
    a("=" * 74)
    a("")
    a("  WAS DER KORPUS NIE VARIIERT HAT")
    a("  (und was damit Bedingung jeder Messung auf ihm ist)")
    a("")
    for feld, (n, ges) in sorted(korpusbedingungen().items()):
        marke = "  <<< unvariiert" if ges and (n == ges or n == 0) else ""
        a(f"    Zielblatt.{feld:<16}{n:>3} von {ges} gefuellt{marke}")
    a("")
    s, ziel = satz(version)
    a("  DIE MESSUNGEN ALS BLAETTER")
    for k in ("E1", "E2", "E3"):
        b = s.blaetter[k]
        a(f"    {k}  {b.behauptung}")
        a(f"        gilt fuer  {b.einschraenkung['was']}")
        a(f"        faellt bei {b.kippkriterium}")
    a("")
    a("  UND JETZT DIE BREITE BEHAUPTUNG DARAUF")
    a(f"    Z   {s.blaetter[ziel].behauptung}")
    a("")
    w = abgleichen(s, ziel)
    if not w:
        a("    keine Beanstandung — das waere ein Fehler")
    for x in w:
        a(f"    {x.art.paar} {x.art.name}")
        a(f"        {x.warum}")
    a("")
    a("  Das Programm faengt damit den, der seine eigenen Zahlen")
    a("  breiter zitiert, als sie gemessen wurden. In dieser Sitzung")
    a("  war das ein Dutzend Mal ich.")
    return z
