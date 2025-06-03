# Documentation
## Ideas
- Various sounds and kits (including moderately funny sound effects)
- Structured user interface
- Share patterns via server
- Easy installation

## Features
- Save and load patterns
- Export as audio file
- Multiple kits
- Various rhythm settings
- Pattern sequences
- Highlight the first beat
- Individual volume for each track
- Quickly share patterns over the internet
- Easy installation

## Required Libraries and Programs
- tkinter
- pillow
- pygame
- os
- json
- pydub
- subprocess
- ffmpeg

## Data Structure
### Kits
Kits are defined by JSON files in the "kits" subfolder. The objects contain information about the samples and more. These samples are then loaded from the "samples" subfolder as .wav files.
```json
{
    "name": "Basic kit",
    "description": "Description",
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
Patterns are also saved in JSON format. They can be found in the "patterns" subfolder. Each file contains information about the name, the pattern itself, the kit used, volumes, and other parameters such as playback speed (BPM) and length.
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
### Pattern Sequences
Pattern sequences are relatively simple. They are saved as JSON in the "collections" subfolder. The structure looks like this:
```json
{
  "name": "My Sequence",
  "patterns": [
    "patterns/1.json",
    "patterns/2.json"
  ]
}
```

## Devlog
### 2025-05-06
- Searching for samples: Hit, Hat, Kick, and Snare
- Creating the basic project structure
- main.py: Basic pattern editing
- main.py: Saving patterns
### 2025-05-07
- main.py: 
    - Styling changes: Instruments now have their own colors
    - Styling changes: The currently played beat is highlighted
    - Playback settings: The pattern can now be played, paused, and stopped
    - Playback speed: The pattern speed can be changed (limit: 500 BPM)
    - Pattern length: The number of beats in a pattern can now be changed
- Samples: Added new snare sample
### 2025-05-08
- main.py:
    - Styling changes: Inactive buttons are now also highlighted when their beat is played
    - Pattern length: Pattern length is now saved and loaded from the pattern file
### 2025-05-11
- New samples
- Meme samples
- New kits created with the samples
- main.py:
    - Bugfix: The last played column is reset when playback stops
### 2025-05-13
- main.py:
    - The first beat of a bar can now be emphasized
    - Individual instruments can now have different volumes
- New samples
- New kit (Percussion) created with new samples
- Testing the current program features
### 2025-05-16
- main.py:
    - Set application icon
- First compilation attempts
### 2025-05-20
- main.py:
    - Translated to German
    - Pattern sequences can now be created, saved, loaded, and played
    - Preview and editor are disabled when a sequence is playing
### 2025-05-27
- main.py:
    - Moved the sequence menu below the playback menu
    - Pattern export:
        - Export as .mp3
        - To "exports" folder
        - Automatically opens the folder
*For more information about changes, see the [changelog](https://github.com/sossinayDev/synthesizer/activity?ref=main)*
### 2025-05-31
- main.py:
    - Quick sharing over the internet (own server)
        - Patterns can be uploaded
        - A five-digit code is generated
        - The pattern can be downloaded on another device
    - Changed sound cutoff
        - Samples are only shortened if:
            - The time between notes is less than 100 milliseconds
            - The "Sfx" kit is loaded
    - Automatic installation of libraries
        - If at least one additional library is missing, it is installed with pip
    - Bugfix:
        - The program could not run if no patterns existed
- working_history.md renamed to devlog.md
- A simple installer was created
    - Python or .exe available
### 2025-06-02
- installer.py
    - Automatically install ffmpeg after confirmation
- Deleted unused patterns
- Renamed devlog.md to README.md
- English version of devlog
- New installer and main EXEs
- Small design changes
- Diverse bugfixes
### 2025-06-03
- New drum kit (80s Drum Machine)
- New sounds:
    - 80s Drum
    - 80s Cowbell
    - 80s Conga
    - And more

## ChatGPT / Copilot Conversations
See [copilot_history.md](copilot_history.md)