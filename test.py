import tkinter as tk
import math
from time import sleep, time
frames = 0
start = time()
window = tk.Tk()
canvas = tk.Canvas(window, width=750, height=750)
canvas.pack()
def drawPlayer(x: int, y:int, dir:float) -> None:
	SIZE = 20
	canvas.create_polygon([
			(x, y), 
			(x + (SIZE * math.cos(dir + (3 * math.pi / 4))), y - (SIZE * math.sin(dir + (3 * math.pi / 4)))), 
			(x + (SIZE * (3/4) * math.cos(math.pi / 4) * math.cos(dir + math.pi)), y - (SIZE * (3/4) * math.cos(math.pi / 4) * math.sin(dir + math.pi))),
			(x + (SIZE * math.cos(dir + (5 * math.pi / 4))), y - (SIZE * math.sin(dir + (5 * math.pi / 4))))
		], fill="red")

# sleep(0.5)
theta = 0
r = 100
def f():
	global frames
	global theta
	global r
	canvas.delete("all")
	drawPlayer(250 + (r * math.cos(theta)), 250 + (r * math.sin(theta)), -1*theta - math.pi/2)
	theta += 0.005
	frames += 1
	if frames % 100 == 0:
		print("{} frames a second.".format(frames / int(time() - start)))
	canvas.after(10, f)

drawPlayer(200, 200, 3.14 / 4)
# canvas.create_polygon([(100, 100), (100 - 15, 100 - 15), (100 - 15, 100 + 15)], fill="red")
label = tk.Label(text="test")
label.pack()
canvas.after(0, f)
window.mainloop()


