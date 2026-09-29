"""
ka.py — K|A, die Kontrollinstanz fuer die Wissensausweitung.

WAS K|A IST UND WAS NICHT

  K|A ist KEINE weitere Regel. Regeln sperren. K|A erzeugt einen
  UNTERSUCHUNGSAUFTRAG. Der Unterschied ist der ganze Punkt:

      Ergebnis -> Befund -> K|A -> Untersuchungsauftrag
      und NICHT
      Ergebnis -> Regelaenderung

  K|A darf deshalb KEINEN STATUS SETZEN. Duerfte sie es, koennte sie
  ihre eigenen Befunde zu Paragraphen machen und sich selbst
  bestaetigen — genau das, was sie verhindern soll. Der Regress endet
  dort, wo die Instanz nur Auftraege erzeugt und nie Zustaende.

DREI KORREKTUREN AM ENTWURF

  1 · ZIRKULAER IST NICHT JA/NEIN.
      Gefragt ist nicht 'liegt Selbstbestaetigung vor', sondern
      'wie viel der Stuetzung bleibt uebrig, wenn man die Wege
      entfernt, die durch die Behauptung selbst laufen'. Das ist eine
      Zahl plus die Wege — und beides wird geliefert.

  2 · 'ES KOMMT IMMER RICHTIG HERAUS' IST KEIN VERDACHT.
      Eine Naturkonstante kommt immer richtig heraus. Ein Zirkel auch.
      Von aussen sehen beide gleich aus. Unterscheiden laesst sie nur
      eine Frage: AUF WIE VIELEN WEGEN HAETTE ES SCHIEFGEHEN KOENNEN?

          Naturkonstante   viele unabhaengige Wege, keiner widersprach
          Zirkel           null Wege, weil jeder die Behauptung benutzt

      Diese Zahl ist die eigentliche Ausgabe von K|A.

  3 · EINE GUELTIGE RECHNUNG AUF EMPIRISCHEN EINGABEN IST EMPIRISCH.
      Sonst waescht das Etikett 'mathematisch' die Unsicherheit der
      Eingaben weg. 119.400 / 240.000 = 0,4975 ist exakt als Rechnung
      und empirisch als Aussage.

AUFRUF
  python -m schablone ka
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple


# ══════════════════════════════════════════════════════════════════════
# Die Art einer Aussage — und die Regel, die das Etikett ehrlich haelt
# ══════════════════════════════════════════════════════════════════════

class Aussageart(Enum):
    DEFINITORISCH = "definitorisch"   # wahr per Festlegung
    LOGISCH       = "logisch"         # formale Schlusskette
    MATHEMATISCH  = "mathematisch"    # formale Ableitung
    EMPIRISCH     = "empirisch"       # Evidenz, Messung, Quelle


# Je weiter unten, desto schwaecher. Eine Ableitung erbt das Schwaechste.
RANG = {Aussageart.DEFINITORISCH: 0, Aussageart.LOGISCH: 1,
        Aussageart.MATHEMATISCH: 2, Aussageart.EMPIRISCH: 3}


def erbt_schwaechste(eingaben: Sequence[Aussageart],
                     ableitung: Aussageart) -> Aussageart:
    """Die Ableitung kann formal einwandfrei sein — die Aussage ist
    trotzdem nur so stark wie ihre schwaechste Eingabe."""
    if not eingaben:
        return ableitung
    return max(list(eingaben) + [ableitung], key=lambda a: RANG[a])


# ══════════════════════════════════════════════════════════════════════
# Der Ableitungsgraph
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Knoten:
    kennung: str
    text: str
    art: Aussageart
    stuetzt_sich_auf: Tuple[str, ...] = ()   # andere Paragraphen
    wurzel: Optional[str] = None             # eigene, externe Wurzel


@dataclass
class Auftrag:
    """Was K|A liefert. Kein Status, kein Urteil — ein Auftrag."""
    kandidat: str
    anlass: str
    wege_gesamt: int
    wege_unabhaengig: int
    trag_anteil: float
    selbstbezug: List[List[str]] = field(default_factory=list)
    unabhaengig: List[List[str]] = field(default_factory=list)
    frage: str = ""

    def zeilen(self) -> List[str]:
        z = [f"UNTERSUCHUNGSAUFTRAG zu {self.kandidat}",
             f"  Anlass              {self.anlass}",
             f"  Stuetzwege gesamt   {self.wege_gesamt}",
             f"  davon unabhaengig   {self.wege_unabhaengig}",
             f"  Trag-Anteil ohne Selbstbezug  "
             f"{self.trag_anteil*100:.0f} %",
             "  WEGE MIT SELBSTBEZUG"]
        z += [f"    {' -> '.join(w)}" for w in self.selbstbezug] or ["    —"]
        z.append("  WEGE OHNE SELBSTBEZUG")
        z += [f"    {' -> '.join(w)}" for w in self.unabhaengig] or ["    —"]
        z.append(f"  FRAGE AN DEN MENSCHEN")
        z.append(f"    {self.frage}")
        return z


@dataclass
class Wissensnetz:
    knoten: Dict[str, Knoten] = field(default_factory=dict)

    def k(self, x: Knoten) -> None:
        self.knoten[x.kennung] = x

    def wege(self, start: str, gesehen: Optional[Tuple[str, ...]] = None
             ) -> List[List[str]]:
        """Alle Stuetzwege von start bis zu einer eigenen Wurzel.
        Ein Weg, der auf sich selbst zurueckkommt, wird dort beendet
        und ausdruecklich zurueckgegeben — nicht weggeworfen."""
        gesehen = gesehen or ()
        if start in gesehen:
            return [list(gesehen) + [start]]          # Zyklus, sichtbar
        x = self.knoten.get(start)
        if x is None:
            return [list(gesehen) + [start]]
        if not x.stuetzt_sich_auf:
            return [list(gesehen) + [start]]
        out: List[List[str]] = []
        for v in x.stuetzt_sich_auf:
            out += self.wege(v, gesehen + (start,))
        return out

    def wurzel_von(self, weg: Sequence[str]) -> Optional[str]:
        letzter = self.knoten.get(weg[-1])
        return letzter.wurzel if letzter else None

    # ── Die eigentliche Arbeit ────────────────────────────────────────
    def untersuchen(self, kandidat: str) -> Auftrag:
        alle = self.wege(kandidat)
        selbst = [w for w in alle if w.count(kandidat) > 1]
        rest = [w for w in alle if w.count(kandidat) == 1]
        # unabhaengig heisst: eigene externe Wurzel, die nicht schon
        # ueber einen anderen Weg gezaehlt wurde
        wurzeln: Set[str] = set()
        unabhaengig: List[List[str]] = []
        for w in rest:
            r = self.wurzel_von(w)
            if r and r not in wurzeln:
                wurzeln.add(r)
                unabhaengig.append(w)
        anteil = len(unabhaengig) / len(alle) if alle else 0.0
        if selbst:
            anlass = (f"{len(selbst)} von {len(alle)} Stuetzwegen laufen "
                      "durch die Behauptung selbst")
        elif len(wurzeln) <= 1:
            anlass = (f"{len(alle)} Stuetzwege, aber nur "
                      f"{len(wurzeln)} eigene Wurzel")
        else:
            anlass = (f"{len(wurzeln)} unabhaengige Wurzeln — kein Anlass, "
                      "Auftrag nur zur Kenntnis")
        return Auftrag(
            kandidat=kandidat, anlass=anlass, wege_gesamt=len(alle),
            wege_unabhaengig=len(unabhaengig), trag_anteil=anteil,
            selbstbezug=selbst, unabhaengig=unabhaengig,
            frage=self.frage_stellen(kandidat, len(wurzeln), bool(selbst)))

    def frage_stellen(self, kandidat: str, wurzeln: int,
                      selbstbezug: bool) -> str:
        if selbstbezug:
            return ("Gibt es einen Beleg fuer " + kandidat +
                    ", der NICHT ueber " + kandidat + " laeuft? "
                    "Wenn nein: VERMERK, nicht widerlegt.")
        if wurzeln <= 1:
            return ("Alles haengt an einer Wurzel. Auf welchem zweiten Weg "
                    "haette dieser Satz scheitern koennen?")
        return (f"{wurzeln} unabhaengige Wege, keiner widersprach. "
                "Erweiterung zulaessig; der Auftrag dokumentiert nur, "
                "worauf sie steht.")

    def haette_scheitern_koennen(self, kandidat: str) -> int:
        """DIE ZAHL, DIE NATURKONSTANTE UND ZIRKEL TRENNT.

        Auf wie vielen voneinander unabhaengigen Wegen haette dieser
        Satz falsch herauskommen koennen? Eine Naturkonstante hat viele.
        Ein Zirkel hat null — jeder Weg benutzt die Behauptung."""
        a = self.untersuchen(kandidat)
        return a.wege_unabhaengig


# ══════════════════════════════════════════════════════════════════════
# Konfliktsuche ueber einer ENDLICHEN Menge — entscheidbar und billig
# ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Folgerung:
    kennung: str
    groesse: str
    unten: float
    oben: float
    annahmen: FrozenSet[str]


@dataclass(frozen=True)
class Konfliktkandidat:
    a: str
    b: str
    groesse: str
    annahmen: FrozenSet[str]
    text: str


def konflikte(fs: Sequence[Folgerung]) -> List[Konfliktkandidat]:
    """Zwei Folgerungen widersprechen sich, wenn sie dieselbe Groesse
    betreffen, ihre Annahmen vertraeglich sind und ihre Intervalle sich
    NICHT ueberlappen. Kein Schnitt, keine Mittelung — die Feststellung
    des Widerspruchs ist das Ergebnis."""
    out = []
    for i, x in enumerate(fs):
        for y in fs[i+1:]:
            if x.groesse != y.groesse:
                continue
            vereint = x.annahmen | y.annahmen
            if any(a.startswith("nicht_") and a[6:] in vereint
                   for a in vereint):
                continue                      # Annahmen schliessen sich aus
            if x.oben < y.unten or y.oben < x.unten:
                out.append(Konfliktkandidat(
                    x.kennung, y.kennung, x.groesse, vereint,
                    f"[{x.unten}, {x.oben}] und [{y.unten}, {y.oben}] "
                    "sind disjunkt"))
    return out


def kerne(fs: Sequence[Folgerung]) -> List[Tuple[str, List[str], List[str]]]:
    """DIE KORREKTUR AN DER PAARWEISEN SUCHE.

    Paarweise Konflikte wachsen quadratisch: fuenf Folgerungen ergeben
    sieben Meldungen, die fast alle denselben Ursprung haben. Bei
    hundert Folgerungen sind es Hunderte, und der Befund verschwindet
    im Rauschen — dieselbe Aufmerksamkeitsfalle wie beim
    Kandidatenstrom.

    Brauchbar ist eine Meldung JE GROESSE: welche Folgerungen haben
    zusammen keinen gemeinsamen Punkt, und welche groesste Teilmenge
    haette noch einen. Die zweite Liste sagt, was man aufgeben muesste.
    """
    aus: List[Tuple[str, List[str], List[str]]] = []
    groessen = sorted({f.groesse for f in fs})
    for g in groessen:
        gruppe = [f for f in fs if f.groesse == g]
        vertraeglich = [f for f in gruppe
                        if not any(a.startswith("nicht_") and a[6:] in
                                   {b for h in gruppe for b in h.annahmen}
                                   for a in f.annahmen)]
        if len(vertraeglich) < 2:
            continue
        unten = max(f.unten for f in vertraeglich)
        oben = min(f.oben for f in vertraeglich)
        if unten <= oben:
            continue                       # gemeinsamer Punkt vorhanden
        # groesste Teilmenge mit gemeinsamem Punkt, gierig nach Breite
        nach_breite = sorted(vertraeglich, key=lambda f: f.oben - f.unten,
                             reverse=True)
        beste: List[Folgerung] = []
        for f in nach_breite:
            probe = beste + [f]
            if max(x.unten for x in probe) <= min(x.oben for x in probe):
                beste = probe
        aus.append((g, [f.kennung for f in vertraeglich],
                    [f.kennung for f in beste]))
    return aus


ERKLAERUNGEN = [
    "die Annahmen X und Y sind nicht gleichzeitig moeglich",
    "eine versteckte Annahme fehlt in mindestens einer Ableitung",
    "die Formalisierung einer der beiden Folgerungen ist falsch",
    "die Theorie hat an dieser Stelle tatsaechlich ein Problem",
]


# ══════════════════════════════════════════════════════════════════════
def beispiel_naturkonstante() -> Wissensnetz:
    n = Wissensnetz()
    n.k(Knoten("§C", "Die Lichtgeschwindigkeit ist konstant.",
               Aussageart.EMPIRISCH,
               stuetzt_sich_auf=("§M1", "§M2", "§M3", "§M4", "§M5")))
    for i, (kennung, was) in enumerate([
            ("§M1", "Interferometer 1887"), ("§M2", "Resonator 1932"),
            ("§M3", "Laser 1972"), ("§M4", "Satellitenlaufzeit"),
            ("§M5", "Astronomische Aberration")], start=1):
        n.k(Knoten(kennung, was, Aussageart.EMPIRISCH, wurzel=f"apparat_{i}"))
    return n


def beispiel_zirkel() -> Wissensnetz:
    """Der adversariale Fall, der vorgeschlagen wurde: ein Paragraph,
    dessen Ausweitung sich ausschliesslich aus seinem eigenen
    Ableitungsnetz rechtfertigt."""
    n = Wissensnetz()
    n.k(Knoten("§P", "Die Anlage liegt auf Plan.", Aussageart.EMPIRISCH,
               stuetzt_sich_auf=("§A", "§B", "§C2", "§D", "§E")))
    n.k(Knoten("§A", "Der Halbjahresertrag entspricht der halben Prognose.",
               Aussageart.MATHEMATISCH, stuetzt_sich_auf=("§P",)))
    n.k(Knoten("§B", "Die Prognose war realistisch.", Aussageart.EMPIRISCH,
               stuetzt_sich_auf=("§A",)))
    n.k(Knoten("§C2", "Die Abweichung ist unauffaellig.",
               Aussageart.MATHEMATISCH, stuetzt_sich_auf=("§B",)))
    n.k(Knoten("§D", "Keine Nachpruefung noetig.", Aussageart.LOGISCH,
               stuetzt_sich_auf=("§C2",)))
    n.k(Knoten("§E", "Die Anlage arbeitet planmaessig.",
               Aussageart.EMPIRISCH, stuetzt_sich_auf=("§D",)))
    return n


def bericht() -> List[str]:
    z = ["K|A — KONTROLLINSTANZ FUER DIE WISSENSAUSWEITUNG", ""]

    z.append("1 · ZWEI FAELLE, DIE VON AUSSEN GLEICH AUSSEHEN")
    z.append("")
    for name, netz, kandidat in [
            ("Naturkonstante", beispiel_naturkonstante(), "§C"),
            ("Selbstbestaetigung", beispiel_zirkel(), "§P")]:
        a = netz.untersuchen(kandidat)
        z.append(f"  {name}: {kandidat} wird von "
                 f"{len(netz.knoten[kandidat].stuetzt_sich_auf)} Paragraphen "
                 "gestuetzt, kein einziger widerspricht.")
        z.append(f"    haette scheitern koennen auf "
                 f"{netz.haette_scheitern_koennen(kandidat)} unabhaengigen Wegen")
        z.append("")
    z.append("  Beide 'kommen immer richtig heraus'. Die Stuetzungszahl")
    z.append("  unterscheidet sie NICHT. Nur die Frage, auf wie vielen")
    z.append("  unabhaengigen Wegen es haette schiefgehen koennen.")
    z.append("")
    z.append("  Ein Verbot von 'kommt immer richtig heraus' wuerde die")
    z.append("  Naturkonstante mit sperren. Deshalb ist K|A keine Regel,")
    z.append("  sondern eine Untersuchung.")
    z.append("")

    z.append("2 · WAS K|A LIEFERT — kein Ja/Nein, sondern der Weg")
    z.append("")
    netz = beispiel_zirkel()
    z += ["  " + w for w in netz.untersuchen("§P").zeilen()]
    z.append("")
    netz2 = beispiel_naturkonstante()
    z += ["  " + w for w in netz2.untersuchen("§C").zeilen()]
    z.append("")

    z.append("3 · DAS ETIKETT DARF DIE UNSICHERHEIT NICHT WASCHEN")
    z.append("")
    for eingaben, ableitung, satz in [
        ([Aussageart.EMPIRISCH, Aussageart.EMPIRISCH],
         Aussageart.MATHEMATISCH,
         "119.400 / 240.000 = 0,4975"),
        ([Aussageart.DEFINITORISCH], Aussageart.MATHEMATISCH,
         "1 kWh = 3,6 MJ"),
        ([Aussageart.MATHEMATISCH], Aussageart.LOGISCH,
         "aus A=B und B=C folgt A=C"),
    ]:
        erg = erbt_schwaechste(eingaben, ableitung)
        z.append(f"  {satz:<32} Ableitung {ableitung.value:<14}"
                 f"-> Aussage ist {erg.value}")
    z.append("")
    z.append("  Die erste Zeile ist der Fall, um den es geht: die Rechnung")
    z.append("  ist exakt, die AUSSAGE ist empirisch. Wer sie als")
    z.append("  'mathematisch' fuehrt, hat die Unsicherheit der Eingaben")
    z.append("  im Etikett verschwinden lassen.")
    z.append("")
    z.append("  EINSCHRAENKUNG, ausdruecklich: dass EMPIRISCH das")
    z.append("  schwaechste Glied ist, laesst sich begruenden. Die")
    z.append("  Reihenfolge zwischen LOGISCH und MATHEMATISCH ist eine")
    z.append("  Festlegung von mir und traegt die dritte Zeile oben.")
    z.append("")

    z.append("4 · KONFLIKTSUCHE — entscheidbar, weil die Menge endlich ist")
    z.append("")
    fs = [
        Folgerung("§2  T -> A", "eta", 0.90, 0.95, frozenset({"T"})),
        Folgerung("§3  T -> B", "eta", 0.88, 0.96, frozenset({"T"})),
        Folgerung("§4  T+X -> C", "eta", 0.60, 0.70, frozenset({"T", "X"})),
        Folgerung("§5  T+X+Y -> D", "eta", 0.97, 0.99,
                  frozenset({"T", "X", "Y"})),
        Folgerung("§6  T+nX -> E", "eta", 0.30, 0.50,
                  frozenset({"T", "nicht_X"})),
    ]
    ks = konflikte(fs)
    kk = kerne(fs)
    z.append(f"  {len(fs)} Folgerungen  ->  {len(ks)} paarweise Meldungen")
    z.append(f"                  ->  {len(kk)} Kern(e)")
    z.append("")
    z.append("  PAARWEISE (so, wie es zuerst gebaut war):")
    for k in ks[:3]:
        z.append(f"    {k.a} gegen {k.b} — {k.text}")
    if len(ks) > 3:
        z.append(f"    ... und {len(ks)-3} weitere, fast alle mit demselben")
        z.append("        Ursprung. Paare wachsen quadratisch; bei hundert")
        z.append("        Folgerungen sind das Hunderte Meldungen.")
    z.append("")
    z.append("  ALS KERN (so, wie es brauchbar ist):")
    for g, alle_k, beste in kk:
        z.append(f"    Groesse {g}: {', '.join(alle_k)}")
        z.append(f"      haben zusammen KEINEN gemeinsamen Punkt")
        z.append(f"      groesste vertraegliche Teilmenge: {', '.join(beste)}")
        z.append(f"      -> aufzugeben waere: "
                 f"{', '.join(k for k in alle_k if k not in beste)}")
    z.append("")
    z.append("  §6 steht unter 'nicht_X' und faellt aus dem Kern heraus —")
    z.append("  unvertraegliche Annahmen sind kein Widerspruch.")
    z.append("")
    z.append("  EIN KONFLIKTKANDIDAT HEISST NICHT, DASS T FALSCH IST.")
    for e in ERKLAERUNGEN:
        z.append(f"    - {e}")
    z.append("")
    z.append("  Das System erzeugt einen Auftrag. Entscheiden muss ein Mensch.")
    return z
