"""
proben.py — die Konformitaetssuite.

VIER FALLKLASSEN

    A  Regel muss blockieren     bequeme Antwort ist falsch
    B  Regel muss durchlassen    bequeme Antwort ist richtig
    C  Regel muss unterscheiden  beide plausibel, nur eine Einstufung passt
    D  Regel muss sich fuer unzustaendig erklaeren

  B verhindert, dass ein System gewinnt, indem es auf alles nein sagt.
  C misst, was greift/still nicht messen kann: mehrere Regeln haben drei
  oder vier Ausgaenge, und ein Bit reicht dafuer nicht.
  D trennt 'geprueft und nichts gefunden' von 'gar nicht hingesehen'.

DER STROHMANN
  gibt bei jedem Fall die richtige Ja/Nein-Antwort und nennt immer die
  vorsichtigste Begruendung. Er besteht eine reine greift/still-Probe
  vollstaendig und faellt nur ueber die C-Faelle.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

from . import regeln as R
from .kern import (Art, Eintrag, Modellform, Netz, Quelle, Status, Zahl)


class Klasse(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


@dataclass(frozen=True)
class Fall:
    regel: str
    klasse: Klasse
    was: str
    ruf: Callable[[], R.Befund]
    greift: bool
    einstufung: Optional[str] = None


VORSICHTIG = {
    "R1": "geteilte_aussage", "R2": "ohne_messwurzel",
    "R5": "in_sample", "R8": "merkmal_fehlt",
    "R9": "unbestimmt_ohne_toleranz", "R13": "scheinauswahl",
    "R14": "anteil_fehlt", "R16": "ohne_datum", "R17": "eine_hand",
}


def strohmann(b: R.Befund) -> R.Befund:
    if b.greift and b.regel in VORSICHTIG:
        return replace(b, einstufung=VORSICHTIG[b.regel])
    return b


# ══ Das Pruefnetz ═══════════════════════════════════════════════════════
def netz_bauen() -> Netz:
    n = Netz(deckel=3)
    for q in [
        Quelle("abrechnung", "interne Abrechnungsdaten", Art.AUSSAGE, "mittel"),
        Quelle("praesentation", "Projektleitung", Art.AUSSAGE, "mittel",
               ("abrechnung",)),
        Quelle("verwaltung", "interner Bericht", Art.AUSSAGE, "hoch",
               ("praesentation",)),
        Quelle("projektbericht", "Projektbericht", Art.AUSSAGE, "hoch",
               ("verwaltung",)),
        Quelle("zaehler", "Ertragszaehler", Art.MESSUNG, "hoch"),
        Quelle("datenblatt", "Datenblatt des Herstellers", Art.MESSUNG, "hoch"),
        Quelle("maerz", "Ablesung Maerz", Art.MESSUNG, "hoch",
               ("zaehler",), vorgang="2026-03-31"),
        Quelle("april", "Ablesung April", Art.MESSUNG, "hoch",
               ("zaehler",), vorgang="2026-04-30"),
        Quelle("maerz2", "dieselbe Ablesung, zweites Blatt", Art.MESSUNG,
               "hoch", ("zaehler",), vorgang="2026-03-31"),
        Quelle("modell", "Simulationsmodell", Art.RECHNUNG, "hoch"),
        Quelle("sim1", "Lauf 1", Art.RECHNUNG, "hoch", ("modell",)),
    ]:
        n.quelle(q)
    n.variable("V1", "Jahresertragsprognose", 240_000, "2026-01-15")
    n.variable("V2", "Inbetriebnahme", None, "2026-01-15")

    n.aufnehmen(Eintrag(
        "E27", "Die Anlage liegt auf Plan.", Status.VERMERK,
        "2026-02-01", "2026-02-01", quellen=("zaehler",),
        variablen=("V1", "V2"),
        geltungsbereich={"anlagentyp": "dach_250kwp", "jahr": "2026",
                         "thema": "ertrag"},
        stand=(("V1", 1), ("V2", 1))))
    n.aufnehmen(Eintrag(
        "E31", "Halbjahresmarke ist die Haelfte der Prognose.", Status.VERMERK,
        "2026-02-01", "2026-02-01", quellen=("zaehler",), variablen=("V1",),
        geltungsbereich={"thema": "ertrag"}, stand=(("V1", 1),)))
    return n


def faelle(n: Netz) -> List[Fall]:
    e27 = n.eintraege["E27"]
    im = {"anlagentyp": "dach_250kwp", "jahr": "2026", "thema": "ertrag"}
    exakt_ohne = Eintrag("E44", "dK = ...", Status.VERMERK, "2026-03-01",
                         "2026-03-01", exakt=True)
    exakt_mit = Eintrag("E45", "dK = dG + ...", Status.VERMERK, "2026-03-01",
                        "2026-03-01", exakt=True,
                        modellform=Modellform("K = G + V*p",
                                              ("Tarif hat Grundpreis",)))
    schlicht = Eintrag("E46", "Notiz", Status.VERMERK, "2026-03-01",
                       "2026-03-01")
    zwei_h = Eintrag("E47", "Die Anlage leistet 250 kWp.", Status.VERMERK,
                     "2026-03-01", "2026-03-01",
                     quellen=("zaehler", "datenblatt"))
    F = Fall
    return [
        # R1
        F("R1", Klasse.B, "zwei Ablesungen, zwei Vorgaenge",
          lambda: R.r1_unabhaengig(n, "maerz", "april"), False),
        F("R1", Klasse.A, "zwei Dokumente, eine Abrechnung",
          lambda: R.r1_unabhaengig(n, "projektbericht", "praesentation"), True),
        F("R1", Klasse.C, "geteilte Aussage",
          lambda: R.r1_unabhaengig(n, "projektbericht", "verwaltung"),
          True, "geteilte_aussage"),
        F("R1", Klasse.C, "derselbe Messvorgang",
          lambda: R.r1_unabhaengig(n, "maerz", "maerz2"),
          True, "gleicher_vorgang"),
        # R2
        F("R2", Klasse.B, "Herabstufung",
          lambda: R.r2_offline(n, ["sim1"], "herab"), False),
        F("R2", Klasse.B, "Hochstufung mit Messwurzel",
          lambda: R.r2_offline(n, ["maerz"], "hoch"), False),
        F("R2", Klasse.C, "nur gerechnete Wurzeln",
          lambda: R.r2_offline(n, ["sim1"], "hoch"), True, "nur_deduktiv"),
        F("R2", Klasse.C, "nur Aussage-Wurzeln",
          lambda: R.r2_offline(n, ["projektbericht"], "hoch"),
          True, "ohne_messwurzel"),
        # R3
        F("R3", Klasse.B, "alle Eingaenge auf Stand",
          lambda: R.r3_veraltet(n, e27), False),
        # R4
        F("R4", Klasse.A, "Variable mit Abhaengigen",
          lambda: R.r4_rueckwaerts(n, "V1"), True),
        F("R4", Klasse.D, "Variable ohne Abhaengige",
          lambda: R.r4_rueckwaerts(n, "V9"), False, "nicht_zustaendig"),
        # R5
        F("R5", Klasse.B, "Frage vor den Daten",
          lambda: R.r5_vorher(n, Zahl(0.96, verfahren="Quote",
                                      kandidaten_geprueft=12,
                                      festgelegt_am="2026-01-02",
                                      daten_ab="2026-02-01")), False),
        F("R5", Klasse.C, "Zeitpunkte fehlen",
          lambda: R.r5_vorher(n, Zahl(0.96, verfahren="Quote",
                                      kandidaten_geprueft=12)),
          True, "zeitpunkte_fehlen"),
        F("R5", Klasse.C, "Frage nach den Daten",
          lambda: R.r5_vorher(n, Zahl(0.99, verfahren="Quote",
                                      kandidaten_geprueft=40,
                                      festgelegt_am="2026-03-10",
                                      daten_ab="2026-01-01")),
          True, "in_sample"),
        # R6
        F("R6", Klasse.B, "Kandidatenzahl genannt",
          lambda: R.r6_kandidaten(n, Zahl(0.96, kandidaten_geprueft=12)), False),
        F("R6", Klasse.A, "Musterstaerke ohne Kandidatenzahl",
          lambda: R.r6_kandidaten(n, Zahl(0.96)), True),
        # R7
        F("R7", Klasse.B, "exakt mit Modellform",
          lambda: R.r7_modellform(n, exakt_mit), False),
        F("R7", Klasse.A, "exakt ohne Modellform",
          lambda: R.r7_modellform(n, exakt_ohne), True),
        F("R7", Klasse.D, "gar nicht als exakt gefuehrt",
          lambda: R.r7_modellform(n, schlicht), False, "nicht_zustaendig"),
        # R8
        F("R8", Klasse.B, "Fall im Geltungsbereich",
          lambda: R.r8_geltung(n, e27, im), False),
        F("R8", Klasse.C, "Merkmal des Falls unbekannt",
          lambda: R.r8_geltung(n, e27, {"jahr": "2026"}),
          True, "merkmal_fehlt"),
        F("R8", Klasse.C, "Merkmal bekannt, ausserhalb",
          lambda: R.r8_geltung(n, e27, {"anlagentyp": "freiflaeche",
                                        "jahr": "2026", "thema": "ertrag"}),
          True, "ausserhalb"),
        # R9
        F("R9", Klasse.B, "enge Toleranz — widerlegt zu Recht",
          lambda: R.r9_gegenbeispiel(n, e27, im, 43, 50, 2), False),
        F("R9", Klasse.C, "ohne Toleranz",
          lambda: R.r9_gegenbeispiel(n, e27, im, 43, 50, None),
          True, "unbestimmt_ohne_toleranz"),
        F("R9", Klasse.C, "Toleranz erreicht die Schwelle",
          lambda: R.r9_gegenbeispiel(n, e27, im, 43, 50, 9),
          True, "unbestimmt_toleranz"),
        F("R9", Klasse.C, "Messung ausserhalb",
          lambda: R.r9_gegenbeispiel(n, e27, {"anlagentyp": "freiflaeche",
                                              "jahr": "2026",
                                              "thema": "ertrag"},
                                     43, 50, 2),
          True, "kein_gegenbeispiel"),
        # R10
        F("R10", Klasse.B, "Zahl mit Verfahren",
          lambda: R.r10_verfahren(n, Zahl(0.32, verfahren="8 von 25")), False),
        F("R10", Klasse.A, "Vertrauenswuerdigkeit = 32 %",
          lambda: R.r10_verfahren(n, Zahl(0.32)), True),
        # R11
        F("R11", Klasse.B, "neue Fassung neben der alten",
          lambda: R.r11_version(n, "E27", 2), False),
        F("R11", Klasse.A, "gleiche Fassungsnummer",
          lambda: R.r11_version(n, "E27", 1), True),
        F("R11", Klasse.D, "Eintrag existiert nicht",
          lambda: R.r11_version(n, "E99", 1), False, "nicht_zustaendig"),
        # R12
        F("R12", Klasse.B, "beide Raten",
          lambda: R.r12_zwei_raten(n, {"erfindungsrate": .08,
                                       "uebervorsichtsrate": .14}), False),
        F("R12", Klasse.A, "nur eine Quote",
          lambda: R.r12_zwei_raten(n, {"erfindungsrate": .08}), True),
        # R13
        F("R13", Klasse.B, "zwei lebende Hypothesen",
          lambda: R.r13_rivalen(n, 2, False), False),
        F("R13", Klasse.C, "eine Hypothese, Probe erklaert",
          lambda: R.r13_rivalen(n, 1, True), False, "probe_erklaert"),
        F("R13", Klasse.A, "eine Hypothese, als Unterscheidung ausgegeben",
          lambda: R.r13_rivalen(n, 1, False), True),
        # R14
        F("R14", Klasse.B, "Probenanteil mit Datum",
          lambda: R.r14_probenanteil(n, {"probenanteil": .2,
                                         "festgelegt_am": "2026-01-01"}), False),
        F("R14", Klasse.C, "Anteil ohne Datum",
          lambda: R.r14_probenanteil(n, {"probenanteil": .2}),
          True, "ohne_datum"),
        F("R14", Klasse.C, "kein Anteil erklaert",
          lambda: R.r14_probenanteil(n, {}), True, "anteil_fehlt"),
        # R15
        F("R15", Klasse.B, "Attest mit Negativliste",
          lambda: R.r15_negativliste(n, {"nicht_geprueft": ["Rechnung"]}),
          False),
        F("R15", Klasse.A, "Attest ohne Negativliste",
          lambda: R.r15_negativliste(n, {"geprueft": ["Form"]}), True),
        # R16
        F("R16", Klasse.B, "Stufe vor der Aussage",
          lambda: R.r16_stufe_vorher(n, "2026-01-01", "2026-02-01"), False),
        F("R16", Klasse.C, "Stufe nachtraeglich",
          lambda: R.r16_stufe_vorher(n, "2026-03-01", "2026-02-01"),
          True, "nachtraeglich"),
        F("R16", Klasse.C, "Stufe ohne Datum",
          lambda: R.r16_stufe_vorher(n, None, "2026-02-01"), True, "ohne_datum"),
        # R17
        F("R17", Klasse.B, "zwei Wurzeln",
          lambda: R.r17_zweite_hand(n, zwei_h), False),
        F("R17", Klasse.A, "eine Wurzel",
          lambda: R.r17_zweite_hand(n, e27), True),
        # R18
        F("R18", Klasse.B, "im Rahmen", lambda: R.r18_deckel(n), False),
    ]


def bewerten(f: Fall, b: R.Befund, streng: bool) -> bool:
    if b.greift != f.greift:
        return False
    if streng and f.klasse in (Klasse.C, Klasse.D):
        return b.einstufung == f.einstufung
    return True


def lauf(verdreht: bool = False, streng: bool = True) -> Tuple[int, int, List[Fall]]:
    n = netz_bauen()
    ok, durch = 0, []
    for f in faelle(n):
        b = f.ruf()
        if verdreht:
            b = strohmann(b)
        if bewerten(f, b, streng):
            ok += 1
        else:
            durch.append(f)
    return ok, ok + len(durch), durch


def bericht() -> List[str]:
    n = netz_bauen()
    alle = faelle(n)
    nach = {k: [f for f in alle if f.klasse is k] for k in Klasse}
    z = ["KONFORMITAETSPROBE", ""]
    for k in Klasse:
        z.append(f"  Klasse {k.value}   {len(nach[k]):>3} Faelle")
    z.append(f"  gesamt     {len(alle):>3}")
    z.append("")
    # Gezaehlt wird, ob die Regel ueberhaupt einen ausloesenden und einen
    # stillen Fall hat — nicht, ob er A oder B HEISST. Ein C-Fall, der
    # greift, ist ein Scheiterfall; ein D-Fall, der still bleibt, ist ein
    # Positivfall. Die erste Fassung zaehlte nach Etikett und meldete
    # acht Regeln faelschlich als ungeprueft.
    ohne_a = [r for r in R.ALLE
              if not any(f.regel == r and f.greift for f in alle)]
    ohne_b = [r for r in R.ALLE
              if not any(f.regel == r and not f.greift for f in alle)]
    for name, verdreht, streng in [("echte Regeln", False, False),
                                   ("echte Regeln", False, True),
                                   ("Strohmann", True, False),
                                   ("Strohmann", True, True)]:
        ok, ges, durch = lauf(verdreht, streng)
        probe = "streng (greift + Einstufung)" if streng else "nur greift"
        z.append(f"  {name:<14}{probe:<30}{ok:>3} / {ges}")
    z.append("")
    _, _, durch = lauf(True, True)
    z.append("  Der Strohmann faellt ueber:")
    for f in durch:
        z.append(f"    {f.regel} {f.klasse.value}  {f.was}"
                 f"  (erwartet: {f.einstufung})")
    if ohne_a:
        z.append("")
        z.append(f"  OHNE SCHEITERFALL: {', '.join(ohne_a)} — ungeprueft")
    if ohne_b:
        z.append(f"  OHNE POSITIVFALL:  {', '.join(ohne_b)} — Dauerfehlalarm "
                 "moeglich")
    return z
