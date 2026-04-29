from ursina import *

app = Ursina()

speed = 0.05

# BALL
ball = Entity(
    model='sphere',
    color=color.red,
    scale=0.5,
    position=(-3, 0, 0),
    collider='box'
)

# CUBE
cube = Entity(
    model='cube',
    color=color.blue,
    scale=1,
    position=(2, 0, 0),
    collider='box'
)

def update():
    global speed
    
    ball.x += speed

    # CHECK COLLISION
    hit_info = ball.intersects()

    if hit_info.hit:
        print("Collision detected")
        speed *= -1           # bounce back
        ball.color = color.green

app.run()
