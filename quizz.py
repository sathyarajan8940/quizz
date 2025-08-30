"""
quiz_app.py
Simple Quiz App using Tkinter.

Features:
- Multiple choice questions
- Next / Previous navigation
- Score calculation
- Save high scores to scores.json
- Progress indicator
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

# ---------- Sample questions ----------
# Each question: {'q': question_text, 'options': [...], 'a': correct_index}
QUESTIONS = [
    {
        'q': 'What is the output of print(2 + 3 * 4)?',
        'options': ['20', '14', '24', '10'],
        'a': 1
    },
    {
        'q': 'Which HTML tag is used for a paragraph?',
        'options': ['<p>', '<div>', '<span>', '<h1>'],
        'a': 0
    },
    {
        'q': 'Which data structure uses LIFO?',
        'options': ['Queue', 'Stack', 'Array', 'Graph'],
        'a': 1
    },
    {
        'q': 'Which keyword defines a function in Python?',
        'options': ['function', 'fn', 'def', 'fun'],
        'a': 2
    },
    {
        'q': 'CSS stands for?',
        'options': ['Cascading Style Sheets', 'Computer Style Sheet', 'Creative Styling Syntax', 'Colorful Style Sheets'],
        'a': 0
    }
]

SCORES_FILE = "scores.json"

# ---------- Persistence for high scores ----------
def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_score(name, score, total):
    scores = load_scores()
    scores.append({"name": name, "score": score, "total": total})
    # sort descending by score
    scores = sorted(scores, key=lambda s: (-s['score'], -s['total']))
    # keep top 10
    scores = scores[:10]
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

# ---------- Tkinter GUI ----------
class QuizApp:
    def __init__(self, master):
        self.master = master
        master.title("Quiz App")
        master.geometry("700x420")
        master.resizable(False, False)

        self.questions = QUESTIONS
        self.total = len(self.questions)
        self.current = 0
        # user answers stored as indices (or None)
        self.answers = [None] * self.total

        # UI frames
        self.top_frame = tk.Frame(master, padx=16, pady=12)
        self.top_frame.pack(fill="x")

        self.title_label = tk.Label(self.top_frame, text="Quiz App", font=("Arial", 18, "bold"))
        self.title_label.pack(side="left")

        self.progress_label = tk.Label(self.top_frame, text=self.progress_text(), font=("Arial", 12), fg="#5b6a82")
        self.progress_label.pack(side="right")

        self.card = tk.Frame(master, padx=20, pady=18, bd=0)
        self.card.pack(fill="both", expand=True)

        # Question text
        self.q_text = tk.Label(self.card, text="", font=("Arial", 14), wraplength=640, justify="left")
        self.q_text.pack(anchor="w")

        # Radio options
        self.selected = tk.IntVar(value=-1)
        self.options_frame = tk.Frame(self.card)
        self.options_frame.pack(anchor="w", pady=(12,0))

        self.option_buttons = []
        for i in range(4):  # up to 4 options
            rb = tk.Radiobutton(self.options_frame, text="", variable=self.selected, value=i, font=("Arial", 12), anchor="w", justify="left", wraplength=620)
            rb.pack(fill="x", pady=6, anchor="w")
            self.option_buttons.append(rb)

        # Control buttons
        self.controls = tk.Frame(master, pady=12)
        self.controls.pack(fill="x")

        self.prev_btn = tk.Button(self.controls, text="◀ Previous", width=12, command=self.prev_question)
        self.prev_btn.pack(side="left", padx=(20,8))

        self.next_btn = tk.Button(self.controls, text="Next ▶", width=12, command=self.next_question)
        self.next_btn.pack(side="left")

        self.submit_btn = tk.Button(self.controls, text="Submit Quiz", width=14, bg="#2b7a78", fg="white", command=self.submit_quiz)
        self.submit_btn.pack(side="right", padx=(8,20))

        self.view_scores_btn = tk.Button(self.controls, text="View High Scores", width=16, command=self.show_high_scores)
        self.view_scores_btn.pack(side="right", padx=8)

        # keyboard bindings
        master.bind("<Left>", lambda e: self.prev_question())
        master.bind("<Right>", lambda e: self.next_question())
        master.bind("<Return>", lambda e: self.next_question())

        # load first question
        self.load_question()

    def progress_text(self):
        return f"Question {self.current+1} / {self.total}"

    def load_question(self):
        q = self.questions[self.current]
        self.q_text.config(text=f"{self.current+1}. {q['q']}")
        opts = q['options']
        # set options text; hide extra radio buttons if fewer than 4 options
        for i, rb in enumerate(self.option_buttons):
            if i < len(opts):
                rb.config(text=opts[i], value=i)
                rb.pack(fill="x", pady=6, anchor="w")
            else:
                rb.pack_forget()
        # set selected if previously answered
        ans = self.answers[self.current]
        self.selected.set(ans if ans is not None else -1)
        # update progress label
        self.progress_label.config(text=self.progress_text())
        # enable/disable prev button
        self.prev_btn.config(state="normal" if self.current > 0 else "disabled")

    def save_current_answer(self):
        val = self.selected.get()
        if val >= 0:
            self.answers[self.current] = val

    def next_question(self):
        self.save_current_answer()
        if self.current < self.total - 1:
            self.current += 1
            self.load_question()
        else:
            # at the end, prompt to submit
            if messagebox.askyesno("Submit", "You are at the last question. Submit quiz now?"):
                self.submit_quiz()

    def prev_question(self):
        self.save_current_answer()
        if self.current > 0:
            self.current -= 1
            self.load_question()

    def calculate_score(self):
        score = 0
        for i, q in enumerate(self.questions):
            if self.answers[i] is not None and self.answers[i] == q['a']:
                score += 1
        return score

    def submit_quiz(self):
        self.save_current_answer()
        # ensure at least one question answered
        if all(a is None for a in self.answers):
            if not messagebox.askyesno("No answers", "You haven't answered any questions. Submit anyway?"):
                return
        score = self.calculate_score()
        total = self.total
        pct = round(score/total * 100, 1)
        msg = f"You scored {score} out of {total} ({pct}%)."
        messagebox.showinfo("Result", msg)
        # ask to save score
        if messagebox.askyesno("Save Score", "Do you want to save your score to high scores?"):
            name = simpledialog.askstring("Your name", "Enter your name (max 20 chars):", parent=self.master)
            if name:
                name = name.strip()[:20]
                save_score(name, score, total)
                messagebox.showinfo("Saved", "Your score was saved.")
        # disable UI after submit
        self.disable_quiz_after_submit()

    def disable_quiz_after_submit(self):
        for rb in self.option_buttons:
            rb.config(state="disabled")
        self.next_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
        self.submit_btn.config(state="disabled")

    def show_high_scores(self):
        scores = load_scores()
        if not scores:
            messagebox.showinfo("High Scores", "No high scores yet.")
            return
        text = "Top Scores:\n\n"
        for i, s in enumerate(scores, 1):
            text += f"{i}. {s['name']} — {s['score']}/{s['total']}\n"
        messagebox.showinfo("High Scores", text)

# ---------- Run the app ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
