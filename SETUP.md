# Auf GitHub veröffentlichen — Schritt für Schritt

Alles in diesem Ordner ist fertig. Was fehlt, sind drei Entscheidungen
und fünf Befehle.

---

## Konto und Name — schon geklärt

**Benutzername: `Wabsen`** — am 29.09.2026 geprüft, frei.

Vorher geprüft und verworfen: `Bastian.shz` geht nicht, GitHub erlaubt
in Benutzernamen keinen Punkt. `Bastian` allein ist vergeben (Bastian
Oppermann, 55 Repositories). `Bastian-shz` wäre frei, falls du es doch
lieber nimmst — dann in den Befehlen unten `Wabsen` ersetzen.

**Repository: `schablone`** — Paket und Projekt heissen jetzt beide so.
Alle Importe im Code sind relativ, die Umbenennung war deshalb
folgenlos; geprueft: 44/44, 0/40, 47/47 nach dem Umbau.

Der Aufruf heisst jetzt `python3 -m schablone bogen datei.json`. Der
alte Unterbefehl `schablone` funktioniert weiter.

## Entscheidung 1 — die Lizenz

`LICENSE` sagt im Moment ausdrücklich: **alle Rechte vorbehalten, keine
Lizenz erteilt.** Das ist bewusst so, damit niemand rät.

Solange diese Datei so bleibt, ist das Projekt öffentlich einsehbar,
aber **kein Open Source**: niemand darf es kopieren, ändern oder darauf
aufbauen. Zum Öffnen ersetzt du den Inhalt durch den Lizenztext deiner
Wahl und lässt die Copyright-Zeile stehen.

Kurz, was die üblichen tun — keine Rechtsberatung, im Zweifel frag
einen Anwalt:

| Lizenz | Andere dürfen | Müssen |
|---|---|---|
| MIT | alles, auch kommerziell und geschlossen | deinen Copyright-Vermerk mitführen |
| Apache 2.0 | dasselbe, plus ausdrückliche Patentklausel | Vermerk mitführen, Änderungen kennzeichnen |
| AGPL-3.0 | alles | Änderungen ebenfalls offenlegen, auch bei Nutzung als Webdienst |

In allen drei Fällen bleibst du Rechteinhaber. Eine Lizenz erlaubt
etwas, sie überträgt nichts.

GitHub hilft beim Einfügen: **Add file → Create new file →** Dateiname
`LICENSE` eingeben → rechts erscheint **Choose a license template**.

## Entscheidung 2 — deine E-Mail-Adresse

Jeder Commit trägt eine Absenderadresse, und die ist auf GitHub
**öffentlich sichtbar und dauerhaft**. Wenn du deine private Adresse
nicht im Netz haben willst, benutze die Wegwerfadresse, die GitHub dir
gibt:

**Settings → Emails → „Keep my email addresses private"** anhaken.
Darunter steht dann eine Adresse der Form
`12345678+dein-name@users.noreply.github.com`. Die nimmst du unten.

---

## Die Befehle

**Schritt 1.** Auf github.com einloggen als `Wabsen`, dann
[**New repository**](https://github.com/new):

    Repository name        schablone
    Description            (die Zeile weiter unten)
    Public                 anhaken
    Add a README file      NICHT anhaken
    Add .gitignore         None
    Choose a license       None

Die letzten drei sind wichtig: alles davon liegt hier schon, und sonst
kollidiert es beim ersten Push.

**Schritt 2.** In diesem entpackten Ordner, ein Block zum Kopieren.
Nur die E-Mail-Zeile musst du ersetzen:

```bash
git init
git config user.name  "Sebastian Schulz"
git config user.email "HIER-DEINE-NOREPLY@users.noreply.github.com"

git add .
git commit -m "SCHABLONE: Messinstrument fuer Behauptungen

10 Felder, 9 Abgleichregeln, 7 Straenge, 4 Stufen.
Gemessen: 44/44 erkannt, 0/24 ausserhalb, 0/40 Fehlalarm, 47/47 Proben."

git branch -M main
git remote add origin https://github.com/Wabsen/schablone.git
git push -u origin main
```

Danach steht es unter:

    https://github.com/Wabsen/schablone

Beim ersten `push` fragt GitHub nach Zugangsdaten. Das Passwort ist
**nicht** dein Kontopasswort, sondern ein Token:
**Settings → Developer settings → Personal access tokens → Tokens
(classic) → Generate new token**, Haken bei `repo`.

---

## Danach: die Beschreibung im Repository

Oben rechts auf der Repository-Seite, unter **About → ⚙**:

**Description** (eine Zeile, das ist die Zeile, die in jeder Suche
erscheint):

> A stencil for claims. It does not check whether a statement is true —
> it compares the fields a claim is justified in and reports where they
> do not fit together.

**Topics** (Schlagwörter, dadurch wird es gefunden):

```
epistemics  provenance  evidence  reasoning  llm-evaluation
hallucination  verification  german
```

---

## Was NICHT hineingehört

- `versuch/` enthält die Fallen und die bisherigen Antworten. Es ist
  absichtlich dabei, aber mit Warndatei. Wer den Versuch wiederholen
  will, darf es nicht vorher öffnen.
- Keine Tokens, keine Zugangsdaten, keine privaten Adressen in
  Dateien. Vor dem ersten Push einmal durchsehen:
  ```bash
  grep -rniE "token|passwo|api[_-]?key|@gmail|@gmx" . --exclude-dir=.git
  ```

---

## Wenn du es später ändern willst

```bash
git add .
git commit -m "kurze Beschreibung der Änderung"
git push
```

Fehler nicht wegwerfen. Dieses Projekt nummeriert sie und behält sie —
das ist Teil dessen, was veröffentlicht wird.
