import os
import tkinter as tk
from tkinter import font
import json
from PIL import ImageFont, ImageTk

silkscreen = None

settings = {}

active = "#aaccff"
inactive = "#001133"
background = "#000000"
panels= "#333333"
buttons= "#aaaaaa"

current_kit_name = ""

instruments = []
pattern = []

def load_settings():
    global settings, active, inactive, background, panels, buttons
    settings = json.load(open("user/settings.json"))
    active=settings["theme"]["active"]
    inactive=settings["theme"]["inactive"]
    background=settings["theme"]["background"]
    panels=settings["theme"]["panels"]
    buttons=settings["theme"]["buttons"]
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
                label = tk.Label(frame, text=f"{instrument_data['short']}", bg=background, fg="white", font=silkscreen)
                label.grid(row=row, column=col, padx=5, pady=2, sticky="nsew", columnspan=1)
            else:
                button = tk.Button(frame, text="", bg=instru_inac, fg="white", border=0, relief="flat", highlightthickness=0)
                button.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                button.config(command=lambda b=button: on_button_click(b))
    # Adjust the frame's padding to ensure all buttons fit within the visible area
    frame.grid_propagate(False)

def on_button_click(button):
    global instruments, pattern
    if button.winfo_name().replace("!button", "") == "":
        col = 0
        row = 0
    else:
        button_id = int(button.winfo_name().replace("!button", ""))
        cols = 16
        row = (button_id-1) // cols
        col = (button_id-1) % cols
    print(col, row)
    
    instrument_data = instruments[list(instruments.keys())[row]]
    instru_inac = instrument_data["inactive"]
    instru_ac = instrument_data["active"]
    
    pattern[col][row]["enabled"] = not pattern[col][row]["enabled"]
    if pattern[col][row]["enabled"]:
        button.config(bg=instru_ac)
    else:
        button.config(bg=instru_inac)
    

def apply_pattern(pattern_data):
    global pattern, instruments
    pattern = pattern_data
    for column in range(len(pattern)):
        for row in range(len(pattern[column])):
            button = top_frame.grid_slaves(row=row, column=column+1)[0]
            instrument_data = instruments[list(instruments.keys())[row]]
            instru_inac = instrument_data["inactive"]
            instru_ac = instrument_data["active"]
            if pattern[column][row]["enabled"]:
                button.config(bg=instru_ac)
            else:
                button.config(bg=instru_inac)

            
def save_pattern(filename):
    print("saving pattern to "+filename)
    global current_kit_name, pattern
    pattern_data = {
        "kit": current_kit_name,
        "pattern": pattern
    }
    json.dump(pattern_data, open(filename, "w"))
    update_file_menu()
    
def load_pattern(filename):
    global pattern
    data = json.load(open(filename, "r"))
    load_kit(data["kit"])
    pattern = data["pattern"]
    apply_pattern(pattern)


def load_kit(kit_name):
    global instruments, pattern, top_frame, bottom_left_frame, bottom_middle_frame, bottom_right_frame, bottom_extra_left_frame, bottom_extra_right_frame, current_kit_name
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

    # Top section: 16x7 grid of buttons
    top_frame = tk.Frame(root, bg="black")
    top_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")
    fill_buttons(top_frame, len(instruments), 16, on_button_click)

    # Bottom left section
    bottom_left_frame = tk.Frame(root, bg=panels)
    bottom_left_frame.grid(row=1, column=0, sticky="nsew")
    
    update_file_menu()

    # Bottom middle section
    bottom_middle_frame = tk.Frame(root, bg=panels)
    bottom_middle_frame.grid(row=1, column=1, sticky="nsew")

    # Bottom right section
    bottom_right_frame = tk.Frame(root, bg=panels)
    bottom_right_frame.grid(row=1, column=2, sticky="nsew")

    # Bottom extra left section
    bottom_extra_left_frame = tk.Frame(root, bg=panels)
    bottom_extra_left_frame.grid(row=1, column=3, sticky="nsew")

    # Bottom extra right section
    bottom_extra_right_frame = tk.Frame(root, bg=panels)
    bottom_extra_right_frame.grid(row=1, column=4, sticky="nsew")
    
    pattern = []
    for e in range(16):
        column = []
        for e in range(len(instruments)):
            column.append({
                "enabled": False
            })
        pattern.append(column)
    
    root.configure(bg="black")

def delete_pattern(pattern):
    try:
        os.remove(pattern)
        update_file_menu()
    except FileNotFoundError:
        pass
    
filename_entry = None
pattern_var = None


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
    pattern_var = tk.StringVar(value=pattern_var.get() if pattern_var else (pattern_names[0] if patterns_available else "No patterns available"))
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
