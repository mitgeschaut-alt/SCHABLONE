"""
leitung.py — die Uebersetzung zwischen kern und ka. Sonst nichts.

WARUM EIN EIGENES MODUL

  ka.py importiert nichts aus dem Paket, und das soll so bleiben. Es
  rechnet auf seinem eigenen Graphen und kennt weder Status noch Stufe
  noch Attest. Genau deshalb kann es keine Zustandsentscheidung treffen
  — nicht weil es sich zurueckhaelt, sondern weil es die Begriffe nicht
  hat. Eine Leitung, die diese Eigenschaft aufgibt, ist keine
  Verbesserung.

  Also: kern <- leitung -> ka. Beide Seiten bleiben unberuehrt.

WAS HIER UEBERSETZT WIRD

    ka.Knoten           kern
    kennung             Quelle.kennung
    text                Quelle.was
    stuetzt_sich_auf    Quelle.uebernommen_aus
    wurzel              Netz.pfade() — der gehaertete Pfadschluessel
    art (Aussageart)    KEIN Gegenstueck. Wird auf EMPIRISCH gesetzt.

  Die fuenfte Zeile ist eine bekannte Luecke, keine Abbildung:
  Aussageart {definitorisch, logisch, mathematisch, empirisch} und
  Art {messung, aussage, rechnung} sind zwei Achsen. Gemessen wurde,
  dass wege/wurzel_von/untersuchen/frage_stellen das Feld NICHT lesen —
  fuer die Selbstbezugspruefung ist die Luecke folgenlos. Fuer
  ka.erbt_schwaechste() waere sie es nicht; die Funktion bleibt
  deshalb ausserhalb dieser Leitung.

  Bemerkenswert: Knoten.wurzel ist in ka ein GESPEICHERTES Feld. Hier
  wird es aus Netz.pfade() GERECHNET. Die Leitung bringt also nicht nur
  ka an den Betrieb, sie ersetzt dabei ein setzbares Feld durch eine
  Rechnung — dasselbe Muster wie ueberall sonst in dieser Sitzung.

DIE ARBEITSTEILUNG, ausdruecklich

    ka         meldet einen TATBESTAND:   'dieser Weg laeuft durch die
               Behauptung selbst'. Kein Status, keine Stufe, kein Urteil.
    tor        traegt den Befund als DIAGNOSE im Attest. Attest.ergebnis
               liest ihn nicht — das ist geprueft, nicht behauptet.
    buch/bilanz faellt die ENTSCHEIDUNG: ein selbstbezueglich gestuetzter
               Eintrag wird nicht automatisch bestaetigt. Diese Politik
               steht dort und nur dort.

  Wer die Reihenfolge umdreht und ka entscheiden laesst, hat ein Modul
  mit Meinung und keine Diagnose mehr.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from . import ka
from .kern import Eintrag, Netz


@dataclass(frozen=True)
class Diagnose:
    """ka.Auftrag, auf das reduziert, was der Betrieb braucht. Eigene
    Klasse, damit tor.py ka nicht importieren muss — die Richtung der
    Abhaengigkeit bleibt kern <- leitung -> ka."""
    kandidat: str
    anlass: str
    wege_gesamt: int
    wege_unabhaengig: int
    trag_anteil: float
    selbstbezug: Tuple[Tuple[str, ...], ...]
    frage: str

    @property
    def greift(self) -> bool:
        """Ein Tatbestand liegt vor. NICHT: etwas ist falsch."""
        return bool(self.selbstbezug)


def nach_wissensnetz(netz: Netz) -> ka.Wissensnetz:
    knoten: Dict[str, ka.Knoten] = {}
    for k, q in netz.quellen.items():
        pf = netz.pfade(k)
        knoten[k] = ka.Knoten(
            kennung=k, text=q.was,
            art=ka.Aussageart.EMPIRISCH,       # Luecke, s. Kopf
            stuetzt_sich_auf=tuple(q.uebernommen_aus),
            wurzel=(sorted(pf)[0] if len(pf) == 1 else None))
    return ka.Wissensnetz(knoten=knoten)


def diagnose(netz: Netz, e: Eintrag) -> Tuple[Diagnose, ...]:
    """Je Quelle des Eintrags ein Befund. Liest nur, aendert nichts."""
    wn = nach_wissensnetz(netz)
    out: List[Diagnose] = []
    for k in e.quellen:
        if k not in wn.knoten:
            continue
        a = wn.untersuchen(k)
        out.append(Diagnose(
            kandidat=a.kandidat, anlass=a.anlass,
            wege_gesamt=a.wege_gesamt,
            wege_unabhaengig=a.wege_unabhaengig,
            trag_anteil=a.trag_anteil,
            selbstbezug=tuple(tuple(w) for w in a.selbstbezug),
            frage=a.frage))
    return tuple(out)


def selbstbezueglich(d: Tuple[Diagnose, ...]) -> Tuple[str, ...]:
    """Reine Auskunft: welche Quellen stuetzen sich auf sich selbst.
    Was daraus folgt, entscheidet der Aufrufer."""
    return tuple(x.kandidat for x in d if x.selbstbezug)
