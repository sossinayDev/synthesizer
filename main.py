import tkinter as tk

def on_button_click(button_text):
    print(f"Button {button_text} clicked")

# Create the main window
root = tk.Tk()
root.title("Synthesizer")

# Configure the grid for the main layout
root.grid_rowconfigure(0, weight=2)  # Top section (2/3 height)
root.grid_rowconfigure(1, weight=1)  # Bottom sections (1/3 height)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Top section: 16x7 grid of buttons
top_frame = tk.Frame(root, bg="white")
top_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

for row in range(7):
    top_frame.grid_rowconfigure(row, weight=1)
for col in range(16):
    top_frame.grid_columnconfigure(col, weight=1)

for row in range(7):
    for col in range(16):
        button_text = ""
        button = tk.Button(top_frame, text=button_text, width=4, height=2, command=lambda bt=button_text: on_button_click(bt))
        button.grid(row=row, column=col, padx=2, pady=2)

# Bottom left section
bottom_left_frame = tk.Frame(root, bg="red")
bottom_left_frame.grid(row=1, column=0, sticky="nsew")

# Bottom middle section
bottom_middle_frame = tk.Frame(root, bg="green")
bottom_middle_frame.grid(row=1, column=1, sticky="nsew")

# Bottom right section
bottom_right_frame = tk.Frame(root, bg="blue")
bottom_right_frame.grid(row=1, column=2, sticky="nsew")

# Start the main loop
root.mainloop()