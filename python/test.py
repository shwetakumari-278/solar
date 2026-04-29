from ursina import*
app= Ursina()
box=Entity(model="cube", color=color.yellow, position=(1,0,0),scale=(1,2,2), rotation=(0,0,0),texture="horizontal_gradient")
txt=Text(text="click here", color=color.red)




app.run()