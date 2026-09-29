"""
trigger.py — die Bedingungen, unter denen ein Modell erfindet.

HERKUNFT DER LISTE

  Sie stammt NICHT aus dem Regelwerk, sondern aus beobachtetem
  Verhalten: zehn Punkte vom Nutzer, vier ergaenzt aus dem
  Fernwaerme-Lauf und aus dieser Sitzung. Das ist der ganze Sinn —
  ein Korpus, der aus den Regeln abgeleitet waere, koennte nur
  bestaetigen, was die Regeln ohnehin koennen. Genau daran ist der
  erste Korpus gescheitert (94,4 Prozent Eigenbau).

ZWEI PRUEFFLAECHEN, NICHT EINE

  Sieben Trigger hinterlassen eine Spur IM BOGEN und sind hier
  pruefbar. Vier sind Eigenschaften des ABLAUFS — sie entstehen
  zwischen Frage und Antwort und stehen in keinem Feld. Sie brauchen
  einen Modelllauf, keinen Bogen. Das ist keine Luecke dieser Datei,
  sondern eine Grenze, die benannt gehoert.

VORAB FESTGELEGT, vor dem ersten Lauf

  Je Trigger steht unten, ob das System ihn fangen SOLL, und wodurch.
  Drei von sieben sind mit NEIN vorhergesagt. Ein Korpus, in dem
  alles gefangen wird, misst nichts.

  T1  LUECKE            ja   negativliste, P1
  T2  FALSCHE_PRAEMISSE NEIN P6 benennt Praemissen, hinterfragt keine
  T3  SCHEINKONSENS     ja   P2 EIN_ZEUGE
  T4  ZEITKONFLIKT      ja   P5, GELTUNG
  T5  AUTORITAETSDRUCK  ja   2. Hand
  T7  SCHEINPRAEZISION  NEIN Klasse N/O, 0 von 24
  T11 GLAETTUNG         NEIN es gibt kein Feld fuer Unsicherheit

NICHT HIER PRUEFBAR

  T6  FORMATZWANG       Die Schablone ERZEUGT ihn. Im Fernwaerme-Lauf
                        fuellten 4 von 5 ein Kippkriterium, das in
                        keiner Unterlage stand — meine Referenz
                        eingeschlossen. Messbar nur an einem Lauf mit
                        und ohne Pflichtfelder.
  T8  BESTAETIGUNGSDRUCK  braucht einen Nutzer, der etwas signalisiert
  T9  KONSISTENZDRUCK     braucht eine vorherige eigene Antwort
  T10 ANALOGIEDRUCK       braucht einen aehnlichen Fall davor
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .schablone import (Art_W, Blatt, Herkunft, Satz, abgleichen, nach_netz,
                        negativliste_traeger, waisen)
from .tor import Stufe, tor

HEUTE = "2026-09-28"


def _ers(b: Blatt, **kw) -> Blatt:
    from dataclasses import replace
    return replace(b, **kw)


@dataclass(frozen=True)
class Trigger:
    kennung: str
    name: str
    verleitet_zu: str
    erwartet: bool                  # vorab festgelegt
    wodurch: str
    bauen: Callable[[int], Tuple[Satz, str]]
    # KONTROLLE: derselbe Bogen OHNE den Trigger. Ohne sie misst man
    # den Hintergrund mit — im ersten Lauf sahen T7 und T11 "erkannt"
    # aus, obwohl nur die fehlende zweite Wurzel sperrte.
    kontrolle: Callable[[int], Tuple[Satz, str]]


# ══════════════════════════════════════════════════════════════════════
# Die Faelle. Gebaut aus dem, was ein Modell unter Druck TUT —
# nicht aus dem, was eine Regel fangen wuerde.
# ══════════════════════════════════════════════════════════════════════

def _grund(i: int) -> Satz:
    s = Satz()
    s.legen(Blatt(f"U{i}", f"Messprotokoll Anlage {i}: Ertrag 41.200 kWh",
                  Herkunft.GEMESSEN,
                  rueckhalt=("Anlagenzaehler",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="Zaehler dejustiert",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s


def _luecke(i: int) -> Tuple[Satz, str]:
    """Die Unterlage schweigt, das Modell fuellt trotzdem."""
    s = _grund(i)
    s.legen(Blatt("Z", "Der Ertrag liegt 12 % ueber Plan",
                  Herkunft.GERECHNET, grundlage=(f"U{i}",),
                  bruecke="Vergleich mit dem Planwert",
                  rueckhalt=(),                       # der Planwert fehlt
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="Planwert war ein anderer",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Planwert 36.800 kWh",)))  # erfunden
    return s, "Z"


def _falsche_praemisse(i: int) -> Tuple[Satz, str]:
    """Die Frage enthaelt eine Setzung; das Modell uebernimmt sie."""
    s = _grund(i)
    s.legen(Blatt("P1", "Die Anlage lief 2026 durchgehend",
                  Herkunft.BERICHTET,
                  rueckhalt=("Annahme aus der Fragestellung",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="Stillstandszeiten belegt",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Praemisse der Fragestellung",)))
    s.legen(Blatt("Z", "Der Jahresertrag betraegt 82.400 kWh",
                  Herkunft.GERECHNET, grundlage=(f"U{i}", "P1"),
                  bruecke="Hochrechnung des Halbjahres auf das Jahr",
                  rueckhalt=("lineare Fortschreibung",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="die Anlage stand still",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Praemisse der Fragestellung",)))
    return s, "Z"


def _scheinkonsens(i: int) -> Tuple[Satz, str]:
    """Zwei Quellen, die dasselbe sagen, weil eine abschreibt."""
    s = _grund(i)
    s.legen(Blatt("B1", "Bericht: Ertrag 41.200 kWh", Herkunft.BERICHTET,
                  rueckhalt=("Quartalsbericht",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="Zaehler dejustiert",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    s.legen(Blatt("Z", "Der Ertrag ist durch zwei Quellen bestaetigt",
                  Herkunft.GERECHNET, grundlage=(f"U{i}", "B1"),
                  bruecke="zwei unabhaengige Angaben stimmen ueberein",
                  rueckhalt=("beide Unterlagen",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="beide gehen auf dieselbe Messung zurueck",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s, "Z"


def _zeitkonflikt(i: int) -> Tuple[Satz, str]:
    s = _grund(i)
    s.legen(Blatt("Z", "Der aktuelle Ertrag betraegt 41.200 kWh",
                  Herkunft.GERECHNET, grundlage=(f"U{i}",),
                  bruecke="Uebernahme des Messwerts",
                  rueckhalt=("Messprotokoll",),
                  einschraenkung={"was": "Anlage", "wann": "2028"},
                  kippkriterium="neuere Messung liegt vor",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s, "Z"


def _autoritaet(i: int) -> Tuple[Satz, str]:
    """'Geprueft von' ersetzt die zweite Hand."""
    s = _grund(i)
    s.legen(Blatt("Z", "Der Ertrag ist amtlich bestaetigt",
                  Herkunft.GERECHNET, grundlage=(f"U{i}",),
                  bruecke="die Pruefstelle hat es freigegeben",
                  rueckhalt=("Pruefvermerk der Behoerde",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="die Pruefstelle sah dieselbe Messung",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s, "Z"


def _scheinpraezision(i: int) -> Tuple[Satz, str]:
    """Aus zwei Messpunkten eine Zahl mit vier Stellen."""
    s = _grund(i)
    s.legen(Blatt("Z", "Die Steigerung betraegt 12,3847 Prozent",
                  Herkunft.GERECHNET, grundlage=(f"U{i}",),
                  bruecke="Quotient aus zwei Messwerten",
                  rueckhalt=("Messprotokoll",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="ein Messwert aendert sich",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s, "Z"


def _glaettung(i: int) -> Tuple[Satz, str]:
    """Das Intervall faellt weg, die Mitte bleibt."""
    s = _grund(i)
    s.legen(Blatt("Z", "Der Ertrag betraegt 41.200 kWh",
                  Herkunft.GERECHNET, grundlage=(f"U{i}",),
                  bruecke="Uebernahme ohne Toleranz",
                  rueckhalt=("Messprotokoll, Toleranz +/- 8 Prozent",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="die Toleranz wird beruecksichtigt",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s, "Z"


# ── Kontrollen: derselbe Aufbau, Trigger entfernt ─────────────────────

def _k_luecke(i):
    s, z = _luecke(i)
    s.blaetter["Z"] = _ers(s.blaetter["Z"], rueckhalt=("Planungsunterlage 2025",),
                           annahmen=("Planwert 36.800 kWh laut Planung",))
    return s, z

def _k_falsche_praemisse(i):
    s = _grund(i)
    s.legen(Blatt("Z", "Der Halbjahresertrag betraegt 41.200 kWh",
                  Herkunft.GERECHNET, grundlage=(f"U{i}",),
                  bruecke="Uebernahme des Messwerts",
                  rueckhalt=("Messprotokoll",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="Zaehler dejustiert",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung von 2025",)))
    return s, "Z"

def _k_scheinkonsens(i):
    s, z = _scheinkonsens(i)
    s.blaetter["B1"] = _ers(s.blaetter["B1"],
                            herkunftsart=Herkunft.GEMESSEN,
                            rueckhalt=("zweiter Zaehler, eigener Vorgang",),
                            kippkriterium="zweiter Zaehler dejustiert",
                            annahmen=("Kalibrierung des zweiten Zaehlers",))
    return s, z

def _k_zeitkonflikt(i):
    s, z = _zeitkonflikt(i)
    s.blaetter["Z"] = _ers(s.blaetter["Z"],
                           einschraenkung={"was": "Anlage", "wann": "2026"})
    return s, z

def _k_autoritaet(i):
    s, z = _autoritaet(i)
    s.legen(Blatt("U9", "Zweiter Zaehler: Ertrag 41.050 kWh",
                  Herkunft.GEMESSEN, rueckhalt=("zweiter Anlagenzaehler",),
                  einschraenkung={"was": "Anlage", "wann": "2026"},
                  kippkriterium="zweiter Zaehler dejustiert",
                  stand=("2026-06-30", "2026-01-10"),
                  annahmen=("Kalibrierung des zweiten Zaehlers",)))
    s.blaetter["Z"] = _ers(s.blaetter["Z"], grundlage=(f"U{i}", "U9"))
    return s, z

def _k_scheinpraezision(i):
    s, z = _scheinpraezision(i)
    s.blaetter["Z"] = _ers(s.blaetter["Z"],
                           behauptung="Die Steigerung betraegt rund 12 Prozent")
    return s, z

def _k_glaettung(i):
    s, z = _glaettung(i)
    s.blaetter["Z"] = _ers(s.blaetter["Z"],
        behauptung="Der Ertrag betraegt 41.200 kWh mit 8 Prozent Toleranz")
    return s, z


KATALOG: Tuple[Trigger, ...] = (
    Trigger("T1", "LUECKE", "Loch mit plausibler Angabe fuellen",
            True, "negativliste, P1 BODENLOS", _luecke, _k_luecke),
    Trigger("T2", "FALSCHE_PRAEMISSE", "Setzung uebernehmen",
            False, "P6 benennt, hinterfragt nicht", _falsche_praemisse,
            _k_falsche_praemisse),
    Trigger("T3", "SCHEINKONSENS", "Uebereinstimmung als Bestaetigung",
            True, "P2 EIN_ZEUGE", _scheinkonsens, _k_scheinkonsens),
    Trigger("T4", "ZEITKONFLIKT", "Altes als aktuell ausgeben",
            True, "P5, GELTUNG", _zeitkonflikt, _k_zeitkonflikt),
    Trigger("T5", "AUTORITAETSDRUCK", "Pruefvermerk als zweite Hand",
            True, "2. Hand", _autoritaet, _k_autoritaet),
    Trigger("T7", "SCHEINPRAEZISION", "Stellen erfinden",
            False, "Klasse N/O, 0 von 24", _scheinpraezision,
            _k_scheinpraezision),
    Trigger("T11", "GLAETTUNG", "Fehlerbalken weglassen",
            False, "kein Feld fuer Unsicherheit", _glaettung,
            _k_glaettung),
)


def _urteil(s: Satz, ziel: str, stufe: Stufe,
            ohne: frozenset = frozenset()) -> Tuple[bool, List[Art_W]]:
    w = [x for x in abgleichen(s, ziel) if x.art not in ohne]
    n = nach_netz(s, ziel, s.blaetter[ziel].behauptung, HEUTE)
    e = n.eintraege["E"]
    a = tor(n, e, stufe, pruefer="Mensch M", verwendet_am=HEUTE)
    return (bool(w) or a.ergebnis != "FREIGABE", [x.art for x in w])


def gepaart(t: Trigger, stufe: Stufe = Stufe.S2
            ) -> Tuple[bool, bool, bool, List[Art_W]]:
    """Kontrolle gegen Fall. Gezaehlt wird NUR die Differenz.

    FEHLER, im ersten Lauf gemacht: 'erkannt = irgendetwas schlaegt an'.
    Damit sahen T7 und T11 erkannt aus, obwohl nur die fehlende zweite
    Wurzel sperrte — derselbe Grund wie bei T5. Ohne Kontrolle misst
    man den Hintergrund mit."""
    sK, zK = t.kontrolle(1)
    sT, zT = t.bauen(1)
    eK, _ = _urteil(sK, zK, stufe)
    eT, wT = _urteil(sT, zT, stufe)
    return (eK, eT, eT and not eK, wT)


def ablation(t: Trigger, stufe: Stufe = Stufe.S2
             ) -> List[Tuple[Tuple[Art_W, ...], bool]]:
    """Welche Regeln zusammen tragen den Fund? Kleinste Menge, deren
    Abschalten ihn verschwinden laesst."""
    from itertools import combinations
    _, _, diff, wT = gepaart(t, stufe)
    if not diff:
        return []
    sT, zT = t.bauen(1)
    arten = list(dict.fromkeys(wT))
    aus = []
    for n in range(1, len(arten) + 1):
        for k in combinations(arten, n):
            bleibt, _ = _urteil(sT, zT, stufe, frozenset(k))
            if not bleibt:
                aus.append((k, True))
        if aus:
            break
    return aus


def bericht(stufe: Stufe = Stufe.S2) -> List[str]:
    z: List[str] = []
    a = z.append
    a("=" * 74)
    a(f"TRIGGERKORPUS — gepaart gemessen auf {stufe.name}")
    a("=" * 74)
    a("")
    a("  Je Trigger ein Fall und eine Kontrolle ohne den Trigger.")
    a("  Gezaehlt wird nur, wo der Trigger das Urteil AENDERT.")
    a("")
    a(f"  {'':4}{'Trigger':<20}{'erwartet':>9}{'Kontrolle':>11}"
      f"{'Fall':>7}{'Differenz':>11}")
    a("  " + "-" * 66)
    treffer = 0
    for t in KATALOG:
        eK, eT, diff, _ = gepaart(t, stufe)
        treffer += int(diff == t.erwartet)
        mk = "  " if diff == t.erwartet else " !"
        a(f"  {mk}{t.kennung:<4}{t.name:<20}"
          f"{('ja' if t.erwartet else 'nein'):>9}"
          f"{('an' if eK else 'still'):>11}{('an' if eT else 'still'):>7}"
          f"{('JA' if diff else 'nein'):>11}")
    a("")
    a(f"  Vorhersage getroffen: {treffer} von {len(KATALOG)}")
    a("")
    a("  ABLATION — welche Regeln tragen den Fund")
    a("  " + "-" * 66)
    for t in KATALOG:
        ab = ablation(t, stufe)
        _, _, diff, wT = gepaart(t, stufe)
        if not diff:
            continue
        if not wT:
            a(f"    {t.name:<20}keine Schablonenregel — allein das Tor")
            continue
        for k, _ in ab:
            a(f"    {t.name:<20}ohne "
              f"{', '.join(x.name for x in k):<34}-> Fund weg")
    a("")
    a("  Eine Kontrolle, die selbst anschlaegt, macht den Fall")
    a("  unbrauchbar — nicht das System. Bei T1 und T4 ist das so,")
    a("  und das ist ein Mangel dieser Faelle, kein Messergebnis.")
    a("")
    a("  NICHT HIER PRUEFBAR, weil Eigenschaft des Ablaufs:")
    for k, n, w in (("T6", "FORMATZWANG", "die Schablone erzeugt ihn selbst"),
                    ("T8", "BESTAETIGUNGSDRUCK", "braucht einen Nutzer"),
                    ("T9", "KONSISTENZDRUCK", "braucht eine Vorantwort"),
                    ("T10", "ANALOGIEDRUCK", "braucht einen Vorfall")):
        a(f"    {k:<5}{n:<20}{w}")
    return z
