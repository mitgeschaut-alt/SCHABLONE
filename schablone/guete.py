"""
guete.py — geschlossener Katalog von Abwertungsgruenden.

DIE LUECKE, DIE DAS SCHLIESST

  Zehn extern eingestufte Faelle ergaben zehnmal denselben Wert. Grund:
  das System kann ueber die SCHAETZUNG nichts sagen, nur ueber ihre
  HERKUNFT. Es fehlt die halbe Sprache.

  Und: eine Negativliste ohne festen Katalog ist zwischen zwei Attesten
  nicht vergleichbar. 'nicht geprueft' ohne Angabe WORAUFHIN ist keine
  Auskunft.

DIE FUENF GRUENDE — hergeleitet, dann verglichen

  Aus dem eigenen Aufbau ergeben sich vier Fragen, die das System bisher
  nicht stellen konnte, plus eine fuenfte, die nur DIESES System stellen
  kann:

    STREUBREITE      Deckt das Intervall Werte ab, die zu
                     VERSCHIEDENEN Entscheidungen fuehren?
    UNEINIGKEIT      Widersprechen sich die Quellen staerker, als bei
                     einem gemeinsamen Sachverhalt zu erwarten waere?
    ABSTAND          Wurde gemessen, was gefragt war? (Surrogat, andere
                     Population, zu kurze Beobachtung)
    AUSWAHL          Ist das Vorliegende moeglicherweise eine Auswahl
                     aus dem, was existiert?
    SCHEINEINIGKEIT  Teilen die uebereinstimmenden Quellen ihre Wurzel?
                     Uebereinstimmung unter Abschriften ist keine.

  Vergleich NACH der Herleitung: die ersten vier entsprechen GRADEs
  imprecision, inconsistency, indirectness, publication bias. Zwei
  unabhaengige Wege, dasselbe Ergebnis — das staerkt beide.
  SCHEINEINIGKEIT hat in GRADE kein Gegenstueck. Es ist die
  Wurzelrechnung, auf die Schaetzgueteseite gebracht.

DER UNTERSCHIED ZU GRADE, DER AUS DEN EIGENEN AXIOMEN FOLGT

  GRADE kennt 'not serious'. Das vermischt zwei Dinge:

      geprueft und unbedenklich   !=   nicht bewertet

  Das ist die zweite Nicht-Gleichung, auf den Katalog angewandt. Eine
  nicht bewertete Domaene kostet deshalb KEINE Stufe — 'unbekannt !=
  falsch' —, erscheint aber in der Negativliste und im Ergebnis.

  Folge: das Ergebnis ist nie eine Zahl allein, sondern ein Paar:

      Stufe  +  Anzahl nicht bewerteter Domaenen

VORAB FESTGELEGTE SCHWELLEN — vor dem ersten Lauf geschrieben

  STREUBREITE (Verhaeltnismasse, Entscheidungsschwelle 1,0)
      SEHR_ERNST  Intervall enthaelt 1,0 UND obere/untere Grenze > 10
      ERNST       Intervall enthaelt 1,0
      KEINE       sonst
  ABSTAND
      ERNST       Surrogatgroesse ODER Beobachtungsdauer unter 3 Monaten
                  bei einem Ereignis, das selten und spaet auftritt
      KEINE       sonst
  UNEINIGKEIT
      NICHT_BEWERTET  bei weniger als 2 Quellen — mit einer Quelle gibt
                      es nichts, worueber man uneinig sein koennte
  AUSWAHL
      NICHT_BEWERTET  ohne Registereintrag oder Protokoll laesst sich
                      nicht sagen, ob ausgewaehlt wurde
  SCHEINEINIGKEIT
      ERNST           mehrere Quellen, aber nur eine Wurzel
      NICHT_BEWERTET  eine einzige Quelle
      KEINE           mehrere Quellen mit verschiedenen Wurzeln

AUFRUF
  python -m schablone guete
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Grund(Enum):
    STREUBREITE     = "Streubreite"
    UNEINIGKEIT     = "Uneinigkeit"
    ABSTAND         = "Abstand zur Frage"
    AUSWAHL         = "Auswahl des Berichteten"
    SCHEINEINIGKEIT = "Scheineinigkeit"


KATALOG: Tuple[Grund, ...] = tuple(Grund)          # geschlossen, fuenf


class Schwere(Enum):
    KEINE          = ("keine Bedenken", 0)
    ERNST          = ("ernst", 1)
    SEHR_ERNST     = ("sehr ernst", 2)
    NICHT_BEWERTET = ("nicht bewertet", 0)         # kostet NICHTS

    @property
    def text(self) -> str:
        return self.value[0]

    @property
    def kosten(self) -> int:
        return self.value[1]


@dataclass(frozen=True)
class Befund:
    grund: Grund
    schwere: Schwere
    warum: str                       # Pflicht. Eine Stufe ohne Grund
                                     # ist eine Behauptung.


@dataclass(frozen=True)
class Schaetzung:
    """Was ueber die Schaetzung bekannt ist — nicht ueber ihre Herkunft."""
    name: str
    wert: float
    unten: Optional[float] = None
    oben: Optional[float] = None
    quellen: int = 1
    wurzeln: int = 1
    # FEHLER 34, beim Versuch gefunden, guete an den produktiven Pfad zu
    # haengen: surrogat und spaetes_seltenes_ereignis hatten den
    # Vorgabewert False. Wer die Schaetzung aus einem Eintrag baute, der
    # diese Angaben gar nicht kennt, bekam deshalb
    #     'Abstand zur Frage: keine Bedenken — direkt gemessen'
    # ueber Daten, die das Programm nie gesehen hat. Das ist die zweite
    # Nicht-Gleichung, von innen gebrochen:
    #     geprueft und unbedenklich  !=  nicht bewertet
    # False heisst 'nachgesehen, ist kein Surrogat'. Nicht angegeben
    # heisst None. Der Unterschied kostet hier nichts und rettet die
    # Auskunft.
    surrogat: Optional[bool] = None
    beobachtung_monate: Optional[float] = None
    spaetes_seltenes_ereignis: Optional[bool] = None
    registriert: Optional[bool] = None            # Protokoll/Register?


# ══ Die Bewertung — nach den oben festgelegten Schwellen ══════════════
def bewerten(s: Schaetzung) -> List[Befund]:
    b: List[Befund] = []

    # STREUBREITE
    if s.unten is None or s.oben is None:
        b.append(Befund(Grund.STREUBREITE, Schwere.NICHT_BEWERTET,
                        "kein Intervall angegeben"))
    else:
        enthaelt1 = s.unten <= 1.0 <= s.oben
        spanne = s.oben / s.unten if s.unten > 0 else float("inf")
        if enthaelt1 and spanne > 10:
            b.append(Befund(Grund.STREUBREITE, Schwere.SEHR_ERNST,
                            f"Intervall {s.unten:g} bis {s.oben:g} enthaelt "
                            f"1,0 und spannt Faktor {spanne:.0f}"))
        elif enthaelt1:
            b.append(Befund(Grund.STREUBREITE, Schwere.ERNST,
                            f"Intervall {s.unten:g} bis {s.oben:g} enthaelt "
                            f"1,0 — Nutzen und Schaden beide gedeckt"))
        else:
            b.append(Befund(Grund.STREUBREITE, Schwere.KEINE,
                            f"Intervall {s.unten:g} bis {s.oben:g} liegt "
                            f"ganz auf einer Seite von 1,0"))

    # UNEINIGKEIT
    # FEHLER 21, beim Angriff auf den eigenen Entwurf gefunden:
    # die erste Fassung zaehlte QUELLEN. Drei Abschriften derselben
    # Wurzel ergaben damit 'keine Bedenken' — die Domaene belohnte
    # genau die Scheineinigkeit, die eine Zeile tiefer bestraft wird.
    # Zwei Domaenen desselben Katalogs arbeiteten gegeneinander.
    # Korrigiert: Uneinigkeit ist nur ueber WURZELN beobachtbar.
    # Das ist eine Logikkorrektur, keine Schwellenaenderung.
    if s.wurzeln < 2:
        b.append(Befund(Grund.UNEINIGKEIT, Schwere.NICHT_BEWERTET,
                        f"{s.quellen} Quelle(n), aber nur {s.wurzeln} "
                        f"Wurzel(n) — Abschriften koennen nicht uneinig sein"))
    else:
        b.append(Befund(Grund.UNEINIGKEIT, Schwere.KEINE,
                        f"{s.wurzeln} unabhaengige Wurzeln, keine Streuung "
                        f"gemeldet"))

    # ABSTAND
    kurz = (s.beobachtung_monate is not None
            and s.beobachtung_monate < 3 and s.spaetes_seltenes_ereignis)
    if s.surrogat is None and s.beobachtung_monate is None:
        b.append(Befund(Grund.ABSTAND, Schwere.NICHT_BEWERTET,
                        "weder Surrogatangabe noch Beobachtungsdauer "
                        "bekannt — ueber den Abstand zur Frage laesst "
                        "sich nichts sagen"))
    elif s.surrogat:
        b.append(Befund(Grund.ABSTAND, Schwere.ERNST,
                        "Surrogatgroesse statt der gefragten Groesse"))
    elif kurz:
        b.append(Befund(Grund.ABSTAND, Schwere.ERNST,
                        f"{s.beobachtung_monate:g} Monate Beobachtung fuer "
                        f"ein spaetes, seltenes Ereignis"))
    else:
        b.append(Befund(Grund.ABSTAND, Schwere.KEINE,
                        "direkt gemessen, Dauer angemessen"))

    # AUSWAHL
    if s.registriert is None:
        b.append(Befund(Grund.AUSWAHL, Schwere.NICHT_BEWERTET,
                        "kein Register- oder Protokollstand bekannt"))
    elif s.registriert:
        b.append(Befund(Grund.AUSWAHL, Schwere.KEINE,
                        "vorab registriert"))
    else:
        b.append(Befund(Grund.AUSWAHL, Schwere.ERNST,
                        "nicht vorab registriert"))

    # SCHEINEINIGKEIT — der eigene Beitrag
    if s.quellen < 2:
        b.append(Befund(Grund.SCHEINEINIGKEIT, Schwere.NICHT_BEWERTET,
                        "eine Quelle — es gibt keine Uebereinstimmung, "
                        "die scheinbar sein koennte"))
    elif s.wurzeln < s.quellen:
        b.append(Befund(Grund.SCHEINEINIGKEIT, Schwere.ERNST,
                        f"{s.quellen} Quellen, aber nur {s.wurzeln} "
                        f"Wurzel(n) — Uebereinstimmung unter Abschriften"))
    else:
        b.append(Befund(Grund.SCHEINEINIGKEIT, Schwere.KEINE,
                        f"{s.quellen} Quellen mit {s.wurzeln} verschiedenen "
                        f"Wurzeln"))
    return b


STUFEN = ("S3", "S2", "S1", "S0")


@dataclass
class Guetebericht:
    schaetzung: Schaetzung
    befunde: List[Befund]

    @property
    def abzug(self) -> int:
        return sum(f.schwere.kosten for f in self.befunde)

    @property
    def stufe(self) -> str:
        return STUFEN[min(self.abzug, len(STUFEN) - 1)]

    @property
    def offen(self) -> int:
        return len([f for f in self.befunde
                    if f.schwere is Schwere.NICHT_BEWERTET])

    def zeilen(self) -> List[str]:
        z = [f"{self.schaetzung.name}   Wert {self.schaetzung.wert:g}",
             f"  GUETESTUFE   {self.stufe}   (Abzug {self.abzug}, "
             f"{self.offen} von {len(KATALOG)} Domaenen nicht bewertet)",
             "  KATALOG"]
        for f in self.befunde:
            mk = {"keine Bedenken": "ok  ", "ernst": "AB-1",
                  "sehr ernst": "AB-2", "nicht bewertet": " -- "}[
                      f.schwere.text]
            z.append(f"    [{mk}] {f.grund.value:<24}{f.warum}")
        return z


def pruefen(s: Schaetzung) -> Guetebericht:
    return Guetebericht(s, bewerten(s))


# ══ Praktischer Test: dieselben zehn Fremdfaelle ══════════════════════
# NUR Rohangaben aus den CDC/ACIP-Profilen — keine GRADE-Urteile.
# Fehlende Angaben bleiben leer; nichts wird ergaenzt.
FAELLE: List[Tuple[str, Schaetzung, str]] = [
    ("F01", Schaetzung("Symptomatisches COVID 6M-4J", 0.20, 0.05, 0.77,
                       beobachtung_monate=1.3), "Very Low"),
    ("F02", Schaetzung("Immunbrueckenschluss 6M-4J", 1.19, 1.00, 1.43,
                       surrogat=True), "Moderate"),
    ("F03", Schaetzung("Schwere Ereignisse 6M-4J", 0.66, 0.38, 1.15,
                       spaetes_seltenes_ereignis=True), "Very Low"),
    ("F04", Schaetzung("Reaktogenitaet 6M-4J", 1.20, 0.88, 1.64), "Moderate"),
    ("F05", Schaetzung("Symptomatisches COVID 12-17", 0.11, 0.02, 0.50),
     "Moderate"),
    ("F06", Schaetzung("Immunbrueckenschluss 12-17", 1.1, 0.9, 1.2,
                       surrogat=True), "Moderate"),
    ("F07", Schaetzung("Asymptomatische Infektion 12-17", 0.64, 0.34, 1.22),
     "Low"),
    ("F08", Schaetzung("Schwere Ereignisse 12-17", 1.50, 0.30, 7.40,
                       beobachtung_monate=2,
                       spaetes_seltenes_ereignis=True), "Very Low"),
    ("F09", Schaetzung("Reaktogenitaet 12-17", 5.23, 4.05, 6.76), "High"),
    ("F10", Schaetzung("Symptomatisches COVID 5-11", 0.10, 0.03, 0.31),
     "High"),
]

ABB = {"S3": "High", "S2": "Moderate", "S1": "Low", "S0": "Very Low"}


def bericht() -> List[str]:
    z = ["GUETE — geschlossener Katalog von Abwertungsgruenden", ""]
    z.append("1 · DER KATALOG")
    z.append("")
    for g in KATALOG:
        z.append(f"    {g.name:<18}{g.value}")
    z.append("")
    z.append("    Geschlossen und fest. Zwei Atteste sind dadurch")
    z.append("    vergleichbar: dieselben fuenf Zeilen, jede beantwortet.")
    z.append("")
    z.append("    'nicht bewertet' kostet KEINE Stufe (unbekannt != falsch),")
    z.append("    erscheint aber im Ergebnis. Das Ergebnis ist nie eine")
    z.append("    Zahl allein, sondern Stufe PLUS offene Domaenen.")
    z.append("")

    z.append("2 · EIN VOLLSTAENDIGES BEISPIEL")
    z.append("")
    for zeile in pruefen(FAELLE[7][1]).zeilen():
        z.append("    " + zeile)
    z.append("")

    z.append("3 · PRAKTISCHER TEST — dieselben zehn Fremdfaelle")
    z.append("")
    z.append("    Eingaben: nur Rohangaben aus den CDC/ACIP-Profilen.")
    z.append("    Die GRADE-Stufe bleibt zurueckgehalten, Abbildung wie")
    z.append("    im Vorab-Protokoll festgelegt.")
    z.append("")
    z.append(f"    {'Fall':<6}{'Abzug':>6}{'offen':>7}  {'guete':<11}"
             f"{'GRADE':<11}")
    z.append("    " + "-" * 44)
    treffer = 0
    stufen = []
    for kennung, s, grade in FAELLE:
        r = pruefen(s)
        eigen = ABB[r.stufe]
        stufen.append(eigen)
        ok = "=" if eigen == grade else ""
        treffer += eigen == grade
        z.append(f"    {kennung:<6}{r.abzug:>6}{r.offen:>7}  {eigen:<11}"
                 f"{grade:<11}{ok}")
    verschieden = len(set(stufen))
    z.append("")
    z.append(f"    verschiedene Werte ausgegeben   {verschieden} von 4 "
             f"moeglichen")
    z.append(f"    Uebereinstimmung                {treffer} von 10")
    z.append("")
    z.append("    VORHER war der Wert bei allen zehn identisch (1 von 4).")
    z.append("")
    z += NACHTRAG.strip("\n").splitlines()
    return z


# ══ NACHTRAG — nach dem ersten Lauf, Schwellen NICHT geaendert ════════
NACHTRAG = """
4 · WAS DER LAUF GEZEIGT HAT

    Kappa +0,20 statt 0,00. Die Uebereinstimmung ist von 4/10 auf
    4/10 geblieben — die ZAHL hat sich nicht bewegt, der
    INFORMATIONSGEHALT schon. Ein konstanter Rater hat Kappa 0 per
    Definition, egal wie oft er zufaellig richtig liegt.

    Abweichung nicht zufaellig verteilt: 4 zu hoch, 2 zu niedrig,
    mittlere Verschiebung +0,5 Stufen. Das System ist milder als
    die Fachleute.

5 · DER DEFEKT, DEN DER LAUF AUFGEDECKT HAT

    F01 bekommt High, GRADE sagt Very Low. Das Intervall ist
    0,05 bis 0,77 — spannt den Faktor 15, enthaelt aber nicht 1,0.
    Meine vorab festgelegte Regel prueft die Weite NUR, wenn das
    Intervall 1,0 enthaelt.

    Das ist falsch: ein sehr weites Intervall ist auch dann
    unpraezise, wenn es ganz auf einer Seite liegt. Der Fehler war
    schon beim Festlegen der Schwelle drin.

    NICHT JETZT KORRIGIERT. Eine Schwelle nach Blick auf die
    Antwort zu aendern, ist Anpassung an das Ergebnis — genau das,
    was R5 und R16 verbieten. Die naechste Fassung legt vorher
    fest: Weite unabhaengig von der Lage bewerten, Faktor > 10 als
    ernst, > 25 als sehr ernst. Dann ein neuer Lauf.

6 · WAS DIESER KORPUS NICHT ZEIGEN KANN

    Drei der fuenf Domaenen sind bei allen zehn Faellen NICHT
    BEWERTET: alle Faelle sind Einzelstudien ohne Registerangabe.
    Nur STREUBREITE und ABSTAND haben ueberhaupt gearbeitet.

    Vor allem: SCHEINEINIGKEIT — der einzige Grund, den GRADE nicht
    hat — konnte in keinem einzigen Fall greifen. Der eigene Beitrag
    bleibt auf diesem Korpus ungeprueft.
"""
