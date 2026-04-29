from tkinter import *
import random

# Generate secret number
def generate_secret():
    while True:
        num = str(random.randint(1000, 9999))
        if len(set(num)) == 4:
            return num

secret = generate_secret()

# Check user's guess

def check_guess():
    guess = entry.get()

    if len(guess) != 4 or not guess.isdigit():
        result_text.set("Enter a valid 4-digit number")
        return

    if len(set(guess)) != 4:
        result_text.set("Digits should not repeat")
        return

    bulls = 0
    cows = 0

    for i in range(4):
        if guess[i] == secret[i]:
            bulls += 1
        elif guess[i] in secret:
            cows += 1

    result_text.set(f"Bulls: {bulls}   Cows: {cows}")

    if bulls == 4:
        result_text.set("🎉 Congratulations! You guessed it!")


# ---------------------------
# GUI Window
# ---------------------------
window = Tk()
window.title("Cows and Bulls Game")
window.geometry("400x300")

# ---------------------------
# Variables
# ---------------------------
result_text = StringVar()
result_text.set("Start guessing the number!")

# ---------------------------
# Widgets
# ---------------------------
Label(
    window,
    text="Cows and Bulls Game",
    font=("Arial", 16, "bold"),
    fg="blue"
).pack(pady=10)

Label(  window,  text="Guess the 4-digit number\n(No repeated digits)",  font=("Arial", 10)).pack(pady=5)

entry = Entry(  window, font=("Arial", 14), justify="center")
entry.pack(pady=10)

Button(
    window, text="Check Guess", font=("Arial", 12), bg="green", fg="white",  command=check_guess).pack(pady=10)

Label(  window,  textvariable=result_text,  font=("Arial", 12),  fg="purple").pack(pady=10)

# ---------------------------
# Start the app
# ---------------------------
window.mainloop()
