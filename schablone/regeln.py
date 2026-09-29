"""
regeln.py — R1 bis R18, jede aufrufbar, jede scheiterfaehig.

Jede Regel gibt einen Befund mit drei Teilen:
    greift      ja/nein — ein Bit
    einstufung  WELCHER Fall vorliegt — der Rest der Information
    text        die Begruendung im Klartext

Die Einstufung ist noetig, weil mehrere Regeln drei oder vier Ausgaenge
haben. Eine Probe, die nur greift/still prueft, misst hoechstens ein Bit
und laesst einem Strohmann den Rest.

HERKUNFT JEDER REGEL steht in ihrem Docstring: der Fall, der sie
erzwungen hat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .kern import Art, Eintrag, Modellform, Netz, Status, Zahl


@dataclass(frozen=True)
class Befund:
    regel: str
    greift: bool
    text: str
    einstufung: Optional[str] = None

    def __str__(self) -> str:
        mk = "GREIFT" if self.greift else "still "
        return f"[{mk}] {self.regel:<4} {self.text}"


# ══ R1 · Unabhaengigkeit ════════════════════════════════════════════════
def r1_unabhaengig(netz: Netz, a: str, b: str) -> Befund:
    """Geteilte AUSSAGE -> ein Zeuge. Geteilter APPARAT mit verschiedenen
    Vorgaengen -> zwei Zeugen fuer die Welt, einer fuer den Apparat.

    Fall: Projektbericht und Praesentation, beide ueber den
    Verwaltungsbericht aus derselben Abrechnung."""
    # R1 und R17 benutzen jetzt DIESELBE Definition von 'ein Pfad'
    # (Netz.pfade). Vorher hatte jede ihre eigene, und die von R1 sah
    # Wurzelkennungen, die von R17 ebenfalls — beide ohne die
    # Vorgangszusammenfassung ausdruecklich zu machen.
    wa = netz.pfade(a)
    wb = netz.pfade(b)
    gemeinsam = set(wa) & set(wb)
    if not gemeinsam:
        return Befund("R1", False, f"{a} und {b}: Pfade disjunkt",
                      "wurzeln_disjunkt")
    aussage = sorted(i for i in gemeinsam if wa[i][1] is not Art.MESSUNG)
    if aussage:
        return Befund("R1", True,
                      f"{a} und {b} teilen die Aussage "
                      f"{', '.join(wa[i][0] for i in aussage)} "
                      "— ein Zeuge", "geteilte_aussage")
    gleich = sorted(gemeinsam)
    if gleich:
        return Befund("R1", True,
                      f"{a} und {b}: derselbe Messvorgang "
                      f"{wa[gleich[0]][2]} — ein Zeuge", "gleicher_vorgang")
    return Befund("R1", False,
                  f"Apparat {', '.join(sorted(gemeinsam))} geteilt, Vorgaenge "
                  "verschieden — unabhaengig fuer den Sachverhalt",
                  "apparat_geteilt")


# ══ R2 · Offline darf nur herabstufen ═══════════════════════════════════
def r2_offline(netz: Netz, belege: Sequence[str], richtung: str) -> Befund:
    """Hochstufen braucht eine fremde Wurzel. Deduktive Ergebnisse
    duerfen als gueltig gefuehrt werden, nie als empirisch bestaetigt.

    Fall: 10.000 Simulationslaeufe desselben Modells."""
    if richtung == "herab":
        return Befund("R2", False,
                      "Herabstufung — immer zulaessig, ein Gegenbeispiel "
                      "genuegt", "herabstufung")
    arten = {w[1] for b in belege for w in netz.wurzeln(b)}
    if arten <= {Art.RECHNUNG}:
        return Befund("R2", True,
                      f"{len(belege)} Beleg(e), nur gerechnete Wurzeln — "
                      "deduktiv gueltig, nicht empirisch bestaetigt",
                      "nur_deduktiv")
    if Art.MESSUNG not in arten:
        return Befund("R2", True,
                      "Hochstufung ohne jede Messwurzel", "ohne_messwurzel")
    return Befund("R2", False, "Hochstufung mit Messwurzel — zulaessig",
                  "mit_messwurzel")


# ══ R3 · Invalidierung ══════════════════════════════════════════════════
def r3_veraltet(netz: Netz, e: Eintrag) -> Befund:
    """Ein Eintrag traegt die Fassungen seiner Eingaenge.

    Fall: V1 wird revidiert, der Paragraph bleibt auf BESTAETIGT."""
    ab = [(k, f, netz.variablen[k].stand) for k, f in e.stand
          if k in netz.variablen and netz.variablen[k].stand != f]
    if not ab:
        return Befund("R3", False, f"{e.marke}: alle Eingaenge auf Stand",
                      "auf_stand")
    teile = ", ".join(f"{k} v{f}->v{n}" for k, f, n in ab)
    return Befund("R3", True, f"{e.marke} ist VERALTET: {teile}", "veraltet")


# ══ R4 · Rueckwaertsindex ═══════════════════════════════════════════════
def r4_rueckwaerts(netz: Netz, variable: str) -> Befund:
    """Eine Revision muss jeden Eintrag erreichen, der auf der Variablen
    steht. Ohne Rueckwaertsindex ist die Menge nicht einmal angebbar."""
    betroffen = netz.rueckwaerts().get(variable, set())
    if not betroffen:
        return Befund("R4", False, f"{variable}: kein Eintrag betroffen",
                      "nicht_zustaendig")
    return Befund("R4", True,
                  f"{variable} -> neu zu pruefen: "
                  f"{', '.join(sorted(betroffen))} ({len(betroffen)})",
                  "betroffene_gefunden")


# ══ R5 · Das Kriterium steht vor den Daten ══════════════════════════════
def r5_vorher(netz: Netz, z: Zahl) -> Befund:
    """Fall: Muster auf Datensatz D gefunden, auf D bewertet."""
    if z.festgelegt_am is None or z.daten_ab is None:
        return Befund("R5", True,
                      f"Zahl {z.wert}: festgelegt_am oder daten_ab fehlt — "
                      "nicht pruefbar, also nicht gueltig", "zeitpunkte_fehlen")
    if z.festgelegt_am >= z.daten_ab:
        return Befund("R5", True,
                      f"Zahl {z.wert}: Frage ({z.festgelegt_am}) nicht vor "
                      f"den Daten ({z.daten_ab}) — In-Sample", "in_sample")
    return Befund("R5", False, f"Zahl {z.wert}: Frage vor den Daten",
                  "gueltig")


# ══ R6 · Kandidatenzahl ═════════════════════════════════════════════════
def r6_kandidaten(netz: Netz, z: Zahl) -> Befund:
    """'Musterstaerke 96 %' — unter wie vielen?"""
    if z.kandidaten_geprueft is None:
        return Befund("R6", True,
                      f"Zahl {z.wert}: Kandidatenzahl fehlt, keine Korrektur "
                      "auf Multiplizitaet moeglich", "kandidatenzahl_fehlt")
    return Befund("R6", False,
                  f"Zahl {z.wert}: aus {z.kandidaten_geprueft} Kandidaten",
                  "vollstaendig")


# ══ R7 · Modellform ═════════════════════════════════════════════════════
def r7_modellform(netz: Netz, e: Eintrag) -> Befund:
    """Fall: eine Kostenidentitaet, 'gilt exakt' genannt, ohne Grundpreis."""
    if not e.exakt:
        return Befund("R7", False, f"{e.marke}: nicht als exakt gefuehrt",
                      "nicht_zustaendig")
    if e.modellform is None or not e.modellform.annahmen:
        return Befund("R7", True,
                      f"{e.marke} ist als EXAKT gefuehrt, nennt aber keine "
                      "Definitionsannahmen", "exakt_ohne_form")
    return Befund("R7", False,
                  f"{e.marke}: exakt unter {len(e.modellform.annahmen)} "
                  "genannten Annahmen", "exakt_mit_form")


# ══ R8 · Geltungsbereich ════════════════════════════════════════════════
def r8_geltung(netz: Netz, e: Eintrag, fall: Dict[str, str]) -> Befund:
    """Fehlt dem Fall ein Merkmal, lautet die Antwort 'nicht anwendbar'."""
    fehlend = [k for k in e.geltungsbereich if k not in fall]
    if fehlend:
        return Befund("R8", True,
                      f"{e.marke} nicht anwendbar: Fall nennt "
                      f"{', '.join(fehlend)} nicht", "merkmal_fehlt")
    falsch = [f"{k}={fall[k]}!={v}" for k, v in e.geltungsbereich.items()
              if fall[k] != v]
    if falsch:
        return Befund("R8", True,
                      f"{e.marke} ausserhalb: {', '.join(falsch)}",
                      "ausserhalb")
    return Befund("R8", False, f"{e.marke} im Geltungsbereich", "innerhalb")


# ══ R9 · Gegenbeispiel ══════════════════════════════════════════════════
def r9_gegenbeispiel(netz: Netz, e: Eintrag, fall: Dict[str, str],
                     wert: float, schwelle: float,
                     unsicherheit: Optional[float]) -> Befund:
    """Widerlegt nur im Geltungsbereich und nur, wenn die Toleranz die
    Schwelle nicht erreicht. Sonst UNBESTIMMT — etwas anderes."""
    bereich = r8_geltung(netz, e, fall)
    if bereich.greift:
        return Befund("R9", True,
                      f"{e.marke}: kein Gegenbeispiel — {bereich.text}",
                      "kein_gegenbeispiel")
    if unsicherheit is None:
        return Befund("R9", True,
                      f"{e.marke}: UNBESTIMMT — Messwert {wert} ohne Toleranz",
                      "unbestimmt_ohne_toleranz")
    if wert + unsicherheit >= schwelle:
        return Befund("R9", True,
                      f"{e.marke}: UNBESTIMMT — {wert}+-{unsicherheit} "
                      f"erreicht {schwelle}", "unbestimmt_toleranz")
    return Befund("R9", False,
                  f"{e.marke}: WIDERLEGT zu Recht — {wert}+-{unsicherheit} "
                  f"bleibt unter {schwelle}", "widerlegt")


# ══ R10 · Keine Zahl ohne Verfahren ═════════════════════════════════════
def r10_verfahren(netz: Netz, z: Zahl) -> Befund:
    """Fall: 'Vertrauenswuerdigkeit = 32 %'."""
    if z.verfahren:
        return Befund("R10", False, f"Zahl {z.wert}: Verfahren "
                      f"'{z.verfahren}'", "verfahren_genannt")
    return Befund("R10", True, f"Zahl {z.wert} ohne Verfahren — eine "
                  "Behauptung in Zahlenform", "ohne_verfahren")


# ══ R11 · Versionierung ═════════════════════════════════════════════════
def r11_version(netz: Netz, kennung: str, neue_fassung: int) -> Befund:
    """Eine Revision erzeugt eine neue Fassung; die alte bleibt."""
    alt = netz.eintraege.get(kennung)
    if alt is None:
        return Befund("R11", False, f"{kennung}: Ersteintrag",
                      "nicht_zustaendig")
    if neue_fassung <= alt.fassung:
        return Befund("R11", True,
                      f"{kennung}: Fassung {neue_fassung} ueberschreibt "
                      f"{alt.marke}", "ueberschreibt")
    return Befund("R11", False,
                  f"{kennung}: {alt.marke} bleibt, v{neue_fassung} kommt dazu",
                  "neue_fassung")


# ══ R12 · Zwei Raten ════════════════════════════════════════════════════
def r12_zwei_raten(netz: Netz, bericht: Dict[str, object]) -> Befund:
    """Eine Zahl allein laesst sich maximieren, indem man auf alles
    'nicht bestimmbar' antwortet."""
    fehlt = {"erfindungsrate", "uebervorsichtsrate"} - set(bericht)
    if fehlt:
        return Befund("R12", True,
                      f"Bericht nennt {', '.join(sorted(fehlt))} nicht",
                      "rate_fehlt")
    return Befund("R12", False, "Bericht nennt beide Raten", "beide_raten")


# ══ R13 · Kein Lauf ohne Rivalen ════════════════════════════════════════
def r13_rivalen(netz: Netz, lebende: int, als_probe: bool) -> Befund:
    """Bei einer lebenden Hypothese ist der Unterscheidungswert null —
    der Falsifikationswert nicht. Gemessen: ohne diese Regel bleibt die
    Erkennung eines unvollstaendigen Hypothesenraums bei 0,0 %."""
    if lebende >= 2:
        return Befund("R13", False,
                      f"{lebende} lebende Hypothesen — Unterscheidung moeglich",
                      "unterscheidung")
    if als_probe:
        return Befund("R13", False,
                      "eine Hypothese, Lauf ausdruecklich als Probe dagegen "
                      "erklaert", "probe_erklaert")
    return Befund("R13", True,
                  f"{lebende} lebende Hypothese, Lauf als Unterscheidung "
                  "ausgegeben — erwarteter Gewinn ist null", "scheinauswahl")


# ══ R14 · Probenanteil vorher ═══════════════════════════════════════════
def r14_probenanteil(netz: Netz, plan: Dict[str, object]) -> Befund:
    """Ein erklaerter Anteil der Laeufe wird gegen die fuehrende
    Hypothese gewaehlt, nicht von ihr."""
    anteil = plan.get("probenanteil")
    if anteil is None:
        return Befund("R14", True, "Plan ohne erklaerten Probenanteil",
                      "anteil_fehlt")
    if not plan.get("festgelegt_am"):
        return Befund("R14", True,
                      f"Probenanteil {anteil} ohne Datum — nachtraeglich "
                      "waehlbar", "ohne_datum")
    return Befund("R14", False,
                  f"Probenanteil {anteil}, festgelegt am "
                  f"{plan['festgelegt_am']}", "erklaert")


# ══ R15 · Kein Attest ohne Negativliste ═════════════════════════════════
def r15_negativliste(netz: Netz, attest: Dict[str, object]) -> Befund:
    """Ein Stempel, der nur 'geprueft' sagt, erzeugt Sicherheit, die er
    nicht decken kann."""
    if "nicht_geprueft" not in attest:
        return Befund("R15", True,
                      "Attest ohne Negativliste — sagt nicht, was NICHT "
                      "geprueft wurde", "keine_negativliste")
    return Befund("R15", False,
                  f"Attest nennt {len(attest['nicht_geprueft'])} nicht "
                  "gelaufene Straenge", "negativliste_da")


# ══ R16 · Die Stufe steht vor der Aussage ═══════════════════════════════
def r16_stufe_vorher(netz: Netz, stufe_erklaert_am: Optional[str],
                     aussage_am: str) -> Befund:
    """Wer die Folgenklasse nachtraeglich waehlt, waehlt die, die gerade
    besteht."""
    if stufe_erklaert_am is None:
        return Befund("R16", True, "Stufe ohne Zeitpunkt erklaert",
                      "ohne_datum")
    if stufe_erklaert_am > aussage_am:
        return Befund("R16", True,
                      f"Stufe erst am {stufe_erklaert_am} erklaert, Aussage "
                      f"vom {aussage_am}", "nachtraeglich")
    return Befund("R16", False,
                  f"Stufe am {stufe_erklaert_am} erklaert, vor der Aussage",
                  "vorher")


# ══ R17 · Zweite Hand ═══════════════════════════════════════════════════
def r17_zweite_hand(netz: Netz, e: Eintrag) -> Befund:
    """Alle anderen Regeln pruefen die Beziehung zur Quelle. Keine prueft
    die Quelle. Dagegen hilft nur ein zweiter Strom aus anderer Hand."""
    # Gezaehlt werden PFADE, nicht Wurzelkennungen. Der Unterschied ist
    # nicht kosmetisch: #unbekannt und #zyklus zaehlen nicht mehr mit,
    # und zwei Wurzeln desselben Vorgangs zaehlen einmal. Vorher reichte
    # ein Tippfehler in einer Quellenangabe fuer 'zwei unabhaengige
    # Wurzeln'. Die Quellen selbst stehen unveraendert im Vermerk.
    w = netz.unabhaengige_pfade(e)
    roh = {x[0] for x in netz.wurzeln_von(e)}
    verworfen = sorted(
        k for k, _a, v in netz.wurzeln_von(e)
        if v in (netz.UNBEKANNT, netz.ZYKLUS))
    zusatz = (f"; nicht gezaehlt: {', '.join(verworfen)}"
              if verworfen else "")
    if len(w) < 2:
        return Befund("R17", True,
                      f"nur {len(w)} Pfad ({', '.join(sorted(w)) or '—'}) "
                      f"aus {len(roh)} Wurzel(n) — keine zweite Hand"
                      f"{zusatz}", "eine_hand")
    return Befund("R17", False,
                  f"{len(w)} unabhaengige Pfade: {', '.join(sorted(w))}"
                  f"{zusatz}", "zweite_hand")


# ══ R18 · Schuldendeckel ════════════════════════════════════════════════
def r18_deckel(netz: Netz) -> Befund:
    """Waechst der Bestand offener Vermerke ueber die Kapazitaet, ist die
    Ablage kein Gedaechtnis mehr, sondern ein Friedhof."""
    offen = len(netz.offene_vermerke())
    if offen >= netz.deckel:
        return Befund("R18", True,
                      f"{offen} offene Vermerke, Deckel {netz.deckel} — "
                      "keine Aufnahme mehr", "deckel_erreicht")
    return Befund("R18", False,
                  f"{offen} von {netz.deckel} offenen Vermerken", "im_rahmen")


ALLE = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9",
        "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18"]
