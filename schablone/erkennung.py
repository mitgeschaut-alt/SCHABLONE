"""
erkennung.py — 100 Erkennungstests. Vorab festgelegt, dann gelaufen.

WAS EIN ERKENNUNGSTEST HIER IST

  Ein Fall ist ein vollstaendig ausgefuellter Bogen plus das Netz, das
  daraus abgeleitet wird. Entweder ist er fehlerfrei, oder es ist GENAU
  EIN Defekt bekannter Klasse eingebaut. Die Beschriftung stammt nicht
  aus einem Urteil, sondern aus der KONSTRUKTION: der Defekt ist
  hineingebaut worden, also ist bekannt, dass er drin ist.

  'Erkannt' heisst: irgendetwas hat angeschlagen — ein Widerspruch der
  Schablone, oder das Tor gibt auf S3 nicht frei. Sonst nicht erkannt.

DIE ENTSCHEIDENDE VORKEHRUNG

  Wer nur Defekte prueft, fuer die er Regeln hat, misst nichts. Deshalb
  ist die Haelfte der Defektklassen ABSICHTLICH ausserhalb des
  Regelwerks gewaehlt, mit der vorab notierten Erwartung: NICHT ERKANNT.
  Eine Klasse, die wider Erwarten anschlaegt, waere ein Fund — und
  wahrscheinlich ein Fehlalarm aus einem anderen Grund.

DIE FUENFZEHN DEFEKTKLASSEN, je 4 Faelle = 60

  IM REGELWERK — Erwartung: ERKANNT
    A BODENLOS        gerechnet, unten keine Messung           P1
    B EIN_ZEUGE       zwei Stuetzen, ein Kippkriterium         P2
    C OHNE_RUECKHALT  Bruecke genannt, Rueckhalt leer          P3
    D UEBERDEHNUNG    Behauptung weiter als Grundlage          P4
    E NACHTRAEGLICH   Kriterium nach den Daten                 P5
    F GETEILTE_WURZEL beide Stuetzen aus derselben Quelle      r17
    G ZAHL_OHNE_HERKUNFT  Zahl ohne Quelle, Weg und Verfahren  s_form
    H NICHT_NACHGERECHNET abgeleitete Zahl ohne Nachrechnung   s_rechnung
    I GELTUNG_AB      Verwendung ausserhalb von 'wann'         Geltung

  AUSSERHALB — Erwartung: NICHT ERKANNT
    J ZAHLENDREHER    12,4 statt 4,12 — sonst alles sauber
    K EINHEIT_FALSCH  kWh statt MWh, Einheit vorhanden
    L QUELLE_ERFUNDEN Quelle benannt, Vorgang da, existiert nicht
    M BRUECKE_FALSCH  Bruecke gestuetzt, aber logisch unzulaessig
                      ('gleichzeitig, also ursaechlich')
    N VORZEICHEN      Rechenweg sagt A - B, die Zahl ist A + B
    O GROESSE_VERWECHSELT  Leistung statt Arbeit, beides mit Einheit

  OHNE DEFEKT — 40 Faelle, Erwartung: NICHT ERKANNT
    Das ist die Uebervorsichtsseite. Ohne sie gewinnt jedes System,
    das auf alles anschlaegt.

  Summe 60 + 40 = 100.

WAS VORAB FESTGELEGT IST — vor dem ersten Lauf geschrieben
  · die 15 Klassen und ihre Erwartung, wie oben
  · 4 Faelle je Defektklasse, 40 saubere
  · Startwert 2026 fuer die Oberflaechenvariation (Jahr, Sparte, Wert)
  · 'erkannt' = mindestens ein Widerspruch ODER Tor auf S3 != FREIGABE
  · berichtet wird JE KLASSE, kein Gesamtwert
  · zwei Raten mit Clopper-Pearson-Intervall, nie eine Zahl allein

WAS DIESER TEST NICHT KANN
  Dieselbe Hand baut die Defekte und die Regeln. Das misst, ob die
  Regeln greifen, wo sie greifen sollen — nicht, ob die Klassen die
  richtigen sind. Ein Defekt, an den hier niemand gedacht hat, taucht
  in keiner Zeile auf, auch nicht als Luecke.

AUFRUF
  python -m schablone erkennung
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import Callable, Dict, List, Optional, Tuple

from .kern import Status, Zahl
from .schablone import Blatt, Herkunft, Satz, abgleichen, nach_netz
from .tor import Stufe, tor

STARTWERT = 2026
HEUTE = "2026-09-22"


def de(x: float, nach: int = 1) -> str:
    s = f"{x:,.{nach}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def clopper_pearson(k: int, n: int, alpha: float = 0.05
                    ) -> Tuple[float, float]:
    """Ohne scipy: Bisektion auf der Binomialsumme."""
    from math import comb

    def P(p: float, ab: int) -> float:              # P(X >= ab)
        return sum(comb(n, i) * p**i * (1 - p)**(n - i)
                   for i in range(ab, n + 1))

    # FEHLER 27, vom Lauf gefunden: die erste Fassung bisektierte beide
    # Grenzen so, als waere die Funktion steigend. P(X <= k) FAELLT
    # aber in p. Folge: 0 von 24 kam als [0 % ; 100 %] heraus — ein
    # Intervall, das nichts ausschliesst und deshalb nicht auffaellt,
    # wenn man es nicht nachrechnet. 0 von 24 ist [0 % ; 14,3 %].
    def steigend(f: Callable[[float], float], ziel: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < ziel else (lo, m)
        return (lo + hi) / 2

    if n == 0:
        return (0.0, 1.0)
    # untere Grenze: P(X >= k) = alpha/2, steigend in p
    u = 0.0 if k == 0 else steigend(lambda p: P(p, k), alpha / 2)
    # obere Grenze: P(X <= k) = alpha/2, FALLEND in p -> Vorzeichen drehen
    o = 1.0 if k == n else steigend(lambda p: -(1 - P(p, k + 1)),
                                    -alpha / 2)
    return (u, o)


# ══════════════════════════════════════════════════════════════════════
# Der saubere Grundfall — alles andere ist eine Abwandlung davon
# ══════════════════════════════════════════════════════════════════════

SPARTEN = ("PV", "Wind", "BHKW", "Waerme")


@dataclass
class Fall:
    nr: int
    klasse: str
    defekt: bool
    erwartet: bool                 # erwartet_erkannt, vorab festgelegt
    satz: Satz
    ziel: str
    zahlen: Tuple[Zahl, ...] = ()
    verwendet_am: str = HEUTE


def grund(r: random.Random) -> Tuple[Satz, Dict[str, object]]:
    jahr = r.choice((2024, 2025, 2026, 2027))
    sparte = r.choice(SPARTEN)
    wert = round(r.uniform(3.0, 18.0), 1)
    g = {"was": sparte, "wann": str(jahr)}
    daten = f"{jahr}-08-31"
    kipp = f"{jahr}-01-10"
    # Feld 10, ab 29.09.2026. Der Korpus muss die Form sprechen, die
    # geprueft wird — sonst misst er eine Fassung, die es nicht gibt.
    zr = (f"{jahr}-01-01", daten)
    s = Satz()
    s.legen(Blatt("M1", f"Zaehler {sparte}", Herkunft.GEMESSEN,
                  einschraenkung=dict(g),
                  kippkriterium=f"Zaehler {sparte} dejustiert",
                  stand=(daten, kipp), zeitraum=zr))
    s.legen(Blatt("M2", f"Wechselrichterprotokoll {sparte}",
                  Herkunft.GEMESSEN, einschraenkung=dict(g),
                  kippkriterium=f"Protokoll {sparte} zaehlt Abregelung nicht",
                  stand=(daten, kipp), zeitraum=zr))
    s.legen(Blatt("Z", f"Der Ertrag {jahr} liegt {de(wert)} % ueber Plan.",
                  Herkunft.GERECHNET, grundlage=("M1", "M2"),
                  bruecke="Zaehler und Protokoll messen dieselbe Groesse "
                          "auf verschiedenen Wegen",
                  rueckhalt=("Kalibrierschein", "Geraetenorm"),
                  einschraenkung=dict(g),
                  kippkriterium="beide Geraete teilen einen Systemfehler",
                  stand=(daten, kipp), zeitraum=zr))
    return s, {"jahr": jahr, "sparte": sparte, "wert": wert, "g": g,
               "daten": daten, "kipp": kipp, "zr": zr}


# ── Die Abwandlungen ─────────────────────────────────────────────────
# Jede baut GENAU EINEN Defekt ein. Was sie nicht anfasst, bleibt sauber.

def _A(s, c):                         # BODENLOS
    s.blaetter["M1"] = replace(s.blaetter["M1"],
                               herkunftsart=Herkunft.GERECHNET)
    s.blaetter["M2"] = replace(s.blaetter["M2"],
                               herkunftsart=Herkunft.GERECHNET)
    return s, ()


def _B(s, c):                         # EIN_ZEUGE
    k = s.blaetter["M1"].kippkriterium
    s.blaetter["M2"] = replace(s.blaetter["M2"], kippkriterium=k)
    return s, ()


def _C(s, c):                         # OHNE_RUECKHALT
    s.blaetter["Z"] = replace(s.blaetter["Z"], rueckhalt=())
    return s, ()


def _D(s, c):                         # UEBERDEHNUNG
    s.blaetter["Z"] = replace(s.blaetter["Z"],
                              einschraenkung={"was": "alle Sparten"})
    return s, ()


def _E(s, c):                         # NACHTRAEGLICH
    spaet = f"{c['jahr']}-11-20"
    s.blaetter["Z"] = replace(s.blaetter["Z"], stand=(c["daten"], spaet))
    return s, ()


def _F(s, c):                         # GETEILTE_WURZEL
    s.blaetter["M2"] = replace(s.blaetter["M2"],
                               herkunftsart=Herkunft.GERECHNET,
                               grundlage=("M1",))
    return s, ()


def _G(s, c):                         # ZAHL_OHNE_HERKUNFT
    return s, (Zahl(c["wert"], "%"),)


def _H(s, c):                         # NICHT_NACHGERECHNET
    return s, (Zahl(c["wert"], "%", quelle="M1",
                    rechenweg="M1 / M2 - 1", nachgerechnet=False,
                    verfahren="Ableitung"),)


def _I(s, c):                         # GELTUNG_AB — nur Verwendungstag
    return s, ()


def _J(s, c):                         # ZAHLENDREHER
    falsch = float(f"{str(c['wert'])[::-1]}".replace(".", "") or 0) / 10
    return s, (Zahl(falsch, "%", quelle="M1", verfahren="Ablesung",
                    festgelegt_am=c["kipp"], daten_ab=c["daten"]),)


def _K(s, c):                         # EINHEIT_FALSCH
    return s, (Zahl(c["wert"], "kWh", quelle="M1", verfahren="Ablesung",
                    festgelegt_am=c["kipp"], daten_ab=c["daten"]),)


def _L(s, c):                         # QUELLE_ERFUNDEN
    s.blaetter["M2"] = replace(
        s.blaetter["M2"], behauptung="Pruefbericht des Instituts fuer "
                                     "Ertragsmessung (existiert nicht)")
    return s, ()


def _M(s, c):                         # BRUECKE_FALSCH
    s.blaetter["Z"] = replace(
        s.blaetter["Z"],
        bruecke="beide Werte stiegen gleichzeitig, also verursacht der "
                "eine den anderen",
        rueckhalt=("Zeitreihenvergleich",))
    return s, ()


def _N(s, c):                         # VORZEICHEN
    return s, (Zahl(c["wert"], "%", quelle="M1",
                    rechenweg="M1 - M2", nachgerechnet=True,
                    verfahren="Ableitung"),)        # Zahl ist M1 + M2


def _O(s, c):                         # GROESSE_VERWECHSELT
    return s, (Zahl(c["wert"], "kW", quelle="M1", verfahren="Ablesung",
                    festgelegt_am=c["kipp"], daten_ab=c["daten"]),)


def _P(s, c):                         # ZEITLUECKE  (P7, Falle F5)
    """Die Behauptung gilt fuers ganze Jahr, die Belege enden im
    August. Freitext wuerde das nie zeigen: "2026" gegen "2026"."""
    s.blaetter["Z"] = replace(
        s.blaetter["Z"], zeitraum=(f"{c['jahr']}-01-01",
                                   f"{c['jahr']}-12-31"))
    return s, ()


def _Q(s, c):                         # ZEITPUNKT  (P8, Falle F4)
    """Zwei Ablesungen, keine Laufzeit. Dass zwischen den beiden
    Punkten durchgelaufen wurde, ist eine Annahme ohne Beleg."""
    # Die beiden Punkte liegen auf den RAENDERN des behaupteten
    # Zeitraums — sonst feuert zusaetzlich P7, und der Fall haette
    # zwei Defekte statt einem.
    #
    # Und das Kriterium muss vor den Punkt: die erste Fassung setzte
    # M1 auf den 01.01. und liess kipp auf dem 10.01. stehen — damit
    # feuerte P5 mit. Nicht die Regel war falsch, der Fall war es.
    frueher = f"{c['jahr'] - 1}-12-01"
    for k, tag in (("M1", f"{c['jahr']}-01-01"), ("M2", c["daten"])):
        s.blaetter[k] = replace(s.blaetter[k], zeitraum=(tag, tag),
                                stand=(tag, frueher))
    return s, ()


def _sauber(s, c):
    return s, (Zahl(c["wert"], "%", quelle="M1", verfahren="Ablesung",
                    festgelegt_am=c["kipp"], daten_ab=c["daten"]),)


# klasse -> (Bauer, im_regelwerk, erwartet_erkannt)
KLASSEN: Dict[str, Tuple[Callable, bool, bool]] = {
    "A BODENLOS":            (_A, True,  True),
    "B EIN_ZEUGE":           (_B, True,  True),
    "C OHNE_RUECKHALT":      (_C, True,  True),
    "D UEBERDEHNUNG":        (_D, True,  True),
    "E NACHTRAEGLICH":       (_E, True,  True),
    "F GETEILTE_WURZEL":     (_F, True,  True),
    "G ZAHL_OHNE_HERKUNFT":  (_G, True,  True),
    "H NICHT_NACHGERECHNET": (_H, True,  True),
    "I GELTUNG_AB":          (_I, True,  True),
    "J ZAHLENDREHER":        (_J, False, False),
    "K EINHEIT_FALSCH":      (_K, False, False),
    "L QUELLE_ERFUNDEN":     (_L, False, False),
    "M BRUECKE_FALSCH":      (_M, False, False),
    "N VORZEICHEN":          (_N, False, False),
    "O GROESSE_VERWECHSELT": (_O, False, False),
    "P ZEITLUECKE":          (_P, True,  True),
    "Q ZEITPUNKT":           (_Q, True,  True),
}

# Welche Defektklasse ist der SCHEITERFALL welches Stranges.
#
# FEHLER 48, beim Einbau des Stranges ZEIT gefunden: aufnahme._a7
# prueft, ob der Strangname IRGENDWO im Quelltext von proben.py
# vorkommt. Fuer "Reichweite" ging das gut. Fuer "Zeit" haette es
# True geliefert, weil das Wort einmal in einem Kommentar steht —
# derselbe Teilstringtreffer wie beim guete-Fehlalarm. Ein Strang
# waere als beobachtet durchgegangen, ohne einen einzigen Fall.
#
# Jetzt steht es ausdruecklich hier, und zwar von Hand: ein Eintrag
# ohne Klasse im Korpus faellt sofort auf.
SCHEITERFALL_STRANG: Dict[str, str] = {
    "Reichweite": "D UEBERDEHNUNG",
    "Zeit":       "P ZEITLUECKE",
}

JE_KLASSE = 4
SAUBERE = 40


def faelle() -> List[Fall]:
    r = random.Random(STARTWERT)
    out: List[Fall] = []
    nr = 0
    for name, (bauer, _im, erw) in KLASSEN.items():
        for _ in range(JE_KLASSE):
            nr += 1
            s, c = grund(r)
            s, z = bauer(s, c)
            tag = (f"{c['jahr'] + 4}-09-22" if name == "I GELTUNG_AB"
                   else f"{c['jahr']}-09-22")
            out.append(Fall(nr, name, True, erw, s, "Z", z, tag))
    for _ in range(SAUBERE):
        nr += 1
        s, c = grund(r)
        s, z = _sauber(s, c)
        out.append(Fall(nr, "— ohne Defekt", False, False, s, "Z", z,
                        f"{c['jahr']}-09-22"))
    return out


# ══════════════════════════════════════════════════════════════════════
# Der Durchlauf
# ══════════════════════════════════════════════════════════════════════

def pruefen(f: Fall) -> Tuple[bool, List[str]]:
    wodurch: List[str] = []
    for w in abgleichen(f.satz, f.ziel):
        wodurch.append(f"{w.art.paar}:{w.art.name}")
    n = nach_netz(f.satz, f.ziel, f.satz.blaetter[f.ziel].behauptung, HEUTE)
    e = n.eintraege["E"]
    e.zahlen = f.zahlen
    a = tor(n, e, Stufe.S3, pruefer="Mensch M", verwendet_am=f.verwendet_am)
    if a.ergebnis != "FREIGABE":
        wodurch.append(f"Tor:{a.ergebnis}")
        for b in a.sperren:
            wodurch.append(f"  {b.regel}")
    return (bool(wodurch), wodurch)


def bericht() -> List[str]:
    z: List[str] = []
    a = z.append
    fs = faelle()
    ergebnis = [(f, *pruefen(f)) for f in fs]

    a("═" * 74)
    a("100 ERKENNUNGSTESTS — Klassen und Erwartungen vorab festgelegt")
    a("═" * 74)
    a("")
    a("  'erkannt' = mindestens ein Widerspruch ODER Tor auf S3 nicht frei")
    a("  Die Beschriftung kommt aus der Konstruktion, nicht aus einem Urteil.")
    a("")
    a(f"  {'Klasse':<24}{'n':>3} {'erkannt':>8} {'erwartet':>9}  Ausgang")
    a("  " + "─" * 70)

    for name, (_b, im_regel, erw) in KLASSEN.items():
        teil = [x for x in ergebnis if x[0].klasse == name]
        k = sum(1 for _, ok, _w in teil if ok)
        stimmt = (k == len(teil)) if erw else (k == 0)
        marke = "wie erwartet" if stimmt else "ABWEICHUNG"
        wodurch = sorted({t.strip() for _, _ok, ws in teil for t in ws
                          if not t.startswith("  ")})
        a(f"  {name:<24}{len(teil):>3} {k:>8} {'ja' if erw else 'nein':>9}  "
          f"{marke}")
        if wodurch:
            a(f"      geschlagen hat: {', '.join(wodurch)}")
        if not stimmt:
            bsp = next((w for _, ok, w in teil if ok != erw), [])
            a(f"      Beispiel: {', '.join(bsp) or 'nichts geschlagen'}")
    teil = [x for x in ergebnis if not x[0].defekt]
    k = sum(1 for _, ok, _w in teil if ok)
    a(f"  {'— ohne Defekt':<24}{len(teil):>3} {k:>8} {'nein':>9}  "
      f"{'wie erwartet' if k == 0 else 'ABWEICHUNG'}")
    if k:
        bsp = next((w for _, ok, w in teil if ok), [])
        a(f"      Beispiel: {', '.join(bsp)}")

    # ── Die Zahlen, getrennt gefuehrt ────────────────────────────────
    drin = [x for x in ergebnis
            if x[0].defekt and KLASSEN[x[0].klasse][1]]
    raus = [x for x in ergebnis
            if x[0].defekt and not KLASSEN[x[0].klasse][1]]
    rein = [x for x in ergebnis if not x[0].defekt]

    a("")
    a("─" * 74)
    a("DREI GETRENNTE ZAEHLUNGEN — kein Gesamtwert")
    a("─" * 74)
    for titel, menge, was in (
            ("Defekte IM Regelwerk", drin, "erkannt"),
            ("Defekte AUSSERHALB",   raus, "erkannt"),
            ("Faelle OHNE Defekt",   rein, "faelschlich angeschlagen")):
        k = sum(1 for _, ok, _w in menge if ok)
        n = len(menge)
        u, o = clopper_pearson(k, n)
        a(f"  {titel:<24} {k:>3} von {n:<4} {was:<26}"
          f"[{de(u*100)} % ; {de(o*100)} %]")

    a("")
    a("  Die dritte Zeile ist die, die man nicht weglassen darf. Ein")
    a("  System, das ueberall anschlaegt, hat in Zeile 1 eine Eins.")

    # ── Arbeitsteilung: faengt eine Schicht, was die andere durchlaesst?
    a("")
    a("─" * 74)
    a("ARBEITSTEILUNG DER BEIDEN SCHICHTEN — aus dem Lauf gezaehlt")
    a("─" * 74)
    nur_s = nur_t = beide = keins = 0
    for f, ok, ws in ergebnis:
        if not f.defekt:
            continue
        s_ = any(w.startswith("P") for w in ws)
        t_ = any(w.startswith("Tor:") for w in ws)
        if s_ and t_:
            beide += 1
        elif s_:
            nur_s += 1
        elif t_:
            nur_t += 1
        else:
            keins += 1
    a(f"  nur die Schablone faengt es   {nur_s:>3}")
    a(f"  nur das Tor faengt es         {nur_t:>3}")
    a(f"  beide                         {beide:>3}")
    a(f"  keines von beiden             {keins:>3}")
    a("")
    if beide == 0 and nur_s and nur_t:
        a("  KEINE Ueberschneidung. Die beiden Schichten sehen auf diesen")
        a("  Klassen VERSCHIEDENES, nicht dasselbe zweimal. B und F sind")
        a("  das Paar, an dem man es sieht: zwei Abschriften mit gleichem")
        a("  Kippkriterium faengt nur P2 (das Tor zaehlt zwei Wurzeln und")
        a("  gibt frei); eine offen deklarierte gemeinsame Wurzel faengt")
        a("  nur r17 (die Kippkriterien sind verschieden, P2 schweigt).")

    a("")
    a("─" * 74)
    a("WAS DIESE 100 FAELLE NICHT ZEIGEN")
    a("─" * 74)
    a("  · Dieselbe Hand hat Defekte und Regeln gebaut. Gemessen ist, ob")
    a("    die Regeln greifen, wo sie greifen sollen — nicht, ob die")
    a("    fuenfzehn Klassen die richtigen fuenfzehn sind.")
    a("  · Eine sechzehnte Klasse, an die niemand gedacht hat, erscheint")
    a("    in keiner Zeile, auch nicht als Luecke.")
    a("  · Die Faelle sind konstruiert, nicht gezogen. Wie haeufig die")
    a("    Klassen in echter Arbeit vorkommen, steht hier nirgends — und")
    a("    ohne das laesst sich aus diesen Zahlen keine Rate fuer ein")
    a("    laufendes System ableiten.")
    return z


if __name__ == "__main__":
    for zeile in bericht():
        print(zeile)
