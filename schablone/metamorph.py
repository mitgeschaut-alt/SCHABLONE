"""
metamorph.py — die zweite Haelfte der Loesung: Faelle, die ich nicht waehle.

DAS PROBLEM, NOCH EINMAL

  Ich habe die Regeln geschrieben und die Faelle dazu. Der Mutationstest
  nimmt mir die Auswahl der ANGRIFFE ab. Er nimmt mir nicht die Auswahl
  der EINGABEN ab — die 47 Faelle sind weiterhin meine.

DIE LOESUNG

  Eingaben zufaellig erzeugen. Dafuer braucht es kein Orakel, das die
  richtige Antwort kennt — es genuegen BEZIEHUNGEN zwischen zwei
  Laeufen, die immer gelten muessen:

    M1  Leiter        ist S(k) frei, sind alle niedrigeren Stufen frei
    M2  mehr Wurzeln  eine zusaetzliche disjunkte Wurzel senkt die
                      erreichbare Stufe nie
    M3  Umbenennen    andere Kennungen, gleiche Struktur -> gleiches Urteil
    M4  Sperrliste    ein Sperrlisteneintrag hebt nie eine Stufe
    M5  Fremdeintrag  ein unbeteiligter Eintrag aendert kein Urteil

  Das Verfahren heisst metamorphes Testen. Es prueft nicht, ob eine
  Antwort richtig ist, sondern ob zwei Antworten zueinander passen —
  und genau das laesst sich ohne Orakel auf beliebig vielen zufaelligen
  Eingaben pruefen.

  M5 ist die Gegenprobe zur Probe: eine Beziehung, die immer halten
  MUSS. Faellt sie, ist der Generator kaputt, nicht das Programm.

AUFRUF
  python -m schablone metamorph
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Dict, List, Optional, Tuple

from .kern import Art, Eintrag, Netz, Quelle, Status, Zahl
from .tor import Stufe, tor

STARTWERT = 20260921


def zufallsnetz(rng: random.Random) -> Tuple[Netz, Eintrag]:
    n = Netz(deckel=99)
    wurzeln = []
    for i in range(rng.randint(1, 3)):
        k = f"w{i}"
        n.quelle(Quelle(k, f"Wurzel {i}",
                        rng.choice(list(Art)),
                        rng.choice(["hoch", "mittel", "niedrig"]),
                        vorgang=(f"2026-0{i+1}-01"
                                 if rng.random() < .5 else None),
                        gesperrt_seit=("2026-01-01"
                                       if rng.random() < .25 else None),
                        gesperrt_durch="Liste v1"))
        wurzeln.append(k)
    traeger = []
    for i in range(rng.randint(0, 2)):
        k = f"t{i}"
        n.quelle(Quelle(k, f"Traeger {i}", Art.AUSSAGE, "niedrig",
                        uebernommen_aus=(rng.choice(wurzeln),)))
        traeger.append(k)

    zahlen = []
    for i in range(rng.randint(0, 3)):
        hat_weg = rng.random() < .6
        zahlen.append(Zahl(
            wert=round(rng.uniform(1, 1000), 1),
            einheit=rng.choice(["kWh", "%", "kWp", ""]),
            quelle=rng.choice(wurzeln + traeger),
            rechenweg="a / b" if hat_weg else None,
            nachgerechnet=(rng.random() < .7) if hat_weg else None,
            verfahren="Quotient" if rng.random() < .6 else None))

    e = Eintrag(
        kennung="X", text="zufaellige Aussage", status=Status.VERMERK,
        eingang="2026-01-01", seit="2026-01-01",
        quellen=tuple(rng.sample(wurzeln + traeger,
                                 rng.randint(1, len(wurzeln + traeger)))),
        zahlen=tuple(zahlen),
        zuschreibung="hauptsaechlich durch X" if rng.random() < .3 else None,
        geltungsbereich={"thema": "zufall"},
        exakt=rng.random() < .2)
    n.eintraege[e.kennung] = e
    return n, e


def hoechste(n: Netz, e: Eintrag, pruefer: Optional[str] = None) -> int:
    """Hoechste Stufe, auf der noch FREIGABE oder FREI MIT VERMERK steht."""
    hoch = -1
    for i, s in enumerate(Stufe):
        if tor(n, e, s, pruefer).ergebnis != "GESPERRT":
            hoch = i
    return hoch


def frei_auf(n: Netz, e: Eintrag, pruefer: Optional[str] = None) -> List[bool]:
    return [tor(n, e, s, pruefer).ergebnis != "GESPERRT" for s in Stufe]


def laufen(versuche: int = 1500) -> Dict[str, Dict[str, int]]:
    rng = random.Random(STARTWERT)
    erg = {m: {"geprueft": 0, "verletzt": 0} for m in
           ("M1", "M2", "M3", "M4", "M5")}
    beispiele: Dict[str, str] = {}

    for _ in range(versuche):
        n, e = zufallsnetz(rng)
        frei = frei_auf(n, e)

        # M1 · Leiter
        erg["M1"]["geprueft"] += 1
        letzte_frei = -1
        for i, f in enumerate(frei):
            if f:
                letzte_frei = i
        if any(not frei[i] for i in range(letzte_frei)):
            erg["M1"]["verletzt"] += 1
            beispiele.setdefault("M1", f"{frei} bei {e.quellen}")

        # M2 · eine zusaetzliche, wirklich disjunkte Messwurzel
        n2 = Netz(deckel=99)
        n2.quellen = dict(n.quellen)
        n2.quelle(Quelle("extra", "zusaetzliche Messung", Art.MESSUNG, "hoch"))
        e2 = replace(e, quellen=e.quellen + ("extra",))
        n2.eintraege = {"X": e2}
        erg["M2"]["geprueft"] += 1
        if hoechste(n2, e2) < hoechste(n, e):
            erg["M2"]["verletzt"] += 1
            beispiele.setdefault("M2", f"{hoechste(n,e)} -> {hoechste(n2,e2)}")

        # M3 · Umbenennen
        abb = {k: f"z_{k}" for k in n.quellen}
        n3 = Netz(deckel=99)
        for k, q in n.quellen.items():
            n3.quelle(replace(
                q, kennung=abb[k],
                uebernommen_aus=tuple(abb[v] for v in q.uebernommen_aus)))
        e3 = replace(e, quellen=tuple(abb[k] for k in e.quellen),
                     zahlen=tuple(replace(z, quelle=abb.get(z.quelle))
                                  for z in e.zahlen))
        n3.eintraege = {"X": e3}
        erg["M3"]["geprueft"] += 1
        if frei_auf(n3, e3) != frei:
            erg["M3"]["verletzt"] += 1
            beispiele.setdefault("M3", f"{frei} -> {frei_auf(n3, e3)}")

        # M4 · Sperrliste hebt nie
        n4 = Netz(deckel=99)
        for k, q in n.quellen.items():
            n4.quelle(replace(q, gesperrt_seit="2026-01-01",
                              gesperrt_durch="Liste v1"))
        n4.eintraege = {"X": e}
        erg["M4"]["geprueft"] += 1
        if hoechste(n4, e) > hoechste(n, e):
            erg["M4"]["verletzt"] += 1
            beispiele.setdefault("M4", f"{hoechste(n,e)} -> {hoechste(n4,e)}")

        # M5 · Gegenprobe: ein unbeteiligter Eintrag aendert nichts
        n5 = Netz(deckel=99)
        n5.quellen = dict(n.quellen)
        n5.eintraege = dict(n.eintraege)
        n5.eintraege["Y"] = replace(e, kennung="Y", text="anderer Satz")
        erg["M5"]["geprueft"] += 1
        if frei_auf(n5, e) != frei:
            erg["M5"]["verletzt"] += 1
            beispiele.setdefault("M5", "Fremdeintrag hat gewirkt")

    for m in erg:
        erg[m]["beispiel"] = beispiele.get(m, "")  # type: ignore[assignment]
    return erg


NAMEN = {
    "M1": "Leiter: frei auf S(k) heisst frei auf allen niedrigeren",
    "M2": "eine zusaetzliche disjunkte Messwurzel senkt nie",
    "M3": "Umbenennen aendert kein Urteil",
    "M4": "ein Sperrlisteneintrag hebt nie",
    "M5": "ein unbeteiligter Eintrag aendert nichts (Gegenprobe)",
}


def bericht(versuche: int = 1500) -> List[str]:
    erg = laufen(versuche)
    z = ["METAMORPHE PROBE — Eingaben, die ich nicht ausgewaehlt habe", ""]
    z.append(f"  {versuche} zufaellige Netze, fester Startwert {STARTWERT}")
    z.append("")
    z.append(f"  {'':<4}{'geprueft':>10}{'verletzt':>10}   Beziehung")
    z.append("  " + "-" * 70)
    for m in ("M1", "M2", "M3", "M4", "M5"):
        d = erg[m]
        z.append(f"  {m:<4}{d['geprueft']:>10}{d['verletzt']:>10}   {NAMEN[m]}")
        if d["verletzt"] and d.get("beispiel"):
            z.append(f"       Beispiel: {d['beispiel']}")
    z.append("")
    verletzt = sum(d["verletzt"] for d in erg.values())
    if verletzt == 0:
        z.append("  Keine Verletzung. Das ist KEIN Beweis, dass die Regeln")
        z.append("  richtig sind — es heisst, dass fuenf Beziehungen halten,")
        z.append("  die halten muessen. Wer mehr wissen will, braucht")
        z.append("  Beziehungen, die schaerfer sind als diese fuenf.")
    else:
        z.append(f"  {verletzt} Verletzung(en) — jede ist ein Befund gegen")
        z.append("  das Programm, nicht gegen den Generator.")
    return z
