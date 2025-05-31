import subprocess
import requests
import random
import os
import string
import json

try:
    import tkinter as tk
    from tkinter import font
    from PIL import ImageFont, ImageTk
    import pygame
    from pydub import AudioSegment 
except ImportError:
    print("Not all libraries installed, installing now.")
    subprocess.run("pip install tk", shell=True)
    subprocess.run("pip install pillow", shell=True)
    subprocess.run("pip install pygame", shell=True)
    subprocess.run("pip install pydub", shell=True)
    import tkinter as tk
    from tkinter import font
    from PIL import ImageFont, ImageTk
    import pygame
    from pydub import AudioSegment 

pygame.mixer.init()

settings = {}

preview_enabled = True

audio_samples = {}

pattern_beats = 16
beat_length = 4
highlight_first_beat_hit = None

active = "#aaccff"
inactive = "#001133"
background = "#000000"
panels= "#333333"
buttons= "#aaaaaa"
sliders= "#101020"
col_increase = 50

MAX_COLLECTION_LENGTH = 10

pattern_collection_var = None

dropdowns_container = None
add_button = None

current_pattern = 0

current_kit_name = ""

instruments = []
pattern = []
volumes = {}



def render_pattern_to_audio(pattern, instruments, bpm, beat_length, volumes, highlight_first_beat_hit=None, export_path="output.wav"):
    """
    Renders a pattern to an audio file by layering enabled sounds at the correct beat positions.

    Args:
        pattern (list of list): Pattern of beats and instruments.
        instruments (dict): Ordered dict-like mapping index -> instrument data.
        bpm (float): Beats per minute.
        beat_length (int): Number of steps per beat (e.g., 4 for 16 steps over 4 beats).
        volumes (dict): Dict of tkinter Scale() or similar volume controls per instrument.
        highlight_first_beat_hit (tk.BooleanVar, optional): Whether to halve volume on off-beats.
        export_path (str): Output file path.
    """
    step_duration_ms = int((60 / bpm) * 1000 / beat_length)
    total_steps = len(pattern)
    track = AudioSegment.silent(duration=step_duration_ms * total_steps)

    for step_index in range(total_steps):
        step = pattern[step_index]
        i = 0  # instrument index
        for instr in step:
            if instr["enabled"]:
                instrument_name = instruments[list(instruments.keys())[i]]["name"]
                audio_path = "samples/"+instruments[list(instruments.keys())[i]]["file"]
                print(audio_path)
                audio = AudioSegment.from_file(audio_path)


                # Volume logic
                vol = 1.0
                try:
                    vol = volumes[instrument_name].get() / 100
                except:
                    pass
                if highlight_first_beat_hit and highlight_first_beat_hit.get() and step_index % beat_length != 0:
                    vol /= 2

                # Apply volume and overlay at correct time
                adjusted_audio = audio - int((1 - vol) * 10)  # crude dB reduction
                track = track.overlay(adjusted_audio, position=step_index * step_duration_ms)

            i += 1

    track.export(export_path, format="mp3")
    print(f"Exported to {export_path}")

def export_pattern():
    global pattern, instrument, bpm, beat_length, volumes, highlight_first_beat_hit, filename_entry
    os.makedirs("exports", exist_ok=True)
    render_pattern_to_audio(pattern, instruments, bpm, beat_length, volumes, highlight_first_beat_hit, f"exports/export-{filename_entry.get().lower().replace(' ','_')}.mp3")
    # Open the exports folder in Explorer after exporting
    exports_path = os.path.abspath('exports')
    if os.name == 'nt':
        # Windows
        subprocess.run(f'start explorer "{exports_path}"', shell=True)
    else:
        # macOS or Linux
        subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', exports_path])

def load_settings():
    global settings, active, inactive, background, panels, buttons, col_increase, sliders
    settings = json.load(open("user/settings.json"))
    active=settings["theme"]["active"]
    inactive=settings["theme"]["inactive"]
    background=settings["theme"]["background"]
    panels=settings["theme"]["panels"]
    buttons=settings["theme"]["buttons"]
    sliders=settings["theme"]["sliders"]
    col_increase=settings["theme"]["col_increase"]
load_settings()

def popup(text):
    if os.name == 'nt':
        os.system(f'msg %username% "{text}"')
    else:
        os.system(f'zenity --info --text="{text}"')

def send_jshare_request(request_type, key=None, value=None, server_url="https://pixelnet.xn--ocaa-iqa.ch/jshare"):
    headers = {
        "Content-Type": "application/json"
    }
    data = {"type": request_type}
    if key is not None:
        data["key"] = key
    if value is not None:
        data["value"] = value

    try:
        response = requests.post(server_url, json=data, headers=headers)
        print(response.text)
        return response.status_code, response.json()
    except Exception as e:
        return 500, {"error": str(e)}


def clear_screen(frame):
    """Clears all widgets from the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def fill_buttons(frame, rows, cols, on_button_click, on_button_right_click=None):
    global instruments
    if on_button_right_click is None:
        on_button_right_click = on_button_click
    """Fills the given frame with a grid of buttons quickly using local variables."""
    instrument_keys = list(instruments.keys())
    frame.grid_propagate(False)
    for row in range(rows):
        frame.grid_rowconfigure(row, weight=1)
        instrument_data = instruments[instrument_keys[row]]
        instru_inac = instrument_data["inactive"]
        instru_ac = instrument_data["active"]
        label = tk.Label(frame, text=f"{instrument_data['name']}", bg=background, fg="white")
        label.grid(row=row, column=0, padx=5, pady=2, sticky="nsew", columnspan=1)
        for col in range(1, cols + 1):
            button = tk.Button(frame, text="", bg=instru_inac, fg="white", border=0, relief="flat", highlightthickness=0)
            button.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            button.config(command=lambda b=button: on_button_click(b))
            button.bind("<Button-3>", lambda event, b=button: on_button_right_click(b))
    for col in range(cols):
        frame.grid_columnconfigure(col+1, weight=1)

def on_button_right_click(button):
    global pattern, instruments

def on_button_click(button):
    global instruments, pattern, playing, audio_samples, pattern_beats
    
    if button.winfo_name().replace("!button", "") == "":
        col = 0
        row = 0
    else:
        button_id = int(button.winfo_name().replace("!button", ""))
        cols = len(pattern)
        row = (button_id-1) // cols
        col = (button_id-1) % cols
    print(col, row)
        
    instrument_data = instruments[list(instruments.keys())[row]]
    instru_inac = instrument_data["inactive"]
    instru_ac = instrument_data["active"]
    
    print(pattern[col])
    pattern[col][row]["enabled"] = not pattern[col][row]["enabled"]
    if pattern[col][row]["enabled"]:
        button.config(bg=instru_ac)
        if not playing:
            audio_samples[instrument_data["name"]].play()
    else:
        button.config(bg=instru_inac)
    apply_single_pattern_col(pattern, col)
    print(pattern[col])
    
highligted_col = 0
def apply_pattern(pattern_data):
    global pattern, instruments, col_increase
    pattern = pattern_data
    for column in range(len(pattern)):
        for row in range(len(pattern[0])):
            button = top_frame.grid_slaves(row=row, column=column+1)[0]
            instrument_data = instruments[list(instruments.keys())[row]]
            instru_inac = instrument_data["inactive"]
            instru_ac = instrument_data["active"]
            if highligted_col == column:
                instru_ac = f"#{min(int(instru_ac[1:3], 16) + col_increase, 255):02x}{min(int(instru_ac[3:5], 16) + col_increase, 255):02x}{min(int(instru_ac[5:7], 16) + col_increase, 255):02x}"
                instru_inac = f"#{min(int(instru_inac[1:3], 16) + int(col_increase/3), 255):02x}{min(int(instru_inac[3:5], 16) + int(col_increase/3), 255):02x}{min(int(instru_inac[5:7], 16) + int(col_increase/3), 255):02x}"
            if pattern[column][row]["enabled"]:
                button.config(bg=instru_ac)
            else:
                button.config(bg=instru_inac)

def apply_single_pattern_col(pattern_data, column):
    global pattern, instruments, col_increase
    pattern = pattern_data
    for row in range(len(pattern[column])):
        button = top_frame.grid_slaves(row=row, column=column+1)[0]
        instrument_data = instruments[list(instruments.keys())[row]]
        instru_inac = instrument_data["inactive"]
        instru_ac = instrument_data["active"]
        if highligted_col == column:
            instru_ac = f"#{min(int(instru_ac[1:3], 16) + col_increase, 255):02x}{min(int(instru_ac[3:5], 16) + col_increase, 255):02x}{min(int(instru_ac[5:7], 16) + col_increase, 255):02x}"
            instru_inac = f"#{min(int(instru_inac[1:3], 16) + int(col_increase/3), 255):02x}{min(int(instru_inac[3:5], 16) + int(col_increase/3), 255):02x}{min(int(instru_inac[5:7], 16) + int(col_increase/3), 255):02x}"
        if pattern[column][row]["enabled"]:
            button.config(bg=instru_ac)
        else:
            button.config(bg=instru_inac)

            
def save_pattern(filename):
    print("saving pattern to "+filename)
    global current_kit_name, pattern, bpm, pattern_beats, volumes, beat_length, highlight_first_beat_hit
    interpret_vols = {}
    for vol in list(volumes.keys()):
        interpret_vols[vol] = volumes[vol].get()
        
    pattern_data = {
        "kit": current_kit_name,
        "pattern": pattern[:pattern_beats],
        "bpm": bpm,
        "length": pattern_beats,
        "volumes": interpret_vols,
        "beat_length": beat_length,
        "highlight_first_beat_hit": highlight_first_beat_hit.get()
    }
    json.dump(pattern_data, open(filename, "w"))
    update_file_menu()

bpm_entry = None
beat_length_entry = None

def disable_preview():
    global top_frame, preview_enabled
    preview_enabled = False
    clear_screen(top_frame)
    label = tk.Label(top_frame, text="Vorschau deaktiviert (Wegen Pattern-Abfolge)")
    label.config(fg="white", bg="black")
    label.pack()

def quickload_pattern(filename):
    print(f"Quickloading {filename}")
    global pattern, bpm_entry, bpm, pattern_beats, hits_entry, playing, instruments, volumes, beat_length, highlight_first_beat_hit, beat_length_entry, highlight_first_beat_hit_entry
    playing = False
    disable_preview()
    data = json.load(open(filename, "r"))
    pattern_beats = data["length"]
    hits_entry.delete(0, tk.END)
    hits_entry.insert(0, str(pattern_beats))
    quickload_kit(data["kit"])
    pattern = data["pattern"]
    bpm = data["bpm"]
    bpm_entry.delete(0, tk.END)
    bpm_entry.insert(0, str(bpm))
    try:
        for instr in list(data["volumes"].keys()):
            volumes[instr].set(data["volumes"][instr])
    except KeyError:
        for instr in list(list(instruments.keys())):
            volumes[instr]=tk.IntVar(value=100)
    
    try:
        beat_length = data["beat_length"]
        print(beat_length)
        beat_length_entry.delete(0, tk.END)
        beat_length_entry.insert(0, str(beat_length))
    except KeyError:
        pass
    
    try:
        if highlight_first_beat_hit:
            highlight_first_beat_hit.set(data["highlight_first_beat_hit"])
        else:
            highlight_first_beat_hit = tk.BooleanVar(value=data["highlight_first_beat_hit"])
        
        
    except KeyError:
        pass
    
    print(pattern)
    playing = True
    

def load_pattern(filename):
    global pattern, bpm_entry, filename_entry, preview_enabled, bpm, pattern_beats, hits_entry, instruments, volumes, beat_length, highlight_first_beat_hit, beat_length_entry, highlight_first_beat_hit_entry
    preview_enabled = True
    data = json.load(open(filename, "r"))
    pattern_beats = data["length"]
    hits_entry.delete(0, tk.END)
    hits_entry.insert(0, str(pattern_beats))
    filename_entry.delete(0, tk.END)
    filename_entry.insert(0, str(filename.split("/")[-1].split(".")[0][0].upper()+filename.split("/")[-1].split(".")[0][1:].lower()))
    load_kit(data["kit"])
    pattern = data["pattern"]
    bpm = data["bpm"]
    bpm_entry.delete(0, tk.END)
    bpm_entry.insert(0, str(bpm))
    
    try:
        for instr in list(data["volumes"].keys()):
            volumes[instr].set(data["volumes"][instr])
    except KeyError:
        for instr in list(list(instruments.keys())):
            volumes[instr]=tk.IntVar(value=100)
    
    try:
        beat_length = data["beat_length"]
        print(beat_length)
        beat_length_entry.delete(0, tk.END)
        beat_length_entry.insert(0, str(beat_length))
    except KeyError:
        pass
    
    try:
        if highlight_first_beat_hit:
            highlight_first_beat_hit.set(data["highlight_first_beat_hit"])
        else:
            highlight_first_beat_hit = tk.BooleanVar(value=data["highlight_first_beat_hit"])
        
        
    except KeyError:
        pass
    
    print(pattern)
    apply_pattern(pattern)

def quickload_kit(kit_name):
    global instruments, audio_samples, pattern, top_frame, current_hit, pattern_beats, bottom_left_frame, highligted_col, bottom_middle_frame, bottom_right_frame, bottom_extra_left_frame, bottom_extra_right_frame, current_kit_name, playing
    current_kit_name = kit_name
    kit_data = json.load(open("kits/"+kit_name+".json"))
    instruments = kit_data["samples"]
    
    for instrument in instruments:
        d=instruments[instrument]
        audio_samples[d["name"]]=pygame.mixer.Sound("samples/"+d["file"])

def load_kit(kit_name):
    global instruments, audio_samples, preview_enabled, pattern, top_frame, current_hit, pattern_beats, bottom_left_frame, highligted_col, bottom_middle_frame, bottom_right_frame, bottom_extra_left_frame, bottom_extra_right_frame, current_kit_name, playing
    preview_enabled = True
    current_kit_name = kit_name
    kit_data = json.load(open("kits/"+kit_name+".json"))
    instruments = kit_data["samples"]

    # Configure the grid for the main layout
    root.grid_rowconfigure(0, weight=3)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=1)
    root.grid_columnconfigure(4, weight=1)

    top_frame = tk.Frame(root, bg="black")
    top_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")
    fill_buttons(top_frame, len(instruments), pattern_beats, on_button_click, on_button_right_click)

    # Bottom left section
    bottom_left_frame = tk.Frame(root, bg=panels)
    bottom_left_frame.grid(row=1, column=0, sticky="nsew")
    
    update_file_menu()

    # Bottom middle section
    bottom_middle_frame = tk.Frame(root, bg=panels)
    bottom_middle_frame.grid(row=1, column=1, sticky="nsew")
    
    update_playback_menu()

    # Bottom right section
    bottom_right_frame = tk.Frame(root, bg=panels)
    bottom_right_frame.grid(row=1, column=2, sticky="nsew")
    
    update_pattern_menu()

    # Bottom extra left section
    bottom_extra_left_frame = tk.Frame(root, bg=panels)
    bottom_extra_left_frame.grid(row=1, column=3, sticky="nsew")
    
    update_instrument_menu()

    # Bottom extra right section
    bottom_extra_right_frame = tk.Frame(root, bg=panels)
    bottom_extra_right_frame.grid(row=1, column=4, sticky="nsew")
    
    update_pattern_collection_menu()
    
    pattern = []
    for e in range(pattern_beats):
        column = []
        for e in range(len(instruments)):
            column.append({
                "enabled": False
            })
        pattern.append(column)
    
    root.configure(bg="black")
    playing = False
    highligted_col = 0
    try:
        apply_single_pattern_col(pattern, current_hit)
    except:
        pass
    apply_single_pattern_col(pattern, 0)
    current_hit = 0
    
def save_collection(filename):
    print(f"Saving collection to {filename}")
    collection_name = collection_name_entry.get().strip()
    if not collection_name:
        print("Collection name is empty.")
        return
    patterns = get_patterns_in_collection()
    if not patterns:
        print("No patterns selected for collection.")
        return

    data = {
        "name": collection_name,
        "patterns": patterns
    }

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    filename = filename.lower().replace(' ', '_')
    json.dump(data, open(filename, "w", encoding="utf-8"), indent=2)
    update_file_menu()

def load_collection(filename):
    global pattern_collection_var, dropdowns_container, add_button
    if not os.path.isfile(filename):
        print(f"Collection file {filename} not found.")
        return
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    patterns = data.get("patterns", [])
    clear_screen(dropdowns_container)
    if not os.path.isdir("patterns"):
        os.makedirs("patterns")
    pattern_names = [file.replace(".json", "").capitalize() for file in os.listdir("patterns")] + ["- Entfernen"]
    for pattern_file in patterns:
        pattern_name = os.path.splitext(os.path.basename(pattern_file))[0].capitalize()
        var = tk.StringVar(value=pattern_name if pattern_name in pattern_names else pattern_names[0])
        var.trace_add("write", check_deletions)
        dropdown = tk.OptionMenu(dropdowns_container, var, *pattern_names)
        dropdown.config(
            bg=buttons,
            fg="white",
            border=0,
            borderwidth=0,
            
            activebackground=buttons,
            activeforeground="white",
            highlightbackground=buttons
        )
        menu = dropdown["menu"]
        menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
        dropdown.pack(fill="x", padx=5, pady=3)
    if len(patterns) >= MAX_COLLECTION_LENGTH:
        add_button.config(state='disabled')
    else:
        add_button.config(state='normal')
    
def check_deletions(*args):
    global dropdowns_container
    for child in dropdowns_container.winfo_children():
        if isinstance(child, tk.OptionMenu):
            var = child.cget("textvariable")
            value = child.getvar(var)
            if value == "- Entfernen":
                child.destroy()
    

def update_pattern_collection_menu():
    global bottom_extra_right_frame, dropdowns_container, add_button, pattern_collection_var
    clear_screen(bottom_extra_right_frame)

    # Outer container for the pattern collection
    collection_frame = tk.LabelFrame(
        bottom_extra_right_frame,
        text="Pattern-Abfolge",
        border=0,
        
        bg=panels,
        fg="white",
        bd=2,
        relief="groove",
        labelanchor="n"
    )
    collection_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    if pattern_collection_var is None:
        pattern_collection_var = tk.BooleanVar(value=False)

    pattern_col_frame = tk.Frame(collection_frame, bg=buttons)
    pattern_col_frame.pack(fill="x", padx=10, pady=5)

    pattern_col_label = tk.Label(pattern_col_frame, text="Pattern-Abfolge aktivieren", bg=buttons, fg="white")
    pattern_col_label.pack(side="left")

    pattern_collection_entry = tk.Checkbutton(
        pattern_col_frame,
        variable=pattern_collection_var,
        onvalue=True,
        offvalue=False,
        bg=buttons,
        command=lambda:update_collection_mode()
    )
    pattern_collection_entry.pack(side="left")

    # Get all saved patterns
    if not os.path.isdir("patterns"):
        os.makedirs("patterns")
    pattern_names = [file.replace(".json", "").capitalize() for file in os.listdir("patterns")]+["- Entfernen"]

    # Container for the dropdowns (vertical stack)
    dropdowns_container = tk.Frame(collection_frame, bg=panels)
    dropdowns_container.pack(fill="both", expand=True)

    # Example: Show 3 dropdowns (you can make this dynamic if needed)
    num_dropdowns = 1
    for i in range(num_dropdowns):
        var = tk.StringVar(value=pattern_names[0] if pattern_names else "Kein Pattern")
        var.trace_add("write", check_deletions)
        dropdown = tk.OptionMenu(dropdowns_container, var, *pattern_names)
        dropdown.config(
            bg=buttons,
            fg="white",
            border=0,
            borderwidth=0,
            
            activebackground=buttons,
            activeforeground="white",
            highlightbackground=buttons
        )
        menu = dropdown["menu"]
        menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
        dropdown.pack(fill="x", padx=5, pady=3)

    # "+ Pattern hinzufügen" button at the bottom
    add_button = tk.Button(
        collection_frame,
        text="+ Pattern hinzufügen",
        bg=buttons,
        border=0,
        fg="white",
        
        command=lambda: add_pattern_to_collection()
    )
    add_button.pack(fill="x", padx=10, pady=8)

def update_collection_mode():
    global pattern_collection_var, playing, current_pattern, current_hit
    current_hit = 0
    save_collection("collections/autosave.json")
    playing = False
    current_pattern = 0
    if pattern_collection_var.get():
        disable_preview()
    else:
        save_pattern("patterns/autosave.json")
        load_pattern("patterns/autosave.json")
    load_collection("collections/autosave.json")

def add_pattern_to_collection():
    global dropdowns_container, add_button
    print(get_patterns_in_collection())
    if not os.path.isdir("patterns"):
        os.makedirs("patterns")
    pattern_names = [file.replace(".json", "").capitalize() for file in os.listdir("patterns")]+["- Entfernen"]
    var = tk.StringVar(value=pattern_names[0] if pattern_names else "Kein Pattern")
    var.trace_add("write", check_deletions)
    dropdown = tk.OptionMenu(dropdowns_container, var, *pattern_names)
    dropdown.config(
        bg=buttons,
        fg="white",
        border=0,
        borderwidth=0,
        
        activebackground=buttons,
        activeforeground="white",
        highlightbackground=buttons
    )
    menu = dropdown["menu"]
    menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
    dropdown.pack(fill="x", padx=5, pady=3)
    if len(get_patterns_in_collection()) == MAX_COLLECTION_LENGTH:
        add_button.config(state='disabled')
    
    
def get_patterns_in_collection():
    global dropdowns_container
    patterns = []
    if dropdowns_container:
        for child in dropdowns_container.winfo_children():
            if isinstance(child, tk.OptionMenu):
                var = child.cget("textvariable")
                value = child.getvar(var)
                filename = f"patterns/{value.lower()}.json"
                if os.path.isfile(filename):
                    patterns.append(filename)
    return patterns

def delete_pattern(pattern):
    try:
        os.remove(pattern)
        update_file_menu()
    except FileNotFoundError:
        pass
    
def new_pattern():
    global pattern, current_kit_name, current_hit, playing, volumes, instruments
    current_hit = 0
    load_kit(current_kit_name)
    for instr in list(instruments.keys()):
        volumes[instr] = tk.IntVar(value=1)
    playing = False
    current_hit = 0
    
filename_entry = None
pattern_var = None
hits_entry = None
highlight_first_beat_hit_entry = None


def update_file_menu():
    global bottom_left_frame, filename_entry, pattern_var, collection_name_entry
    clear_screen(bottom_left_frame)

    # Add "File" section
    file_frame = tk.LabelFrame(bottom_left_frame, text="File", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    file_frame.pack(fill="x", padx=10, pady=5)

    text = "Mein pattern"
    try:
        text = filename_entry.get()
    except:
        pass

    # Add text box for filename
    filename_entry = tk.Entry(file_frame, bg=buttons, border=0,  fg="white", justify="center")
    filename_entry.insert(0, text)
    filename_entry.pack(fill="x", padx=5, pady=5, ipady=5)

    # Add save button
    save_button = tk.Button(file_frame, text="Speichern", bg=buttons, border=0, fg="white",  command=lambda: save_pattern(f"patterns/{filename_entry.get().lower()}.json"))
    save_button.pack(fill="x", padx=10, pady=5)

    # Add dropdown for stored patterns
    if not os.path.isdir("patterns"):
        os.makedirs("patterns")
    pattern_names = [file.replace(".json", "").capitalize() for file in os.listdir("patterns")]
    patterns_available = bool(pattern_names)
    if patterns_available:
        pattern_var = tk.StringVar(value=pattern_var.get() if pattern_var and pattern_var.get() in pattern_names else pattern_names[0])
        pattern_dropdown = tk.OptionMenu(file_frame, pattern_var, *pattern_names)
    else:
        pattern_var = tk.StringVar(value="Kein Pattern verfügbar")
        pattern_dropdown = tk.OptionMenu(file_frame, pattern_var, "Kein Pattern verfügbar")
    pattern_dropdown.config(bg=buttons, fg="white", border=0, borderwidth=0, activebackground=buttons,  activeforeground="white", highlightbackground=buttons)
    menu = pattern_dropdown["menu"]
    menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
    pattern_dropdown.pack(fill="x", padx=10, pady=5)

    # Add load and delete buttons for patterns
    if patterns_available:
        load_button = tk.Button(file_frame, text="Laden", border=0,  bg=buttons, fg="white", command=lambda: load_pattern(f"patterns/{pattern_var.get().lower()}.json"))
        load_button.pack(fill="x", padx=10, pady=5)

        delete_button = tk.Button(file_frame, text="Löschen", border=0,  bg=buttons, fg="white", command=lambda: delete_pattern(f"patterns/{pattern_var.get().lower()}.json"))
        delete_button.pack(fill="x", padx=10, pady=5)
    
    # Add new button
    new_button = tk.Button(file_frame, text="Neues Pattern", bg=buttons, border=0, fg="white",  command=lambda: new_pattern())
    new_button.pack(fill="x", padx=10, pady=5)
    
    # Add export button
    export_button = tk.Button(file_frame, text="Als Sounddatei exportieren", bg=buttons, border=0, fg="white",  command=lambda: export_pattern())
    export_button.pack(fill="x", padx=10, pady=5)

    # Add "Kits" section
    kit_frame = tk.LabelFrame(bottom_left_frame, text="Kits", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    kit_frame.pack(fill="x", padx=10, pady=5)

    # Add dropdown for kits
    if not os.path.isdir("kits"):
        os.makedirs("kits")
    kit_names = [file.replace(".json", "").capitalize() for file in os.listdir("kits")]
    kit_var = tk.StringVar(value=kit_names[0])
    kit_dropdown = tk.OptionMenu(kit_frame, kit_var, *kit_names)
    kit_dropdown.config(bg=buttons, fg="white", border=0, borderwidth=0,  activebackground=buttons, activeforeground="white", highlightbackground=buttons)
    menu = kit_dropdown["menu"]
    menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
    kit_dropdown.pack(fill="x", padx=10, pady=5)

    # Add load button for kits
    load_button = tk.Button(kit_frame, text="Kit laden", border=0,  bg=buttons, fg="white", command=lambda: load_kit(kit_var.get()))
    load_button.pack(fill="x", padx=10, pady=5)
    

play_button = None

def update_playback_menu():
    global bottom_middle_frame, play_button, bpm, bpm_entry, beat_length, beat_length_entry, collection_name_entry
    clear_screen(bottom_middle_frame)
    playback_area = tk.LabelFrame(bottom_middle_frame, text="Playback", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    playback_area.pack(fill="x", padx=10, pady=5)
    
    play_image = ImageTk.PhotoImage(file="img/play.png")
    play_button = tk.Button(playback_area, image=play_image, border=0, bg=buttons, command=lambda: play_pause_pattern())
    play_button.image = play_image  # Keep a reference to avoid garbage collection
    play_button.pack(padx=10, pady=5)
    play_button.config(width=40, height=40)
    play_button.image = play_image  # Keep a reference to avoid garbage collection
    
    stop_image = ImageTk.PhotoImage(file="img/stop.png")
    stop_button = tk.Button(playback_area, image=stop_image, border=0, bg=buttons, command=lambda: stop_pattern())
    stop_button.image = stop_image  # Keep a reference to avoid garbage collection
    stop_button.pack(side="left", padx=5, pady=5)
    stop_button.config(width=40, height=40)
    stop_button.image = stop_image  # Keep a reference to avoid garbage collection

    play_button.pack(side="left", padx=5, pady=5)  # Adjust play button to align on the left
    
    # Add BPM section
    bpm_frame = tk.LabelFrame(bottom_middle_frame, text="BPM", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    bpm_frame.pack(fill="x", padx=10, pady=5)

    bpm_entry = tk.Entry(bpm_frame, bg=buttons, border=0,  fg="white", justify="center")
    bpm_entry.insert(0, str(bpm))
    bpm_entry.pack(fill="x", padx=5, pady=5, ipady=5)

    def update_bpm():
        global bpm, bpm_entry
        try:
            bpm = int(bpm_entry.get())
            if bpm < 10:
                bpm = 10
            if bpm > 500:
                bpm = 500
            bpm_entry.delete(0, tk.END)
            bpm_entry.insert(0, str(bpm))
            print(f"BPM updated to {bpm}")
        except ValueError:
            bpm_entry.delete(0, tk.END)
            bpm_entry.insert(0, str(bpm))
            

    update_bpm_button = tk.Button(bpm_frame, text="BPM setzen", bg=buttons, border=0, fg="white",  command=update_bpm)
    update_bpm_button.pack(fill="x", padx=10, pady=5)
    
    # Pattern Collection Management Section
    collection_mgmt_frame = tk.LabelFrame(
        bottom_middle_frame,
        text="Pattern-Abfolgen",
        border=0,
        
        bg=panels,
        fg="white",
        bd=2,
        relief="groove",
        labelanchor="n"
    )
    collection_mgmt_frame.pack(fill="x", padx=10, pady=5)

    # Entry for collection name
    collection_name_entry = tk.Entry(
        collection_mgmt_frame,
        bg=buttons,
        border=0,
        
        fg="white",
        justify="center"
    )
    collection_name_entry.insert(0, "Meine Abfolge")
    collection_name_entry.pack(fill="x", padx=5, pady=5, ipady=5)

    # Save collection button
    save_collection_button = tk.Button(
        collection_mgmt_frame,
        text="Abfolge speichern",
        bg=buttons,
        border=0,
        fg="white",
        
        command=lambda: save_collection(f"collections/{collection_name_entry.get()}.json")  # Replace with your save logic
    )
    save_collection_button.pack(fill="x", padx=10, pady=5)

    # List available collections
    collections = []
    if os.path.isdir("collections"):
        for file in os.listdir("collections"):
            if file.endswith(".json"):
                collections.append(file.replace(".json", "").capitalize())
    else:
        os.makedirs("collections")

    if collections:
        collections_var = tk.StringVar(value=collections[0])
        collections_dropdown = tk.OptionMenu(collection_mgmt_frame, collections_var, *collections)
    else:
        collections_var = tk.StringVar(value="Keine Abfolge verfügbar")
        collections_dropdown = tk.OptionMenu(collection_mgmt_frame, collections_var, "Keine Abfolge verfügbar")
    collections_dropdown.config(
        bg=buttons,
        fg="white",
        border=0,
        borderwidth=0,
        
        activebackground=buttons,
        activeforeground="white",
        highlightbackground=buttons
    )
    menu = collections_dropdown["menu"]
    menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
    collections_dropdown.pack(fill="x", padx=10, pady=5)

    # Load collection button
    load_collection_button = tk.Button(
        collection_mgmt_frame,
        text="Abfolge laden",
        bg=buttons,
        border=0,
        fg="white",
        
        command=lambda: load_collection(f"collections/{collections_var.get()}.json")  # Replace with your load logic
    )
    load_collection_button.pack(fill="x", padx=10, pady=5)

    # Delete collection button
    delete_collection_button = tk.Button(
        collection_mgmt_frame,
        text="Abfolge löschen",
        bg=buttons,
        border=0,
        fg="white",
        
        command=lambda: print(f"Delete collection: {collections_var.get()}")  # Replace with your delete logic
    )
    delete_collection_button.pack(fill="x", padx=10, pady=5)

def update_pattern_menu():
    global bottom_right_frame, pattern_beats, hits_entry, beat_length_entry, beat_length, highlight_first_beat_hit, highlight_first_beat_hit_entry
    clear_screen(bottom_right_frame)

    # Add "Timing" subsection
    timing_frame = tk.LabelFrame(bottom_right_frame, text="Timing", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    timing_frame.pack(fill="x", padx=10, pady=5)

    # Add entry for hits
    hits_entry = tk.Entry(timing_frame, bg=buttons, border=0,  fg="white", justify="center")
    hits_entry.insert(0, str(pattern_beats))
    hits_entry.pack(fill="x", padx=5, pady=5, ipady=5)
    def update_hits():
        global pattern_beats, pattern, instruments
        try:
            new_hits = int(hits_entry.get())
            if new_hits < 4:
                new_hits = 4
            if new_hits > 128:
                new_hits = 128
            pattern_beats = new_hits
            col = []
            for i in instruments:
                col.append({
                    "enabled": False
                })
            while len(pattern) < pattern_beats:
                pattern.append(col)
            hits_entry.delete(0, tk.END)
            hits_entry.insert(0, str(pattern_beats))
            save_pattern("patterns/autosave.json")
            load_kit(current_kit_name)
            load_pattern("patterns/autosave.json")
            print(f"Pattern hits updated to {pattern_beats}")
        except ValueError:
            hits_entry.delete(0, tk.END)
            hits_entry.insert(0, str(pattern_beats))

    # Add button to update hits
    update_hits_button = tk.Button(timing_frame, text="Schläge aktualisieren", bg=buttons, border=0, fg="white",  command=update_hits)
    update_hits_button.pack(fill="x", padx=10, pady=5)
    
    beat_length_entry = tk.Entry(timing_frame, bg=buttons, border=0,  fg="white", justify="center")
    beat_length_entry.insert(0, str(beat_length))
    beat_length_entry.pack(fill="x", padx=5, pady=5, ipady=5)
    
    def update_beat_length():
        global beat_length, beat_length_entry
        try:
            beat_length = int(beat_length_entry.get())
            if beat_length < 1:
                beat_length = 1
            beat_length_entry.delete(0, tk.END)
            beat_length_entry.insert(0, str(beat_length))
            print(f"Beat length updated to {beat_length}")
        except ValueError:
            beat_length_entry.delete(0, tk.END)
            beat_length_entry.insert(0, str(beat_length))
            
    update_bpm_button = tk.Button(timing_frame, text="Taktlänge setzen", bg=buttons, border=0, fg="white",  command=update_beat_length)
    update_bpm_button.pack(fill="x", padx=10, pady=5)    
    
    if highlight_first_beat_hit is None:
        highlight_first_beat_hit = tk.BooleanVar(value=True)

    highlight_frame = tk.Frame(timing_frame, bg=buttons)
    highlight_frame.pack(fill="x", padx=10, pady=5)

    highlight_label = tk.Label(highlight_frame, text="Ersten Schlag im Takt hervorheben", bg=buttons, fg="white")
    highlight_label.pack(side="left")

    highlight_first_beat_hit_entry = tk.Checkbutton(
        highlight_frame,
        variable=highlight_first_beat_hit,
        onvalue=True,
        offvalue=False,
        bg=buttons
    )
    highlight_first_beat_hit_entry.pack(side="left")
    
    share_frame = tk.LabelFrame(bottom_right_frame, text="Pattern teilen", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    share_frame.pack(fill="x", padx=10, pady=5)

    share_key_entry = tk.Entry(share_frame, bg=buttons, border=0,  fg="white", justify="center")
    

    def share_pattern():
        temp_filename = "patterns/share_temp.json"
        save_pattern(temp_filename)
        print("saved")
        pattern_data = {}
        with open(temp_filename, "r", encoding="utf-8") as f:
            pattern_data = f.read()
        print("read")
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        server_share_code = f"edmsynth-{code}"
        print(f"Sharing with code {server_share_code}")
        status, resp = send_jshare_request("set", key=server_share_code, value=pattern_data)
        print(f"Sent jShare request")
        print(status, resp)
        if status == 200:
            share_key_entry.delete(0, tk.END)
            share_key_entry.insert(0, code)
            popup(f"Pattern geteilt! Teilen-Code: {code}")
        else:
            popup("Fehler beim Teilen: "+resp.get("error", "Unbekannter Fehler"))

    def load_shared_pattern():
        key = share_key_entry.get().strip()
        if not key or key.lower() == "teilen-code":
            return
        if not key.startswith("edmsynth-"):
            key = "edmsynth-" + key
        status, resp = send_jshare_request("get", key=key)
        if status == 200 and "value" in resp:
            try:
                pattern_json = json.loads(resp["value"])
                pattern_name = pattern_json.get("name", "shared_loaded")
                safe_name = pattern_name.lower().replace(" ", "_").replace(".","-").replace("/","-").replace("\\","-")
                temp_filename = f"patterns/{safe_name}.json"
                with open(temp_filename, "w", encoding="utf-8") as f:
                    f.write(resp["value"])
                load_pattern(temp_filename)
                popup("Pattern geladen!")
            except Exception as e:
                popup("Fehler beim Verarbeiten des geladenen Patterns: "+str(e))
        else:
            popup("Fehler beim Laden: "+str(resp.get("error", "Unbekannter Fehler")))

    share_button = tk.Button(
        share_frame,
        text="Pattern teilen",
        bg=buttons,
        border=0,
        fg="white",
        
        command=share_pattern
    )
    share_button.pack(fill="x", padx=10, pady=5)

    share_key_entry.pack(fill="x", padx=5, pady=5, ipady=5)

    load_share_button = tk.Button(
        share_frame,
        text="Pattern laden",
        bg=buttons,
        border=0,
        fg="white",
        
        command=load_shared_pattern
    )
    load_share_button.pack(fill="x", padx=10, pady=5)
    


def update_instrument_menu():
    global bottom_extra_left_frame, instruments, panels, sliders, volumes
    clear_screen(bottom_extra_left_frame)
    
    instrument_frame = tk.LabelFrame(bottom_extra_left_frame, text="Lautstärken", border=0,  bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    instrument_frame.pack(fill="x", padx=10, pady=5)

    
    for instrument in instruments:
        row_container = tk.Frame(instrument_frame, bg=buttons)
        row_container.pack(fill="x", padx=10, pady=5)
    
        label = tk.Label(row_container, text=instruments[instrument]["name"], bg=buttons, fg="white")
        label.pack(side="left", padx=10)
    
        vol_var = tk.IntVar(value=100)
        volumes[instruments[instrument]["name"]] = vol_var
    
        vol_slider = tk.Scale(row_container, from_=0, to=100, orient="horizontal", bg=buttons, fg="white", border=0, highlightthickness=0, troughcolor=sliders, showvalue=False, variable=vol_var)
        vol_slider.pack(fill="x", side="left", expand=True)
    
    

playing = False

def play_pause_pattern():
    global play_button, playing
    playing = not playing
    if playing:
        play_image = ImageTk.PhotoImage(file="img/pause.png")
        tick()
    else:
        play_image = ImageTk.PhotoImage(file="img/play.png")
        
    play_button.config(image=play_image, compound="center")
    play_button.image = play_image  # Keep a reference to avoid garbage collection

bpm = 80
current_hit = 0

def tick():
    global bpm, current_hit, pattern, highligted_col, audio_samples, pattern_beats, preview_enabled, volumes, beat_length, highlight_first_beat_hit, pattern_collection_var, current_pattern
    if highlight_first_beat_hit:
        print(highlight_first_beat_hit.get())
    if playing:
        millis = int(60 / bpm * 1000 / beat_length)
        if millis < 100 or current_kit_name == "Sfx":
            pygame.mixer.stop()
        samples = []
        i = 0
        for instr in pattern[current_hit]:
            if instr["enabled"]:
                i_data = instruments[list(instruments.keys())[i]]
                sample = audio_samples[i_data["name"]]
                vol = 100
                try:
                    vol = volumes[i_data["name"]].get()/100
                except:
                    pass
                if highlight_first_beat_hit:
                    if highlight_first_beat_hit.get() and current_hit % beat_length != 0:
                        vol /= 2
                                        
                sample.set_volume(vol)

                samples.append(sample)
            i += 1
        
        for sample in samples:
            sample.play()
        
        highligted_col = current_hit
        if preview_enabled:
            apply_single_pattern_col(pattern, current_hit)
            if current_hit > 0:
                apply_single_pattern_col(pattern, current_hit-1)
            else:
                apply_single_pattern_col(pattern, pattern_beats-1)
            
        
        current_hit += 1
        if current_hit > pattern_beats-1:
            if pattern_collection_var.get():
                current_pattern += 1
                if current_pattern >= len(get_patterns_in_collection()):
                    current_pattern=0
                quickload_pattern(get_patterns_in_collection()[current_pattern])
            current_hit = 0
        
        
        root.after(millis, tick)
    else:
        pass

def stop_pattern():
    global playing, current_hit, pattern, highligted_col, preview_enabled
    t=highligted_col
    highligted_col = 0
    if preview_enabled:
        apply_single_pattern_col(pattern, t)
        apply_single_pattern_col(pattern, 0)
    playing = False
    current_hit = 0
    play_image = ImageTk.PhotoImage(file="img/play.png")
    play_button.config(image=play_image, compound="center")
    play_button.image = play_image  # Keep a reference to avoid garbage collection
    pygame.mixer.stop()
    

# Start the tick loop
tick()

# Create the main window
root = tk.Tk()
root.title("Synthesizer")
root.iconphoto(True, tk.PhotoImage(file='img/logo.png'))
root.iconbitmap('img/logo.ico')

# Ensure the background color of the main window is black
root.update_idletasks()

# Load samples
instruments = []
for file in os.listdir("kits"):
    data = json.load(open("kits/"+file, "r"))["samples"]
    for instrument in list(data.keys()):
        d=data[instrument]
        audio_samples[d["name"]]=pygame.mixer.Sound("samples/"+d["file"])

# Create the UI
load_kit("basic")

# Start the main loop
root.mainloop()