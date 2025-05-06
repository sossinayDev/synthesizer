import tkinter as tk
import json

active = "#aaccff"
inactive = "#001133"

instruments = []
pattern = []

def clear_screen(frame):
    """Clears all widgets from the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def fill_buttons(frame, rows, cols, on_button_click):
    """Fills the given frame with a grid of buttons."""
    for row in range(rows):
        frame.grid_rowconfigure(row, weight=1)
    for col in range(cols):
        frame.grid_columnconfigure(col, weight=1)

    for row in range(rows):
        for col in range(cols):
            button = tk.Button(frame, text="", bg=inactive, fg="white", border=0)
            button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            button.config(command=lambda b=button: on_button_click(b))

def on_button_click(button):
    global instruments, pattern
    if button.winfo_name().replace("!button", "") == "":
        col = 0
        row = 0
    else:
        button_id = int(button.winfo_name().replace("!button", ""))
        cols = len(instruments)
        row = button_id // cols
        col = button_id % cols
    print(col, row)
    print(pattern)
    pattern[row][col] = not pattern[row][col]
    if pattern[row][col]:
        button.config(bg=active)
    else:
        button.config(bg=inactive)
    
    


def load_kit(kit_name):
    global instruments, pattern, top_frame, bottom_left_frame, bottom_middle_frame, bottom_right_frame
    kit_data = json.load(open("kits/"+kit_name+".json"))
    instruments = kit_data["samples"]

    # Configure the grid for the main layout
    root.grid_rowconfigure(0, weight=2)  # Top section (2/3 height)
    root.grid_rowconfigure(1, weight=1)  # Bottom sections (1/3 height)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    # Top section: 16x7 grid of buttons
    top_frame = tk.Frame(root, bg="black")
    top_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
    fill_buttons(top_frame, len(instruments), 16, on_button_click)

    # Bottom left section
    bottom_left_frame = tk.Frame(root, bg="black")
    bottom_left_frame.grid(row=1, column=0, sticky="nsew")

    # Bottom middle section
    bottom_middle_frame = tk.Frame(root, bg="black")
    bottom_middle_frame.grid(row=1, column=1, sticky="nsew")

    # Bottom right section
    bottom_right_frame = tk.Frame(root, bg="black")
    bottom_right_frame.grid(row=1, column=2, sticky="nsew")
    
    pattern = []
    for e in range(16):
        column = []
        for e in range(len(instruments)):
            column.append(False)
        pattern.append(column)
    
    print(pattern)
    root.configure(bg="black")

# Create the main window
root = tk.Tk()
root.title("Synthesizer")

# Ensure the background color of the main window is black
root.update_idletasks()

# Create the UI
load_kit("basic")

# Start the main loop
root.mainloop()
