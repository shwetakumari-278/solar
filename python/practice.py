from ursina import*
speed= 0.05
def update():
  global speed
  ball.x=ball.x + speed
  hit_info=ball.intersects()
  if hit_info.hit:
    speed*=-1
app= Ursina()
ball= Entity(model="sphere",scale=0.5, color=color.yellow, collider="box" )
box_1=Entity(model="cube",scale=(1,2,1), position=(2,0,0), color=color.cyan, texture="white_cube", collider="box")
box_2=duplicate(box_1, x=-2)

app.run()
