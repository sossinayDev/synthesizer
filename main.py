import os
import tkinter as tk
from tkinter import font
import json
from PIL import ImageFont, ImageTk
import pygame

pygame.mixer.init()

silkscreen = None

settings = {}

audio_samples = {}

pattern_beats = 32

active = "#aaccff"
inactive = "#001133"
background = "#000000"
panels= "#333333"
buttons= "#aaaaaa"
col_increase = 50

current_kit_name = ""

instruments = []
pattern = []

def load_settings():
    global settings, active, inactive, background, panels, buttons, col_increase
    settings = json.load(open("user/settings.json"))
    active=settings["theme"]["active"]
    inactive=settings["theme"]["inactive"]
    background=settings["theme"]["background"]
    panels=settings["theme"]["panels"]
    buttons=settings["theme"]["buttons"]
    col_increase=settings["theme"]["col_increase"]
load_settings()


def clear_screen(frame):
    """Clears all widgets from the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def fill_buttons(frame, rows, cols, on_button_click):
    global instruments
    """Fills the given frame with a grid of buttons."""
    for row in range(rows):
        frame.grid_rowconfigure(row, weight=1)
    for col in range(cols):
        frame.grid_columnconfigure(col+1, weight=1)

    for row in range(rows):
        for col in range(cols + 1):
            instrument_data = instruments[list(instruments.keys())[row]]
            
            instru_inac = instrument_data["inactive"]
            instru_ac = instrument_data["active"]
            
            if col == 0:
                label = tk.Label(frame, text=f"{instrument_data['name']}", bg=background, fg="white", font=silkscreen)
                label.grid(row=row, column=col, padx=5, pady=2, sticky="nsew", columnspan=1)
            else:
                button = tk.Button(frame, text="", bg=instru_inac, fg="white", border=0, relief="flat", highlightthickness=0)
                button.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                button.config(command=lambda b=button: on_button_click(b))
    # Adjust the frame's padding to ensure all buttons fit within the visible area
    frame.grid_propagate(False)

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
    global current_kit_name, pattern, bpm, pattern_beats
    pattern_data = {
        "kit": current_kit_name,
        "pattern": pattern[:pattern_beats],
        "bpm": bpm,
        "length": pattern_beats
    }
    json.dump(pattern_data, open(filename, "w"))
    update_file_menu()

bpm_entry = None
def load_pattern(filename):
    global pattern, bpm_entry, bpm, pattern_beats, hits_entry, instruments
    data = json.load(open(filename, "r"))
    pattern_beats = data["length"]
    hits_entry.delete(0, tk.END)
    hits_entry.insert(0, str(pattern_beats))
    load_kit(data["kit"])
    pattern = data["pattern"]
    bpm = data["bpm"]
    bpm_entry.delete(0, tk.END)
    bpm_entry.insert(0, str(bpm))
    print(pattern)
    apply_pattern(pattern)


def load_kit(kit_name):
    global instruments, audio_samples, pattern, top_frame, current_hit, pattern_beats, bottom_left_frame, highligted_col, bottom_middle_frame, bottom_right_frame, bottom_extra_left_frame, bottom_extra_right_frame, current_kit_name, playing
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
    fill_buttons(top_frame, len(instruments), pattern_beats, on_button_click)

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

    # Bottom extra right section
    bottom_extra_right_frame = tk.Frame(root, bg=panels)
    bottom_extra_right_frame.grid(row=1, column=4, sticky="nsew")
    
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
    apply_single_pattern_col(pattern, current_hit)
    apply_single_pattern_col(pattern, 0)
    current_hit = 0
    
    for instrument in instruments:
        d=instruments[instrument]
        audio_samples[d["name"]]=pygame.mixer.Sound("samples/"+d["file"])
    

def delete_pattern(pattern):
    try:
        os.remove(pattern)
        update_file_menu()
    except FileNotFoundError:
        pass
    
def new_pattern():
    global pattern, current_kit_name, current_hit, playing
    current_hit = 0
    load_kit(current_kit_name)
    playing = False
    current_hit = 0
    
filename_entry = None
pattern_var = None
hits_entry = None


def update_file_menu():
    global bottom_left_frame, filename_entry, pattern_var
    clear_screen(bottom_left_frame)

    # Add "File" section
    file_frame = tk.LabelFrame(bottom_left_frame, text="File", border=0, font=silkscreen, bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    file_frame.pack(fill="x", padx=10, pady=5)

    text = "My pattern"
    try:
        text = filename_entry.get()
    except:
        pass

    # Add text box for filename
    filename_entry = tk.Entry(file_frame, bg=buttons, border=0, font=silkscreen, fg="white", justify="center")
    filename_entry.insert(0, text)
    filename_entry.pack(fill="x", padx=5, pady=5, ipady=5)

    # Add save button
    save_button = tk.Button(file_frame, text="Save", bg=buttons, border=0, fg="white", font=silkscreen, command=lambda: save_pattern(f"patterns/{filename_entry.get().lower()}.json"))
    save_button.pack(fill="x", padx=10, pady=5)

    # Add dropdown for stored patterns
    pattern_names = [file.replace(".json", "").capitalize() for file in os.listdir("patterns")]
    patterns_available = bool(pattern_names)
    pattern_var = tk.StringVar(value=pattern_var.get() if pattern_var in pattern_names else (pattern_names[0] if patterns_available else "No patterns available"))
    if pattern_var.get() == "No patterns available":
        pattern_dropdown = tk.OptionMenu(file_frame, pattern_var, *pattern_names, value=pattern_var.get())
    else:
        pattern_dropdown = tk.OptionMenu(file_frame, pattern_var, *pattern_names)
    pattern_dropdown.config(bg=buttons, fg="white", border=0, borderwidth=0, activebackground=buttons, font=silkscreen, activeforeground="white", highlightbackground=buttons)
    menu = pattern_dropdown["menu"]
    menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
    pattern_dropdown.pack(fill="x", padx=10, pady=5)

    # Add load and delete buttons for patterns
    if patterns_available:
        load_button = tk.Button(file_frame, text="Load", border=0, font=silkscreen, bg=buttons, fg="white", command=lambda: load_pattern(f"patterns/{pattern_var.get().lower()}.json"))
        load_button.pack(fill="x", padx=10, pady=5)

        delete_button = tk.Button(file_frame, text="Delete", border=0, font=silkscreen, bg=buttons, fg="white", command=lambda: delete_pattern(f"patterns/{pattern_var.get().lower()}.json"))
        delete_button.pack(fill="x", padx=10, pady=5)
    
    # Add new button
    new_button = tk.Button(file_frame, text="New Pattern", bg=buttons, border=0, fg="white", font=silkscreen, command=lambda: new_pattern())
    new_button.pack(fill="x", padx=10, pady=5)

    # Add "Kits" section
    kit_frame = tk.LabelFrame(bottom_left_frame, text="Kits", border=0, font=silkscreen, bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    kit_frame.pack(fill="x", padx=10, pady=5)

    # Add dropdown for kits
    kit_names = [file.replace(".json", "").capitalize() for file in os.listdir("kits")]
    kit_var = tk.StringVar(value=kit_names[0])
    kit_dropdown = tk.OptionMenu(kit_frame, kit_var, *kit_names)
    kit_dropdown.config(bg=buttons, fg="white", border=0, borderwidth=0, font=silkscreen, activebackground=buttons, activeforeground="white", highlightbackground=buttons)
    menu = kit_dropdown["menu"]
    menu.config(bg=buttons, fg="white", border=0, activebackground=buttons, activeforeground="white")
    kit_dropdown.pack(fill="x", padx=10, pady=5)

    # Add load button for kits
    load_button = tk.Button(kit_frame, text="Load", border=0, font=silkscreen, bg=buttons, fg="white", command=lambda: load_kit(kit_var.get()))
    load_button.pack(fill="x", padx=10, pady=5)

play_button = None

def update_playback_menu():
    global bottom_middle_frame, play_button, bpm, bpm_entry
    clear_screen(bottom_middle_frame)
    playback_area = tk.LabelFrame(bottom_middle_frame, text="Playback", border=0, font=silkscreen, bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
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
    bpm_frame = tk.LabelFrame(bottom_middle_frame, text="BPM", border=0, font=silkscreen, bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    bpm_frame.pack(fill="x", padx=10, pady=5)

    bpm_entry = tk.Entry(bpm_frame, bg=buttons, border=0, font=silkscreen, fg="white", justify="center")
    bpm_entry.insert(0, str(bpm))
    bpm_entry.pack(fill="x", padx=5, pady=5, ipady=5)

    def update_bpm():
        global bpm
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
            

    update_bpm_button = tk.Button(bpm_frame, text="Update BPM", bg=buttons, border=0, fg="white", font=silkscreen, command=update_bpm)
    update_bpm_button.pack(fill="x", padx=10, pady=5)

def update_pattern_menu():
    global bottom_right_frame, pattern_beats, hits_entry
    clear_screen(bottom_right_frame)

    # Add "Timing" subsection
    timing_frame = tk.LabelFrame(bottom_right_frame, text="Timing", border=0, font=silkscreen, bg=panels, fg="white", bd=2, relief="groove", labelanchor="n")
    timing_frame.pack(fill="x", padx=10, pady=5)

    # Add entry for hits
    hits_entry = tk.Entry(timing_frame, bg=buttons, border=0, font=silkscreen, fg="white", justify="center")
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
    update_hits_button = tk.Button(timing_frame, text="Update Hits", bg=buttons, border=0, fg="white", font=silkscreen, command=update_hits)
    update_hits_button.pack(fill="x", padx=10, pady=5)

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
    global bpm, current_hit, pattern, highligted_col, audio_samples, pattern_beats
    if playing:
        samples = []
        i = 0
        for instr in pattern[current_hit]:
            if instr["enabled"]:
                i_data = instruments[list(instruments.keys())[i]]
                samples.append(audio_samples[i_data["name"]])
            i += 1
        
        for sample in samples:
            sample.play()
        
        highligted_col = current_hit
        apply_single_pattern_col(pattern, current_hit)
        if current_hit > 0:
            apply_single_pattern_col(pattern, current_hit-1)
        else:
            apply_single_pattern_col(pattern, pattern_beats-1)
            
        
        current_hit += 1
        if current_hit > pattern_beats-1:
            current_hit = 0
        
        millis = int(60 / bpm * 1000)
        root.after(millis, tick)  # Schedule the tick function to run
    else:
        pass

def stop_pattern():
    global playing, current_hit, pattern, highligted_col
    highligted_col = 0
    apply_single_pattern_col(pattern, 0)
    apply_single_pattern_col(pattern, current_hit)
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

# Load the custom font using Pillow
silkscreen_path = "fonts/silkscreen.ttf"  # Path to your .ttf file
silkscreen_font = ImageFont.truetype(silkscreen_path, size=12)

# Register the font with Tkinter
silkscreen = font.Font(family="Silkscreen", size=12)

# Ensure the background color of the main window is black
root.update_idletasks()

# Create the UI
load_kit("basic")

# Start the main loop
root.mainloop()