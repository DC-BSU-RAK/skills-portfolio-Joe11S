import tkinter as tk
from tkinter import ttk
import random

#region INITIALIZATION
root = tk.Tk()
root.title("Alexa, Tell me a Joke!")
root.geometry("800x600")
#endregion INITIALIZATION

#region SCRIPT

def get_random_joke():
    """Read randomJokes.txt, extract a random joke, and separate Q & A."""
    try:
        with open("Assessment 1 - Skills Portfolio/A1 - Resources/randomJokes.txt", "r") as file:
            content = file.read()
    except FileNotFoundError:
        return ("Error: Joke file not found.", "")

    # Split content by blank lines to get individual jokes
    jokes = content.strip().split("\n\n")
    
    if not jokes or not jokes[0].strip():
        return ("Error: Joke file is empty.", "")
    
    # Select a random joke block
    random_joke_block = random.choice(jokes)
    
    parts = random_joke_block.split('\n###\n', 1) 
    
    if len(parts) == 2:
        question = parts[0].strip()
        punchline = parts[1].strip()
        return (question, punchline)
    else:
        # Handle malformed jokes that don't have the delimiter
        return (random_joke_block.strip(), "Error: Missing punchline delimiter.")
current_punchline = ""

def display_joke(show_punchline=False):
    global current_punchline
    
    if not show_punchline:
        # Get a NEW joke only if we are starting a new joke sequence
        question, punchline = get_random_joke()
        current_punchline = punchline # Save the punchline globally
        text_to_display = question + "\n\n(Click 'Show Punchline' to reveal!)"
    else:
        # Reveal the punchline based on the saved variables
        question_with_hint = joke_display.get(1.0, tk.END).split('\n\n')[0].strip()
        text_to_display = question_with_hint + "\n\n" + current_punchline
        
    joke_display.config(state="normal")
    joke_display.delete(1.0, tk.END)
    joke_display.insert(1.0, text_to_display)
    joke_display.config(state="disabled")

def show_punchline():
    if current_punchline:
        display_joke(show_punchline=True)
    else:
        # Handle case where no joke has been loaded yet
        joke_display.config(state="normal")
        joke_display.delete(1.0, tk.END)
        joke_display.insert(1.0, "Please click 'Next Joke' first.")
        joke_display.config(state="disabled")

    joke_display.config(state="disabled")

#endregion SCRIPT

#region STYLESHEET
style = ttk.Style()
#endregion STYLESHEET

#region GUI
#head
header = ttk.Label(root, text="Alexa, Tell me a Joke!", font=("Arial", 24, "bold"))
header.pack(pady=10) # Use the improved packing suggested earlier

# Text widget to display the joke
joke_display = tk.Text(root, height=8, width=60, font=("Arial", 12), wrap="word")
joke_display.pack(padx=20, pady=10, fill="x")
joke_display.config(state="disabled")

# Frame to hold the two buttons side-by-side
button_frame = ttk.Frame(root)
button_frame.pack(padx=20, pady=10, fill="x")

# Button to get the next joke (calls display_joke without arguments)
next_joke_button = ttk.Button(button_frame, text="Next Joke", command=lambda: display_joke(show_punchline=False))
next_joke_button.pack(side="left", expand=True, fill="x", padx=(0, 5)) # Pack to the left

# Button to show the punchline (calls the new show_punchline function)
punchline_button = ttk.Button(button_frame, text="Show Punchline", command=show_punchline)
punchline_button.pack(side="right", expand=True, fill="x", padx=(5, 0)) # Pack to the right


#endregion GUI

#region UPDATE
root.mainloop()
#endregion UPDATE