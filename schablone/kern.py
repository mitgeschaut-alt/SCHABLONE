"""
kern.py — Datenmodell und Zustandsuebergaenge.

HIER LIEGT DAS EIGENTLICHE. Die fuenf Nicht-Gleichungen sind keine
Kommentare, sondern eine Uebergangstabelle: ein verbotener Wechsel
loest einen Fehler aus, statt stillschweigend zu passieren.

    unbekannt                     != falsch
    ungeprueft                    != vorlaeufig bestaetigt
    Pruefung offen                != Bestaetigung wahrscheinlich
    geprueft und nicht bestaetigt != widerlegt
    widerlegt                     != wertlos
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple


# ══════════════════════════════════════════════════════════════════════
# Zustaende
# ══════════════════════════════════════════════════════════════════════

class Status(Enum):
    KANDIDAT   = "kandidat"      # strukturierte Hypothese, noch keine Einheit
    VERMERK    = "vermerk"       # erkannt, Pruefung steht aus — die Uhr laeuft
    BESTAETIGT = "bestaetigt"    # Pruefung bestanden, im Geltungsbereich
    WIDERLEGT  = "widerlegt"     # Gegenbeleg liegt vor
    VERALTET   = "veraltet"      # war tragfaehig, Eingang hat sich geaendert


# Erlaubte Wechsel. Was hier fehlt, ist verboten — und zwar mit Grund.
UEBERGAENGE: Dict[Status, FrozenSet[Status]] = {
    Status.KANDIDAT:   frozenset({Status.VERMERK, Status.WIDERLEGT}),
    Status.VERMERK:    frozenset({Status.BESTAETIGT, Status.WIDERLEGT,
                                  Status.VERMERK}),
    Status.BESTAETIGT: frozenset({Status.VERALTET, Status.WIDERLEGT}),
    Status.VERALTET:   frozenset({Status.BESTAETIGT, Status.WIDERLEGT,
                                  Status.VERMERK}),
    Status.WIDERLEGT:  frozenset(),      # endgueltig, aber NICHT wertlos
}

BEGRUENDUNG_VERBOTEN = {
    (Status.KANDIDAT, Status.BESTAETIGT):
        "ein Kandidat wird nie direkt bestaetigt — er wird erst zum "
        "Vermerk, dann geprueft (ungeprueft != vorlaeufig bestaetigt)",
    (Status.VERMERK, Status.VERALTET):
        "veraltet setzt voraus, dass etwas einmal getragen hat",
    (Status.WIDERLEGT, Status.BESTAETIGT):
        "ein Gegenbeleg wird nicht durch Wiederholung aufgehoben — "
        "dafuer braucht es eine neue Fassung mit eigener Kennung",
    (Status.WIDERLEGT, Status.VERMERK):
        "widerlegt bleibt widerlegt und filtert den Zulauf "
        "(widerlegt != wertlos)",
}


class Uebergangsfehler(Exception):
    pass


class Aufnahmefehler(Exception):
    pass


# ══════════════════════════════════════════════════════════════════════
# Quellen
# ══════════════════════════════════════════════════════════════════════

class Art(Enum):
    MESSUNG  = "messung"     # Beobachtung an einem Apparat, zu einem Vorgang
    AUSSAGE  = "aussage"     # jemand behauptet etwas
    RECHNUNG = "rechnung"    # deduktiv aus anderen


@dataclass(frozen=True)
class Quelle:
    """Die Quelle wird VERMERKT, nie gefiltert. guete und gesperrt sind
    Notizen; auf den Wahrheitswert wirken sie nie, auf die Freigabestufe
    schon."""
    kennung: str
    was: str
    art: Art
    guete: str = "unbekannt"
    uebernommen_aus: Tuple[str, ...] = ()
    vorgang: Optional[str] = None
    gesperrt_seit: Optional[str] = None      # Eintrag aus der Sperrliste
    gesperrt_durch: Optional[str] = None

    @property
    def gesperrt(self) -> bool:
        return self.gesperrt_seit is not None


# ══════════════════════════════════════════════════════════════════════
# Zahlen, Variablen, Modellformen
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Zahl:
    """R10: ohne verfahren nicht speicherbar.
    R5: ohne festgelegt_am < daten_ab nicht gueltig.
    R6: ohne kandidaten_geprueft unvollstaendig."""
    wert: float
    einheit: str = ""
    quelle: Optional[str] = None
    rechenweg: Optional[str] = None
    nachgerechnet: Optional[bool] = None
    verfahren: Optional[str] = None
    kandidaten_geprueft: Optional[int] = None
    festgelegt_am: Optional[str] = None      # question_time
    daten_ab: Optional[str] = None           # data_time


@dataclass(frozen=True)
class Fassung:
    nummer: int
    wert: object
    grund: str
    daten_ab: str


@dataclass
class Variable:
    kennung: str
    name: str
    fassungen: List[Fassung]

    @property
    def stand(self) -> int:
        return self.fassungen[-1].nummer

    @property
    def wert(self) -> object:
        return self.fassungen[-1].wert


@dataclass(frozen=True)
class Modellform:
    """R7: wer 'exakt' sagt, nennt die Annahmen, unter denen es exakt ist."""
    gleichung: str
    annahmen: Tuple[str, ...] = ()


# ══════════════════════════════════════════════════════════════════════
# Der Eintrag — eine Behauptung im Buch
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Eintrag:
    kennung: str
    text: str
    status: Status
    eingang: str                                   # ISO-Datum
    seit: str                                      # letzter Statuswechsel
    quellen: Tuple[str, ...] = ()
    zahlen: Tuple[Zahl, ...] = ()
    variablen: Tuple[str, ...] = ()
    zuschreibung: Optional[str] = None
    geltungsbereich: Dict[str, str] = field(default_factory=dict)
    modellform: Optional[Modellform] = None
    exakt: bool = False
    stand: Tuple[Tuple[str, int], ...] = ()        # Eingangsfassungen
    fassung: int = 1
    gegenbeleg: Optional[str] = None
    # FEHLER 46: die Schablone fand die UEBERDEHNUNG, das Tor erfuhr
    # nie davon — nach_netz() rief abgleichen() gar nicht auf. Damit
    # hing die Torentscheidung allein an der Belegstruktur, und eine
    # These ohne jeden Geltungsbereich kam genauso durch wie die
    # blosse Wiedergabe einer Messung.
    # ABGELEITET, NICHT GESETZT: nur nach_netz() schreibt hier hinein.
    # Wer einen Bogen ausfuellt, kann dieses Feld nicht erreichen.
    reichweite: Tuple[str, ...] = ()
    # Dasselbe eine Achse weiter: WANN die Behauptung gilt, gegen den
    # Zeitraum, den ihre Belege abdecken. ABGELEITET, NICHT SETZBAR —
    # nur nach_netz() schreibt hier hinein. Die Falle, die in allen
    # zehn Laeufen des Fuenf-Arm-Versuchs zugeschnappt hat.
    zeitluecke: Tuple[str, ...] = ()
    # FEHLER 49: ein leeres zeitluecke hiess bisher "keine Luecke
    # gefunden". Es hiess aber in Wahrheit zweierlei — "geprueft, nichts
    # gefunden" ODER "gar nicht pruefbar, weil kein Zeitraum dasteht".
    # Das Tor machte aus beidem denselben gruenen Haken.
    zeit_pruefbar: bool = False
    versuche: int = 0
    verlauf: List[Tuple[str, Status, str]] = field(default_factory=list)

    @property
    def marke(self) -> str:
        return f"{self.kennung}.v{self.fassung}"

    def alter(self, heute: str) -> int:
        return (date.fromisoformat(heute) - date.fromisoformat(self.eingang)).days

    def wartet(self, heute: str) -> int:
        """Wie lange die ENTSCHEIDUNG aussteht — ab dem letzten
        Statuswechsel, nicht ab dem Eingang. Fuer einen VERMERK ist das
        meist dasselbe; fuer einen VERALTETEN nicht: der hat einmal
        getragen und wartet erst seit der Revision wieder."""
        return (date.fromisoformat(heute) - date.fromisoformat(self.seit)).days

    def wechseln(self, neu: Status, tag: str, grund: str,
                 gegenbeleg: Optional[str] = None) -> None:
        if neu is Status.WIDERLEGT and not gegenbeleg:
            raise Uebergangsfehler(
                f"{self.marke}: WIDERLEGT ohne Gegenbeleg. Eine gescheiterte "
                "Pruefung ohne Gegenbeleg fuehrt zurueck nach VERMERK "
                "(geprueft und nicht bestaetigt != widerlegt)")
        if neu not in UEBERGAENGE[self.status]:
            warum = BEGRUENDUNG_VERBOTEN.get(
                (self.status, neu), "nicht vorgesehen")
            raise Uebergangsfehler(
                f"{self.marke}: {self.status.value} -> {neu.value} "
                f"nicht erlaubt — {warum}")
        self.verlauf.append((tag, neu, grund))
        self.status, self.seit = neu, tag
        if gegenbeleg:
            self.gegenbeleg = gegenbeleg


# ══════════════════════════════════════════════════════════════════════
# Das Netz
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Netz:
    quellen: Dict[str, Quelle] = field(default_factory=dict)
    variablen: Dict[str, Variable] = field(default_factory=dict)
    eintraege: Dict[str, Eintrag] = field(default_factory=dict)
    deckel: int = 50                    # R18: Obergrenze offener Vermerke
    abgewiesen: List[Tuple[str, str]] = field(default_factory=list)

    # ── Eintragen ─────────────────────────────────────────────────────
    def quelle(self, q: Quelle, ersetzen: bool = False) -> None:
        """FEHLER 29: die erste Fassung schrieb stillschweigend drueber.
        Zwei Aufrufe mit derselben Kennung und verschiedenem Inhalt
        loeschten die erste Herkunft spurlos. Ersetzen ist erlaubt, aber
        nur ausdruecklich — dann steht es an der Aufrufstelle."""
        alt = self.quellen.get(q.kennung)
        if alt is not None and alt != q and not ersetzen:
            raise Aufnahmefehler(
                f"Quelle {q.kennung} ist bereits eingetragen "
                f"({alt.was!r}, Art {alt.art.value}). Eine andere Quelle "
                f"unter derselben Kennung loescht Herkunft. Entweder eine "
                f"eigene Kennung vergeben oder quelle(..., ersetzen=True).")
        self.quellen[q.kennung] = q

    def variable(self, kennung: str, name: str, wert: object,
                 daten_ab: str, grund: str = "Ersteintrag") -> None:
        self.variablen[kennung] = Variable(
            kennung, name, [Fassung(1, wert, grund, daten_ab)])

    def neue_fassung(self, kennung: str, wert: object, grund: str,
                     daten_ab: str) -> Tuple[List[str], List[str]]:
        """Das Original bleibt. Rueckgabe: ZWEI Listen — der Rueckweg,
        den die Kette sonst nicht hat.

        FEHLER 23, gemessen am 22.09.2026:
          Die erste Fassung sah nur in e.stand nach. Ein Eintrag, der
          die Variable unter e.variablen fuehrt, aber keine Fassung
          notiert hat, blieb BESTAETIGT — die Kante war da, der
          Rueckweg benutzte sie nicht. Damit war der Rueckweg ueber ein
          SETZBARES FELD abschaltbar: stand=() und die Revision geht
          vorbei. Viertes Mal dasselbe Muster in dieser Sitzung.

          Korrigiert: wer die Variable nennt, ist betroffen. Wo keine
          Fassung notiert ist, ist NICHT BEKANNT, auf welcher der
          Eintrag steht — und 'unbekannt != falsch' heisst hier gerade
          nicht 'also bleibt es stehen', sondern VERALTET mit dem Grund
          'Fassung ungeklaert'. VERALTET behauptet nicht, der Satz sei
          falsch; es sagt, die Grundlage hat sich bewegt.

        Zwei Listen, nie eine Zahl: was nachweislich auf einer alten
        Fassung stand, und was nur deshalb faellt, weil niemand
        mitgeschrieben hat. Die zweite Liste ist der Preis dieser
        Korrektur und muss sichtbar bleiben."""
        v = self.variablen[kennung]
        v.fassungen.append(Fassung(v.stand + 1, wert, grund, daten_ab))
        gefuehrt: List[str] = []
        ungeklaert: List[str] = []
        for e in self.eintraege.values():
            notiert = [f for k, f in e.stand if k == kennung]
            if notiert:
                if all(f == v.stand for f in notiert):
                    continue
                warum = f"{kennung} v{min(notiert)} -> v{v.stand}: {grund}"
                ziel = gefuehrt
            elif kennung in e.variablen:
                warum = (f"{kennung} -> v{v.stand}: {grund} "
                         f"(Fassung im Eintrag nicht notiert)")
                ziel = ungeklaert
            else:
                continue
            if e.status is Status.BESTAETIGT:
                e.wechseln(Status.VERALTET, daten_ab, warum)
                ziel.append(e.marke)
        return gefuehrt, ungeklaert

    def offene_vermerke(self) -> List[Eintrag]:
        """Nur VERMERK. Der Schuldendeckel zaehlt weiter nur diese: ein
        VERALTETER ist schon einmal bezahlt worden."""
        return [e for e in self.eintraege.values()
                if e.status is Status.VERMERK]

    def offen(self) -> List[Eintrag]:
        """Was eine ENTSCHEIDUNG braucht: ungeprueft ODER ueberholt.

        FEHLER 24: faellige() sah nur offene_vermerke(). Ein VERALTETER
        Eintrag fiel damit aus der Buchhaltung — kein Vermerk, keine
        Wiedervorlage, kein Alter. Er verschwand still. Gemessen: nach
        der Revision tauchte er weder 2027 noch 2030 in faellige() auf."""
        return [e for e in self.eintraege.values()
                if e.status in (Status.VERMERK, Status.VERALTET)]

    def aufnehmen(self, e: Eintrag) -> Eintrag:
        """Zwei Gruende, einen Eintrag GAR NICHT erst anzunehmen."""
        alt = self.eintraege.get(e.kennung)
        if alt is not None and alt.status is Status.WIDERLEGT:
            self.abgewiesen.append(
                (e.kennung, "bereits widerlegt — Gegenbeleg " +
                 (alt.gegenbeleg or "?") + "; neue Fassung noetig"))
            raise Aufnahmefehler(
                f"{e.kennung} ist widerlegt. Wiedervorlage wird nicht "
                "angenommen — widerlegt filtert den Zulauf.")
        if alt is not None and alt is not e:
            # FEHLER 28: die erste Fassung legte den neuen Eintrag einfach
            # ins Verzeichnis. Damit liess sich JEDER Zustand setzen, ohne
            # die Uebergangstabelle zu beruehren — ein BESTAETIGTER Eintrag
            # wurde durch einen anderen Text mit frischem Verlauf ersetzt,
            # und niemand sah es. Die Zustandsmaschine war umgehbar, indem
            # man sie nicht benutzte.
            self.abgewiesen.append(
                (e.kennung, f"Kennung belegt ({alt.status.value})"))
            raise Aufnahmefehler(
                f"{e.kennung} ist bereits vergeben (Status "
                f"{alt.status.value}, Fassung {alt.fassung}). Ein Eintrag "
                f"wird nie ueberschrieben — er wechselt den Zustand ueber "
                f"wechseln() oder bekommt eine eigene Kennung.")
        if alt is None and len(self.offene_vermerke()) >= self.deckel:
            self.abgewiesen.append(
                (e.kennung, f"Schuldendeckel {self.deckel} erreicht"))
            raise Aufnahmefehler(
                f"Schuldendeckel {self.deckel} erreicht: es wartet mehr, "
                "als geprueft werden kann. Pruefen oder verwerfen, nicht "
                "annehmen.")
        self.eintraege[e.kennung] = e
        e.verlauf.append((e.eingang, e.status, "aufgenommen"))
        return e

    # ── Graph ─────────────────────────────────────────────────────────
    # Sichtbare Markierungen im Vorgang-Feld. Sie verschwinden nie
    # stillschweigend — sie stehen in jeder Wurzelliste und im Attest.
    UNBEKANNT = "#unbekannt"
    ZYKLUS = "#zyklus"

    def wurzeln(self, kennung: str,
                gesehen: Optional[Set[str]] = None
                ) -> Set[Tuple[str, Art, Optional[str]]]:
        """REINE PROVENIENZ. Gibt ALLE Wurzeln zurueck, trifft keine
        Auswahl, fasst nichts zusammen, stuerzt nicht ab.

        FEHLER 30: die erste Fassung hatte bei einer abgeleiteten MESSUNG
        'mess[0]' — sie nahm von mehreren Messwurzeln die alphabetisch
        erste und liess die anderen fallen. Eine Quelle, die Zebra und
        Adler zusammenfuehrt, hatte danach nur noch Adler als Wurzel.
        Das ist eine epistemische Entscheidung, versteckt in einer
        Sortierung. Jetzt: keine Auswahl. Das Zusammenfassen gleicher
        Vorgaenge ist eine ANDERE Frage und steht ausdruecklich in
        unabhaengige_pfade().

        FEHLER 31: ohne 'gesehen' warf ein Zyklus in uebernommen_aus
        einen RecursionError — der Provenienzgraph brachte den Kern zum
        Absturz. Jetzt wird der Zyklus zu einer sichtbaren Wurzel.

        FEHLER 32: eine nicht eingetragene Kennung wurde zu
        (kennung, AUSSAGE, None) — also zu einer vollwertigen,
        unabhaengigen Wurzel. Ein Tippfehler in einer Quellenangabe
        reichte damit fuer 'zwei unabhaengige Wurzeln' und S3-Freigabe.
        Jetzt traegt sie die Marke #unbekannt: sie wird weiter VERMERKT
        (nie gefiltert), zaehlt aber nicht als Pfad.
        """
        gesehen = set() if gesehen is None else gesehen
        q = self.quellen.get(kennung)
        if q is None:
            return {(kennung, Art.AUSSAGE, self.UNBEKANNT)}
        if kennung in gesehen:
            return {(kennung, q.art, self.ZYKLUS)}
        gesehen = gesehen | {kennung}
        # FEHLER 33, von der Konformitaetsprobe gefunden (46/47), nicht
        # beim Lesen: die erste Haertung liess eine MESSUNG mit eigenem
        # Vorgang ihre Wurzeln erben, sobald sie uebernommen_aus fuehrte.
        # Damit fielen 'Ablesung Maerz' und 'Ablesung April' auf dieselbe
        # Wurzel (zaehler, ohne Vorgang) zusammen — zwei Beobachtungen
        # der Welt wurden ein Zeuge.
        #
        # Der Grund liegt tiefer: uebernommen_aus traegt ZWEI Bedeutungen.
        #   'abgeschrieben von'  -> Wurzel wird geerbt
        #   'gemessen MIT'       -> eigener Zeuge, Apparat nur vermerkt
        # Eine MESSUNG MIT EIGENEM VORGANG ist immer der zweite Fall: sie
        # hat selbst hingesehen. Ihr Apparat steht im Quellenvermerk, in
        # der Wurzelrechnung hat er nichts verloren.
        if q.art is Art.MESSUNG and q.vorgang is not None:
            return {(q.kennung, Art.MESSUNG, q.vorgang)}
        if not q.uebernommen_aus:
            return {(q.kennung, q.art, q.vorgang)}
        out: Set[Tuple[str, Art, Optional[str]]] = set()
        for v in q.uebernommen_aus:
            out |= self.wurzeln(v, gesehen)
        return out

    def pfade(self, kennung: str) -> Dict[str, Tuple[str, Art, Optional[str]]]:
        """Pfadschluessel -> Wurzel, fuer EINE Quelle. Ein Vorgang ist
        EIN Pfad, egal wie viele Blaetter darueber liegen; eine Wurzel
        ohne Vorgang ist ihr eigener Pfad. #unbekannt und #zyklus
        bekommen keinen Pfad — sie bleiben aber in wurzeln() sichtbar."""
        out: Dict[str, Tuple[str, Art, Optional[str]]] = {}
        for k, art, vorgang in self.wurzeln(kennung):
            if vorgang in (self.UNBEKANNT, self.ZYKLUS):
                continue
            out[f"vorgang:{vorgang}" if vorgang else k] = (k, art, vorgang)
        return out

    def unabhaengige_pfade(self, e: Eintrag) -> Set[str]:
        """WIE VIELE ZEUGEN. Hier — und nur hier — wird aus Provenienz
        eine Aussage ueber Unabhaengigkeit. Drei Schritte, alle sichtbar:

          1. #unbekannt faellt raus. Was nirgends eingetragen ist, kann
             nicht bezeugen. (unbekannt != unabhaengig)
          2. #zyklus faellt raus. Eine Kette ohne Boden traegt nichts.
          3. Wurzeln mit demselben VORGANG zaehlen einmal. Zwei
             Ablesungen desselben Vorgangs sind ein Zeuge, auch wenn
             zwei Apparate darauf stehen.

        Rueckgabe sind die Schluessel der Pfade, nicht der Quellen —
        deshalb Menge, nie Zahl allein."""
        pfade: Set[str] = set()
        for k in e.quellen:
            pfade |= set(self.pfade(k))
        return pfade

    def kette(self, kennung: str,
              gesehen: Optional[Set[str]] = None) -> Set[str]:
        """Alle Quellen auf dem Weg, auch die Traeger. Zyklusfest."""
        gesehen = set() if gesehen is None else gesehen
        if kennung in gesehen:
            return set()
        q = self.quellen.get(kennung)
        out = {kennung}
        if q:
            for v in q.uebernommen_aus:
                out |= self.kette(v, gesehen | {kennung})
        return out

    def wurzeln_von(self, e: Eintrag) -> Set[Tuple[str, Art, Optional[str]]]:
        out: Set[Tuple[str, Art, Optional[str]]] = set()
        for k in e.quellen:
            out |= self.wurzeln(k)
        return out

    def ketten_von(self, e: Eintrag) -> Set[str]:
        out: Set[str] = set()
        for k in e.quellen:
            out |= self.kette(k)
        return out

    def rueckwaerts(self) -> Dict[str, Set[str]]:
        """Variable -> Eintraege, die auf ihr stehen."""
        out: Dict[str, Set[str]] = {}
        for e in self.eintraege.values():
            for v in e.variablen:
                out.setdefault(v, set()).add(e.marke)
        return out
