"""
nachrechnen.py — ein vorgelegtes Ergebnis auf eigenem Weg erreichen.

DIE RICHTIGE FRAGE

  Nicht: 'welche Konsequenzen hat die Theorie?'  — das ist unendlich.
  Sondern: 'kann ich DIESES eine Ergebnis selbst erreichen?'

  Das ist etwas voellig anderes, und es ist der einfache Fall: das
  Ziel ist gegeben. Gesucht wird ein Weg dorthin, nicht alle Wege
  ueberallhin. Genau deshalb ist es umsetzbar.

DER UNTERSCHIED, AN DEM ALLES HAENGT

      NACHVOLLZIEHEN  den vorgelegten Rechenweg noch einmal gehen
      NACHRECHNEN     dasselbe Ergebnis auf einem ANDEREN Weg erreichen

  Das erste prueft nichts. Wer die Schritte eines anderen wiederholt,
  wiederholt auch seine Annahmen. Unabhaengig ist eine Pruefung erst,
  wenn sie ANDERE EINGABEN benutzt.

VIER AUSGAENGE, NICHT ZWEI

      REPRODUZIERT     anderer Weg, gleiches Ergebnis innerhalb der
                       VORHER erklaerten Toleranz
      ABWEICHEND       anderer Weg, anderes Ergebnis — der wertvollste
                       Ausgang, und ein Konflikt braucht kein Wertmass
      NUR_NACHGESPIELT es gibt nur den vorgelegten Weg — geprueft ist
                       nichts
      NICHT_ERREICHBAR kein Weg gefunden — und das ist KEINE Widerlegung

  Der letzte Ausgang ist der, an dem die meisten Systeme falsch
  abbiegen. 'Nicht herleitbar' heisst zweierlei, und die beiden sehen
  gleich aus:
      das Ergebnis ist falsch
      mein Methodenvorrat ist unvollstaendig

  Unterscheiden laesst sie nur eine Zahl: die ABDECKUNG. Auf wie viel
  Prozent nachweislich richtiger Ergebnisse kommt das System von
  selbst? Ohne diese Zahl ist 'nicht herleitbar' ein Wert ohne
  Einheit.

AUFRUF
  python -m schablone nachrechnen
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple


def de(x: float, nach: int = 1) -> str:
    """Deutsche Zahl. NICHT per .replace(',', '.') ueber einen Block —
    das erzeugt '72.834.0' (Fehler 17, dritter Fall dieser Art)."""
    s = f"{x:,.{nach}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


class Ausgang(Enum):
    REPRODUZIERT     = "reproduziert"
    ABWEICHEND       = "abweichend"
    NUR_NACHGESPIELT = "nur nachgespielt"
    NICHT_ERREICHBAR = "nicht erreichbar"


@dataclass(frozen=True)
class Methode:
    name: str
    groesse: str
    braucht: Tuple[str, ...]
    rechne: Callable[[Dict[str, float]], float]
    beschreibung: str = ""


@dataclass(frozen=True)
class Behauptung:
    groesse: str
    wert: float
    weg: str                      # Name der vom LLM benutzten Methode
    toleranz: float               # VORHER erklaert
    toleranz_erklaert_am: str


@dataclass
class Pruefbericht:
    behauptung: Behauptung
    ausgang: Ausgang
    eigener_weg: Optional[str] = None
    eigener_wert: Optional[float] = None
    disjunkt_zu: Tuple[str, ...] = ()      # neue, eigene Eingaben
    geteilt: Tuple[str, ...] = ()          # gemeinsame — die Schwachstelle
    erreichbar_stattdessen: List[Tuple[str, str, float]] = field(
        default_factory=list)
    bemerkung: str = ""

    def zeilen(self) -> List[str]:
        b = self.behauptung
        z = [f"{b.groesse} = {b.wert:g}   (Weg: {b.weg}, "
             f"Toleranz {b.toleranz:g}, erklaert am {b.toleranz_erklaert_am})",
             f"  AUSGANG   {self.ausgang.value.upper()}"]
        if self.eigener_weg:
            z.append(f"  eigener Weg   {self.eigener_weg}")
            z.append(f"  ergibt        {self.eigener_wert:g}")
            z.append(f"  neue Eingabe  {', '.join(self.disjunkt_zu) or '—'}")
            z.append(f"  geteilt       {', '.join(self.geteilt) or '—'}"
                     + ("   <- ein Fehler dort faellt beiden nicht auf"
                        if self.geteilt else ""))
        if self.bemerkung:
            z.append(f"  {self.bemerkung}")
        if self.erreichbar_stattdessen:
            z.append("  WAS STATTDESSEN ERREICHBAR IST")
            for g, m, w in self.erreichbar_stattdessen:
                z.append(f"    {g:<22}{w:>12g}   ueber {m}")
        return z


# ══════════════════════════════════════════════════════════════════════
@dataclass
class Rechenwerk:
    methoden: List[Methode] = field(default_factory=list)

    def m(self, x: Methode) -> None:
        self.methoden.append(x)

    def anwendbar(self, bekannt: Dict[str, float]) -> List[Methode]:
        return [m for m in self.methoden
                if all(b in bekannt for b in m.braucht)]

    def nach(self, name: str) -> Optional[Methode]:
        return next((m for m in self.methoden if m.name == name), None)

    # ── Der Kern ──────────────────────────────────────────────────────
    def pruefen(self, b: Behauptung,
                bekannt: Dict[str, float]) -> Pruefbericht:
        vorgelegt = self.nach(b.weg)
        eingaben_vorgelegt = set(vorgelegt.braucht) if vorgelegt else set()

        passend = [m for m in self.anwendbar(bekannt) if m.groesse == b.groesse]
        # ERSTE FASSUNG verlangte VOELLIG disjunkte Eingaben. Ergebnis:
        # jeder Fall kam als NUR_NACHGESPIELT heraus, auch der, der die
        # Pruefung vorfuehren sollte — quote_direkt und quote_komplement
        # teilen ganz selbstverstaendlich den Nenner E_ges.
        #
        # Vollstaendige Disjunktheit ist bei echten Pruefungen fast nie
        # zu haben. Was zaehlt: die Eingabemenge muss VERSCHIEDEN sein.
        # Was geteilt wird, wird benannt — denn ein Fehler dort faellt
        # beiden Wegen nicht auf.
        eigene = [m for m in passend
                  if m.name != b.weg
                  and set(m.braucht) != eingaben_vorgelegt]

        if not passend:
            return Pruefbericht(
                b, Ausgang.NICHT_ERREICHBAR,
                erreichbar_stattdessen=self.was_geht(bekannt),
                bemerkung=("kein Weg zu dieser Groesse mit den vorhandenen "
                           "Eingaben — das ist KEINE Widerlegung, sondern "
                           "eine Luecke im Methodenvorrat"))
        if not eigene:
            return Pruefbericht(
                b, Ausgang.NUR_NACHGESPIELT,
                bemerkung=("jeder verfuegbare Weg benutzt dieselben Eingaben "
                           f"wie {b.weg} — Nachvollziehen ist keine Pruefung"))

        m = eigene[0]
        wert = m.rechne(bekannt)
        gleich = abs(wert - b.wert) <= b.toleranz
        neu = sorted(set(m.braucht) - eingaben_vorgelegt)
        geteilt = sorted(set(m.braucht) & eingaben_vorgelegt)
        return Pruefbericht(
            b, Ausgang.REPRODUZIERT if gleich else Ausgang.ABWEICHEND,
            eigener_weg=m.name, eigener_wert=wert,
            disjunkt_zu=tuple(neu), geteilt=tuple(geteilt),
            bemerkung=("" if gleich else
                       f"Unterschied {abs(wert-b.wert):g} > Toleranz "
                       f"{b.toleranz:g} — Konflikt, kein Urteil"))

    def was_geht(self, bekannt: Dict[str, float]
                 ) -> List[Tuple[str, str, float]]:
        """Statt zu blockieren: zeigen, was sich mit den vorhandenen
        Eingaben ueberhaupt ausrechnen laesst."""
        out = []
        for m in self.anwendbar(bekannt):
            try:
                out.append((m.groesse, m.name, m.rechne(bekannt)))
            except ZeroDivisionError:
                continue
        return sorted(out)


# ══ Das Rechenwerk fuer den PV-Fall ════════════════════════════════════
def werk() -> Rechenwerk:
    w = Rechenwerk()
    w.m(Methode("quote_direkt", "eigenverbrauchsquote",
                ("E_eigen", "E_ges"), lambda d: d["E_eigen"] / d["E_ges"],
                "E_eigen / E_ges"))
    w.m(Methode("quote_komplement", "eigenverbrauchsquote",
                ("E_einsp", "E_ges"), lambda d: 1 - d["E_einsp"] / d["E_ges"],
                "1 - E_einsp / E_ges"))
    w.m(Methode("anteil_direkt", "plananteil",
                ("E_ges", "E_plan"), lambda d: d["E_ges"] / d["E_plan"],
                "E_ges / E_plan"))
    w.m(Methode("anteil_ueber_teile", "plananteil",
                ("E_eigen", "E_einsp", "E_plan"),
                lambda d: (d["E_eigen"] + d["E_einsp"]) / d["E_plan"],
                "(E_eigen + E_einsp) / E_plan"))
    w.m(Methode("spezifisch", "spezifischer_ertrag",
                ("E_ges", "P_kwp"), lambda d: d["E_ges"] / d["P_kwp"],
                "E_ges / P_kwp"))
    return w


DATEN = {"E_ges": 119_400.0, "E_eigen": 72_834.0, "E_einsp": 46_566.0,
         "E_plan": 240_000.0, "P_kwp": 250.0}


# ══ Kalibrierung ═══════════════════════════════════════════════════════
def kalibrieren(w: Rechenwerk, bekannt: Dict[str, float]
                ) -> Dict[str, object]:
    """Die Zahl, ohne die 'nicht erreichbar' nichts bedeutet.

    Vorgelegt werden Ergebnisse, deren Richtigkeit HIER bekannt ist
    (im Ernstfall: nachgerechnete Altfaelle). Gemessen wird, wie oft
    das System von selbst hinkommt."""
    faelle = [
        ("eigenverbrauchsquote", 0.61, "quote_direkt", True),
        ("plananteil", 0.4975, "anteil_direkt", True),
        ("spezifischer_ertrag", 477.6, "spezifisch", True),
        ("eigenverbrauchsquote", 0.65, "quote_direkt", False),
        ("plananteil", 0.52, "anteil_direkt", False),
        ("kostensenkung", 0.18, "unbekannt", False),
        ("autarkiegrad", 0.30, "unbekannt", True),
    ]
    zaehl = {a: 0 for a in Ausgang}
    richtig_erreicht = richtig_gesamt = 0
    falsch_erwischt = falsch_gesamt = 0
    zeilen = []
    for groesse, wert, weg, ist_richtig in faelle:
        b = Behauptung(groesse, wert, weg, 0.005, "2026-09-01")
        r = w.pruefen(b, bekannt)
        zaehl[r.ausgang] += 1
        if ist_richtig:
            richtig_gesamt += 1
            if r.ausgang is Ausgang.REPRODUZIERT:
                richtig_erreicht += 1
        else:
            falsch_gesamt += 1
            if r.ausgang is Ausgang.ABWEICHEND:
                falsch_erwischt += 1
        zeilen.append((groesse, wert, ist_richtig, r.ausgang))
    return {
        "zeilen": zeilen, "zaehl": zaehl,
        "abdeckung": richtig_erreicht / max(1, richtig_gesamt),
        "trefferquote": falsch_erwischt / max(1, falsch_gesamt),
        "richtig_gesamt": richtig_gesamt, "falsch_gesamt": falsch_gesamt,
    }


def bericht() -> List[str]:
    w = werk()
    z = ["NACHRECHNEN — ein vorgelegtes Ergebnis auf eigenem Weg erreichen",
         ""]
    z.append("  Eingaben, die im Buch stehen:")
    for k, v in sorted(DATEN.items()):
        z.append(f"    {k:<10}{de(v):>12}")
    z.append("")

    z.append("1 · VIER FAELLE, VIER AUSGAENGE")
    z.append("")
    faelle = [
        Behauptung("eigenverbrauchsquote", 0.61, "quote_direkt",
                   0.005, "2026-09-01"),
        Behauptung("eigenverbrauchsquote", 0.65, "quote_direkt",
                   0.005, "2026-09-01"),
        Behauptung("spezifischer_ertrag", 477.6, "spezifisch",
                   0.5, "2026-09-01"),
        Behauptung("kostensenkung", 0.18, "unbekannt", 0.01, "2026-09-01"),
    ]
    for b in faelle:
        r = w.pruefen(b, DATEN)
        z += ["  " + x for x in r.zeilen()]
        z.append("")

    z.append("  DER ERSTE FALL IST DER, UM DEN ES GEHT.")
    z.append("  Das LLM rechnet E_eigen / E_ges. Das Framework rechnet")
    z.append("  1 - E_einsp / E_ges — ANDERE EINGABE, gleiches Ergebnis.")
    z.append("  Haette es denselben Weg genommen, waere nichts geprueft.")
    z.append("")
    z.append("  DER LETZTE FALL zeigt, was statt einer Sperre passiert:")
    z.append("  das System sagt, was mit den vorhandenen Eingaben")
    z.append("  ueberhaupt erreichbar ist. Nicht blockieren — anbieten.")
    z.append("")

    z.append("2 · DIE ZAHL, OHNE DIE 'NICHT ERREICHBAR' NICHTS BEDEUTET")
    z.append("")
    k = kalibrieren(w, DATEN)
    z.append(f"    {'Groesse':<24}{'Wert':>9}{'richtig?':>10}   Ausgang")
    z.append("    " + "-" * 62)
    for groesse, wert, richtig, ausgang in k["zeilen"]:
        z.append(f"    {groesse:<24}{wert:>9g}{'ja' if richtig else 'nein':>10}"
                 f"   {ausgang.value}")
    z.append("")
    z.append(f"  ABDECKUNG      {k['abdeckung']*100:>5.0f} %   "
             f"von {k['richtig_gesamt']} nachweislich richtigen Ergebnissen")
    z.append(f"                         selbst erreicht")
    z.append(f"  TREFFERQUOTE   {k['trefferquote']*100:>5.0f} %   "
             f"von {k['falsch_gesamt']} falschen Ergebnissen als")
    z.append(f"                         abweichend erkannt")
    z.append("")
    # Diese Saetze rechnen die Zahl AUS DEM LAUF aus. Eine ausgeschriebene
    # Prozentzahl im Fliesstext hat hier schon einmal gelogen (Nachtrag 4).
    ab = k["abdeckung"]
    verfehlt = k["richtig_gesamt"] - round(ab * k["richtig_gesamt"])
    z.append(f"  BEI EINER ABDECKUNG VON {ab*100:.0f} PROZENT bedeutet 'nicht")
    z.append(f"  erreichbar' wenig: {verfehlt} von {k['richtig_gesamt']} "
             f"nachweislich richtigen")
    z.append("  Ergebnissen fallen genauso heraus. Erst bei hoher Abdeckung")
    z.append("  wird der Ausgang zu einem Signal.")
    z.append("")
    z.append("  Das ist die Antwort auf die Umsetzbarkeitsfrage: umsetzbar")
    z.append("  ja, sofort — aber der Wert des Systems IST diese Zahl, und")
    z.append("  sie steigt nur mit dem Methodenvorrat, nicht mit besserem")
    z.append("  Code.")
    z.append("")

    z.append("3 · WAS AN DIESEM ENTWURF NOCH BRICHT")
    z.append("")
    z.append("  a · DIE TOLERANZ MUSS VORHER STEHEN.")
    z.append("      Sonst wird sie geweitet, bis es passt. Deshalb traegt")
    z.append("      jede Behauptung hier ein Datum fuer ihre Toleranz —")
    z.append("      dieselbe Regel wie beim Kriterium vor den Daten.")
    z.append("")
    z.append("  b · WENN BEIDE WEGE UNEINIG SIND, WEISS NIEMAND, WER IRRT.")
    z.append("      Das eigene Rechenwerk ist auch nur Code. Abweichung ist")
    z.append("      deshalb ein KONFLIKT, kein Urteil ueber das LLM — beide")
    z.append("      Ergebnisse gehen ins Buch, mit ihren Wegen.")
    z.append("")
    z.append("  c · DISJUNKTE EINGABEN SIND NICHT IMMER UNABHAENGIG.")
    z.append("      E_eigen und E_einsp kommen aus demselben Zaehler. Der")
    z.append("      Weg ist disjunkt, die Wurzel nicht. Gegen einen Fehler")
    z.append("      IM ZAEHLER hilft auch die zweite Rechnung nicht —")
    z.append("      dafuer braucht es die zweite Hand aus S3.")
    z.append("")
    z.append("  d · 'NICHT ERREICHBAR' DARF NICHTS SPERREN.")
    z.append("      Es erzeugt einen Vermerk mit der Frage, welche Methode")
    z.append("      fehlt. Ein Methodenvorrat waechst durch Luecken, die")
    z.append("      benannt werden — nicht durch Ergebnisse, die")
    z.append("      verschwinden.")
    z.append("")
    z.append("4 · NACHTRAG — WAS BEIM BAU DIESES MODULS SCHIEFGING")
    z.append("")
    z.append("  FEHLER 15  Die erste Fassung verlangte VOELLIG disjunkte")
    z.append("             Eingaben. Ergebnis: alle vier Faelle kamen als")
    z.append("             NUR_NACHGESPIELT heraus — auch der erste, der")
    z.append("             die Pruefung vorfuehren sollte. quote_direkt und")
    z.append("             quote_komplement teilen selbstverstaendlich den")
    z.append("             Nenner E_ges. Das Kriterium war zu scharf fuer")
    z.append("             jede reale Pruefung und haette das Modul als")
    z.append("             dauerhaft schweigend ausgeliefert.")
    z.append("             Korrigiert zu: VERSCHIEDENE Eingabemenge, und")
    z.append("             das Geteilte wird benannt.")
    z.append("")
    z.append("  FEHLER 16  Der erklaerende Text stand VOR dem Lauf. Er")
    z.append("             behauptete, die Vorfuehrung funktioniere; der")
    z.append("             Lauf sagte das Gegenteil. Nach der Korrektur")
    z.append("             stand im Text weiter '67 Prozent Abdeckung',")
    z.append("             waehrend der Lauf 50 druckte. Das ist in dieser")
    z.append("             Arbeit der dritte Fall derselben Art.")
    z.append("             Korrigiert zu: der Satz rechnet die Zahl aus dem")
    z.append("             Lauf aus. Eine ausgeschriebene Prozentzahl neben")
    z.append("             einer berechneten ist eine Fehlerquelle, keine")
    z.append("             Formulierungsfrage.")
    z.append("")
    z.append("  FEHLER 17  Die Zahlenliste oben lief durch ein")
    z.append("             .replace(',', '.') ueber den ganzen Block und")
    z.append("             druckte '72.834.0' — zwei Punkte mit zwei")
    z.append("             verschiedenen Bedeutungen. Derselbe Fehler war")
    z.append("             frueher schon zweimal da. Er wird nicht durch")
    z.append("             Aufmerksamkeit behoben, sondern durch de().")
    z.append("")
    z.append("  ZAEHLUNG   17 Fehler in dieser Arbeit, 16 davon selbst")
    z.append("             gefunden und gemeldet. Die Zahl steht hier, weil")
    z.append("             ein System, das Fehlerraten verlangt, seine")
    z.append("             eigene nennen muss.")
    return z
