"""
tor.py — die Kette und das Tor.

DIE KETTE, in der korrigierten Form

    Quelle -> Inhalt -> Zerlegung -> Graph
           -> pruefbar?  --nein--> VERMERK (nicht pruefbar, mit Grund)
                |ja
           -> geprueft?  --nein--> VERMERK (pruefbar, die Uhr laeuft)
                |ja
           -> Evidenzstufe -> Status

  'pruefbar' ist eine Eigenschaft der AUSSAGE, 'geprueft' eine der
  BUCHHALTUNG. Nur die zweite darf in die Evidenzstufe. Ohne diese
  Trennung schleicht sich 'ungeprueft = vorlaeufig bestaetigt' zurueck.

  Und die Kette hat einen Rueckweg: aendert sich eine Abhaengigkeit,
  faellt jeder Eintrag auf dieser Kante nach VERALTET und beginnt
  wieder vor 'geprueft?'. Das erledigt Netz.neue_fassung().

DAS TOR

  Die Stufe richtet sich nach der FOLGE, nicht nach dem Inhalt.
  Die Straenge sind unabhaengig, weil sie VERSCHIEDENES sehen.
  Das Attest nennt, was geprueft wurde UND was nicht.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

from .kern import Art, Eintrag, Netz, Quelle, Status
from .regeln import (Befund, r5_vorher, r6_kandidaten, r7_modellform,
                     r10_verfahren, r17_zweite_hand)


class Stufe(Enum):
    S0 = "S0 · bleibt im Gespraech"
    S1 = "S1 · intern zitierfaehig"
    S2 = "S2 · geht an Dritte"
    S3 = "S3 · loest eine Handlung mit Geldfolge aus"


class Strang(Enum):
    FORM        = "Form"
    INHALT      = "Inhalt"
    RECHNUNG    = "Rechnung"
    MENSCH      = "Mensch"
    ZWEITE_HAND = "2. Hand"
    REICHWEITE  = "Reichweite"
    ZEIT        = "Zeit"


VERLANGT: Dict[Stufe, Tuple[Strang, ...]] = {
    Stufe.S0: (Strang.FORM,),
    Stufe.S1: (Strang.FORM, Strang.INHALT),
    Stufe.S2: (Strang.FORM, Strang.INHALT, Strang.RECHNUNG,
               Strang.REICHWEITE, Strang.ZEIT),
    Stufe.S3: (Strang.FORM, Strang.INHALT, Strang.RECHNUNG,
               Strang.MENSCH, Strang.ZWEITE_HAND, Strang.REICHWEITE,
               Strang.ZEIT),
}

# Auf S0 wird nur VERMERKT. Gesperrt wird erst, wo der Satz das
# Gespraech verlaesst — sonst entsteht die Zwangsjacke, die nicht
# gebaut werden soll.
SPERRT: Dict[Stufe, Tuple[Strang, ...]] = {
    Stufe.S0: (),
    Stufe.S1: (Strang.FORM, Strang.INHALT),
    Stufe.S2: (Strang.FORM, Strang.INHALT, Strang.RECHNUNG,
               Strang.REICHWEITE, Strang.ZEIT),
    Stufe.S3: (Strang.FORM, Strang.INHALT, Strang.RECHNUNG,
               Strang.MENSCH, Strang.ZWEITE_HAND, Strang.REICHWEITE,
               Strang.ZEIT),
}

WARUM_NICHT = {
    Strang.INHALT:      "nicht verlangt — Inhalt NICHT nachgeprueft",
    Strang.RECHNUNG:    "nicht verlangt — abgeleitete Zahlen NICHT nachgerechnet",
    Strang.MENSCH:      "nicht verlangt — kein Mensch hat das gesehen",
    Strang.ZWEITE_HAND: "nicht verlangt — moeglicherweise nur eine Hand",
    Strang.REICHWEITE:  "nicht verlangt — die Behauptung darf weiter "
                        "reichen als ihre Grundlage",
    Strang.ZEIT:        "nicht verlangt — die Behauptung darf fuer "
                        "Zeiten gelten, die kein Beleg abdeckt",
}


# ══════════════════════════════════════════════════════════════════════
# Die Kette
# ══════════════════════════════════════════════════════════════════════

class Pruefbar(Enum):
    DEDUKTIV  = "deduktiv nachvollziehbar"
    EMPIRISCH = "empirisch mehrfach gestuetzt"
    NEIN      = "nicht nachpruefbar"


@dataclass
class Kettenbericht:
    schritte: List[Tuple[str, str]] = field(default_factory=list)
    pruefbar: Pruefbar = Pruefbar.NEIN
    geprueft: bool = False
    status: Status = Status.VERMERK

    def zeile(self, schritt: str, text: str) -> None:
        self.schritte.append((schritt, text))


def kette(netz: Netz, e: Eintrag) -> Kettenbericht:
    """Die Aussage einmal durch die Kette. Die Quelle kommt dabei in
    der Bewertung NICHT vor — sie wird nur vermerkt."""
    k = Kettenbericht()
    k.zeile("Quelle", ", ".join(e.quellen) or "—")
    k.zeile("Inhalt", e.text)
    k.zeile("Zerlegung",
            f"{len(e.zahlen)} Zahl(en)" +
            (f", Zuschreibung '{e.zuschreibung}'" if e.zuschreibung else ""))
    # FEHLER 35, bei der Ablationsmessung gefunden: kette() zaehlte
    # weiterhin rohe Wurzelkennungen, waehrend r17 laengst
    # unabhaengige_pfade() benutzt. Ein Zirkel A->B->A zaehlte in der
    # Kette als eigene Wurzel — der Kettenstatus sagte BESTAETIGT, und
    # befehl_bilanz befoerderte den Eintrag automatisch, waehrend das
    # Tor ihn ueber die 2. Hand sperrte. Zwei Definitionen von
    # 'unabhaengig' im selben Durchlauf, genau der Befund, der R1 und
    # R17 eine Ebene tiefer schon getroffen hatte.
    roh = {w[0] for w in netz.wurzeln_von(e)}
    wurzeln = netz.unabhaengige_pfade(e)
    k.zeile("Graph", f"{len(wurzeln)} Pfad(e) aus {len(roh)} Wurzel(n): "
                     f"{', '.join(sorted(wurzeln)) or '—'}")

    # pruefbar? — Eigenschaft der Aussage
    abgeleitet = [z for z in e.zahlen if z.rechenweg]
    if abgeleitet:
        k.pruefbar = Pruefbar.DEDUKTIV
    elif len(wurzeln) >= 2:
        k.pruefbar = Pruefbar.EMPIRISCH
    else:
        k.pruefbar = Pruefbar.NEIN
    k.zeile("pruefbar?", k.pruefbar.value)

    if k.pruefbar is Pruefbar.NEIN:
        k.zeile("Status", "VERMERK — nicht pruefbar, Grund notiert")
        k.status = Status.VERMERK
        return k

    # geprueft? — Eigenschaft der Buchhaltung
    k.geprueft = (all(z.nachgerechnet for z in abgeleitet)
                  if abgeleitet else len(wurzeln) >= 2)
    k.zeile("geprueft?", "ja" if k.geprueft else
                         "nein — pruefbar, aber noch nicht geprueft")
    if not k.geprueft:
        k.zeile("Status", "VERMERK — die Uhr laeuft")
        k.status = Status.VERMERK
        return k

    k.zeile("Evidenzstufe", k.pruefbar.value)
    k.status = Status.BESTAETIGT
    k.zeile("Status", "bereit zur Bestaetigung (Tor entscheidet die Stufe)")
    return k


# ══════════════════════════════════════════════════════════════════════
# Die Straenge
# ══════════════════════════════════════════════════════════════════════

def s_form(netz: Netz, e: Eintrag) -> Befund:
    ohne_einheit = [z for z in e.zahlen if not z.einheit]
    if ohne_einheit:
        return Befund("Form", True,
                      f"{len(ohne_einheit)} Zahl(en) ohne Einheit")
    b = r7_modellform(netz, e)
    if b.greift:
        return Befund("Form", True, b.text)
    for z in e.zahlen:
        if z.verfahren is None and z.rechenweg is None and z.quelle is None:
            return Befund("Form", True, f"Zahl {z.wert} ohne jede Herkunft")
    if e.zuschreibung and not any(z.rechenweg for z in e.zahlen):
        return Befund("Form", True,
                      f"Zuschreibung '{e.zuschreibung}' ohne Zerlegung")
    return Befund("Form", False, f"{len(e.zahlen)} Zahl(en), Form in Ordnung")


def s_inhalt(netz: Netz, e: Eintrag) -> Befund:
    """Hier wird gesperrt — nach INHALT, nie nach Quellenart."""
    k = kette(netz, e)
    if k.pruefbar is Pruefbar.NEIN:
        return Befund("Inhalt", True, "nicht nachpruefbar — weder Rechenweg "
                      "noch zwei disjunkte Wurzeln")
    if not k.geprueft:
        return Befund("Inhalt", True, "pruefbar, aber noch nicht geprueft "
                      "(ungeprueft != vorlaeufig bestaetigt)")
    return Befund("Inhalt", False, k.pruefbar.value)


def s_rechnung(netz: Netz, e: Eintrag) -> Befund:
    ab = [z for z in e.zahlen if z.rechenweg]
    if not ab:
        return Befund("Rechnung", False, "keine abgeleitete Zahl enthalten")
    offen = [z for z in ab if z.nachgerechnet is not True]
    if offen:
        return Befund("Rechnung", True,
                      f"{len(offen)} Ableitung(en) nicht nachgerechnet")
    return Befund("Rechnung", False,
                  f"{len(ab)} Ableitung(en) nachgerechnet")


def s_mensch(netz: Netz, e: Eintrag, pruefer: Optional[str]) -> Befund:
    if not pruefer:
        return Befund("Mensch", True, "keine namentlich benannte Person")
    return Befund("Mensch", False, f"geprueft von {pruefer}")


def s_zweite_hand(netz: Netz, e: Eintrag) -> Befund:
    b = r17_zweite_hand(netz, e)
    return Befund("2. Hand", b.greift, b.text)


# ══════════════════════════════════════════════════════════════════════
# Die Geltung — KEIN sechster Strang
# ══════════════════════════════════════════════════════════════════════
#
# Die fuenf Straenge pruefen die Aussage gegen ihre Quellen. Das hier
# prueft die VERWENDUNG gegen die Aussage. Das sind zwei Ebenen, und
# sie werden nicht vermischt:
#
#     der Satz bleibt BESTAETIGT   !=   der Satz gilt fuer heute
#
# 'Der Ertrag 2026 liegt 12 % ueber Plan' wird 2030 nicht falscher. Wer
# ihn 2030 ueber die Gegenwart benutzt, wendet ihn ausserhalb seines
# Geltungsbereichs an. Das ist P4 der Schablone (UEBERDEHNUNG) auf der
# Zeitachse — ein Mengenvergleich, kein Urteil ueber Wahrheit.
#
# Deshalb auch ein eigenes Ergebnis und nicht GESPERRT: gesperrt ist die
# Verwendung, nicht der Satz.

def _diagnose(netz: Netz, e: Eintrag) -> Tuple[object, ...]:
    """Spaeter Import: tor kennt leitung, leitung kennt ka. tor kennt ka
    nicht. Faellt die Leitung aus, faellt die Diagnose aus — nie das
    Attest."""
    try:
        from .leitung import diagnose as _d
        return _d(netz, e)
    except Exception:
        return ()


AUSSERHALB = "AUSSERHALB DER GELTUNG"
IMMER = ("laufend", "unbefristet", "dauerhaft", "immer")


def deckt(wann: str, tag: str) -> Optional[bool]:
    """Deckt der Geltungsbereich diesen Tag? None = nicht entscheidbar.
    'unbekannt != falsch' — eine unlesbare Angabe sperrt nichts, sie
    kommt in die Negativliste."""
    w = (wann or "").strip().lower()
    if not w:
        return None
    if w in IMMER:
        return True
    try:
        jahr = int(tag[:4])
    except (ValueError, IndexError):
        return None
    # FEHLER 25: erste Fassung trennte an '-'. 'ab 2020' ergab damit ein
    # einziges Stueck 'ab 2020', das nicht isdigit() ist — die beiden
    # offenen Formen fielen still auf 'nicht bewertet'. Gefunden von der
    # Probe, nicht beim Lesen.
    jahre = [int(x) for x in re.findall(r"\d{4}", w)]
    if w.startswith("ab ") and len(jahre) == 1:
        return jahr >= jahre[0]
    if w.startswith("bis ") and len(jahre) == 1:
        return jahr <= jahre[0]
    if len(jahre) == 1:
        return jahr == jahre[0]
    if len(jahre) >= 2:
        return min(jahre) <= jahr <= max(jahre)
    return None


def s_geltung(e: Eintrag,
              tag: Optional[str]) -> Optional[Tuple[Optional[bool], str]]:
    """Drei Ausgaenge, nicht zwei. 'nicht bewertbar' darf nicht als
    'geprueft und in Ordnung' erscheinen — das ist die zweite
    Nicht-Gleichung, und guete.py macht denselben Unterschied."""
    if tag is None:
        return None
    wann = e.geltungsbereich.get("wann")
    d = deckt(wann or "", tag)
    if d is None:
        return (None, f"Geltungsbereich 'wann' "
                      f"{'fehlt' if not wann else f'unlesbar ({wann})'} — "
                      f"Verwendung am {tag} nicht bewertet")
    if d:
        return (True, f"gilt fuer {wann}, deckt den Verwendungstag {tag}")
    return (False, f"gilt fuer {wann}, verwendet am {tag} — die Aussage "
                   f"bleibt stehen, diese VERWENDUNG liegt ausserhalb")


# ══════════════════════════════════════════════════════════════════════
# Das Attest
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Attest:
    eintrag: str
    text: str
    stufe: Stufe
    beginn: str
    ende: str
    eingaben: Tuple[str, ...]
    person: Optional[str]
    quellenvermerk: List[str] = field(default_factory=list)
    geprueft: List[Befund] = field(default_factory=list)
    nicht_geprueft: List[Tuple[Strang, str]] = field(default_factory=list)
    stufendeckel: Optional[str] = None
    geltung: Optional[Tuple[Optional[bool], str]] = None   # (deckt, Grund)
    verwendet_am: Optional[str] = None
    # DIAGNOSE — erklaerend, nie entscheidend. ergebnis liest dieses
    # Feld nicht, und das ist GEPRUEFT, nicht behauptet
    # (probe_downstream.py, Stufe 3a: tor mit und ohne Diagnose ueber
    # alle Faelle, Ergebnis identisch).
    diagnose: Tuple[object, ...] = ()

    @property
    def sperren(self) -> List[Befund]:
        namen = {s.value for s in SPERRT[self.stufe]}
        return [b for b in self.geprueft if b.greift and b.regel in namen]

    @property
    def vermerke(self) -> List[Befund]:
        namen = {s.value for s in SPERRT[self.stufe]}
        return [b for b in self.geprueft if b.greift and b.regel not in namen]

    @property
    def ergebnis(self) -> str:
        # Die Geltung kommt ZUERST und hat ein eigenes Wort: sie sagt
        # nichts ueber den Beleg, sondern ueber die Verwendung. Auf S0
        # wird nichts gesperrt, auch das nicht.
        if (self.geltung is not None and self.geltung[0] is False
                and SPERRT[self.stufe]):
            return AUSSERHALB
        if self.sperren:
            return "GESPERRT"
        return "FREI MIT VERMERK" if self.vermerke else "FREIGABE"

    def zeilen(self) -> List[str]:
        z = [f"ATTEST   {self.stufe.value}",
             f"Eintrag  {self.eintrag}",
             f"Aussage  {self.text}",
             f"Zeit     {self.beginn}",
             f"Person   {self.person or '— keine benannt —'}",
             f"Eingaben {', '.join(self.eingaben) or '—'}",
             "QUELLENVERMERK (notiert, nicht bewertet)"]
        z += [f"  {q}" for q in self.quellenvermerk] or ["  —"]
        z.append("GEPRUEFT")
        sperr = {s.value for s in SPERRT[self.stufe]}
        for b in self.geprueft:
            mk = "ok  " if not b.greift else ("NEIN" if b.regel in sperr
                                              else "merk")
            z.append(f"  [{mk}] {b.regel:<9} {b.text}")
        z.append("NICHT GEPRUEFT")
        z += [f"  [ -- ] {s.value:<9} {w}" for s, w in self.nicht_geprueft] \
            or ["  —"]
        if self.stufendeckel:
            z.append(f"STUFENDECKEL  {self.stufendeckel}")
        if self.diagnose:
            z.append("DIAGNOSE (erklaerend, nicht entscheidend)")
            for d in self.diagnose:
                mk = "!" if getattr(d, "greift", False) else " "
                z.append(f"  [{mk}] {d.kandidat}: {d.anlass}")
                for weg in getattr(d, "selbstbezug", ()):
                    z.append(f"      Weg  {' -> '.join(weg)}")
                if getattr(d, "greift", False):
                    z.append(f"      Frage  {d.frage}")
        if self.geltung is None:
            z.append("GELTUNG  [ -- ] kein Verwendungstag angegeben — "
                     "nicht geprueft")
        else:
            mk = {True: "ok  ", False: "AUSS", None: " -- "}[self.geltung[0]]
            z.append(f"GELTUNG  [{mk}] {self.geltung[1]}")
        z.append(f"ERGEBNIS {self.ergebnis} auf {self.stufe.name}")
        return z


def s_reichweite(netz: Netz, e: Eintrag) -> Befund:
    """Reicht die Behauptung weiter als ihre Grundlage?

    FEHLER 46. Das Tor rechnet hier NICHTS nach — es liest, was die
    Schablone in P4 gefunden hat. Eine Definition, eine Stelle.
    Ein leeres Feld heisst 'keine Ueberdehnung gefunden', nicht
    'nicht geprueft': wer nach_netz() benutzt, hat P4 laufen lassen."""
    # FEHLER 47, im eigenen Einbau: 'greift' heisst 'der Einwand trifft
    # zu', nicht 'alles in Ordnung'. Die erste Fassung war invertiert —
    # die bescheidene These bekam einen Vermerk, die masslose ging
    # durch. Gefunden, weil die Tabelle verkehrt herum aussah.
    if not e.reichweite:
        return Befund("Reichweite", False,
                      "die Behauptung bleibt im Rahmen ihrer Grundlage")
    return Befund("Reichweite", True,
                  f"{len(e.reichweite)} Ueberdehnung(en): "
                  + "; ".join(e.reichweite))


def s_zeit(netz: Netz, e: Eintrag) -> Befund:
    """Gilt die Behauptung fuer Zeiten, die kein Beleg abdeckt?

    Gebaut am 29.09.2026, nachdem F4 und F5 im Fuenf-Arm-Versuch in
    10 von 10 Laeufen gefallen sind — in JEDEM Arm, mit und ohne
    Werkzeug, mit Anweisung und mit Erklaerung. Kein Eingriff auf der
    Sprachebene hat die Zeitform einer Behauptung beruehrt.

    Der Grund war nicht die Sprache. Es gab kein Feld. Jetzt gibt es
    eines, und der Vergleich ist ein Intervallvergleich statt eines
    Zeichenkettenvergleichs.

    Das Tor rechnet auch hier nichts nach — es liest P7. Eine
    Definition, eine Stelle."""
    # FEHLER 49, von drei unabhaengigen Laeufen am selben Tag gefunden,
    # an dem der Strang gebaut wurde. Die erste Fassung meldete
    # "[ok] die Behauptung bleibt im belegten Zeitraum" GENAU DANN, wenn
    # gar kein Zeitraum dastand — acht Zeilen unter der Auskunft "P5, P7
    # und P8 stumm" im selben Bericht.
    #
    # Ein gruener Haken aus dem Hinsehen auf nichts. Das ist die
    # Nicht-Gleichung, auf der das ganze Programm steht, gebrochen von
    # dem Strang, der sie durchsetzen sollte:
    #
    #     nicht geprueft != in Ordnung
    #
    # Und es ist schlimmer als kein Haken, weil es beruhigt.
    if not e.zeit_pruefbar:
        return Befund("Zeit", True,
                      "NICHT PRUEFBAR — kein Zeitraum angegeben. Das ist "
                      "kein Befund ueber die Behauptung, sondern einer "
                      "ueber den Bogen")
    if not e.zeitluecke:
        return Befund("Zeit", False,
                      "geprueft: die Behauptung bleibt im belegten Zeitraum")
    return Befund("Zeit", True,
                  f"{len(e.zeitluecke)} Zeitluecke(n): "
                  + "; ".join(e.zeitluecke))


def tor(netz: Netz, e: Eintrag, stufe: Stufe,
        pruefer: Optional[str] = None,
        verwendet_am: Optional[str] = None,
        mit_diagnose: bool = False) -> Attest:
    """verwendet_am: der Tag, an dem die Aussage BENUTZT wird. Ohne
    Angabe wird die Geltung nicht geprueft und steht als solche in der
    Negativliste — nicht als stilles 'in Ordnung'."""
    jetzt = datetime.now(timezone.utc).isoformat(timespec="seconds")
    noetig = VERLANGT[stufe]
    wurzeln = sorted({w[0] for w in netz.wurzeln_von(e)})

    vermerk = []
    gesperrte = []
    for k in sorted(netz.ketten_von(e)):
        q = netz.quellen.get(k)
        if q is None:
            vermerk.append(f"{k}: unbekannte Quelle")
            continue
        sp = ""
        if q.gesperrt:
            gesperrte.append(k)
            sp = (f"  [Sperrliste seit {q.gesperrt_seit}, "
                  f"{q.gesperrt_durch or 'ohne Namen'}]")
        vermerk.append(f"{q.kennung}: {q.was} — Art {q.art.value}, "
                       f"Guete {q.guete}{sp}")

    a = Attest(eintrag=e.marke, text=e.text, stufe=stufe, beginn=jetzt,
               ende=jetzt, eingaben=tuple(wurzeln), person=pruefer,
               quellenvermerk=vermerk,
               geltung=s_geltung(e, verwendet_am),
               verwendet_am=verwendet_am,
               diagnose=(_diagnose(netz, e) if mit_diagnose else ()))

    pruefungen: Dict[Strang, Befund] = {
        Strang.FORM: s_form(netz, e),
        Strang.INHALT: s_inhalt(netz, e),
        Strang.RECHNUNG: s_rechnung(netz, e),
        Strang.MENSCH: s_mensch(netz, e, pruefer),
        Strang.ZWEITE_HAND: s_zweite_hand(netz, e),
        Strang.REICHWEITE: s_reichweite(netz, e),
        Strang.ZEIT: s_zeit(netz, e),
    }
    for s in Strang:
        if s in noetig:
            a.geprueft.append(pruefungen[s])
        else:
            a.nicht_geprueft.append((s, WARUM_NICHT[s]))

    # Die Sperrliste wirkt auf die STUFE, nie auf den Wahrheitswert —
    # und nur, wenn der einzige Weg ueber sie laeuft.
    if gesperrte and len(wurzeln) < 2 and stufe in (Stufe.S2, Stufe.S3):
        a.stufendeckel = (f"einziger Weg laeuft ueber "
                          f"{', '.join(sorted(gesperrte))} (Sperrliste) — "
                          "hoechstens S1 ohne zweiten Weg")
        a.geprueft.append(Befund("Inhalt", True, a.stufendeckel))
    a.ende = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return a
