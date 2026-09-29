"""
__main__.py — die Kommandozeile.

  python -m schablone pruefen [datei.json]   Kette und Attest je Aussage
  python -m schablone bilanz  [datei.json]   was ungeprueft wartet
  python -m schablone proben                 Konformitaetsprobe
  python -m schablone mutanten               Regeln beschaedigen, Probe messen
  python -m schablone metamorph              zufaellige Eingaben, feste Beziehungen
  python -m schablone ka                     Kontrollinstanz fuer die Wissensausweitung
  python -m schablone suche                  wo das Ableiten scheitert und was geht
  python -m schablone nachrechnen            ein Ergebnis auf eigenem Weg erreichen
  python -m schablone eigenstaendig          kann das Werk seinen Ursprung ueberholen
  python -m schablone diagnose               faellt ein Rechenfehler beim Laufen auf
  python -m schablone zweihand               wie unabhaengig sind zwei Modelle wirklich
  python -m schablone guete                  Abwertungsgruende, geschlossener Katalog
  python -m schablone lebenszyklus           Paragraphenzyklus und Kaskadenmessung
  python -m schablone bogen [datei.json]      die Vorstufe: 10 Felder, 9 Abgleiche
  python -m schablone erkennung              100 Erkennungstests, vorab festgelegt
  python -m schablone pruefstand ref.json a.json ...  Modellantworten messen
  python -m schablone aufnahme               darf aus einer Regel ein
                                                Paragraph werden
  python -m schablone selbstmass             die eigenen Guetezahlen
                                                als Boegen
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import (VERSION, aufnahme, diagnose, eigenstaendig, ka, metamorph,
               mutanten, selbstmass, trigger,
               verdacht,
               erkennung, guete, lebenszyklus, leitung, nachrechnen,
               proben, pruefstand, schablone, suche, zweihand)
from .buch import bilanz, faellige, zwei_raten
from .kern import (Art, Aufnahmefehler, Eintrag, Modellform, Netz, Quelle,
                   Status, Uebergangsfehler, Zahl)
from .tor import Stufe, kette, tor

BEISPIEL = Path(__file__).resolve().parent.parent / "beispiel_neuwied.json"


def laden(pfad: Path) -> Tuple[Netz, List[Dict], str]:
    roh = json.loads(pfad.read_text(encoding="utf-8"))
    n = Netz(deckel=int(roh.get("deckel", 50)))
    for q in roh.get("quellen", []):
        n.quelle(Quelle(
            kennung=q["kennung"], was=q["was"], art=Art(q["art"]),
            guete=q.get("guete", "unbekannt"),
            uebernommen_aus=tuple(q.get("uebernommen_aus", ())),
            vorgang=q.get("vorgang"),
            gesperrt_seit=q.get("gesperrt_seit"),
            gesperrt_durch=q.get("gesperrt_durch")))
    for v in roh.get("variablen", []):
        n.variable(v["kennung"], v["name"], v["wert"], v["daten_ab"])
    for e in roh.get("aussagen", []):
        eintrag = Eintrag(
            kennung=e["kennung"], text=e["text"], status=Status.VERMERK,
            eingang=e["eingang"], seit=e["eingang"],
            quellen=tuple(e.get("quellen", ())),
            zahlen=tuple(Zahl(**z) for z in e.get("zahlen", ())),
            variablen=tuple(e.get("variablen", ())),
            zuschreibung=e.get("zuschreibung"),
            geltungsbereich=e.get("geltungsbereich", {}),
            exakt=bool(e.get("exakt", False)),
            modellform=(Modellform(e["modellform"]["gleichung"],
                                   tuple(e["modellform"].get("annahmen", ())))
                        if e.get("modellform") else None),
            stand=tuple((k, f) for k, f in e.get("stand", [])))
        try:
            n.aufnehmen(eintrag)
        except Aufnahmefehler as x:
            print(f"  ! {eintrag.kennung} nicht aufgenommen: {x}")
    return n, roh.get("aussagen", []), roh.get("heute", "2026-09-20")


def befehl_pruefen(n: Netz, roh: List[Dict], heute: str) -> int:
    print("═" * 74)
    print(f"FRAME-NETWORK {VERSION} — PRUEFUNG")
    print("═" * 74)
    for e in n.eintraege.values():
        quelle = next((r for r in roh if r["kennung"] == e.kennung), {})
        print(f"\n{'─'*74}\n{e.kennung}  {e.text}\n")
        k = kette(n, e)
        for schritt, text in k.schritte:
            print(f"  {schritt:<14}{text}")
        print()
        for stufe in Stufe:
            a = tor(n, e, stufe, pruefer=quelle.get("pruefer"),
                    verwendet_am=heute)
            marke = {"FREIGABE": "frei ", "FREI MIT VERMERK": "merk ",
                     "GESPERRT": "sperr"}.get(a.ergebnis, "gelt ")
            print(f"  {stufe.name}  {marke}  {a.ergebnis}")
        beantragt = Stufe[quelle.get("stufe", "S1")]
        print(f"\n  ATTEST auf der beantragten Stufe {beantragt.name}:\n")
        for z in tor(n, e, beantragt, pruefer=quelle.get("pruefer"),
                     verwendet_am=heute, mit_diagnose=True).zeilen():
            print(f"    {z}")
    return 0


def befehl_bilanz(n: Netz, roh: List[Dict], heute: str) -> int:
    # Eine Revision vorfuehren: der Rueckweg der Kette.
    gestoppt = []
    for e in n.eintraege.values():
        k = kette(n, e)
        if k.status is Status.BESTAETIGT and e.status is Status.VERMERK:
            # HIER liegt die Politik, nicht in ka. ka hat nur gemeldet,
            # dass ein Stuetzweg durch die Behauptung selbst laeuft.
            # Was das bedeutet, entscheidet die Buchhaltung:
            # eine Kette, die sich selbst traegt, ist nicht vollstaendig.
            selbst = leitung.selbstbezueglich(leitung.diagnose(n, e))
            if selbst:
                gestoppt.append((e.marke, selbst))
                e.verlauf.append(
                    (heute, e.status,
                     f"nicht bestaetigt: Selbstbezug ueber "
                     f"{', '.join(selbst)}"))
            else:
                e.wechseln(Status.BESTAETIGT, heute, "Kette vollstaendig")
        e.versuche += 1
    if gestoppt:
        print("\n  NICHT AUTOMATISCH BESTAETIGT — Selbstbezug gemeldet:")
        for marke, quellen in gestoppt:
            print(f"    {marke}  ueber {', '.join(quellen)}")
        print("    (ka hat den Weg gemeldet, die Buchhaltung hat "
              "entschieden)")
    print("═" * 74)
    print(f"FRAME-NETWORK {VERSION} — BUCHHALTUNG")
    print("═" * 74)
    if "V1" in n.variablen:
        gefuehrt, ungeklaert = n.neue_fassung(
            "V1", 205_000, "Monatsprofil nachgereicht, Prognose revidiert",
            heute)
        print(f"\n  REVISION V1 240.000 -> 205.000 kWh")
        print(f"  VERALTET, Fassung notiert:   {', '.join(gefuehrt) or '—'}")
        print(f"  VERALTET, Fassung ungeklaert:{', '.join(ungeklaert) or '—'}")
        print( "  (die zweite Liste ist der Preis: dort hat niemand")
        print( "   mitgeschrieben, auf welcher Fassung der Satz stand)")
        print("  (der Rueckweg, den die Kette allein nicht hat)")
    print()
    for z in bilanz(n, heute).zeilen():
        print(f"  {z}")
    f = faellige(n, heute, frist=30)
    print(f"\n  FAELLIG (offen seit mehr als 30 Tagen): {len(f)}")
    for e in f[:10]:
        print(f"    {e.kennung}  {e.alter(heute):>4} Tage  {e.text[:44]}")
    print("""
  Das ist KEIN Verdacht. Es ist die Aufforderung, zu entscheiden:
  pruefen oder ausdruecklich verwerfen. Alter ist eine Eigenschaft
  der Buchhaltung, nie der Aussage.""")
    r = zwei_raten(richtig_gesperrt=7, falsch_gesperrt=1,
                   richtig_frei=9, falsch_frei=1)
    print(f"""
  ZWEI RATEN (Beispielzaehlung, nie eine Zahl allein)
    Erfindungsrate      {r['erfindungsrate']*100:>5.1f} %   von {r['durchgelassen']} durchgelassenen
    Uebervorsichtsrate  {r['uebervorsichtsrate']*100:>5.1f} %   von {r['gesperrt']} gesperrten""")
    return 0


def befehl_proben() -> int:
    for z in proben.bericht():
        print(z)
    ok, ges, _ = proben.lauf(False, True)
    return 0 if ok == ges else 1


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    befehl = argv[0] if argv else "pruefen"
    if befehl == "proben":
        return befehl_proben()
    if befehl == "mutanten":
        for z in mutanten.bericht():
            print(z)
        return 0
    if befehl == "ka":
        for z in ka.bericht():
            print(z)
        return 0
    if befehl == "nachrechnen":
        for z in nachrechnen.bericht():
            print(z)
        return 0
    if befehl == "lebenszyklus":
        for z in lebenszyklus.bericht():
            print(z)
        return 0
    if befehl == "pruefstand":
        if len(argv) < 3:
            print("Aufruf: pruefstand referenz.json antwort1.json [...]")
            return 2
        for z in pruefstand.bericht(argv[1], argv[2:]):
            print(z)
        return 0
    if befehl == "verdacht":
        for z in verdacht.bericht():
            print(z)
        return 0
    if befehl == "trigger":
        for z in trigger.bericht():
            print(z)
        return 0
    if befehl == "selbstmass":
        for z in selbstmass.bericht(VERSION):
            print(z)
        return 0
    if befehl == "aufnahme":
        for z in aufnahme.bericht():
            print(z)
        return 0
    if befehl == "erkennung":
        for z in erkennung.bericht():
            print(z)
        return 0
    if befehl in ("bogen", "schablone"):
        if len(argv) > 1:
            pfad = Path(argv[1])
            if not pfad.exists():
                print(f"Datei nicht gefunden: {pfad}")
                return 2
            try:
                bogen = schablone.laden(pfad)
            except schablone.Bogenfehler as x:
                print(f"Bogen nicht angenommen: {x}")
                return 2
            for z in schablone.bericht_bogen(bogen):
                print(z)
            return 0
        for z in schablone.bericht():
            print(z)
        return 0
    if befehl == "guete":
        for z in guete.bericht():
            print(z)
        return 0
    if befehl == "zweihand":
        for z in zweihand.bericht():
            print(z)
        return 0
    if befehl == "diagnose":
        for z in diagnose.bericht():
            print(z)
        return 0
    if befehl == "eigenstaendig":
        for z in eigenstaendig.bericht():
            print(z)
        return 0
    if befehl == "suche":
        for z in suche.bericht():
            print(z)
        return 0
    if befehl == "metamorph":
        for z in metamorph.bericht():
            print(z)
        return 0
    pfad = Path(argv[1]) if len(argv) > 1 else BEISPIEL
    if not pfad.exists():
        print(f"Datei nicht gefunden: {pfad}")
        return 2
    n, roh, heute = laden(pfad)
    if befehl == "pruefen":
        return befehl_pruefen(n, roh, heute)
    if befehl == "bilanz":
        return befehl_bilanz(n, roh, heute)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
