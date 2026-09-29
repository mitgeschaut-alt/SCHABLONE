"""
FRAME-NETWORK — kontrollierte epistemische Buchhaltung.

Was das Programm tut
  Es nimmt Aussagen entgegen, zerlegt sie, verfolgt ihre Herkunft,
  prueft ihren INHALT (nie ihre Quelle), fuehrt Buch ueber das, was
  ungeprueft wartet, und gibt zu jeder Freigabe ein Attest aus, das
  auch nennt, was NICHT geprueft wurde.

Was es nicht tut
  Es garantiert keine Richtigkeit. Alle Regeln pruefen die BEZIEHUNG
  zwischen Aussage und Quelle; keine prueft die Quelle. Gegen einen
  ehrlichen Vorverarbeiter, der sich irrt, hilft es vollstaendig; gegen
  einen unehrlichen hilft nur ein zweiter Datenstrom aus anderer Hand —
  deshalb verlangt Stufe S3 ihn ausdruecklich.

Aufruf
  python -m schablone pruefen [datei.json]
  python -m schablone bilanz  [datei.json]
  python -m schablone proben
"""

from .kern import (Art, Aufnahmefehler, Eintrag, Fassung, Modellform, Netz,
                   Quelle, Status, Uebergangsfehler, Variable, Zahl)
from .regeln import ALLE as ALLE_REGELN, Befund
from .tor import (AUSSERHALB, Attest, Kettenbericht, Pruefbar, Strang,
                  Stufe, deckt, kette, tor)
from .buch import Bilanz, bilanz, faellige, zwei_raten
from .schablone import Blatt, Herkunft, Satz, Widerspruch, abgleichen

VERSION = "2.7"

__all__ = [
    "Art", "Aufnahmefehler", "Eintrag", "Fassung", "Modellform", "Netz",
    "Quelle", "Status", "Uebergangsfehler", "Variable", "Zahl",
    "ALLE_REGELN", "Befund",
    "Attest", "Kettenbericht", "Pruefbar", "Strang", "Stufe", "kette", "tor",
    "AUSSERHALB", "deckt",
    "Bilanz", "bilanz", "faellige", "zwei_raten", "VERSION",
    "Blatt", "Herkunft", "Satz", "Widerspruch", "abgleichen",
]
