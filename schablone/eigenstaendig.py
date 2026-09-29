"""
eigenstaendig.py — kann aus dem Werk eines LLM ein eigenes Werk werden,
das das LLM kontrolliert?

DIE BEHAUPTUNG, DIE HIER GEPRUEFT WIRD

  'Es ist egal, ob ein LLM unser System baut. Wenn die Struktur
   selbstlernend ist, entfernt sie sich von ihrem Ursprung.'

  Die Behauptung ist nicht abwegig. Compiler werden seit sechzig
  Jahren so gebaut. Das Urmeter war eine fehlerhafte Meridianmessung
  und wurde spaeter gegen die Lichtgeschwindigkeit neu definiert.
  Herkunft ist kein Wahrheitsargument — genau der Grundsatz dieses
  Systems, nur auf das System selbst angewandt.

  Aber sie hat eine PRUEFBARE Konsequenz. Die wird hier gemessen.

WAS LERNEN BRAUCHT

  Lernen braucht ein Fehlersignal. Die Frage ist nicht, OB das
  System lernt, sondern WOHER das Signal kommt:

      aus dem LLM                -> zirkulaer, der Fehler ueberlebt
      aus der eigenen Konsistenz -> findet nur WIDERSPRUECHE, nie
                                    durchgaengige Falschheit
      von aussen                 -> dann arbeitet nicht das Lernen,
                                    sondern der Kontakt nach aussen

  Selbstlernen ist keine QUELLE von Korrektur. Es ist ein GETRIEBE
  fuer eine. Ein Getriebe ohne Motor dreht sich trotzdem — es
  konvergiert, nur gegen den eigenen Attraktor.

DER HARTE GEGENFALL

  Ken Thompson, 'Reflections on Trusting Trust' (1984): ein Compiler,
  der eine Hintertuer einbaut UND den Einbaumechanismus in jeden
  Compiler mitkopiert, den er uebersetzt. Der Fehler ueberlebt jede
  VOLLSTAENDIGE Neuschreibung des Quelltexts, weil er dort nicht
  steht.

  Das einzige bekannte Gegenmittel ist Diverse Double-Compiling
  (Wheeler 2005/2009) und verlangt einen ZWEITEN, unabhaengig
  entstandenen Compiler. Nicht mehr Iteration. Nicht besseres
  Lernen. EINEN ZWEITEN URSPRUNG — die zweite Hand aus S3, auf das
  System selbst angewandt.

DIE ZAHL, UM DIE ES WIRKLICH GEHT

  Zwei Pruefer multiplizieren ihre blinden Flecken nur, wenn die
  Flecken UNABHAENGIG sind. Zwei Pruefer aus derselben Hand tun das
  nicht. Der Abschnitt 4 misst, wie viel ein zweiter Pruefer bei
  welcher Abhaengigkeit noch bringt.

AUFRUF
  python -m schablone eigenstaendig
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ── Modellparameter — offen, damit sie angreifbar sind ────────────────
ARTEN = 40              # Fehlerarten, die ueberhaupt vorkommen koennen
BLIND = 0.40            # Anteil, den ein Pruefer NICHT sehen kann
NEU_PRO_RUNDE = 3       # Fehler, die beim Weiterbauen entstehen
FINDEQUOTE = 0.80       # wie oft ein Pruefer einen SICHTBAREN faengt
RUNDEN = 60
LAEUFE = 300            # gemittelt, damit keine Einzelziehung erzaehlt
THOMPSON = 0.15         # Anteil der Arten nach Thompson-Art:
                        # unsichtbar UND ueberlebt jeden Neuschrieb


@dataclass
class Lauf:
    echte: List[float] = field(default_factory=list)
    gemessene: List[float] = field(default_factory=list)
    blindanteil: List[float] = field(default_factory=list)
    thompson: List[float] = field(default_factory=list)


def _blickfeld(r: random.Random) -> List[bool]:
    s = [True] * int(ARTEN * (1 - BLIND))
    s += [False] * (ARTEN - len(s))
    r.shuffle(s)
    return s


def _zweiter(r: random.Random, erster: List[bool], kopplung: float
             ) -> List[bool]:
    """Ein zweiter Pruefer. kopplung=1 heisst: derselbe blinde Fleck
    wie der erste (zwei Pruefer aus derselben Hand). kopplung=0 heisst:
    unabhaengig entstanden."""
    frisch = _blickfeld(r)
    return [erster[i] if r.random() < kopplung else frisch[i]
            for i in range(ARTEN)]


def einmal(r: random.Random, extern_alle: Optional[int] = None,
           neuschrieb_in: Optional[int] = None,
           zweite_hand_ab: Optional[int] = None,
           kopplung: float = 0.0) -> Lauf:
    sicht1 = _blickfeld(r)
    # Thompson-Arten: fuer JEDEN Pruefer unsichtbar, ueberleben alles
    tarten = set(r.sample(range(ARTEN), int(ARTEN * THOMPSON)))
    for a in tarten:
        sicht1[a] = False
    sicht2 = _zweiter(r, sicht1, kopplung)
    for a in tarten:
        sicht2[a] = False           # auch die zweite Hand sieht sie nicht
    blind_urspruenglich = [not sicht1[i] for i in range(ARTEN)]

    bestand: List[int] = []
    L = Lauf()
    for runde in range(RUNDEN):
        for _ in range(NEU_PRO_RUNDE):
            bestand.append(r.randrange(ARTEN))

        if neuschrieb_in is not None and runde == neuschrieb_in:
            # Alles neu geschrieben — nur die Thompson-Arten ueberleben,
            # weil sie nicht im Quelltext stehen.
            bestand = list(dict.fromkeys(a for a in bestand if a in tarten))

        gefunden, rest = 0, []
        zweite_aktiv = (zweite_hand_ab is not None and runde >= zweite_hand_ab)
        for a in bestand:
            if a in tarten:
                # Eine Thompson-Art findet KEIN Blick in den Quelltext.
                # Was sie findet, ist der VERGLEICH zweier unabhaengig
                # entstandener Systeme (Wheeler, Diverse Double-Compiling):
                # ein Unterschied faellt nur auf, wenn die zweite Hand den
                # Fehler nicht teilt. Genau darin liegt ihr ganzer Wert.
                treffer = (zweite_aktiv
                           and r.random() < (1 - kopplung) * FINDEQUOTE)
            else:
                treffer = ((sicht1[a] or (zweite_aktiv and sicht2[a]))
                           and r.random() < FINDEQUOTE)
            if treffer:
                gefunden += 1
            else:
                rest.append(a)
        bestand = rest

        if extern_alle and runde % extern_alle == 0:
            offen = [i for i in range(ARTEN) if not sicht1[i]
                     and i not in tarten]
            if offen:
                sicht1[r.choice(offen)] = True

        L.echte.append(len(bestand))
        L.gemessene.append(gefunden)
        b = [a for a in bestand if blind_urspruenglich[a]]
        L.blindanteil.append(len(b) / len(bestand) if bestand else 0.0)
        L.thompson.append(len([a for a in bestand if a in tarten]))
    return L


def mitteln(keim: int = 7, **kw) -> Lauf:
    r = random.Random(keim)
    s = [[0.0] * RUNDEN for _ in range(4)]
    for _ in range(LAEUFE):
        L = einmal(r, **kw)
        for i, reihe in enumerate((L.echte, L.gemessene, L.blindanteil,
                                   L.thompson)):
            for j, v in enumerate(reihe):
                s[i][j] += v
    return Lauf(*[[x / LAEUFE for x in reihe] for reihe in s])


def balken(werte: List[float], hoehe: int = 7, breite: int = 56,
           deckel: Optional[float] = None) -> List[str]:
    schritt = max(1, len(werte) // breite)
    p = werte[::schritt][:breite]
    oben = deckel if deckel is not None else max(p + [1e-9])
    return ["".join("█" if v >= oben * h / hoehe else " " for v in p)
            for h in range(hoehe, 0, -1)]


# ══ Selbstpruefung: welche Teile sind reines Erbe? ════════════════════
BAUSTEINE: List[Tuple[str, int, str, str]] = [
    ("Uebergangstabelle", 3, "definitorisch",
     "Probe, Mutanten, metamorphe Probe greifen sie an"),
    ("fuenf Nicht-Gleichungen", 0, "definitorisch",
     "kann nicht falsch sein, nur nutzlos — Definitionen erben nichts"),
    ("R1-R18 Regeltexte", 2, "empirisch",
     "47 Faelle + 96 Mutanten — beide von derselben Hand"),
    ("Kriterium 'zwei disjunkte Wurzeln'", 0, "empirisch",
     "keine einzige Pruefung greift es an — reines Erbe"),
    ("Stufenleiter S0-S3", 1, "definitorisch",
     "Monotonie metamorph geprueft, die HOEHE nie"),
    ("Toleranz-vor-Daten", 2, "definitorisch",
     "Standard aus der Praeregistrierung, ausserhalb entstanden"),
    ("Abdeckungszahl", 0, "empirisch",
     "an 7 selbstgewaehlten Faellen gemessen"),
    ("Mutationsverfahren", 3, "ausserhalb entstanden",
     "AST-Mutation ist aelter als dieses System"),
    ("metamorphe Invarianten M1-M5", 1, "empirisch",
     "Verfahren von aussen, die fuenf Beziehungen von mir"),
    ("Trag-Anteil / K|A", 0, "empirisch",
     "keine Gegenprobe, kein Fall von aussen"),
]


def bericht() -> List[str]:
    z = ["EIGENSTAENDIG — kann das Werk seinen Ursprung ueberholen?", ""]
    z.append(f"  {ARTEN} Fehlerarten. Ein Pruefer ist fuer {BLIND*100:.0f} % "
             f"blind. Jede Runde entstehen")
    z.append(f"  {NEU_PRO_RUNDE} neue Fehler; was der Pruefer sieht, faengt "
             f"er zu {FINDEQUOTE*100:.0f} %.")
    z.append(f"  {THOMPSON*100:.0f} % der Arten sind nach Thompson-Art: fuer "
             f"JEDEN Pruefer unsichtbar")
    z.append(f"  und ueberleben jeden Neuschrieb. {RUNDEN} Runden, "
             f"{LAEUFE} Laeufe gemittelt.")
    z.append("")

    a = mitteln()

    z.append("1 · NUR SELBSTLERNEN — WAS DIE PROBE MELDET")
    z.append("")
    for zeile in balken(a.gemessene, deckel=max(a.gemessene)):
        z.append("      " + zeile)
    z.append(f"      Runde 1: {a.gemessene[0]:.1f}   ->   "
             f"Runde {RUNDEN}: {a.gemessene[-1]:.1f}    unveraendert gesund")
    z.append("")
    z.append("   WAS WIRKLICH IM BESTAND IST")
    z.append("")
    for zeile in balken(a.echte, deckel=max(a.echte)):
        z.append("      " + zeile)
    z.append(f"      Runde 1: {a.echte[0]:.1f}   ->   "
             f"Runde {RUNDEN}: {a.echte[-1]:.1f}")
    z.append("")
    z.append(f"      Anteil im blinden Fleck   Runde 1 "
             f"{a.blindanteil[0]*100:>5.1f} %   ->   "
             f"Runde {RUNDEN} {a.blindanteil[-1]*100:>5.1f} %")
    z.append("")
    z.append("   Die gemeldete Zahl ist ein ZUFLUSS, der Bestand ein")
    z.append("   LAGER. Der Zufluss bleibt ruhig, waehrend das Lager")
    z.append("   waechst — und was darin liegt, ist am Ende fast")
    z.append("   ausschliesslich das, was die Probe nie sehen konnte.")
    z.append("   Selbstlernen senkt nicht die Fehlerzahl. Es sortiert")
    z.append("   die Fehler nach Unsichtbarkeit.")
    z.append("")

    z.append("2 · WAS KONTAKT NACH AUSSEN AENDERT")
    z.append("")
    z.append(f"    {'ein Fall von aussen alle ... Runden':<36}"
             f"{'Bestand am Ende':>18}")
    z.append("    " + "-" * 54)
    z.append(f"    {'nie':<36}{a.echte[-1]:>18.1f}")
    for takt in (20, 10, 5, 2, 1):
        e = mitteln(extern_alle=takt)
        z.append(f"    {'alle ' + str(takt):<36}{e.echte[-1]:>18.1f}")
    t = mitteln(extern_alle=1)
    z.append("")
    z.append(f"    Auch bei JEDER Runde bleibt ein Rest von "
             f"{t.echte[-1]:.1f} — davon")
    z.append(f"    {t.thompson[-1]:.1f} nach Thompson-Art. Aeussere Faelle "
             f"heben den blinden")
    z.append("    Fleck auf, aber nicht das, was sich vor jedem Pruefer")
    z.append("    versteckt. Dafuer gibt es nur ein Mittel, Abschnitt 4.")
    z.append("")

    z.append("3 · DER KOMPLETTE NEUSCHRIEB")
    z.append("")
    c = mitteln(neuschrieb_in=30)
    z.append("    In Runde 31 wird alles neu geschrieben.")
    z.append("")
    z.append(f"    {'Runde':<10}{'ohne':>10}{'mit Neuschrieb':>18}"
             f"{'davon Thompson':>18}")
    z.append("    " + "-" * 56)
    for rr in (29, 30, 31, 35, 45, 59):
        z.append(f"    {rr+1:<10}{a.echte[rr]:>10.1f}{c.echte[rr]:>18.1f}"
                 f"{c.thompson[rr]:>18.1f}")
    z.append("")
    z.append("    Der Neuschrieb raeumt viel weg und trifft genau das")
    z.append("    nicht, worauf es ankommt. Was ueberlebt, steht nicht")
    z.append("    im Quelltext — deshalb findet es kein Blick hinein.")
    z.append("")

    z.append("4 · DIE ZWEITE HAND — UND WAS SIE WERT IST")
    z.append("")
    z.append("    Ein zweiter Pruefer ab Runde 31. KOPPLUNG sagt, wie")
    z.append("    sehr sein blinder Fleck dem ersten gleicht:")
    z.append("    0,0 = unabhaengig entstanden, 1,0 = dieselbe Hand.")
    z.append("")
    z.append(f"    {'Kopplung':<12}{'Bestand':>10}{'davon Thompson':>17}"
             f"{'besser als allein':>20}")
    z.append("    " + "-" * 59)
    allein = a.echte[-1]
    z.append(f"    {'keine 2.':<12}{allein:>10.1f}{a.thompson[-1]:>17.1f}"
             f"{0:>19} %")
    for k in (1.0, 0.9, 0.6, 0.3, 0.0):
        e = mitteln(zweite_hand_ab=30, kopplung=k)
        d = (allein - e.echte[-1]) / allein * 100
        z.append(f"    {k:<12.1f}{e.echte[-1]:>10.1f}{e.thompson[-1]:>17.1f}"
                 f"{d:>19.0f} %")
    z.append("")
    z.append("    Das ist die Antwort auf die Frage. Ein zweiter Pruefer")
    z.append("    aus DERSELBEN Hand bringt fast nichts — er ist genau")
    z.append("    dort blind, wo der erste es ist. Ein unabhaengig")
    z.append("    entstandener bringt ein Vielfaches. Nicht die ANZAHL")
    z.append("    der Pruefer entscheidet, sondern ihre UNABHAENGIGKEIT.")
    z.append("")
    z.append("    Dieselbe Rechnung wie bei disjunkten Quellwurzeln —")
    z.append("    nur auf das Pruefsystem selbst angewandt.")
    z.append("")

    z.append("5 · SELBSTPRUEFUNG — WELCHE TEILE SIND REINES ERBE?")
    z.append("")
    z.append("    Auf wie vielen UNABHAENGIGEN Wegen haette der Baustein")
    z.append("    scheitern koennen? 0 heisst nicht 'falsch'. Es heisst:")
    z.append("    uebernommen und nie angegriffen.")
    z.append("")
    z.append(f"    {'Baustein':<36}{'Wege':>5}   Art")
    z.append("    " + "-" * 68)
    for name, wege, art, _ in BAUSTEINE:
        z.append(f"    {name:<36}{wege:>5}   {art}"
                 + ("  <-" if wege == 0 else ""))
    erbe = [b for b in BAUSTEINE if b[1] == 0]
    emp = [b for b in erbe if b[2] == "empirisch"]
    z.append("")
    z.append("    DEFINITORISCHE Bausteine mit null Wegen sind")
    z.append("    unbedenklich — eine Definition kann nicht falsch sein,")
    z.append("    nur unbrauchbar. Sie erbt nichts vom Erbauer.")
    z.append("")
    z.append(f"    EMPIRISCH und ungeprueft: {len(emp)} von {len(BAUSTEINE)}")
    for name, _, _, grund in emp:
        z.append(f"      {name}")
        z.append(f"        {grund}")
    z.append("")
    z.append("    Das ist die Liste, auf der das Erbe tatsaechlich sitzt.")
    z.append("    Sie ist kurz, und sie ist benennbar — das ist der Teil")
    z.append("    der Behauptung, der sich haelt.")
    return z
