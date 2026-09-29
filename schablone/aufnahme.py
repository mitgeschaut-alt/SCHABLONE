"""
aufnahme.py — der Paragraph ueber Paragraphen.

WOZU

  Eine Abgleichregel der Schablone (P1 bis P6) entscheidet nichts. Ein
  Strang des Tores entscheidet. Dazwischen liegt eine AUFNAHME: aus
  einer Regel wird ein Paragraph.

  Diese Aufnahme war bisher nirgends geregelt. Am 28.09.2026 wurde P4
  zum Strang REICHWEITE befoerdert, und die Bedingungen dafuer standen
  in einem Gespraech statt in einer Tabelle. Beim ersten Durchlauf
  dieser Probe fiel genau diese Aufnahme durch — sie hatte keinen
  Scheiterfall. Der Paragraph hat also zuerst seinen eigenen Verfasser
  erwischt.

DIE SIEBEN BEDINGUNGEN

  A1  EINE DEFINITION      Das Tor rechnet nicht nach, es liest. Zwei
                           Definitionen derselben Sache in einem Lauf
                           waren Fehler 35.
  A2  ABGELEITET           Das Feld, das der Strang liest, darf aus
                           keinem Bogen setzbar sein. Jeder erfolgreiche
                           Angriff lief ueber ein setzbares Feld.
  A3  STUFENBEZUG          Der Strang muss auf mindestens einer Stufe
                           verlangt werden und nicht auf allen. Eine
                           Regel ohne Stufenbezug gehoert nicht ans Tor.
  A4  GEMESSEN             Erkennung und Fehlalarm vorher und nachher.
  A5  REDUNDANZ BEZAHLT    Die Schichtueberlappung steigt. Um wieviel,
                           muss dastehen. Alles zu verbinden sperrt
                           46 von 46 Boegen — gemessen, nicht vermutet.
  A6  REGRESSION HAELT     47/47, 36/36, 0/24, 0/40.
  A7  SCHEITERFALL         Ein Fall, in dem der Strang anschlagen MUSS.
                           Ohne ihn ist der Strang unbeobachtet, nicht
                           bewiesen sicher.

WAS DIESER PARAGRAPH NICHT KANN

  A4, A5 und A6 verlangen Messungen, die ein Mensch veranlassen muss.
  Die Probe prueft nur, ob sie AUFGESCHRIEBEN sind — nicht, ob sie
  stimmen. A1, A2, A3 und A7 sind maschinell entscheidbar.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import erkennung, proben, schablone, tor
from .tor import SPERRT, VERLANGT, Strang, Stufe

# Was eine Aufnahme an Messungen mitbringen muss. Wird von Hand
# eingetragen, wenn ein Strang aufgenommen wird — und zwar VOR der
# Aufnahme, nicht danach.
BELEGT: Dict[str, Dict[str, str]] = {
    "Zeit": {
        "regel": "P7 ZEITLUECKE",
        "feld": "zeitluecke",
        "gemessen": ("Erkennung 36/36 -> 44/44 (zwei neue Klassen P, Q), "
                     "Fehlalarm 0/40 -> 0/40, ausserhalb 0/24 -> 0/24"),
        "redundanz": ("Arbeitsteilung auf 108 Faellen: 20 nur Schablone, "
                      "16 nur Tor, 8 beide, 24 keines. Auf sechs echten "
                      "Modellboegen faellt P5 von 28 Treffern auf 0 — "
                      "die Regel hat dort nie zu Recht gefeuert"),
        "regression": "proben 47/47, 44/44, 0/24, 0/40 am 29.09.2026",
    },
    "Reichweite": {
        "regel": "P4 UEBERDEHNUNG",
        "feld": "reichweite",
        "gemessen": "Erkennung 36/36 -> 36/36, Fehlalarm 0/40 -> 0/40",
        "redundanz": "Schichtueberlappung 0/60 -> 4/60",
        "regression": "47/47, 36/36, 0/24, 0/40 am 28.09.2026",
    },
}

ALTBESTAND = {"Form", "Inhalt", "Rechnung", "Mensch", "2. Hand"}


def _a1_eine_definition() -> Tuple[bool, str]:
    """Das Tor darf nicht selbst abgleichen."""
    src = inspect.getsource(tor)
    ruft = "abgleichen(" in src
    return (not ruft,
            "tor.py ruft abgleichen() nicht auf — eine Definition"
            if not ruft else
            "tor.py ruft abgleichen() auf — zwei Definitionen moeglich")


def _a2_abgeleitet(feld: str) -> Tuple[bool, str]:
    """Das Feld darf aus keinem Bogen gesetzt werden koennen."""
    src = inspect.getsource(schablone._blatt) + inspect.getsource(
        schablone.laden)
    setzbar = f'"{feld}"' in src or f"'{feld}'" in src
    return (not setzbar,
            f"{feld} ist aus keinem Bogen setzbar — abgeleitet"
            if not setzbar else
            f"{feld} kann aus dem Bogen gesetzt werden — angreifbar")


def _a3_stufenbezug(s: Strang) -> Tuple[bool, str]:
    wo = [st.name for st in Stufe if s in VERLANGT[st]]
    gut = 0 < len(wo) < len(Stufe)
    return (gut, f"verlangt auf {', '.join(wo) or '—'}")


def _a7_scheiterfall(s: Strang) -> Tuple[bool, str]:
    """Gibt es einen Fall im Korpus, in dem dieser Strang anschlagen MUSS?

    FEHLER 48. Die erste Fassung suchte den Strangnamen als TEILSTRING
    im Quelltext von proben.py. Fuer "Zeit" war das sofort True — das
    Wort steht dort in einem Kommentar. Ein Strang ohne einen einzigen
    Fall waere als beobachtet durchgegangen.

    Das ist dieselbe Klasse wie der guete-Fehlalarm ("im Tor
    verwendet: True" aus einem Wort im Fliesstext). Zweite Fundstelle,
    also kein Ausrutscher: ein Teilstringtreffer ist kein Beleg.

    Jetzt: ein AUSDRUECKLICH eingetragener Fall im Korpus, der auch
    wirklich existieren muss."""
    klasse = erkennung.SCHEITERFALL_STRANG.get(s.value)
    if not klasse:
        return (False, "KEIN Scheiterfall eingetragen — der Strang ist "
                       "unbeobachtet")
    if klasse not in erkennung.KLASSEN:
        return (False, f"Scheiterfall {klasse!r} eingetragen, aber im "
                       f"Korpus gibt es diese Klasse nicht")
    n = sum(1 for f in erkennung.faelle() if f.klasse == klasse)
    if not n:
        return (False, f"Klasse {klasse!r} erzeugt keinen Fall")
    return (True, f"{n} Faelle der Klasse {klasse}")


def pruefen(s: Strang) -> List[Tuple[str, Optional[bool], str]]:
    b = BELEGT.get(s.value)
    aus: List[Tuple[str, Optional[bool], str]] = []
    aus.append(("A1 eine Definition", *_a1_eine_definition()))
    aus.append(("A2 abgeleitet",
                *(_a2_abgeleitet(b["feld"]) if b else
                  (None, "kein Feld eingetragen"))))
    aus.append(("A3 Stufenbezug", *_a3_stufenbezug(s)))
    for schl, name in (("gemessen", "A4 gemessen"),
                       ("redundanz", "A5 Redundanz bezahlt"),
                       ("regression", "A6 Regression haelt")):
        if b and b.get(schl):
            aus.append((name, True, b[schl]))
        else:
            aus.append((name, None, "nicht aufgeschrieben"))
    aus.append(("A7 Scheiterfall", *_a7_scheiterfall(s)))
    return aus


def bericht() -> List[str]:
    z: List[str] = []
    a = z.append
    a("=" * 72)
    a("AUFNAHMEPARAGRAPH — wann darf aus einer Regel ein Paragraph werden")
    a("=" * 72)
    a("")
    a("  Geprueft werden nur AUFGENOMMENE Straenge, nicht der")
    a(f"  Altbestand ({', '.join(sorted(ALTBESTAND))}).")
    a("")
    neu = [s for s in Strang if s.value not in ALTBESTAND]
    if not neu:
        a("  Keine Aufnahme zu pruefen.")
        return z
    offen = 0
    for s in neu:
        b = BELEGT.get(s.value)
        a(f"  STRANG {s.value}"
          + (f"   aus {b['regel']}" if b else "   OHNE EINTRAG"))
        a("  " + "-" * 68)
        for name, ok, warum in pruefen(s):
            mk = {True: "[ok  ]", False: "[NEIN]", None: "[ -- ]"}[ok]
            if ok is not True:
                offen += 1
            a(f"    {mk} {name:<24}{warum}")
        a("")
    a("  " + "=" * 68)
    a(f"  {offen} Bedingung(en) nicht erfuellt.")
    if offen:
        a("")
        a("  Eine Aufnahme mit offenen Bedingungen ist nicht falsch —")
        a("  sie ist UNGEPRUEFT. Das ist derselbe Unterschied wie")
        a("  'nicht bewertet' gegen 'unbedenklich', und er gilt hier")
        a("  fuer das Programm selbst.")
    return z
