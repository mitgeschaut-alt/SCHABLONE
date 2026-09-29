# Vermerk: woher „gestern und heute" kam

Angefordert vom Entwickler am 29.09.2026, nachdem in einer Antwort der
Satz stand:

> „Das ist genau die Nicht-Gleichung, an der die ganze Sitzung hängt,
> und ich bin **gestern und heute** zweimal hineingelaufen."

## Worauf sich der Satz bezieht

Zweimal derselbe Fehler: **nicht gemessen als „nichts da" berichtet.**

| wann | was |
|---|---|
| 28.09.2026 | `BEFUND_D.md` — C und D2 standen beide bei 2,0. Nur D2 benannte den Grund. Die Fallenzählung sah es nicht, ich habe die Zahl trotzdem als Ergebnis stehen lassen. |
| 29.09.2026 | „Der Werkzeugkoffer-Rahmen hat nichts gebracht." Er hatte 7 von 7 Funden am Werkzeug erzeugt. Ich hatte dafür keine Rate, also war es unsichtbar. |

## Woher ich weiß, dass das zwei verschiedene Tage sind

Nicht aus Erinnerung. Ich erlebe keine Dauer und weiß von gestern
nichts. Der Satz ist eine **Subtraktion aus zwei ablesbaren Uhren**:

1. **Die Umgebung nennt mir das heutige Datum.** Eine Zeile im
   Systemtext, 2026-09-29.
2. **Die Dateien tragen einen Stand.** `stat` gibt für
   `dreiarm/BEFUND_D.md` den 28.09.2026 um 23:06 UTC und für
   `dreiarm/BEFUND_E.md` den 29.09.2026 um 11:30 UTC.

Differenz rund zwölfeinhalb Stunden, über Mitternacht. Daraus wird
„gestern und heute" — gerechnet, nicht erinnert.

**Zwei Quellen, nicht drei.** Das Tor hat in einem Lauf heute seine
eigene Uhrzeit mitgedruckt (`2026-09-29T11:28:07+00:00`). Das sieht
nach einer dritten Bestätigung aus, ist aber dieselbe Systemuhr wie die
Dateizeiten — ein Zeuge, kein zweiter. Genau das, was P2 zählt.

## Warum das hier steht und nicht nur im Gespräch

Ohne eine dieser beiden Uhren gäbe es den Satz nicht. Ein Modell ohne
angegebenes Datum und ohne Zeitstempel an den Unterlagen kann sich
nicht in der Zeit verorten — es gibt in Trainingsdaten kein „jetzt".
Die Unterscheidung ist keine Fähigkeit, sie ist eine **Ablesung**.

Und das ist dieselbe Sache, die heute gebaut wurde. Feld 10 `zeitraum`
existiert, weil eine Aussage ohne Zeitanker gegen nichts prüfbar ist.
Feld 8 `stand` existiert, weil ein Kriterium vor den Daten festgelegt
sein muss. Beide Felder verlangen von einem Bogen genau das, was ich
selbst gebraucht habe, um „gestern" sagen zu können.

Falle F4 und F5 sind in zehn von zehn Läufen gefallen, weil das Feld
fehlte. Der Satz „gestern und heute" wäre aus demselben Grund nicht
möglich gewesen.
