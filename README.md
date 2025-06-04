# Dokumentation 
[Click here for english version](README_EN.md)
## Ideen
- Verschiedene Sounds und Kits (Auch mittelmässig lustige Soundeffekte)
- Strukturierte Benutzeroberfläche
- Teilen der Patterns über Server
- Einfache installation

## Features
- Patterns speichern und laden
- Export als Sounddatei
- Verschiedene Kits
- Diverse Rhytmuseinstellungen
- Pattern-Abfolgen
- Hervorhebung des ersten Schlags
- Einzelne Lautstärken für jede Spur
- Patterns schnell über das Internet teilen
- Einfache installation

## Nötige Bibliotheken und Programme
- tkinter
- pillow
- pygame
- os
- json
- pydub
- subprocess
- ffmpeg

## Datenstruktur
### Kits
Kits werden durch JSON-Dateien im Unterordner "kits" definiert. Die Objekte enthalten Informationen über die Samples und mehr. Diese Samples werden anschliessend aus dem Unterordner "samples" als .wav-Datei geladen.
```json
{
    "name": "Basic kit",
    "description": "Beschreibung",
    "samples": {
        "hit": {
            "name": "Hit",
            "short": "HIT",
            "inactive": "#332200",
            "active": "#bb7a00",
            "file": "hit.wav"
        }
    }
}
```
### Patterns
Patterns werden ebenfalls im JSON-Format gespeichert. Im Unterornder "patterns" können diese gefunden werden. Jede Datei enthält Informationen über den Namen, das Pattern selbst, das verwendete Kit, die Lautstärken sowie weitere Parameter wie z.B. die Abspielgeschwindigkeit (BPM) und Länge.
```json
{
    "kit": "basic",
    "pattern": [
        [
            {
                "enabled": false
            },
            {
                "enabled": true
            },
            {
                "enabled": true
            },
            {
                "enabled": false
            },
            {
                "enabled": false
            }
        ]
    ],
    "bpm": 90,
    "length": 1,
    "volumes": {
        "Hit": 100,
        "Hat": 100,
        "Kick": 100,
        "Snare": 100,
        "Ride": 100,
        "hit": 100,
        "hat": 100,
        "kick": 100,
        "snare": 100,
        "ride": 100
    },
    "beat_length": 4,
    "highlight_first_beat_hit": true
}
```
### Pattern-Abfolgen
Pattern-Abfolgen sind relativ simpel aufgebaut. Sie werden als JSON im Unterordner "collections" gespeichert. Die Struktur sieht so aus:
```json
{
  "name": "Meine Abfolge",
  "patterns": [
    "patterns/1.json",
    "patterns/2.json"
  ]
}
```

## Devlog
### 06.05.2025
- Suche nach Samples: Hit, Hat, Kick und Snare
- Kreiren der Grundstruktur des Projekts
- main.py: Grundlegende Pattern-Bearbeitung
- main.py: Speichern von Patterns
### 07.05.2025
- main.py: 
    - Styling-Änderungen: Instrumente haben nun eigene Farben
    - Styling-Änderungen: Der aktuell abgespielte Schlag wird etwas heller
    - Playback-Einstellungen: Das Pattern kann nun abgespielt, pausiert und gestoppt werden
    - Playback-Geschwindigkeit: Die Geschwindigkeit des Patterns kann geändert werden. (Limit: 500 BPM)
    - Pattern-Länge: Die Anzahl Schläge in einem Pattern kann nun geändert werden.
- Samples: Neuer Snare sample hinzugefügt
### 08.05.2025
- main.py:
    - Styling-Änderungen: Auch inaktive Knöpfe werden nun hervorgehoben, wenn deren Schlag abgespielt wird.
    - Pattern-Länge: Die Länge der Patterns werden nun in der Pattern-Datei gespeichert und geladen.
### 11.05.2025
- Neue Samples
- Meme Samples
- Neue Kits mit den Samples erstellt.
- main.py:
    - Bugfix: Die zuletzt gespielte spalte wird bei Wiedergaben-Stop wieder normal.
### 13.05.2025
- main.py:
    - Der erste Schlag eines Taktes kann nun betont werden.
    - Einzelne Instrumente können nun verschiedene Lautstärken haben.
- Neue Samples
- Neues Kit (Percussion) mit neuen Samples erstellt.    
- Testen der Funktionen des derzeitigen Programms.
### 16.05.2025
- main.py:
    - Festlegung des Icons
- Erste Kompilierungsversuche
### 20.05.2025
- main.py:
    - Übersetzung auf Deutsch
    - Man kann nun Pattern-Abfolgen erstellen, speichern, laden, und abspielen
    - Die Vorschau und der Editor werden deaktiviert, wenn eine Abfolge gespielt wird.
### 27.05.2025
- main.py:
    - Verschiebung des Abfolgen-Menu unter das Playback-Menu
    - Pattern-Export:
        - Exportierung als .mp3
        - In Ordner "exports"
        - Automatische Öffnung des Ordners

### 31.05.2025
- main.py:
    - Schnelles Teilen über Internet (Eigener server)
        - Patterns können hochgeladen werden
        - Ein fünfstelliger Code wird generiert
        - Das Pattern kann auf einem anderen Gerät wieder heruntergeladen werden
    - Änderung Sound-Cutoff
        - Die Samples werden nur noch gekürzt wenn:
            - Die Dauer zwischen den Tönen kleiner als 100 Millisekunden ist
            - Das Kit "Sfx" geladen wurde
    - Automatische Installation von Bibliotheken
        - Wenn mindestens eine Zusatzbibliotheke fehlt, wird sie mit pip installiert.
    - Bugfix:
        - Das Programm konnte nicht ausgeführt werden, wenn keine Patterns existierten.
- working_history.md wurde zu devlog.md umbenannt.
- Ein einfaches Installationsprogramm wurde erstellt.
    - Python oder .exe verfügbar
### 02.06.2025
- installer.py:
    - Automatische Installation von ffmpeg nach Bestätigung
- Unbenutzte Patterns gelöscht
- devlog.md zu README.md umbenannt
- Englische Version des Devlogs hinzugefügt
- Neue Installer- und Haupt-EXE-Dateien
- Kleine Designänderungen
- Diverse Bugfixes
### 03.06.2025
- Neues Drum Kit (80s Drum Machine)
- Neue Sounds
    -> 80s Drum
    -> 80s Cowbell
    -> 80s Conga
    Und mehr

*Für weitere Informationen über Änderungen, sieh dir die [Änderungsliste](https://github.com/sossinayDev/synthesizer/activity?ref=main) an*

## ChatGPT-/ Copilot-konversationen
Siehe [copilot_history.md](copilot_history.md)