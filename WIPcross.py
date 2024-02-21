import pandas as pd
import random
import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class CrosswordGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crossword Game")
        self.root.geometry("1200x600")  # Adjusted the window size

        self.total_correct = 0
        self.current_streak = 0
        self.total_tried = 0

        self.load_data()

        self.create_widgets()

    def load_data(self):
        self.df = pd.read_excel('./NYT Crossword_2009_2016.xlsx')


    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, pady=50)

        button_start_game = tk.Button(frame, text="Start Game", command=self.play_game)
        button_start_game.grid(row=0, column=0, pady=(0, 5), columnspan=2, sticky=tk.W)

        # Dropdown for filtering by weekday
        self.weekday_var = tk.StringVar(value="All")  # Default value is "All"
        weekday_dropdown = ttk.Combobox(frame, textvariable=self.weekday_var, values=["All", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        weekday_dropdown.grid(row=1, column=0, pady=(0, 5), columnspan=2, sticky=tk.W)

        self.label_streak = tk.Label(frame, text="", anchor="w")
        self.label_streak.grid(row=0, column=1, pady=(0, 5), sticky=tk.W)

        self.label_clue = tk.Label(frame, text="", wraplength=1100, anchor="w", justify=tk.LEFT)
        self.label_clue.grid(row=2, column=0, pady=(10, 5), columnspan=2, sticky=tk.W)

        self.label_result = tk.Label(frame, text="", anchor="w")
        self.label_result.grid(row=3, column=0, pady=(0, 5), columnspan=2, sticky=tk.W)

        # Scrolled text widget for explanation
        self.explanation_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=10)
        self.explanation_text.grid(row=4, column=0, pady=(0, 5), columnspan=2, sticky=tk.W)

        self.label_correct_answer = tk.Label(frame, text="", wraplength=1100, anchor="w", justify=tk.LEFT, pady=5)
        self.label_correct_answer.grid(row=5, column=0, pady=(0, 5), columnspan=2, sticky=tk.W)

        self.entry_answer = tk.Entry(frame, width=50)
        self.entry_answer.grid(row=6, column=0, pady=(5, 10), sticky=tk.W)

        # Move the "Submit Answer" button to the left of the "Next Clue" button
        button_submit = tk.Button(frame, text="Submit Answer", command=self.check_answer)
        button_submit.grid(row=7, column=0, pady=(5, 10), sticky=tk.W)

        button_next_clue = tk.Button(frame, text="Next Clue", command=self.play_game)
        button_next_clue.grid(row=7, column=1, pady=(10, 5), columnspan=2, sticky=tk.W)
        # Bind the Enter key to the check_answer method
        self.root.bind('<Return>', lambda event: self.check_answer())

        # Bind the Tab key to the play_game method
        self.root.bind('<Command-n>', lambda event: self.play_game())

    def play_game(self):
        # Check if the DataFrame is empty
        if self.df.empty:
            messagebox.showinfo("No Clues Found", "No clues found. Exiting the game.")
            self.root.destroy()
            return

        # Filter clues based on the selected weekday
        selected_weekday = self.weekday_var.get()
        if selected_weekday != "All":
            filtered_df = self.df[self.df['Weekday'] == selected_weekday]
            if filtered_df.empty:
                messagebox.showinfo("No Clues Found", f"No {selected_weekday} clues found. Exiting the game.")
                self.root.destroy()
                return
            self.random_row = filtered_df.sample()
        else:
            self.random_row = self.df.sample()

        # Extract clue information
        self.clue = self.random_row['Clue'].values[0]
        self.word = self.random_row['Word'].values[0]
        self.correct_answer_stripped = re.sub(r'\([^)]*\)', '', self.word.lower()).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")
        clue_length = len(self.correct_answer_stripped)
        year = self.random_row['Year'].values[0]
        weekday = self.random_row['Weekday'].values[0]

        self.label_clue.config(text=f"🤨 Crossword Clue: {self.clue}\n🔢 Clue Length: {clue_length} characters {'_ ' * clue_length}\n🗓️ Date: {year}, {weekday}")
        self.label_result.config(text="")
        self.label_correct_answer.config(text="")
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.config(state=tk.DISABLED)
        self.entry_answer.delete(0, 'end')

        self.label_streak.config(text=f"Current Streak: {'🔥' * self.current_streak}")

    def check_answer(self):
        user_answer = self.entry_answer.get()
        user_answer_stripped = re.sub(r'\([^)]*\)', '', user_answer).replace("-", "").replace(" ", "").replace("'", "").replace("/", "").replace(".", "")
        user_answer_lower = user_answer_stripped.lower()

        if user_answer_lower == "exit":
            messagebox.showinfo("Thanks for playing!", f"Total Attempted: {self.total_tried}\nTotal Correct: {self.total_correct}")
            self.root.destroy()
            return

        if user_answer_lower == self.correct_answer_stripped:
            self.label_result.config(text="✅ Correct!")
            self.total_correct += 1
            self.current_streak += 1
            if self.current_streak + 20 > (self.root.winfo_width() // 2):
                self.label_result.config(text="🔥 STREAK TOO HOT 🔥")
            else:
                self.label_result.config(text=f"Current Streak: {'🔥' * self.current_streak}")
        else:
            self.label_result.config(text=f"❌ Incorrect. The correct answer is: {self.word.lower()}")
            self.current_streak = 0

        explanation = self.random_row['Explanation'].values[0]
        explanation = "No explanation found" if pd.isna(explanation) else explanation
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.insert(tk.END, explanation)
        self.explanation_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    game_gui = CrosswordGameGUI(root)
    root.mainloop()
