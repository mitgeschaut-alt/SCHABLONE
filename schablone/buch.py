"""
buch.py — die epistemische Buchhaltung.

Ein System muss nicht nur wissen, was es weiss, sondern auch, welche
ungepruefte Last es mit sich herumtraegt und wie lange.

DIE FALLE BEIM ALTER
  Ein Vermerk von heute und einer von vor 150 Tagen sind gleich wahr.
  Alter ist eine Eigenschaft der BUCHHALTUNG, nie der Aussage. Erlaubt
  ist genau eine Folge: eine ENTSCHEIDUNG erzwingen — pruefen oder
  ausdruecklich verwerfen. Nie ein Urteil.

  Deshalb laeuft KEINE Uhr, die von allein einen Status aendert. Zeit
  erzeugt eine Frage, nie eine Antwort. Ein automatisches Verfallsdatum
  hiesse 'alt = wahrscheinlich falsch' und waere derselbe Fehler wie
  ein Plausibilitaetswert, nur mit einer Uhr statt einer Formel.

  DREI GROESSEN, DIE NICHT DASSELBE SIND
    alter(heute)    seit dem EINGANG. Eine Messung von 1974, gestern
                    eingetragen, ist hier 1 Tag alt.
    wartet(heute)   seit dem letzten STATUSWECHSEL — wie lange die
                    Entscheidung aussteht. Das ist die Faelligkeitsuhr.
    Zahl.daten_ab   wie alt die DATEN sind. Wird von R5 gegen
                    festgelegt_am geprueft, sonst von nichts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .kern import Eintrag, Netz, Status


@dataclass
class Bilanz:
    tag: str
    bestand: Dict[Status, int]
    offen: List[Eintrag]
    alter_mittel: float
    alter_max: int
    ueber: Dict[int, int]
    deckel: int
    abgewiesen: List[Tuple[str, str]]
    aufmerksamkeit: List[Tuple[str, int]]
    ueberholt: List[Eintrag] = field(default_factory=list)
    wartet_max: int = 0

    def zeilen(self) -> List[str]:
        z = [f"BILANZ zum {self.tag}", ""]
        for s in Status:
            z.append(f"  {s.value:<28}{self.bestand.get(s, 0):>6}")
        z.append("")
        z.append(f"  offene Vermerke                {len(self.offen):>6}")
        for grenze in sorted(self.ueber):
            z.append(f"    davon aelter als {grenze:>3} Tage    "
                     f"{self.ueber[grenze]:>6}")
        z.append(f"  Durchschnittsalter offen      "
                 f"{self.alter_mittel:>6.1f} Tage")
        z.append(f"  aeltester offener Vermerk     {self.alter_max:>6} Tage")
        z.append(f"  ueberholt, wartet auf Neupruefung "
                 f"{len(self.ueberholt):>3}")
        z.append(f"  laengste offene Entscheidung  "
                 f"{self.wartet_max:>6} Tage")
        z.append(f"  Schuldendeckel (nur Vermerke) {self.deckel:>6}")
        z.append(f"  abgewiesene Aufnahmen         "
                 f"{len(self.abgewiesen):>6}")
        for k, warum in self.abgewiesen[:5]:
            z.append(f"    {k}: {warum}")
        if len(self.abgewiesen) > 5:
            z.append(f"    ... und {len(self.abgewiesen)-5} weitere")
        if self.aufmerksamkeit:
            z.append("")
            z.append("  VERTEILUNG DER PRUEFARBEIT — auch das ist eine")
            z.append("  Bilanzgroesse: der Kandidatenstrom bindet die")
            z.append("  Aufmerksamkeit, ohne einen einzigen Status zu aendern.")
            gesamt = sum(n for _, n in self.aufmerksamkeit) or 1
            for thema, n in self.aufmerksamkeit:
                z.append(f"    {thema:<26}{n:>4}  {n/gesamt*100:>5.1f} %")
        return z


def bilanz(netz: Netz, tag: str,
           grenzen: Tuple[int, ...] = (30, 90, 180)) -> Bilanz:
    bestand = Counter(e.status for e in netz.eintraege.values())
    offen = netz.offene_vermerke()
    alter = sorted(e.alter(tag) for e in offen)
    themen = Counter()
    for e in netz.eintraege.values():
        if e.versuche:
            themen[e.geltungsbereich.get("thema", "ohne Thema")] += e.versuche
    return Bilanz(
        tag=tag,
        bestand=dict(bestand),
        offen=offen,
        alter_mittel=sum(alter) / len(alter) if alter else 0.0,
        alter_max=alter[-1] if alter else 0,
        ueber={g: sum(1 for a in alter if a > g) for g in grenzen},
        deckel=netz.deckel,
        abgewiesen=list(netz.abgewiesen),
        aufmerksamkeit=sorted(themen.items(), key=lambda x: -x[1]),
        ueberholt=[e for e in netz.eintraege.values()
                   if e.status is Status.VERALTET],
        wartet_max=max((e.wartet(tag) for e in netz.offen()), default=0),
    )


def faellige(netz: Netz, tag: str, frist: int = 30) -> List[Eintrag]:
    """Was eine ENTSCHEIDUNG erzwingt — nicht, was verdaechtig ist.

    Die Rueckgabe sagt nicht 'diese Saetze sind wohl falsch'. Sie sagt
    'ueber diese Saetze ist seit {frist} Tagen nicht entschieden worden'.

    Gezaehlt wird ab dem letzten Statuswechsel (wartet), nicht ab dem
    Eingang (alter): ein VERALTETER Eintrag wartet erst seit der
    Revision, nicht seit seiner Aufnahme vor drei Jahren."""
    return sorted((e for e in netz.offen() if e.wartet(tag) > frist),
                  key=lambda e: -e.wartet(tag))


def zwei_raten(richtig_gesperrt: int, falsch_gesperrt: int,
               richtig_frei: int, falsch_frei: int) -> Dict[str, object]:
    """R12: nie eine Zahl. Erfindungsrate misst, was faelschlich
    durchkam; Uebervorsichtsrate, was faelschlich gesperrt wurde.

    Ohne die zweite gewinnt jedes System, das auf alles nein sagt."""
    durch = falsch_frei + richtig_frei
    gesperrt = richtig_gesperrt + falsch_gesperrt
    return {
        "erfindungsrate": falsch_frei / durch if durch else 0.0,
        "uebervorsichtsrate": falsch_gesperrt / gesperrt if gesperrt else 0.0,
        "durchgelassen": durch,
        "gesperrt": gesperrt,
    }
