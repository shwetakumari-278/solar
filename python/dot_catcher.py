from tkinter import *
import random

# ---------------------------
# Window
# ---------------------------
window = Tk()
window.title("Pop the Dot Game")
window.geometry("500x400")

# ---------------------------
# Variables
# ---------------------------
score = 0
radius = 20

score_text = StringVar()
score_text.set("Score: 0")

# ---------------------------
# Canvas
# ---------------------------
canvas = Canvas(window, width=480, height=300, bg="lightblue")
canvas.pack(pady=10)

Label(
    window,
    textvariable=score_text,
    font=("Arial", 12, "bold")
).pack()

# ---------------------------
# Draw Dot
# ---------------------------
def draw_dot():
    global x, y

    canvas.delete("all")

    x = random.randint(radius, 460)
    y = random.randint(radius, 280)

    canvas.create_oval(
        x - radius, y - radius,
        x + radius, y + radius,
        fill="red"
    )

draw_dot()

# ---------------------------
# Click Event
# ---------------------------
def pop_dot(event):
    global score

    dx = event.x - x
    dy = event.y - y

    if dx*dx + dy*dy <= radius*radius:
        score += 1
        score_text.set(f"Score: {score}")
        draw_dot()

canvas.bind("<Button-1>", pop_dot)

window.mainloop()