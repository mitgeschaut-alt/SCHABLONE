"""
schablone.py — die Vorstufe. Form vor Rechnung.

WARUM UEBERHAUPT EINE VORSTUFE

  Alle acht Angriffe dieser Sitzung sind durch ein SETZBARES FELD
  gelaufen, keiner durch eine Tabelle. Die Tabellen (UEBERGAENGE,
  VERLANGT, SPERRT, KATALOG) haben kein einziges Mal nachgegeben. Die
  Felder haben jedes Mal nachgegeben:

      Art.RECHNUNG          selbst gesetzt  -> Vermutung wird Rechnung
      uebernommen_aus=()    weggelassen     -> eine Wurzel wird zwei
      surrogat=False        selbst gesetzt  -> ABSTAND verstummt
      nachgerechnet=True    selbst gesetzt  -> Rechnungsstrang gruen

  Daraus folgt nicht 'mehr Regeln'. Daraus folgt: das Ergebnis darf in
  keinem Feld stehen. Es muss zwischen zwei Feldern ENTSTEHEN.

DER MECHANISMUS: REDUNDANZ, NICHT STRUKTUR

  Zwanzig unabhaengige Felder fangen nichts — sie sind zwanzig
  Gelegenheiten, dasselbe einmal zu behaupten. Acht Felder, von denen
  je zwei zusammenpassen MUESSEN, fangen etwas: der Widerspruch
  entsteht als Mengenvergleich, nicht als Urteil.

  Die Schablone bewertet nichts. Sie stellt acht Fragen und vergleicht
  fuenf Paare der Antworten miteinander. Was dabei herauskommt, wird
  AUSGERECHNET und ist deshalb nicht setzbar.

DIE ACHT FELDER — woher sie kommen

  Keines ist erfunden. Alle acht sind aus Verfahren uebernommen, die
  ausserhalb dieses Programms geprueft wurden. Das ist Absicht: die
  Felder selbst auszudenken waere das Eine-Hand-Problem eine Ebene
  hoeher.

    1 BEHAUPTUNG      Toulmin, Claim
    2 HERKUNFTSART    Admiralty Code Achse 1 (seit den 1940ern),
                      ICD 206 Quellenbeschreibung: Herkunftsart wird
                      getrennt vom Inhalt gefuehrt
    3 GRUNDLAGE       Toulmin, Grounds  (= FrameNetwork rechenweg)
    4 BRUECKE         Toulmin, Warrant  — FrameNetwork hat dafuer
                      KEIN Feld. Toulmin selbst: der Warrant bleibt
                      meistens unausgesprochen. Genau deshalb.
    5 RUECKHALT       Toulmin, Backing
    6 EINSCHRAENKUNG  Toulmin, Qualifier
    7 KIPPKRITERIUM   Toulmin, Rebuttal + Vorabregistrierung
                      (AsPredicted/OSF: das Kriterium steht vor den
                      Daten, sonst zaehlt es nicht)
    8 STAND           (Daten ab, Kriterium festgelegt am) — dasselbe
                      Paar, das R5 schon auf der Zahlenebene prueft

  BEHAUPTUNG ist das einzige Feld ohne Partner. Es hat deshalb im
  Ergebnis kein Gewicht. Das ist kein Versehen: der Freitext ist das,
  was behauptet wird, nicht ein Beleg darueber.

DIE FUENF ABGLEICHREGELN — vor dem ersten Lauf festgelegt

  P1  HERKUNFTSART x GRUNDLAGE
      Wer 'gerechnet' sagt, muss unten bei 'gemessen' ankommen.
      Verfolge GRUNDLAGE transitiv. Kein gemessenes Blatt am Boden
      -> BODENLOS. Damit ist 'Hypothese' ausgerechnet statt erklaert.

  P2  GRUNDLAGE x KIPPKRITERIUM
      Zwei Blaetter, die dieselbe Behauptung stuetzen und dasselbe
      Kippkriterium nennen, haben EINEN Versagenspunkt.
      -> EIN_ZEUGE. Gezaehlt werden Versagenspunkte, nicht Quellen.

  P3  BRUECKE x RUECKHALT
      Bruecke genannt, Rueckhalt leer -> BRUECKE_OHNE_RUECKHALT.
      Gleiche Bruecke bei mehreren Blaettern -> GETEILTE_BRUECKE.

  P4  EINSCHRAENKUNG x EINSCHRAENKUNG DER GRUNDLAGE
      Je Schluessel: der Wert der Behauptung muss unter den Werten
      der Grundlage vorkommen. Schluessel, den die Grundlage nennt
      und die Behauptung nicht -> UEBERDEHNUNG.
      Das ist GRADE indirectness als Mengenvergleich statt als
      selbst gesetztes surrogat=True.

  P5  STAND x STAND DER GRUNDLAGE
      Kippkriterium festgelegt NACH dem Datenstand der Grundlage
      -> NACHTRAEGLICH.

  Leeres Feld ist KEIN Widerspruch, sondern Negativliste.
  'unbekannt != falsch' gilt auch hier.

WAS DIE SCHABLONE NICHT KANN — vorab, nicht nachgereicht

  Dieselbe Hand fuellt alle Blaetter. Wer zweimal passend luegt, kommt
  durch. Die Schablone verschiebt den Aufwand, sie baut keine Wand.
  Wie weit sie ihn verschiebt, wird unten GEMESSEN (mindestluege).
  Und sie kostet: ein fauler Ausfueller, der ueberall dasselbe
  Kippkriterium hinschreibt, wird gemeldet, obwohl nichts vorliegt.
  Auch das wird gemessen — zwei Raten, nie eine Zahl allein.

AUFRUF
  python -m schablone schablone
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from itertools import combinations
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .kern import Art, Eintrag, Netz, Quelle, Status


def de(x: float, nach: int = 1) -> str:
    s = f"{x:,.{nach}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


# ══════════════════════════════════════════════════════════════════════
# Zeit als Intervall — Feld 10
#
# DIE REGEL DAHINTER: was nicht gelesen werden kann, wird NICHT
# stillschweigend uebersprungen. Ein unlesbares Datum ist kein
# "passt schon", es ist eine Auskunft. Dieselbe Nicht-Gleichung wie
# ueberall: nicht geprueft != in Ordnung.
# ══════════════════════════════════════════════════════════════════════

_ISO = __import__("re").compile(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$")
_DE = __import__("re").compile(r"^(?:(\d{1,2})\.)?(\d{1,2})\.(\d{4})$")

_LETZTER = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def _tag(text: Optional[str], ende: bool) -> Optional[str]:
    """Ein Datum in beliebiger Schreibweise auf ein ISO-Datum bringen.

    'ende' entscheidet, wohin eine unvollstaendige Angabe aufgeloest
    wird: '2026' ist als Anfang der 01.01., als Ende der 31.12. Das ist
    kein Urteil, das ist die Bedeutung von 'das Jahr 2026'.

    Gibt None zurueck, wenn die Angabe nicht gelesen werden kann —
    Monatsnamen zum Beispiel. Das ist Absicht: lieber sichtbar stumm
    als unsichtbar geraten."""
    if not text:
        return None
    t = text.strip()
    m = _ISO.match(t)
    if m:
        j, mo, tg = m.group(1), m.group(2), m.group(3)
    else:
        m = _DE.match(t)
        if not m:
            return None
        tg, mo, j = m.group(1), m.group(2), m.group(3)
        mo = f"{int(mo):02d}"
        tg = f"{int(tg):02d}" if tg else None
    if mo is None:
        return f"{j}-12-31" if ende else f"{j}-01-01"
    if tg is None:
        letzter = _LETZTER[int(mo)]
        if int(mo) == 2 and int(j) % 4 == 0 and (
                int(j) % 100 != 0 or int(j) % 400 == 0):
            letzter = 29
        return f"{j}-{mo}-{letzter:02d}" if ende else f"{j}-{mo}-01"
    return f"{j}-{mo}-{tg}"


def spanne(b: "Blatt") -> Optional[Tuple[str, str]]:
    """Der Zeitraum eines Blattes als zwei vergleichbare ISO-Daten."""
    if not b.hat_zeit:
        return None
    von, bis = _tag(b.zeit_von, False), _tag(b.zeit_bis, True)
    if von is None or bis is None:
        return None
    return (von, bis) if von <= bis else (bis, von)


# ══════════════════════════════════════════════════════════════════════
# Feld 2 — die Herkunftsachse (Admiralty 1, ICD 206)
# ══════════════════════════════════════════════════════════════════════

class Herkunft(Enum):
    GEMESSEN  = "gemessen"      # an einem Apparat, zu einem Vorgang
    BERICHTET = "berichtet"     # jemand sagt es
    GERECHNET = "gerechnet"     # aus anderen Blaettern abgeleitet


NACH_ART: Dict[Herkunft, Art] = {
    Herkunft.GEMESSEN:  Art.MESSUNG,
    Herkunft.BERICHTET: Art.AUSSAGE,
    Herkunft.GERECHNET: Art.RECHNUNG,
}


# ══════════════════════════════════════════════════════════════════════
# Das Blatt — acht Felder, KEIN Statusfeld
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Blatt:
    kennung: str
    behauptung: str                                  # 1 Claim
    herkunftsart: Herkunft                           # 2 Admiralty/ICD
    grundlage: Tuple[str, ...] = ()                  # 3 Grounds
    bruecke: str = ""                                # 4 Warrant
    rueckhalt: Tuple[str, ...] = ()                  # 5 Backing
    einschraenkung: Dict[str, str] = field(default_factory=dict)  # 6
    kippkriterium: str = ""                          # 7 Rebuttal/vorab
    stand: Tuple[Optional[str], Optional[str]] = (None, None)     # 8
    # 9  Was diese Ableitung VORAUSSETZT. Leer heisst nicht
    # "setzt nichts voraus", sondern "nicht angegeben" — deshalb
    # zaehlt Leeres nie als Unabhaengigkeit. Fehler 43, eine Ebene
    # tiefer: zwei Rechenwege mit gemeinsamer Praemisse sind EIN
    # Rechenweg, und ohne dieses Feld kann das keine Regel sehen.
    annahmen: Tuple[str, ...] = ()                                # 9
    # 10  WELCHEN ZEITRAUM die Aussage abdeckt — (von, bis), als Datum.
    #
    # Warum ein eigenes Feld und nicht einschraenkung["wann"]: gemessen
    # am 29.09.2026 auf sechs modellgefuellten Boegen. Dort stand unter
    # "wann" mal "2026", mal "Betriebsjahr 2026", mal "Kalenderjahr
    # 2026", mal "31.12.2026". P4 vergleicht Zeichenketten — derselbe
    # Zeitraum in vier Schreibweisen ergab drei Befunde, von denen zwei
    # blosse Schreibvarianten waren. Zeit als Text ist nicht
    # vergleichbar. Zeit als Intervall ist es.
    #
    # Und deshalb steht hier NICHT dasselbe wie in stand: stand[0] ist
    # EIN Datum ("Daten ab"), zeitraum sind ZWEI ("von" bis "bis").
    # Sechs von sechs Modellen haben stand als Zeitraum gelesen und
    # ["2026-01-01","2026-12-31"] hineingeschrieben. P5 feuerte
    # daraufhin 28 mal auf 46 Befunde. Das Feld war nicht falsch
    # benutzt, es war falsch gebaut.
    zeitraum: Tuple[Optional[str], Optional[str]] = (None, None)  # 10

    @property
    def daten_ab(self) -> Optional[str]:
        return self.stand[0]

    @property
    def kipp_am(self) -> Optional[str]:
        return self.stand[1]

    @property
    def zeit_von(self) -> Optional[str]:
        return self.zeitraum[0]

    @property
    def zeit_bis(self) -> Optional[str]:
        return self.zeitraum[1]

    @property
    def hat_zeit(self) -> bool:
        return bool(self.zeitraum[0] and self.zeitraum[1])

    @property
    def ist_zeitpunkt(self) -> bool:
        """Eine Ablesung am 31.12. ist ein PUNKT. Ein Betriebsjahr ist
        eine SPANNE. Wer aus dem Punkt die Spanne macht, setzt etwas
        voraus, das nirgends steht."""
        return self.hat_zeit and self.zeitraum[0] == self.zeitraum[1]


FELDER = ("behauptung", "herkunftsart", "grundlage", "bruecke",
          "rueckhalt", "einschraenkung", "kippkriterium", "stand",
          "annahmen", "zeitraum")

OHNE_PARTNER = ("behauptung",)

# Marke fuer ein Blatt ohne benanntes Kippkriterium — sichtbar, aber
# nie als eigener Versagenspunkt gezaehlt.
UNBESTIMMT = "#unbestimmt"


class Art_W(Enum):
    BODENLOS              = ("P1", "gerechnet, aber unten keine Messung")
    EIN_ZEUGE             = ("P2", "gleiches Kippkriterium — ein Zeuge")
    BRUECKE_OHNE_RUECKHALT = ("P3", "Bruecke genannt, Rueckhalt leer")
    GETEILTE_BRUECKE      = ("P3", "gleiche Bruecke, gemeinsamer Schritt")
    UEBERDEHNUNG          = ("P4", "Behauptung reicht weiter als Grundlage")
    NACHTRAEGLICH         = ("P5", "Kriterium nach den Daten festgelegt")
    GETEILTE_ANNAHME      = ("P6", "zwei Ableitungen, eine Praemisse")
    ZEITLUECKE            = ("P7", "Behauptung reicht weiter als der "
                                   "belegte Zeitraum")
    ZEITPUNKT             = ("P8", "Punktmessung traegt eine Spanne")
    UNGETRAGENER_ZWEIG    = ("P1b", "ein Zweig endet ohne Messung und "
                                    "ohne Urheber")

    @property
    def paar(self) -> str:
        return self.value[0]

    @property
    def text(self) -> str:
        return self.value[1]


@dataclass(frozen=True)
class Widerspruch:
    art: Art_W
    betrifft: Tuple[str, ...]
    warum: str


@dataclass
class Satz:
    """Ein Bogen: mehrere Blaetter, eines davon die Behauptung."""
    blaetter: Dict[str, Blatt] = field(default_factory=dict)

    def legen(self, b: Blatt) -> Blatt:
        self.blaetter[b.kennung] = b
        return b

    def boden(self, kennung: str, gesehen: Optional[Set[str]] = None
              ) -> Set[str]:
        """Blaetter am unteren Ende der GRUNDLAGE-Kette."""
        gesehen = gesehen or set()
        if kennung in gesehen:
            return set()
        gesehen.add(kennung)
        b = self.blaetter.get(kennung)
        if b is None or not b.grundlage:
            return {kennung}
        out: Set[str] = set()
        for g in b.grundlage:
            out |= self.boden(g, gesehen)
        return out

    def unbekannt(self, kennung: str) -> Set[str]:
        """Blaetter, die als GRUNDLAGE genannt sind, aber im Bogen fehlen.

        FEHLER 36: die erste Fassung filterte sie in P1 stillschweigend
        weg — 'Kette endet bei —', obwohl sie bei 'GIBTESNICHT' endete.
        Dieselbe Klasse wie kern.#unbekannt vor der Haertung, nur eine
        Ebene hoeher: nicht gefiltert, sondern BENANNT."""
        out: Set[str] = set()
        for k in self.traeger(kennung):
            b = self.blaetter.get(k)
            if b:
                out |= {g for g in b.grundlage if g not in self.blaetter}
        return out

    def zyklen(self, kennung: str) -> List[Tuple[str, ...]]:
        """Kreise in der GRUNDLAGE-Kette, als Weg zurueckgegeben.

        FEHLER 37: boden() gab bei einem Kreis die leere Menge zurueck.
        P1 schlug zwar an, nannte aber '—' als Boden. Richtiges Ergebnis,
        unbrauchbare Begruendung."""
        gefunden: List[Tuple[str, ...]] = []
        def lauf(k: str, weg: Tuple[str, ...]) -> None:
            if k in weg:
                kreis = weg[weg.index(k):] + (k,)
                if kreis not in gefunden:
                    gefunden.append(kreis)
                return
            b = self.blaetter.get(k)
            if b is None:
                return
            for g in b.grundlage:
                lauf(g, weg + (k,))
        lauf(kennung, ())
        return gefunden

    def traeger(self, kennung: str, gesehen: Optional[Set[str]] = None
                ) -> Set[str]:
        """Alle Blaetter auf dem Weg nach unten, das eigene eingeschlossen."""
        gesehen = gesehen or set()
        if kennung in gesehen:
            return set()
        gesehen.add(kennung)
        out = {kennung}
        b = self.blaetter.get(kennung)
        if b:
            for g in b.grundlage:
                out |= self.traeger(g, gesehen)
        return out


# ══════════════════════════════════════════════════════════════════════
# Der Abgleich — fuenf Mengenvergleiche, kein Urteil
# ══════════════════════════════════════════════════════════════════════

def abgleichen(s: Satz, kennung: str) -> List[Widerspruch]:
    w: List[Widerspruch] = []
    b = s.blaetter[kennung]
    stuetzen = [s.blaetter[g] for g in b.grundlage if g in s.blaetter]

    # ── P1  HERKUNFTSART x GRUNDLAGE ─────────────────────────────────
    # FEHLER 22, beim Angriff auf den eigenen Entwurf gefunden: die
    # erste Fassung prueste nur GERECHNET. Ein Zug im Luegenmenue
    # ('sag berichtet statt gerechnet') raeumte den Widerspruch, ohne
    # dass irgendwo ein Urheber stehen musste. Die Regel war also nur
    # halb da. Symmetrisch: WER NICHT SELBST GEMESSEN HAT, MUSS UNTEN
    # ankommen — bei einer Messung oder bei einem benannten Urheber.
    # Auf ehrlicher Arbeit aendert das nichts (dort steht beides).
    if b.herkunftsart is not Herkunft.GEMESSEN:
        boden = [s.blaetter[k] for k in s.boden(kennung) if k in s.blaetter]
        fest = [x.kennung for x in boden
                if x.herkunftsart is Herkunft.GEMESSEN
                or (x.herkunftsart is Herkunft.BERICHTET and x.rueckhalt)]
        if not fest:
            teile = []
            unten = sorted(x.kennung for x in boden)
            if unten:
                teile.append(f"endet bei {', '.join(unten)} — dort steht "
                             f"weder eine Messung noch ein benannter Urheber")
            for kreis in s.zyklen(kennung):
                teile.append(f"laeuft im Kreis {' -> '.join(kreis)}")
            unb = sorted(s.unbekannt(kennung))
            if unb:
                teile.append(f"nennt Blaetter, die im Bogen fehlen: "
                             f"{', '.join(unb)}")
            if not teile:
                teile.append("hat gar keine Grundlage")
            w.append(Widerspruch(
                Art_W.BODENLOS, (kennung,),
                f"{b.herkunftsart.value}, die Kette "
                + "; ".join(teile) + ". Das ist eine Hypothese."))

    # ── P1b  JEDER ZWEIG EINZELN ─────────────────────────────────────
    # FEHLER 53, von einem Lauf gefunden, der das Werkzeug benutzt hat.
    # P1 fragt, ob IRGENDEINE Wurzel traegt — ein ODER ueber die Zweige.
    # Damit macht eine einzige echte Messung alle uebrigen Zweige stumm.
    #
    # Nachgestellt: ein unbelegtes Berichtsblatt allein -> BODENLOS.
    # Dasselbe Blatt plus einer echten Messung -> kein Befund. DER
    # VOLLSTAENDIGERE BOGEN ERZEUGT WENIGER BEANSTANDUNG. Wer sauber
    # arbeitet und alles einträgt, wird dafuer belohnt, dass die Regel
    # schweigt. Das ist derselbe verkehrte Anreiz wie bei Fehler 50.
    #
    # P1 bleibt unveraendert (keine einzige Wurzel traegt). P1b benennt
    # zusaetzlich jeden EINZELNEN Zweig, der nicht unten ankommt.
    def _traegt_blatt(u: Optional[Blatt]) -> bool:
        return bool(u is not None and (
            u.herkunftsart is Herkunft.GEMESSEN
            or (u.herkunftsart is Herkunft.BERICHTET and u.rueckhalt)))

    for x in stuetzen:
        wurzeln = sorted(s.boden(x.kennung))
        offen = [k2 for k2 in wurzeln
                 if not _traegt_blatt(s.blaetter.get(k2))]
        if offen and len(offen) == len(wurzeln):
            w.append(Widerspruch(
                Art_W.UNGETRAGENER_ZWEIG, (x.kennung,),
                f"der Zweig ueber {x.kennung} endet bei "
                f"{', '.join(offen)} — dort steht weder eine Messung "
                f"noch ein benannter Urheber. Andere Zweige tragen, "
                f"dieser nicht"))

    # ── P2  GRUNDLAGE x KIPPKRITERIUM ────────────────────────────────
    nach_kipp: Dict[str, List[str]] = {}
    for x in stuetzen:
        if x.kippkriterium:
            nach_kipp.setdefault(x.kippkriterium.strip().lower(),
                                 []).append(x.kennung)
    for kipp, wer in sorted(nach_kipp.items()):
        if len(wer) > 1:
            w.append(Widerspruch(
                Art_W.EIN_ZEUGE, tuple(sorted(wer)),
                f"{len(wer)} Blaetter, ein Versagenspunkt: "
                f"„{kipp}“ — sie fallen gemeinsam"))

    # ── P3  BRUECKE x RUECKHALT ──────────────────────────────────────
    if b.bruecke and not b.rueckhalt:
        w.append(Widerspruch(
            Art_W.BRUECKE_OHNE_RUECKHALT, (kennung,),
            f"Bruecke „{b.bruecke}“ traegt den Schritt von der "
            f"Grundlage zur Behauptung — ohne Rueckhalt traegt sie nichts"))
    nach_br: Dict[str, List[str]] = {}
    for x in stuetzen:
        if x.bruecke:
            nach_br.setdefault(x.bruecke.strip().lower(), []).append(x.kennung)
    for br, wer in sorted(nach_br.items()):
        if len(wer) > 1:
            w.append(Widerspruch(
                Art_W.GETEILTE_BRUECKE, tuple(sorted(wer)),
                f"{len(wer)} Blaetter gehen ueber dieselbe Bruecke "
                f"„{br}“"))

    # ── P4  EINSCHRAENKUNG x EINSCHRAENKUNG DER GRUNDLAGE ────────────
    unten_schl: Dict[str, Set[str]] = {}
    for x in stuetzen:
        for k, v in x.einschraenkung.items():
            unten_schl.setdefault(k, set()).add(v)
    for k, werte in sorted(unten_schl.items()):
        meiner = b.einschraenkung.get(k)
        if meiner is None:
            w.append(Widerspruch(
                Art_W.UEBERDEHNUNG, (kennung,),
                f"Grundlage nennt „{k}“ ({'/'.join(sorted(werte))}), "
                f"die Behauptung nennt es nicht — sie gilt damit unbegrenzt"))
        elif meiner not in werte:
            w.append(Widerspruch(
                Art_W.UEBERDEHNUNG, (kennung,),
                f"„{k}“: Behauptung {meiner}, Grundlage "
                f"{'/'.join(sorted(werte))}"))

    # ── P6  ANNAHMEN x ANNAHMEN DER GRUNDLAGE ────────────────────────
    # Zwei Rechenwege, die dieselbe Praemisse benutzen, sind EIN
    # Rechenweg. Sie koennen einig sein und beide falsch. Das ist
    # dieselbe Nicht-Gleichung wie EIN_ZEUGE, nur bei Ableitungen
    # statt bei Quellen — und die Idee stand schon in
    # kern.unabhaengige_pfade(), nur eine Ebene zu hoch.
    nach_ann: Dict[str, List[str]] = {}
    for x in stuetzen:
        for ann in x.annahmen:
            nach_ann.setdefault(ann.strip().lower(), []).append(x.kennung)
    for ann, wer in sorted(nach_ann.items()):
        if len(set(wer)) > 1:
            w.append(Widerspruch(
                Art_W.GETEILTE_ANNAHME, tuple(sorted(set(wer))),
                f"{len(set(wer))} Ableitungen setzen dasselbe voraus: "
                f"„{ann}“ — sie sind nicht unabhaengig"))

    # ── P5  KIPPKRITERIUM x ZEITRAUM ─────────────────────────────────
    # UMGEBAUT am 29.09.2026, nachdem die Regel auf sechs echten,
    # modellgefuellten Boegen 28 mal gefeuert hat und kein einziges Mal
    # zu Recht. Die alte Fassung verglich stand[1] > stand[0]. Wer
    # stand als Zeitraum liest — und das taten sechs von sechs —
    # schreibt bei voellig ehrlicher Arbeit ['2026-01-01','2026-12-31']
    # hinein, und die Regel meldet Vorabregistrierungsbetrug.
    #
    # Das war kein Modellfehler. Zwei Daten nebeneinander, das zweite
    # spaeter als das erste, SIND ein Zeitraum — in jedem Formular der
    # Welt. Die Regel hat bestraft, was die Form nahegelegt hat.
    #
    # Jetzt braucht P5 das ausdrueckliche Feld zeitraum. Fehlt es,
    # schweigt die Regel und sagt in der Negativliste, dass sie
    # schweigt. nicht geprueft != in Ordnung.
    for x in stuetzen + [b]:
        if not x.kippkriterium.strip() or not x.kipp_am:
            continue
        sp = spanne(x)
        if sp is None:
            continue
        if x.kipp_am > sp[1]:
            w.append(Widerspruch(
                Art_W.NACHTRAEGLICH, (x.kennung,),
                f"Kriterium am {x.kipp_am} festgelegt, die Daten enden "
                f"am {sp[1]} — nach dem Sehen ist kein Kriterium"))

    # ── P7  ZEITRAUM x ZEITRAUM DER GRUNDLAGE ────────────────────────
    # Das Gegenstueck zu P4 auf der Zeitachse. P4 fragt WOFUER die
    # Grundlage gilt, P7 fragt WANN. Beides war bisher in einem
    # Freitextfeld ("wann": "Betriebsjahr 2026") und damit nur als
    # Zeichenkette vergleichbar — gemessen: von drei Treffern waren
    # zwei blosse Schreibvarianten desselben Jahres.
    #
    # Falle F5 des Fuenf-Arm-Versuchs, 10 von 10 Laeufe gefallen.
    # FEHLER 50, von einem Lauf gefunden, der das Werkzeug benutzt hat:
    # die erste Fassung nahm min/max ueber ALLE Stuetzen. Ein Blatt, das
    # gar nichts gemessen hat und einfach behauptet, es gelte fuers
    # ganze Jahr, schloss damit die Luecke, die die Punktmessungen
    # offenliessen. Nachgestellt und bestaetigt: zwei Ablesungen am
    # 31.12. -> ZEITLUECKE. Ein unbelegtes Berichtsblatt dazu -> still.
    #
    # EIN UNBELEGTES DOKUMENT HAT EINEN BEFUND ENTFERNT. Das ist die
    # falsche Richtung: mehr Papier darf nie weniger Beanstandung
    # ergeben. Dieselbe Klasse wie der BODENLOS-Oder-Zweig.
    #
    # Jetzt traegt eine Stuetze den Zeitraum nur, wenn sie selbst unten
    # ankommt — bei einer Messung oder einem benannten Urheber. Das ist
    # genau die Pruefung aus P1, hier wiederverwendet statt neu erfunden.
    def _traegt(x: Blatt) -> bool:
        if x.herkunftsart is Herkunft.GEMESSEN:
            return True
        for k2 in s.boden(x.kennung):
            u = s.blaetter.get(k2)
            if u is None:
                continue
            if (u.herkunftsart is Herkunft.GEMESSEN
                    or (u.herkunftsart is Herkunft.BERICHTET and u.rueckhalt)):
                return True
        return False

    mein = spanne(b)
    belegt = [(x.kennung, spanne(x)) for x in stuetzen
              if spanne(x) and _traegt(x)]
    if mein and belegt:
        frueh = min(s2[0] for _, s2 in belegt)
        spaet = max(s2[1] for _, s2 in belegt)
        teile = []
        if mein[0] < frueh:
            teile.append(f"beginnt am {mein[0]}, der frueheste Beleg "
                         f"erst am {frueh}")
        if mein[1] > spaet:
            teile.append(f"reicht bis {mein[1]}, der letzte Beleg endet "
                         f"am {spaet}")
        if teile:
            w.append(Widerspruch(
                Art_W.ZEITLUECKE, (kennung,),
                "die Behauptung " + " und ".join(teile)))

    # ── P8  ZEITPUNKT x ZEITRAUM ─────────────────────────────────────
    # Eine Zaehlerablesung am 31.12. ist ein PUNKT. "Die Jahres-
    # arbeitszahl 2026" ist eine SPANNE. Aus dem Punkt die Spanne zu
    # machen setzt voraus, dass die Anlage die Spanne ueber gelaufen
    # ist — und genau das steht nirgends.
    #
    # Falle F4 des Versuchs, ebenfalls 10 von 10 gefallen. KEINE
    # SPERRE: eine Punktmessung darf eine Spanne tragen, es ist der
    # Normalfall der Zaehlerablesung. Falsch ist nur, dass die
    # Voraussetzung lautlos bleibt. Deshalb geht P8 in die Auskunft,
    # nicht in den Strang.
    if mein and mein[0] != mein[1]:
        punkte = sorted(x.kennung for x in stuetzen if x.ist_zeitpunkt)
        if punkte:
            w.append(Widerspruch(
                Art_W.ZEITPUNKT, tuple(punkte),
                f"{len(punkte)} Beleg(e) sind Punktangaben, die "
                f"Behauptung deckt {mein[0]} bis {mein[1]} ab — dass "
                f"dazwischen durchgelaufen wurde, steht nirgends"))
    return w


def negativliste(s: Satz, kennung: str) -> List[str]:
    """Leere Felder. Kein Widerspruch — eine Auskunft darueber, worauf
    NICHT geprueft werden konnte."""
    b = s.blaetter[kennung]
    leer: List[str] = []
    if not b.grundlage and b.herkunftsart is not Herkunft.GEMESSEN:
        leer.append("GRUNDLAGE leer — P1 und P4 laufen ins Leere")
    if not b.bruecke:
        leer.append("BRUECKE leer — der Schritt von Grundlage zu "
                    "Behauptung ist nicht benannt (P3 stumm)")
    if not b.rueckhalt:
        leer.append("RUECKHALT leer")
    if not b.einschraenkung:
        leer.append("EINSCHRAENKUNG leer — die Behauptung gilt unbegrenzt")
    if not b.kippkriterium:
        leer.append("KIPPKRITERIUM leer — P2 kann keine Zeugen zaehlen")
    if b.kipp_am is None:
        leer.append("STAND unvollstaendig — kein Datum der Festlegung, "
                    "P5 stumm")
    if not b.hat_zeit:
        leer.append("ZEITRAUM leer — WANN die Aussage gilt, steht "
                    "nirgends. P5, P7 und P8 stumm. Leer heisst nicht "
                    "„gilt immer“, sondern „nicht angegeben“")
    elif spanne(b) is None:
        leer.append(f"ZEITRAUM {b.zeitraum!r} nicht lesbar — erlaubt sind "
                    f"JJJJ, JJJJ-MM, JJJJ-MM-TT, TT.MM.JJJJ. "
                    f"P5, P7 und P8 stumm")
    if b.herkunftsart is Herkunft.GERECHNET and not b.annahmen:
        leer.append("ANNAHMEN leer — eine Ableitung ohne erklaerte "
                    "Voraussetzung kann nicht als unabhaengig gelten "
                    "(P6 stumm)")
    return leer


def negativliste_traeger(s: Satz, ziel: str) -> Dict[str, List[str]]:
    """Dieselbe Auskunft, aber ueber JEDES tragende Blatt ausser dem Ziel.

    FEHLER 44. Ein Werkzeug, das nur das Zielblatt auf leere Felder
    ansieht, schweigt genau dort, wo eine uebernommene Aussage ihre
    Herkunft verschweigt. Kein Urteil — eine Auskunft."""
    out: Dict[str, List[str]] = {}
    for k in sorted(s.traeger(ziel) - {ziel}):
        if k not in s.blaetter:
            continue
        leer = negativliste(s, k)
        if leer:
            out[k] = leer
    return out


def waisen(s: Satz, ziel: str) -> Set[str]:
    """Blaetter im Bogen, die das Zielblatt ueber keine grundlage-Kette
    erreicht.

    FEHLER 45. Sie gehen nicht ins Netz (nach_netz laeuft ueber
    traeger()), keine Regel sieht sie, kein Bericht nannte sie. Ein
    Bogen konnte die einzigen Messungen des Falls enthalten, ohne dass
    irgendwo stand, dass sie nichts stuetzen.

    KEINE SPERRE. Es ist oft richtig, dass eine Unterlage die
    Behauptung nicht traegt — Hintergrundmaterial tut das nie. Falsch
    ist nur, dass es lautlos geschieht."""
    return set(s.blaetter) - s.traeger(ziel)


# ══════════════════════════════════════════════════════════════════════
# Die Uebergabe an FrameNetwork — nichts wird gesetzt, alles gerechnet
# ══════════════════════════════════════════════════════════════════════

def versagenspunkte(s: Satz, kennung: str) -> Dict[str, List[str]]:
    """Was statt der WURZELN gezaehlt werden sollte. Wurzeln sind
    deklariert (und wurden im Angriff verschwiegen); Versagenspunkte
    muessen ausgefuellt werden, weil P2 sonst leer laeuft.

    Das eigene Blatt zaehlt NICHT mit: der eigene Versagenspunkt ist
    kein Beleg ueber die eigene Unabhaengigkeit."""
    out: Dict[str, List[str]] = {}
    for k in sorted(s.traeger(kennung) - {kennung}):
        b = s.blaetter.get(k)
        if b is None:
            continue
        # FEHLER 43, vom ersten Lauf mit fremder Modellarbeit gefunden:
        # die erste Fassung gab jedem Blatt OHNE Kippkriterium einen
        # EIGENEN Schluessel. Damit zaehlten zwei Blaetter, die beide
        # nichts angeben, als ZWEI unabhaengige Versagenspunkte — die
        # unbestimmte Angabe erzeugte scheinbare Unabhaengigkeit.
        #
        # Das ist dieselbe Klasse wie kern.#unbekannt vor der Haertung,
        # eine Ebene hoeher. Und es ist die gefaehrliche Richtung: wer
        # das Feld korrekt leer laesst, bekam das PERMISSIVSTE Ergebnis.
        #
        # Jetzt: alle unbestimmten fallen in EINEN Topf, und der zaehlt
        # nicht als Versagenspunkt. unbekannt != unabhaengig.
        schluessel = b.kippkriterium.strip().lower() or UNBESTIMMT
        out.setdefault(schluessel, []).append(k)
    return out


def bestimmte(vp: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Nur die Versagenspunkte, die wirklich benannt sind."""
    return {k: v for k, v in vp.items() if k != UNBESTIMMT}


def _reichweite(s: Satz, kennung: str) -> Tuple[str, ...]:
    """Die UEBERDEHNUNGEN des Zielblattes, als Text fuer das Tor.

    FEHLER 46. EINE Definition, nicht zwei: P4 rechnet, das Tor liest.
    Zwei Definitionen derselben Sache in einem Lauf waren Fehler 35."""
    return tuple(w.warum for w in abgleichen(s, kennung)
                 if w.art is Art_W.UEBERDEHNUNG and kennung in w.betrifft)


def _zeitluecke(s: Satz, kennung: str) -> Tuple[str, ...]:
    """Die ZEITLUECKEN des Zielblattes, als Text fuer das Tor.

    NUR P7. P8 (Punktmessung traegt Spanne) bleibt draussen: es ist der
    Normalfall jeder Zaehlerablesung und darf nichts sperren. Es geht in
    die Auskunft und in verdacht.erheben() — dort fordert es Arbeit an,
    statt den Weg zu versperren.

    Dieselbe Bauart wie _reichweite: EINE Definition. P7 rechnet, das
    Tor liest. Fehler 46 war genau die Naht, die hier nicht wieder
    aufgehen darf."""
    return tuple(w.warum for w in abgleichen(s, kennung)
                 if w.art is Art_W.ZEITLUECKE and kennung in w.betrifft)


def nach_netz(s: Satz, kennung: str, text: str, heute: str) -> Netz:
    """Blaetter -> Quellen. art und uebernommen_aus werden aus der Form
    ABGELEITET, nicht uebernommen. Genau die beiden Felder, durch die
    Angriff 1 und Angriff 2 gelaufen sind."""
    n = Netz()
    for k in sorted(s.traeger(kennung)):
        b = s.blaetter.get(k)
        if b is None:
            # FEHLER 39, zweite Fundstelle derselben Klasse: ein nur
            # GENANNTES Blatt bekommt KEINE Quelle. Es bleibt aber in
            # uebernommen_aus stehen — damit macht kern daraus von
            # selbst eine Wurzel mit der Marke #unbekannt, und
            # unabhaengige_pfade() zaehlt sie nicht. Die beiden Ebenen
            # behandeln den Fall also gleich, ohne dass hier eine
            # zweite Regel dafuer noetig waere.
            continue
        n.quelle(Quelle(kennung=b.kennung, was=b.behauptung[:60],
                        art=NACH_ART[b.herkunftsart],
                        uebernommen_aus=tuple(b.grundlage),
                        vorgang=(f"{b.kennung}@{b.daten_ab}"
                                 if b.herkunftsart is Herkunft.GEMESSEN
                                 else None)))
    b = s.blaetter[kennung]
    n.aufnehmen(Eintrag(kennung="E", text=text, status=Status.VERMERK,
                        eingang=heute, seit=heute,
                        quellen=tuple(b.grundlage) or (kennung,),
                        geltungsbereich=dict(b.einschraenkung),
                        reichweite=_reichweite(s, kennung),
                        zeitluecke=_zeitluecke(s, kennung),
                        zeit_pruefbar=spanne(b) is not None))
    return n


# ══════════════════════════════════════════════════════════════════════
# Gegenprobe 1 — wie viele passende Luegen raeumen den Widerspruch weg
# ══════════════════════════════════════════════════════════════════════

# Vorab festgelegtes Luegenmenue. Nur diese Werte, keine anderen.
MENUE: Dict[str, object] = {
    "herkunftsart":   Herkunft.BERICHTET,
    "kippkriterium":  "<anderer, erfundener Versagenspunkt>",
    "bruecke":        "<andere, erfundene Bruecke>",
    "rueckhalt":      ("<erfundener Rueckhalt>",),
    "einschraenkung": "<auf die Behauptung ausgeweitet>",
    "stand":          "<Kriterium zurueckdatiert>",
    "zeitraum":       "<auf den Zeitraum der Behauptung ausgeweitet>",
    # FEHLER 52, von einem Lauf gefunden, der das Werkzeug benutzt hat:
    # dieses Feld fehlte. Damit war JEDER P6-Befund mit keinem Zug des
    # Menues raeumbar, und mindestluege() meldete "nicht raeumbar" —
    # was wie Robustheit aussieht und "das Menue kennt das Feld nicht"
    # heisst. Eine Zahl, die das System UEBER SICH SELBST ausgibt.
    "annahmen":       "<andere, erfundene Voraussetzung>",
}

# Wo die Luege nachpruefbar ist. Das ist der eigentliche Ertrag der
# Schablone: nicht die Zahl der noetigen Luegen, sondern wohin sie
# fallen. Eine Luege INNEN kennt nur das System; eine Luege AUSSEN
# behauptet etwas ueber die Welt und kann dort scheitern.
WO: Dict[str, str] = {
    "kippkriterium":  "innen (bis jemand das Kriterium anwendet)",
    "bruecke":        "innen",
    "rueckhalt":      "aussen — ein benanntes Dokument gibt es oder nicht",
    "einschraenkung": "aussen — wo und wann gemessen wurde",
    "stand":          "aussen — Datum, ausserhalb registrierbar",
    "zeitraum":       "aussen — welchen Zeitraum ein Beleg abdeckt, "
                      "steht im Beleg",
    "annahmen":       "innen (bis jemand die Voraussetzung nachrechnet)",
}


def wo_liegt(s: Satz, blatt: str, feld: str) -> str:
    """HERKUNFTSART haengt vom Blatt ab, nicht vom Feldnamen:
    'gerechnet' behauptet nichts ueber die Welt. 'berichtet' behauptet,
    dass ein BENANNTER Urheber das gesagt hat — und P1 erzwingt den
    Namen. Dieselbe Feldaenderung ist also einmal innen und einmal
    aussen. Das ist eine Eigenschaft der Lage, keine Schwelle."""
    if feld != "herkunftsart":
        return WO[feld]
    b = s.blaetter[blatt]
    if b.rueckhalt:
        return (f"aussen — behauptet, dass {', '.join(b.rueckhalt)} "
                f"das sagt")
    return "innen"


def _luegen(s: Satz, kennung: str, zuege: Sequence[Tuple[str, str]]) -> Satz:
    neu = Satz({k: v for k, v in s.blaetter.items()})
    ziel = s.blaetter[kennung]
    zaehler = 0
    for blatt_k, feld in zuege:
        if blatt_k not in neu.blaetter:
            continue
        b = neu.blaetter[blatt_k]
        if feld == "einschraenkung":
            neu.blaetter[blatt_k] = replace(
                b, einschraenkung=dict(ziel.einschraenkung))
        elif feld == "zeitraum":
            neu.blaetter[blatt_k] = replace(b, zeitraum=ziel.zeitraum)
        elif feld == "stand":
            neu.blaetter[blatt_k] = replace(b, stand=(b.daten_ab,
                                                      b.daten_ab))
        elif feld == "annahmen":
            zaehler += 1
            neu.blaetter[blatt_k] = replace(
                b, annahmen=(f"{MENUE['annahmen']} {zaehler}",))
        elif feld == "kippkriterium":
            zaehler += 1
            neu.blaetter[blatt_k] = replace(
                b, kippkriterium=f"{MENUE['kippkriterium']} {zaehler}")
        else:
            neu.blaetter[blatt_k] = replace(b, **{feld: MENUE[feld]})
    return neu


def mindestluege(s: Satz, kennung: str, tiefe: int = 3
                 ) -> Optional[Tuple[int, Tuple[Tuple[str, str], ...]]]:
    """Kleinste Menge (Blatt, Feld), die ALLE Widersprueche raeumt.
    Gesucht wird erschoepfend bis zur angegebenen Tiefe."""
    if not abgleichen(s, kennung):
        return (0, ())
    # FEHLER 38, vom ersten echten Eingabebogen gefunden: traeger()
    # liefert auch Kennungen, die nur GENANNT sind. _luegen() schlug
    # darauf mit KeyError fehl. Ein Blatt, das es nicht gibt, kann man
    # nicht faelschen — es steht als Hinweis im Bogen und faellt P1 zur
    # Last, hier hat es nichts zu suchen.
    kandidaten = [(k, f) for k in sorted(s.traeger(kennung))
                  if k in s.blaetter for f in MENUE]
    for groesse in range(1, tiefe + 1):
        for zug in combinations(kandidaten, groesse):
            if not abgleichen(_luegen(s, kennung, zug), kennung):
                return (groesse, zug)
    return None


# ══════════════════════════════════════════════════════════════════════
# Die vier Angriffe, die im Tor durchgingen
# ══════════════════════════════════════════════════════════════════════

def angriff_1() -> Tuple[str, Satz, str]:
    """sonde Frage 1-3: Vermutung als RECHNUNG eingetragen. Tor: frei."""
    s = Satz()
    s.legen(Blatt("H1", "Ertrag steigt um 12 %", Herkunft.GERECHNET,
                  bruecke="das Modell bildet den Ertrag ab",
                  rueckhalt=("Modellhandbuch",),
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Modell M ueberschaetzt den Ertrag",
                  stand=("2026-09-01", "2026-09-01")))
    return ("ANGRIFF 1 — Vermutung als Rechnung", s, "H1")


def angriff_2() -> Tuple[str, Satz, str]:
    """sonde Frage 6-7: zwei Quellen, Herkunft verschwiegen. Tor: S3."""
    s = Satz()
    s.legen(Blatt("M1", "Zaehlerstand Anlage A", Herkunft.GEMESSEN,
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Zaehler A ist dejustiert",
                  stand=("2026-08-31", "2026-08-01")))
    s.legen(Blatt("H1", "Ertrag steigt um 12 %", Herkunft.GERECHNET,
                  grundlage=("M1",),
                  bruecke="Trendfortschreibung aus Modell M",
                  rueckhalt=("Modellhandbuch",),
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Modell M ueberschaetzt den Ertrag",
                  stand=("2026-08-31", "2026-08-01")))
    s.legen(Blatt("F1", "Ertrag steigt um 12 %", Herkunft.GERECHNET,
                  grundlage=("M1",),          # Herkunft aus H1 verschwiegen
                  bruecke="Trendfortschreibung aus Modell M",
                  rueckhalt=("Modellhandbuch",),
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Modell M ueberschaetzt den Ertrag",
                  stand=("2026-08-31", "2026-08-01")))
    s.legen(Blatt("E3", "Der Ertrag steigt 2026 um 12 %.",
                  Herkunft.GERECHNET, grundlage=("H1", "F1"),
                  bruecke="zwei unabhaengige Herleitungen stimmen ueberein",
                  rueckhalt=("Konvergenzargument",),
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="beide Herleitungen teilen einen Fehler",
                  stand=("2026-08-31", "2026-08-01")))
    return ("ANGRIFF 2 — zwei Zeugen, eine Wurzel (Tor gab S3 frei)",
            s, "E3")


def angriff_3() -> Tuple[str, Satz, str]:
    """Ueberdehnung. Im Tor kein Feld dafuer; in guete nur als selbst
    gesetztes surrogat=True."""
    s = Satz()
    s.legen(Blatt("M2", "Laborwert an Pruefstand P", Herkunft.GEMESSEN,
                  einschraenkung={"was": "Labor", "wann": "2024",
                                  "wo": "Pruefstand P"},
                  kippkriterium="Pruefstand P weicht vom Feld ab",
                  stand=("2024-06-30", "2024-01-10")))
    s.legen(Blatt("A1", "Der Wert gilt fuer alle Anlagen im Feld.",
                  Herkunft.GERECHNET, grundlage=("M2",),
                  bruecke="Pruefstand bildet das Feld ab",
                  rueckhalt=("Norm 1234",),
                  einschraenkung={"was": "Feld"},
                  kippkriterium="Pruefstand bildet das Feld nicht ab",
                  stand=("2024-06-30", "2024-01-10")))
    return ("ANGRIFF 3 — Ueberdehnung (Labor -> Feld)", s, "A1")


def angriff_4() -> Tuple[str, Satz, str]:
    """Kriterium nach den Daten. R5 prueft das fuer Zahlen, fuer die
    Begruendung gab es bisher kein Feld."""
    s = Satz()
    s.legen(Blatt("M3", "Messreihe", Herkunft.GEMESSEN,
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Messreihe unvollstaendig",
                  stand=("2026-06-30", "2026-01-05")))
    s.legen(Blatt("A2", "Die Massnahme wirkt.", Herkunft.GERECHNET,
                  grundlage=("M3",),
                  bruecke="Anstieg nach der Massnahme zeigt Wirkung",
                  rueckhalt=("Vorher-Nachher-Vergleich",),
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="der Anstieg hat eine andere Ursache",
                  stand=("2026-06-30", "2026-08-20")))   # NACH den Daten
    return ("ANGRIFF 4 — Kriterium nach den Daten", s, "A2")


def sauber() -> Tuple[str, Satz, str]:
    """Gegenprobe: ehrliche, korrekte Arbeit. Wer hier meldet, bestraft
    genau das, was er belohnen soll."""
    s = Satz()
    s.legen(Blatt("M4", "Zaehler Anlage A", Herkunft.GEMESSEN,
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Zaehler A ist dejustiert",
                  stand=("2026-08-31", "2026-01-10")))
    s.legen(Blatt("M5", "Wechselrichterprotokoll Anlage B",
                  Herkunft.GEMESSEN,
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="Protokoll B zaehlt Abregelung nicht mit",
                  stand=("2026-08-31", "2026-01-10")))
    s.legen(Blatt("A3", "Der Ertrag 2026 liegt bei 12 % ueber Plan.",
                  Herkunft.GERECHNET, grundlage=("M4", "M5"),
                  bruecke="Zaehler und Protokoll messen dieselbe Groesse "
                          "auf verschiedenen Wegen",
                  rueckhalt=("Kalibrierschein", "Geraetenorm"),
                  einschraenkung={"was": "PV", "wann": "2026"},
                  kippkriterium="beide Geraete teilen einen Systemfehler",
                  stand=("2026-08-31", "2026-01-10")))
    return ("GEGENPROBE — ehrliche Arbeit, zwei echte Wege", s, "A3")


# ══════════════════════════════════════════════════════════════════════
# Gegenprobe 2 — zwei Raten auf vorab beschrifteten Faellen
# ══════════════════════════════════════════════════════════════════════

# (Name, wirklich_ein_zeuge, Kippkriterien der stuetzenden Blaetter)
# Beschriftung VOR dem Lauf festgelegt.
FAELLE: Tuple[Tuple[str, bool, Tuple[str, ...]], ...] = (
    ("zwei Geraete, zwei Fehlerquellen",      False, ("Zaehler A dejustiert",
                                                      "Protokoll B luecken")),
    ("Zaehler und Gutachten",                 False, ("Zaehler dejustiert",
                                                      "Gutachter irrt")),
    ("drei Labore, drei Verfahren",           False, ("Labor 1 falsch",
                                                      "Labor 2 falsch",
                                                      "Labor 3 falsch")),
    ("Messung und Simulation",                False, ("Sensor driftet",
                                                      "Modell M falsch")),
    ("zwei Abschriften derselben Studie",     True,  ("Studie S ist falsch",
                                                      "Studie S ist falsch")),
    ("Modell und seine Folgerung",            True,  ("Modell M falsch",
                                                      "Modell M falsch")),
    ("drei Presseberichte, eine Agentur",     True,  ("Agentur irrt",
                                                      "Agentur irrt",
                                                      "Agentur irrt")),
    ("zwei Sensoren derselben Charge",        True,  ("Charge C fehlerhaft",
                                                      "Charge C fehlerhaft")),
    ("fauler Ausfueller, zwei echte Wege",    False, ("die Daten sind falsch",
                                                      "die Daten sind falsch")),
    ("fauler Ausfueller, drei echte Wege",    False, ("koennte falsch sein",
                                                      "koennte falsch sein",
                                                      "koennte falsch sein")),
    ("sorgfaeltiger Luegner, eine Wurzel",    True,  ("Modell M falsch",
                                                      "Randbedingung R falsch")),
    ("ein Zeuge, ehrlich als einer gefuehrt", True,  ("Zaehler A dejustiert",)),
)


def raten() -> Dict[str, object]:
    """GEMESSEN wird die Zahl der Versagenspunkte, nicht das Aufleuchten
    einer Marke. Erste Fassung fragte 'ist EIN_ZEUGE gefeuert?' — damit
    galt ein ehrlich als einzeln gefuehrter Zeuge als Fehlschlag,
    obwohl das System die Lage richtig wiedergab. Das war ein Fehler
    der Messung, nicht der Regel (derselbe Fall wie UNEINIGKEIT bei
    weniger als zwei Quellen)."""
    rg = fg = rf = ff = 0
    zeilen: List[Tuple[str, bool, bool, int]] = []
    for name, wirklich, kipps in FAELLE:
        s = Satz()
        for i, kk in enumerate(kipps):
            s.legen(Blatt(f"Q{i}", "Stuetze", Herkunft.GEMESSEN,
                          kippkriterium=kk))
        s.legen(Blatt("Z", "Behauptung", Herkunft.GERECHNET,
                      grundlage=tuple(f"Q{i}" for i in range(len(kipps))),
                      kippkriterium="alle Stuetzen fallen zusammen"))
        n_vp = len(versagenspunkte(s, "Z"))
        gemeldet = n_vp == 1
        zeilen.append((name, wirklich, gemeldet, n_vp))
        if gemeldet and wirklich:
            rg += 1
        elif gemeldet and not wirklich:
            fg += 1
        elif not gemeldet and not wirklich:
            rf += 1
        else:
            ff += 1
    durch, gesperrt = rf + ff, rg + fg
    return {"zeilen": zeilen, "rg": rg, "fg": fg, "rf": rf, "ff": ff,
            "erfindungsrate": ff / durch if durch else 0.0,
            "uebervorsichtsrate": fg / gesperrt if gesperrt else 0.0,
            "durchgelassen": durch, "gesperrt": gesperrt}


# ══════════════════════════════════════════════════════════════════════
# Bericht
# ══════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════
# Der Eingang — ein Bogen als Datei
# ══════════════════════════════════════════════════════════════════════
#
# Bis hierher lief die Schablone nur auf eingebauten Angriffen. Gemessen,
# belegt, und ohne Tuer: wer sie benutzen wollte, musste Python
# schreiben. Das ist derselbe Befund wie bei den 108 nicht erreichten
# Funktionen, nur eine Ebene hoeher.
#
# FORMAT — acht Felder je Blatt, dieselben acht wie oben
#
#   {
#     "ziel": "Z",                     Pflicht: welches Blatt behauptet
#     "stufe": "S3",                   S0..S3, Vorgabe S1
#     "pruefer": "Name",               fuer den Strang MENSCH
#     "verwendet_am": "2026-09-23",    fuer die GELTUNG
#     "blaetter": [
#       {"kennung": "M1",
#        "behauptung": "Zaehlerstand Anlage A",
#        "herkunftsart": "gemessen",          gemessen|berichtet|gerechnet
#        "grundlage": [],
#        "bruecke": "",
#        "rueckhalt": [],
#        "einschraenkung": {"was": "PV", "wann": "2026"},
#        "kippkriterium": "Zaehler A ist dejustiert",
#        "stand": ["2026-08-31", "2026-01-10"]}   [Daten ab, Kriterium am]
#     ]
#   }
#
# WAS BEIM LADEN ABGEWIESEN WIRD und was nur VERMERKT
#   abgewiesen:  doppelte Kennung, unbekannte Herkunftsart, fehlendes
#                oder unbekanntes ziel, Blatt ohne Kennung
#   vermerkt:    Grundlage, die auf ein fehlendes Blatt zeigt; Kreise
#                Beides steht in den Hinweisen und faellt P1 zur Last —
#                gefiltert wird nichts.

class Bogenfehler(Exception):
    pass


@dataclass
class Bogen:
    satz: Satz
    ziel: str
    stufe: str = "S1"
    pruefer: Optional[str] = None
    verwendet_am: Optional[str] = None
    hinweise: List[str] = field(default_factory=list)


def _blatt(roh: Dict) -> Blatt:
    k = roh.get("kennung")
    if not k:
        raise Bogenfehler(f"Blatt ohne Kennung: {roh!r:.80}")
    h = roh.get("herkunftsart")
    try:
        herkunft = Herkunft(h)
    except ValueError:
        raise Bogenfehler(
            f"{k}: herkunftsart {h!r} unbekannt. Erlaubt sind "
            f"{', '.join(x.value for x in Herkunft)}.")
    stand = roh.get("stand") or [None, None]
    if len(stand) != 2:
        raise Bogenfehler(f"{k}: stand braucht zwei Eintraege "
                          f"[Daten ab, Kriterium am], nicht {len(stand)}")
    zr = roh.get("zeitraum") or [None, None]
    if len(zr) != 2:
        raise Bogenfehler(f"{k}: zeitraum braucht zwei Eintraege "
                          f"[von, bis], nicht {len(zr)}")
    return Blatt(
        kennung=k, behauptung=roh.get("behauptung", ""),
        herkunftsart=herkunft,
        grundlage=tuple(roh.get("grundlage", ())),
        bruecke=roh.get("bruecke", ""),
        rueckhalt=tuple(roh.get("rueckhalt", ())),
        einschraenkung=dict(roh.get("einschraenkung", {})),
        kippkriterium=roh.get("kippkriterium", ""),
        stand=(stand[0], stand[1]),
        annahmen=tuple(roh.get("annahmen", ())),
        zeitraum=(zr[0], zr[1]))


def laden(pfad) -> Bogen:
    import json
    from pathlib import Path
    roh = json.loads(Path(pfad).read_text(encoding="utf-8"))
    s = Satz()
    for r in roh.get("blaetter", []):
        b = _blatt(r)
        if b.kennung in s.blaetter:
            raise Bogenfehler(
                f"{b.kennung} ist zweimal im Bogen. Ein Blatt wird nie "
                f"ueberschrieben — dieselbe Regel wie fuer Quellen.")
        s.legen(b)
    ziel = roh.get("ziel")
    if not ziel:
        raise Bogenfehler("kein 'ziel' angegeben — welches Blatt behauptet?")
    if ziel not in s.blaetter:
        raise Bogenfehler(f"ziel {ziel!r} kommt im Bogen nicht vor. "
                          f"Vorhanden: {', '.join(sorted(s.blaetter))}")
    b = Bogen(satz=s, ziel=ziel, stufe=roh.get("stufe", "S1"),
              pruefer=roh.get("pruefer"),
              verwendet_am=roh.get("verwendet_am"))
    for f in sorted(s.unbekannt(ziel)):
        b.hinweise.append(
            f"GRUNDLAGE nennt {f!r} — kein solches Blatt im Bogen. "
            f"Wird nicht gefiltert, faellt P1 zur Last.")
    for kreis in s.zyklen(ziel):
        b.hinweise.append(f"Kreis in der Grundlage: {' -> '.join(kreis)}")
    return b


def bericht_bogen(b: Bogen) -> List[str]:
    """Ein Bogen, einmal durch: Abgleich, Negativliste, Mindestluege —
    und danach durch das Tor, damit eine Datei den ganzen Weg geht."""
    from .tor import Stufe, tor
    z: List[str] = []
    a = z.append
    blatt = b.satz.blaetter[b.ziel]
    a("═" * 74)
    a(f"SCHABLONE — Bogen {b.ziel}")
    a("═" * 74)
    a(f"\n  {blatt.behauptung}")
    a(f"  {len(b.satz.blaetter)} Blatt/Blaetter, "
      f"{len(b.satz.traeger(b.ziel))} davon tragend")
    if b.hinweise:
        a("\n  HINWEISE BEIM LADEN")
        for h in b.hinweise:
            a(f"    · {h}")

    ws = abgleichen(b.satz, b.ziel)
    a(f"\n  ABGLEICH — {len(ws) or 'kein'} Widerspruch/Widersprueche")
    for x in ws:
        a(f"    {x.art.paar} {x.art.name:<22} {', '.join(x.betrifft)}")
        a(f"       {x.warum}")

    vp = versagenspunkte(b.satz, b.ziel)
    best = bestimmte(vp)
    unb = vp.get(UNBESTIMMT, [])
    a(f"\n  VERSAGENSPUNKTE  {len(best)} benannt"
      + (f", {len(unb)} Blatt/Blaetter ohne Kriterium (zaehlen nicht)"
         if unb else ""))
    for schluessel, wer in sorted(best.items()):
        a(f"    {', '.join(sorted(wer)):<24} {schluessel}")
    if unb:
        a(f"    {', '.join(sorted(unb)):<24} #unbestimmt")

    nl = negativliste(b.satz, b.ziel)
    a(f"\n  NICHT GEPRUEFT — ZIELBLATT  {len(nl)}")
    for t in nl:
        a(f"    · {t}")

    # FEHLER 44, im Fernwaerme-Lauf gefunden: die Negativliste las NUR
    # das Zielblatt. Das leere Feld, auf das im ganzen Fall alles ankam,
    # war G1.grundlage — und G1 ist nicht das Zielblatt. Das Werkzeug
    # hat geschwiegen, wo es haette reden muessen.
    rest = negativliste_traeger(b.satz, b.ziel)
    if rest:
        a(f"\n  NICHT GEPRUEFT — TRAGENDE BLAETTER  "
          f"{sum(len(v) for v in rest.values())} in {len(rest)} Blatt/Blaettern")
        for k, zeilen in sorted(rest.items()):
            for t in zeilen:
                a(f"    {k}: {t}")

    # FEHLER 45, gefunden beim Pruefen eines ganz anderen Kandidaten:
    # Blaetter, die das Zielblatt ueber KEINE grundlage-Kette erreicht.
    # Sie liegen im Bogen, gehen aber nicht ins Netz und tauchen in
    # keiner Regel auf. Im Fernwaerme-Lauf traf das bei ALLEN FUENF
    # Boegen die beiden einzigen echten Messungen.
    w = waisen(b.satz, b.ziel)
    if w:
        a(f"\n  NICHT ERREICHT  {len(w)} von {len(b.satz.blaetter)} "
          f"Blaettern, vom Zielblatt {b.ziel} aus")
        for k in sorted(w):
            x = b.satz.blaetter[k]
            a(f"    {k:<6} {x.herkunftsart.value:<10} "
              f"{x.behauptung[:44]}")
        mess = sorted(k for k in w
                      if b.satz.blaetter[k].herkunftsart is Herkunft.GEMESSEN)
        if mess:
            a(f"    ── darunter MESSUNGEN: {', '.join(mess)}")
            a(f"       Das ist keine Sperre. Es kann richtig sein, dass")
            a(f"       eine Messung die Behauptung nicht stuetzt. Aber es")
            a(f"       sollte dastehen, statt lautlos herauszufallen.")

    if len(b.satz.traeger(b.ziel)) <= 8:
        m = mindestluege(b.satz, b.ziel)
        if m is None:
            a("\n  MINDESTLUEGE  mit bis zu 3 Zuegen nicht raeumbar")
        elif m[0] == 0:
            a("\n  MINDESTLUEGE  — (nichts zu raeumen)")
        else:
            a(f"\n  MINDESTLUEGE  {m[0]} passende Aenderung(en):")
            for bl, fe in m[1]:
                a(f"    {bl}.{fe:<15} nachpruefbar: {wo_liegt(b.satz, bl, fe)}")
    else:
        a(f"\n  MINDESTLUEGE  uebersprungen "
          f"({len(b.satz.traeger(b.ziel))} Blaetter, die Suche waere "
          f"unverhaeltnismaessig)")

    a("\n" + "─" * 74)
    a("DERSELBE BOGEN DURCH DAS TOR")
    a("─" * 74)
    n = nach_netz(b.satz, b.ziel, blatt.behauptung,
                  b.verwendet_am or "2026-01-01")
    e = n.eintraege["E"]
    try:
        stufe = Stufe[b.stufe]
    except KeyError:
        stufe = Stufe.S1
        a(f"  (Stufe {b.stufe!r} unbekannt, S1 angenommen)")
    for zeile in tor(n, e, stufe, pruefer=b.pruefer,
                     verwendet_am=b.verwendet_am,
                     mit_diagnose=True).zeilen():
        a(f"  {zeile}")
    a("")
    a("  Die Schablone entscheidet nichts. Sie vergleicht Felder und")
    a("  uebergibt, was dabei herauskommt — art und uebernommen_aus")
    a("  sind aus der Form ABGELEITET, nicht uebernommen.")
    return z


def bericht() -> List[str]:
    z: List[str] = []
    a = z.append
    a("═" * 74)
    a("SCHABLONE — acht Felder, fuenf Abgleichregeln, kein Statusfeld")
    a("═" * 74)
    a("")
    a("  Die Felder sind uebernommen, nicht erfunden:")
    a("    1 BEHAUPTUNG    Toulmin Claim        5 RUECKHALT      Backing")
    a("    2 HERKUNFTSART  Admiralty / ICD 206  6 EINSCHRAENKUNG Qualifier")
    a("    3 GRUNDLAGE     Toulmin Grounds      7 KIPPKRITERIUM  Rebuttal")
    a("    4 BRUECKE       Toulmin Warrant      8 STAND          Vorabreg.")
    a("")
    a("  BRUECKE hat in FrameNetwork kein Gegenstueck. Toulmin: der")
    a("  Warrant bleibt meistens unausgesprochen. Deshalb das Feld.")

    gemessen_luege: List[Tuple[str, Optional[int], List[str]]] = []
    for name, s, k in (angriff_1(), angriff_2(), angriff_3(), angriff_4(),
                       sauber()):
        a("")
        a("─" * 74)
        a(name)
        a("─" * 74)
        b = s.blaetter[k]
        a(f"  Blatt {k}: {b.behauptung}")
        a(f"  Boden der Grundlage: "
          f"{', '.join(sorted(s.boden(k))) or '—'}")
        vp = versagenspunkte(s, k)
        a(f"  Versagenspunkte: {len(vp)}   (Blaetter auf dem Weg: "
          f"{len(s.traeger(k))})")
        ws = abgleichen(s, k)
        if not ws:
            a("  ABGLEICH   kein Widerspruch")
        for x in ws:
            a(f"  {x.art.paar} {x.art.name:<22} {', '.join(x.betrifft)}")
            a(f"     {x.warum}")
        nl = negativliste(s, k)
        a(f"  NICHT GEPRUEFT: {len(nl)}")
        for t in nl:
            a(f"     · {t}")
        m = mindestluege(s, k)
        if m is None:
            a("  MINDESTLUEGE  mit bis zu 3 Zuegen aus dem Menue nicht "
              "raeumbar")
            gemessen_luege.append((name, None, []))
        elif m[0] == 0:
            a("  MINDESTLUEGE  — (nichts zu raeumen)")
        else:
            a(f"  MINDESTLUEGE  {m[0]} passende Aenderung(en):")
            for bl, fe in m[1]:
                a(f"     {bl}.{fe:<15} nachpruefbar: {wo_liegt(s, bl, fe)}")
            gemessen_luege.append(
                (name, m[0], [wo_liegt(s, bl, fe) for bl, fe in m[1]]))

    a("")
    a("─" * 74)
    a("GEGENPROBE — zwei Raten, zwoelf vorab beschriftete Faelle")
    a("─" * 74)
    r = raten()
    a("  Fall                                   wirklich    gezaehlt")
    for name, wirklich, gemeldet, n in r["zeilen"]:   # type: ignore[index]
        ok = "  " if wirklich == gemeldet else " !"
        a(f" {ok} {name:<38} {'ein Zeuge' if wirklich else 'mehrere ':<11} "
          f"{n} Versagenspunkt(e)")
    a("")
    a(f"  richtig gemeldet {r['rg']}   falsch gemeldet {r['fg']}")
    a(f"  richtig frei     {r['rf']}   falsch frei     {r['ff']}")
    a(f"  Erfindungsrate      {de(float(r['erfindungsrate'])*100)} %"
      f"   von {r['durchgelassen']} durchgelassenen")
    a(f"  Uebervorsichtsrate  {de(float(r['uebervorsichtsrate'])*100)} %"
      f"   von {r['gesperrt']} gemeldeten")
    a("")
    a("  Die beiden Fehlschlaege sind KEIN Rauschen, sie sind die Form:")
    a("    faul    — wer ueberall dasselbe hinschreibt, wird gemeldet,")
    a("              obwohl seine Wege verschieden sind.")
    a("    Luegner — wer zwei verschiedene Kriterien erfindet, kommt durch.")

    # Der Schluss wird AUS DEM LAUF gerechnet, nicht vorher geschrieben.
    # (Fehler 16 war dreimal genau das.)
    a("")
    a("─" * 74)
    a("WAS DER LAUF WIRKLICH ERGIBT")
    a("─" * 74)
    zahlen = [x for _, x, _ in gemessen_luege if x]
    aussen = sum(1 for _, x, wo in gemessen_luege if x
                 and all(w.startswith("aussen") for w in wo))
    a(f"  Angriffe mit Widerspruch: {len(zahlen)}")
    a(f"  Noetige passende Luegen:  "
      f"{', '.join(str(x) for x in zahlen)}  (Spanne "
      f"{min(zahlen)} bis {max(zahlen)})")
    a(f"  Davon vollstaendig AUSSEN nachpruefbar: {aussen} von {len(zahlen)}")
    innen_bleibt = [n for n, x, wo in gemessen_luege
                    if x and not all(w.startswith("aussen") for w in wo)]
    for n in innen_bleibt:
        a(f"  BLEIBT INNEN: {n}")
    a("")
    a("  Das Tor brauchte EIN Weglassen (uebernommen_aus=()), und das")
    a("  war innen: niemand ausserhalb des Programms konnte es sehen.")
    a("  Die Schablone hebt die Zahl nur dort, wo eine Behauptung")
    a("  mehrere Stuetzen hat. Der Gewinn liegt woanders:")
    a("")
    a("      nicht  wie VIELE Luegen noetig sind,")
    a("      sondern WO sie liegen muessen.")
    a("")
    a("  Eine Behauptung ueber die Welt — wo gemessen wurde, wann das")
    a("  Kriterium geschrieben wurde, wer es berichtet hat — kann")
    a("  ausserhalb des Programms scheitern. uebernommen_aus konnte das")
    a("  nie. Genau deshalb liegen die Zeitstempel der Vorabregistrierung")
    a("  bei OSF und nicht beim Autor.")
    a("")
    a("  Was NICHT geloest ist: P2 und P3 stehen auf Freitext. Wer zwei")
    a("  verschiedene Kippkriterien und zwei verschiedene Bruecken")
    a("  hinschreibt, kommt durch, und niemand ausserhalb kann das")
    a("  pruefen — bis jemand das Kriterium ANWENDET. Genau an dieser")
    a("  Stelle haengt die Schablone an nachrechnen/proben, nicht an")
    a("  einer weiteren Regel.")
    return z


if __name__ == "__main__":
    for zeile in bericht():
        print(zeile)
