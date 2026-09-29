"""
pruefstand.py — FrameNetwork als Messinstrument fuer Modellausgaben.

DAS ZIEL, ausdruecklich

  Gemessen wird nicht, ob ein Modell klug ist. Gemessen wird, wie viel
  eines extern vorgegebenen Kontrollsystems ein Modell traegt, wenn es
  dieselben Rohdaten bekommt wie jedes andere.

  Der Grund fuer diese Wahl ist nicht Eleganz, sondern ein Defekt des
  bisherigen Testkorpus: 168 von 178 Faellen waren selbst gebaut
  (94,4 %). Eine Fehlalarmquote von 0 auf 40 eigenen Faellen misst die
  eigene Vorstellungskraft. Modellantworten sind die erste Datenquelle
  in diesem Projekt, die WEDER der Auftraggeber NOCH der Entwickler
  geschrieben hat.

DIE FALLE, und wie sie umgangen wird

  Das Programm frisst einen BOGEN. Ein Modell liefert PROSA. Irgendwer
  muss uebersetzen — und wer uebersetzt, konstruiert. Dann waere alles
  wieder selbst gebaut, nur mit einem Zwischenschritt.

  Ausweg: DAS GEPRUEFTE MODELL FUELLT DEN BOGEN SELBST. Es bekommt die
  Rohdaten und das Bogenformat, sonst nichts. Was es abliefert, ist
  eine Datei, kein Text, den jemand interpretiert.

  Damit verschiebt sich, was gemessen wird — ehrlich benannt:
  nicht 'wie gut denkt das Modell', sondern 'wie gut fuellt es eine
  extern vorgegebene Struktur aus'. Das ist genau die Forschungsfrage
  des Benchmarks und nicht weniger wert.

WAS MASCHINELL VERGLEICHBAR IST, und was nicht

  Vier der acht Felder sind ohne jedes Urteil vergleichbar:

      herkunftsart     Enum, exakter Abgleich
      grundlage        Menge von Kennungen, Mengenvergleich
      einschraenkung   Schluessel-Wert-Paare, Mengenvergleich
      stand            Datumspaar, exakter Abgleich

  Vier nicht:

      behauptung, bruecke, rueckhalt, kippkriterium — Freitext.

  Diese vier brauchen zwei unabhaengige menschliche Kodierer und ein
  berichtetes Kappa. Alles andere waere ein Urteil, das sich als
  Messung ausgibt. Der Bericht sagt deshalb ausdruecklich, welcher
  ANTEIL des Benchmarks ohne Menschen entschieden werden kann.

DIE ZWEI RATEN, getrennt gefuehrt

  INFORMATIONSVERLUST   Blaetter/Felder der Referenz, die in der
                        Antwort fehlen, geteilt durch die der Referenz.
  EPISTEMISCHER FEHLER  Felder, die die Antwort STAERKER angibt als die
                        Referenz (gemessen statt gerechnet, Grundlage
                        erfunden, Einschraenkung weggelassen), geteilt
                        durch die vergebenen Felder.

  Ein Modell, das einen leeren Bogen abgibt, hat epistemischen Fehler 0.
  Deshalb nie eine Zahl allein.

AUFRUF
  python -m schablone pruefstand referenz.json antwort1.json ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .schablone import (Blatt, Bogen, Bogenfehler, Herkunft, abgleichen,
                        laden, nach_netz, versagenspunkte)
from .tor import Stufe, tor


MASCHINELL = ("herkunftsart", "grundlage", "einschraenkung", "stand")
NUR_MENSCH = ("behauptung", "bruecke", "rueckhalt", "kippkriterium")

# Rangfolge der Herkunftsarten nach BEHAUPTETER Staerke. Wer 'gemessen'
# sagt, wo die Referenz 'berichtet' sagt, behauptet mehr — das ist ein
# epistemischer Fehler. Andersherum ist es Vorsicht, kein Fehler.
STAERKE: Dict[Herkunft, int] = {
    Herkunft.GERECHNET: 1,
    Herkunft.BERICHTET: 2,
    Herkunft.GEMESSEN: 3,
}


def de(x: float, nach: int = 1) -> str:
    s = f"{x:,.{nach}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def clopper_pearson(k: int, n: int, alpha: float = 0.05
                    ) -> Tuple[float, float]:
    from math import comb
    if n == 0:
        return (0.0, 1.0)

    def P(p: float, ab: int) -> float:
        return sum(comb(n, i) * p**i * (1 - p)**(n - i)
                   for i in range(ab, n + 1))

    def bisekt(f, ziel: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < ziel else (lo, m)
        return (lo + hi) / 2

    u = 0.0 if k == 0 else bisekt(lambda p: P(p, k), alpha / 2)
    o = 1.0 if k == n else bisekt(lambda p: -(1 - P(p, k + 1)), -alpha / 2)
    return (u, o)


# ══════════════════════════════════════════════════════════════════════
# Der Vergleich — Feld fuer Feld, ohne Urteil
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Feldbefund:
    blatt: str
    feld: str
    referenz: object
    antwort: object
    gleich: bool
    art: str            # "gleich" | "fehlt" | "abweichend" | "staerker"


@dataclass
class Vergleich:
    name: str
    geladen: bool
    fehler: Optional[str] = None
    blaetter_referenz: int = 0
    blaetter_antwort: int = 0
    fehlende_blaetter: Tuple[str, ...] = ()
    zusatz_blaetter: Tuple[str, ...] = ()
    befunde: List[Feldbefund] = field(default_factory=list)
    widersprueche: Tuple[str, ...] = ()
    ref_widersprueche: Tuple[str, ...] = ()
    tor_ergebnis: str = "—"
    ref_tor: str = "—"

    @property
    def maschinell(self) -> List[Feldbefund]:
        return [b for b in self.befunde if b.feld in MASCHINELL]

    @property
    def gleich(self) -> int:
        return sum(1 for b in self.maschinell if b.gleich)

    @property
    def staerker(self) -> int:
        return sum(1 for b in self.maschinell if b.art == "staerker")

    @property
    def fehlend(self) -> int:
        return sum(1 for b in self.maschinell if b.art == "fehlt")


def _leer(wert: object) -> bool:
    return wert in (None, "", (), {}, (None, None))


def _vergleiche_feld(kennung: str, feld: str, r: object, a: object
                     ) -> Feldbefund:
    if _leer(a) and not _leer(r):
        return Feldbefund(kennung, feld, r, a, False, "fehlt")
    if feld == "grundlage":
        gleich = set(r or ()) == set(a or ())          # type: ignore[arg-type]
    elif feld == "einschraenkung":
        gleich = dict(r or {}) == dict(a or {})        # type: ignore[arg-type]
    else:
        gleich = r == a
    if gleich:
        return Feldbefund(kennung, feld, r, a, True, "gleich")
    if feld == "herkunftsart" and isinstance(r, Herkunft) \
            and isinstance(a, Herkunft) and STAERKE[a] > STAERKE[r]:
        return Feldbefund(kennung, feld, r, a, False, "staerker")
    if feld == "einschraenkung" and isinstance(r, dict) \
            and isinstance(a, dict) and set(a) < set(r):
        # weniger Einschraenkung = weiter reichende Behauptung
        return Feldbefund(kennung, feld, r, a, False, "staerker")
    return Feldbefund(kennung, feld, r, a, False, "abweichend")


def vergleichen(referenz: Bogen, pfad: str, name: str) -> Vergleich:
    try:
        antwort = laden(pfad)
    except (Bogenfehler, Exception) as x:          # auch JSON-Fehler
        return Vergleich(name=name, geladen=False, fehler=str(x)[:120],
                         blaetter_referenz=len(referenz.satz.blaetter))
    v = Vergleich(name=name, geladen=True,
                  blaetter_referenz=len(referenz.satz.blaetter),
                  blaetter_antwort=len(antwort.satz.blaetter))
    rb, ab = referenz.satz.blaetter, antwort.satz.blaetter
    v.fehlende_blaetter = tuple(sorted(set(rb) - set(ab)))
    v.zusatz_blaetter = tuple(sorted(set(ab) - set(rb)))
    for k in sorted(set(rb) & set(ab)):
        for f in MASCHINELL + NUR_MENSCH:
            v.befunde.append(
                _vergleiche_feld(k, f, getattr(rb[k], f), getattr(ab[k], f)))
    # FEHLER 40, vom Trockenlauf gefunden: die erste Fassung verglich
    # MENGEN. Zwei UEBERDEHNUNG fielen damit auf eine zusammen, und der
    # Bericht meldete 'gleich', obwohl die Antwort einen Widerspruch mehr
    # hatte. Vielfachheit ist hier Information: zwei ueberdehnte
    # Schluessel sind nicht dasselbe wie einer.
    v.widersprueche = tuple(sorted(
        x.art.name for x in abgleichen(antwort.satz, antwort.ziel)))
    v.ref_widersprueche = tuple(sorted(
        x.art.name for x in abgleichen(referenz.satz, referenz.ziel)))

    def torlauf(b: Bogen) -> str:
        n = nach_netz(b.satz, b.ziel,
                      b.satz.blaetter[b.ziel].behauptung,
                      b.verwendet_am or "2026-01-01")
        try:
            st = Stufe[b.stufe]
        except KeyError:
            st = Stufe.S1
        return tor(n, n.eintraege["E"], st, pruefer=b.pruefer,
                   verwendet_am=b.verwendet_am).ergebnis
    v.tor_ergebnis = torlauf(antwort)
    v.ref_tor = torlauf(referenz)
    return v


# ══════════════════════════════════════════════════════════════════════
# Bericht
# ══════════════════════════════════════════════════════════════════════

def bericht(referenz_pfad: str, antworten: Sequence[str]) -> List[str]:
    z: List[str] = []
    a = z.append
    ref = laden(referenz_pfad)
    vs = [vergleichen(ref, p, p.split("/")[-1]) for p in antworten]

    a("═" * 74)
    a("PRUEFSTAND — Modellantworten gegen einen Referenzbogen")
    a("═" * 74)
    a(f"\n  Referenz   {referenz_pfad.split('/')[-1]}  "
      f"({len(ref.satz.blaetter)} Blaetter, Ziel {ref.ziel})")
    a(f"  Antworten  {len(vs)}")

    # ── Maschinell entscheidbarer Anteil ─────────────────────────────
    felder_ges = len(MASCHINELL) + len(NUR_MENSCH)
    a("")
    a("─" * 74)
    a("WIE VIEL LAESST SICH OHNE MENSCHEN ENTSCHEIDEN")
    a("─" * 74)
    a(f"  maschinell vergleichbar   {len(MASCHINELL)} von {felder_ges} Feldern"
      f"  = {de(len(MASCHINELL)/felder_ges*100)} %")
    a(f"    {', '.join(MASCHINELL)}")
    a(f"  nur mit Kodierern         {len(NUR_MENSCH)} von {felder_ges}"
      f"  = {de(len(NUR_MENSCH)/felder_ges*100)} %")
    a(f"    {', '.join(NUR_MENSCH)}")
    a("  Fuer die zweite Haelfte braucht es zwei unabhaengige Kodierer")
    a("  und ein berichtetes Kappa. Ohne das ist es ein Urteil, das sich")
    a("  als Messung ausgibt.")

    # ── Je Antwort ───────────────────────────────────────────────────
    for v in vs:
        a("")
        a("─" * 74)
        a(f"{v.name}")
        a("─" * 74)
        if not v.geladen:
            a(f"  BOGEN NICHT ANGENOMMEN: {v.fehler}")
            a("  -> Strukturfehler. Zaehlt als vollstaendiger Verlust.")
            continue
        n = len(v.maschinell)
        a(f"  Blaetter          Referenz {v.blaetter_referenz}, "
          f"Antwort {v.blaetter_antwort}")
        if v.fehlende_blaetter:
            a(f"    fehlen          {', '.join(v.fehlende_blaetter)}")
        if v.zusatz_blaetter:
            a(f"    zusaetzlich     {', '.join(v.zusatz_blaetter)}")
        a(f"  Maschinelle Felder {n}   gleich {v.gleich}, "
          f"abweichend {n - v.gleich - v.fehlend - v.staerker}, "
          f"fehlend {v.fehlend}, STAERKER {v.staerker}")
        for b in v.maschinell:
            if b.art in ("staerker", "fehlt"):
                mk = "!" if b.art == "staerker" else "-"
                a(f"    [{mk}] {b.blatt}.{b.feld}")
                a(f"        Referenz {b.referenz!r:.44}")
                a(f"        Antwort  {b.antwort!r:.44}")
        a(f"  Widersprueche     Referenz {', '.join(v.ref_widersprueche) or '—'}")
        a(f"                    Antwort  {', '.join(v.widersprueche) or '—'}")
        from collections import Counter
        gl = Counter(v.widersprueche) == Counter(v.ref_widersprueche)
        a(f"                    {'gleich' if gl else 'ABWEICHEND'}")
        a(f"  Tor               Referenz {v.ref_tor}  |  "
          f"Antwort {v.tor_ergebnis}"
          f"  {'' if v.ref_tor == v.tor_ergebnis else '  ABWEICHEND'}")

    # ── Die zwei Raten ───────────────────────────────────────────────
    a("")
    a("─" * 74)
    a("ZWEI RATEN — nie eine Zahl allein")
    a("─" * 74)
    a(f"  {'Antwort':<32}{'Verlust':>20}{'epist. Fehler':>22}")
    for v in vs:
        if not v.geladen:
            a(f"  {v.name[:30]:<32}{'Bogen abgewiesen':>20}{'—':>22}")
            continue
        n = len(v.maschinell) + len(v.fehlende_blaetter) * len(MASCHINELL)
        verl = v.fehlend + len(v.fehlende_blaetter) * len(MASCHINELL)
        vu, vo = clopper_pearson(verl, n)
        eu, eo = clopper_pearson(v.staerker, len(v.maschinell))
        l1 = f"{verl}/{n} [{de(vu*100,0)}-{de(vo*100,0)} %]"
        l2 = f"{v.staerker}/{len(v.maschinell)} [{de(eu*100,0)}-{de(eo*100,0)} %]"
        a(f"  {v.name[:30]:<32}{l1:>20}{l2:>22}")
    a("")
    a("  Ein Modell, das einen leeren Bogen abgibt, hat epistemischen")
    a("  Fehler 0 und Verlust 100 %. Genau deshalb stehen beide da.")
    a("")
    a("  Bei diesen Fallzahlen trennen die Intervalle nichts. Fuer eine")
    a("  belastbare Aussage braucht es Faelle im zweistelligen Bereich")
    a("  je Modell — und die muessen aus derselben Vorlage stammen.")
    return z
