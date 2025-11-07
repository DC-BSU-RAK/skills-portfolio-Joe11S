import tkinter as tk
from tkinter import ttk
import random

#region INITIALIZATION
root = tk.Tk()
root.title("Math Quiz")
root.geometry("800x600")
#endregion INITIALIZATION

#region STATE VARIABLES
OPERATORS = [
    "+", "-"
]
difficulty = "" 
current_answer = 0 # Stores the correct answer for the current question
current_question_count = 0
score = 0
TOTAL_QUESTIONS = 10
#endregion STATE VARIABLES

#region SCRIPT
def select_easy():
    global difficulty
    diff_display.config(text="Difficulty selected: EASY")
    difficulty = "easy"

def select_mod():
    global difficulty
    diff_display.config(text="Difficulty selected: MODERATE")
    difficulty = "moderate"

def select_hard():
    global difficulty
    diff_display.config(text="Difficulty selected: ADVANCED")
    difficulty = "advanced"

def decide_operation():
    return random.choice(OPERATORS)

def generate_number(difficulty):
    # Using random.randint(a, b) includes both endpoints
    if difficulty == "easy":
        # Two-digit + Single-digit
        num1 = random.randint(10, 99)
        num2 = random.randint(0, 9)
    elif difficulty == "moderate":
        # Three-digit + Two-digit
        num1 = random.randint(100, 999)
        num2 = random.randint(10, 99)
    elif difficulty == "advanced": 
        # Four-digit + Three-digit
        num1 = random.randint(1000, 9999)
        num2 = random.randint(100, 999)
    else: # Fallback if difficulty isn't set
        num1, num2 = 20, 5
        
    return [num1, num2]

def format_question(num1, num2, op):
    return f"{num1} {op} {num2} = ?"

def start_quiz():
    """Switches from difficulty frame to in-game frame and starts the first question."""
    global current_question_count, score
    
    # Check if difficulty was actually selected
    if not difficulty:
        print("Please select a difficulty before starting.")
        return

    # Clear previous frames and set up game
    difficulty_frame.grid_forget()
    menu_frame.grid_forget()
    
    # Switch to grid for ingame_frame
    ingame_frame.grid(row=0, column=0, sticky="nsew") 
    
    # Ensure all in-game widgets are shown 
    question_label.grid(row=0, column=0)
    answer_entry.grid(row=1, column=0)
    submit_button.grid(row=2, column=0)
    feedback_label.grid(row=3, column=0)
    
    # Hide the menu return button if it was shown from a previous game
    menu_return.grid_forget() 
    
    current_question_count = 0
    score = 0
    
    # Start the first question
    next_question()

def next_question():
    """Generates, displays the next question, and stores the correct answer."""
    global current_answer, current_question_count
    feedback_label.config(text="")
    submit_button.config(state=tk.NORMAL)
    
    if current_question_count >= TOTAL_QUESTIONS:
        # Game over logic
        question_label.config(text=f"Quiz Over! Final Score: {score}/{TOTAL_QUESTIONS}")
        answer_entry.grid_forget()
        submit_button.grid_forget()
        menu_return.grid(row=4, column=0, columnspan=3, pady=20) # Show menu return
        return

    current_question_count += 1
    
    # 1. Generate Numbers and Operation
    num_pair = generate_number(difficulty)
    num1, num2 = num_pair[0], num_pair[1]
    op = decide_operation()

    # Ensure subtraction results in a non-negative number for simplicity
    if op == "-" and num1 < num2:
        num1, num2 = num2, num1 

    # 2. Calculate Correct Answer
    if op == "+":
        correct = num1 + num2
    elif op == "-":
        correct = num1 - num2
    
    current_answer = correct # Store the correct answer globally
    
    # 3. Format and Display Question
    problem_text = format_question(num1, num2, op)
    question_label.config(text=problem_text)
    score_label.config(text=f"Score: {score}/{TOTAL_QUESTIONS} | Q: {current_question_count}/{TOTAL_QUESTIONS}")

    # 4. Clear the Entry field for the new question
    answer_entry.delete(0, tk.END)

def check_answer():
    """Parses user input, checks it against the correct answer, gives feedback, and moves to the next question."""
    global score
    
    try:
        user_input = int(answer_entry.get())
        
        if user_input == current_answer:
            feedback_label.config(text="Correct! 🎉", foreground="green")
            score += 1
        else:
            feedback_label.config(text=f"Incorrect. The answer was {current_answer}. 😔", foreground="red")
            
        # Update score display (this will be updated fully in next_question too)
        score_label.config(text=f"Score: {score}/{TOTAL_QUESTIONS} | Q: {current_question_count}/{TOTAL_QUESTIONS}")

        # Wait a moment before loading the next question
        submit_button.config(state=tk.DISABLED)
        root.after(1500, next_question)
        
    except ValueError:
        feedback_label.config(text="Please enter a valid number.", foreground="orange")

#REGION SELECTORS
def diff_select():
    """Shows the difficulty selection frame."""
    # Clear previous frames and set up diff selector
    ingame_frame.grid_forget()
    menu_frame.grid_forget()
    # Switch to grid for difficulty_frame
    difficulty_frame.grid(row=0, column=0, sticky="nsew") 

def men_ret():
    """Shows the main menu frame."""
    # Clear previous frames and set up diff selector
    ingame_frame.grid_forget()
    difficulty_frame.grid_forget()
    # Switch to grid for menu_frame
    menu_frame.grid(row=0, column=0, sticky="nsew") 

#endregion SCRIPT

#region STYLESHEET
style = ttk.Style()

style.configure("Diff.TLabel", font=('Arial', 20))
style.configure("Title.TLabel", font=('Arial', 48, "bold"))
style.configure("Question.TLabel", font=('Arial', 24, "bold"))

#endregion STYLESHEET

#region GUI
# Set up grid for the main root window to handle frame switching cleanly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

#region frames 
menu_frame = ttk.Frame(root)
difficulty_frame = ttk.Frame(root)
ingame_frame = ttk.Frame(root)

# Configure the columns of the main frames
for frame in (menu_frame, difficulty_frame, ingame_frame):
    frame.grid_columnconfigure(0, weight=1)

# Start by showing the menu frame
menu_frame.grid(row=0, column=0, sticky="nsew") 
#endregion frame

#region menu 
title = ttk.Label(menu_frame, text="MATH QUIZ", style="Title.TLabel")
title.grid(row=0, column=0, pady=(100, 30))
menu_play = ttk.Button(menu_frame, text="Play!", command=diff_select)
menu_play.grid(row=1, column=0, pady=10)
#endregion menu

#region difficulty IMPLEMENTING SUB-FRAMES HERE

# 1. Sub-frames defined within difficulty_frame
diff_label_frame = ttk.Frame(difficulty_frame)
diff_button_frame = ttk.Frame(difficulty_frame)

# Configure rows in difficulty_frame to center the sub-frames
difficulty_frame.grid_rowconfigure(0, weight=1) # Spacer
difficulty_frame.grid_rowconfigure(3, weight=1) # Spacer

# Position the sub-frames within difficulty_frame
diff_label_frame.grid(row=1, column=0, pady=10)
diff_button_frame.grid(row=2, column=0, pady=10)
# Configure button frame column to center buttons
diff_button_frame.grid_columnconfigure(0, weight=1) 
diff_button_frame.grid_columnconfigure(2, weight=1) 

# Widgets are placed into their respective sub-frames

# Difficulty Label Frame contents (Row 0 in diff_label_frame)
diff_display = ttk.Label(diff_label_frame, text="Difficulty selected: ", style="Diff.TLabel")
diff_display.grid(row=0, column=0, pady=10, columnspan=3)

# Button Frame contents (Column 1 used for centering)
easy_diff_button = ttk.Button(diff_button_frame, text="Easy", command=select_easy)
mod_diff_button = ttk.Button(diff_button_frame, text="Moderate", command=select_mod)
hard_diff_button = ttk.Button(diff_button_frame, text="Advanced", command=select_hard)
start_button = ttk.Button(diff_button_frame, text="Start Quiz!", command=start_quiz)
menu_return_diff = ttk.Button(diff_button_frame, text="Return to Main Menu!", command=men_ret)

# Placing widgets on the grid of diff_button_frame
easy_diff_button.grid(row=1, column=1, pady=5, sticky="ew")
mod_diff_button.grid(row=2, column=1, pady=5, sticky="ew")
hard_diff_button.grid(row=3, column=1, pady=5, sticky="ew")
start_button.grid(row=4, column=1, pady=30, sticky="ew")
menu_return_diff.grid(row=5, column=1, pady=10, sticky="ew")

#endregion difficulty

#region ingame
# Configure ingame frame for better centering
ingame_frame.grid_columnconfigure(1, weight=1) 
ingame_frame.grid_rowconfigure(9, weight=1) # Push score label to the bottom

# Display the question
question_label = ttk.Label(ingame_frame, text="Question text appears here.", style="Question.TLabel")
question_label.grid(row=0, column=0)

# User entry input
answer_entry = ttk.Entry(ingame_frame, font=('Arial', 18), justify='center')
answer_entry.grid(row=1, column=0)

# Submit button (calls the checking function)
submit_button = ttk.Button(ingame_frame, text="Submit Answer", command=check_answer)
submit_button.grid(row=2, column=0)

# Feedback label
feedback_label = ttk.Label(ingame_frame, text="", font=('Arial', 14))
feedback_label.grid(row=3, column=0)

# Return to Menu button (hidden initially, shown on game over)
menu_return = ttk.Button(ingame_frame, text="Return to Main Menu!", command=men_ret) 
# Will be gridded dynamically in next_question()

# Score display (placed near the bottom of the frame)
score_label = ttk.Label(ingame_frame, text="Score: 0/10 | Q: 0/10", font=('Arial', 12))
score_label.grid(row=10, column=0) 

#endregion ingame

#region UPDATE
root.mainloop()
#endregion UPDATE