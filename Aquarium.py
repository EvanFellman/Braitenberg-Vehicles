import tkinter as tk
import math
from random import *
from datetime import datetime
window = tk.Tk()
window.attributes('-fullscreen', True)
label = tk.Label(window, text="AntFarm by Evan Fellman", font=("Helvetica", 30))
label.pack()
WIDTH = window.winfo_screenwidth()
HEIGHT = window.winfo_screenheight() - label.winfo_reqheight()
canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT)
canvas.pack()
NEXT_PLAYER_ID = 0
players = []
foods = []
playerDensity = [[0] * (1 + int(HEIGHT // 20))] * (1 + int(WIDTH // 20))
foodDensity = [[0] * (1 + int(HEIGHT // 20))] * (1 + int(WIDTH // 20))
highlightPlayers = []

#reduce<T, E>: (arr: T[], f: (E, T) => E, initValue: E): E
def reduce(arr, f, initValue):
	if len(arr) == 0:
		return initValue
	else:
		return reduce(arr[1:], f, f(initValue, arr[0]))

class DependObj:
	def __init__(self, nodeNum, dependsOn, allDependants):
		self.nodeNum = nodeNum
		self.dependsOn = dependsOn
		self.allDependants = allDependants
	def __str__(self):
		return "<NodeNum: {}, dependsOn: {}, allDependants: {}>".format(self.nodeNum, [a.start for a in self.dependsOn], self.allDependants)
	def __repr__(self):
		return self.__str__()

def largest(arr):
	if len(arr) == 0:
		return -1 * math.inf
	else:
		return max(arr)

class NeuralNetwork:
	def __init__(self, inputSize, outputSize):
		self.edges = []
		self.inputs = list(range(inputSize))
		self.outputs = list(range(inputSize, inputSize + outputSize))
		self.depend = [DependObj(i, [], {}) for i in (self.inputs + self.outputs) ]
		self.lastCalc = None
		for inputNode in self.inputs:
			for outputNode in self.outputs:
				e = Edge(inputNode, outputNode)
				self.edges.append(e)
				self.depend[outputNode].dependsOn.append(e)
				self.depend[outputNode].allDependants[inputNode] = True
		#This is makes it go super speedy
		self.depend.sort(key=lambda x: len(x.allDependants))
		self.highestNode = inputSize + outputSize - 1

	#NeuralNetwork.computeOutput(inputVector: number[]): number[]
	def computeOutput(self, inputVector):
		nodeValues = {}
		for i in range(len(inputVector)):
			nodeValues[i] = inputVector[i]
		for dependObj in self.depend:
			if dependObj.nodeNum in self.inputs:
				continue
			acc = 0
			for e in dependObj.dependsOn:
				acc += nodeValues[e.start] * e.weight
			nodeValues[dependObj.nodeNum] = acc
		self.lastCalc = nodeValues
		return [nodeValues[i] for i in self.outputs]

	def addNode(self):
		self.highestNode += 1
		edgeIndex = int(math.floor(len(self.edges) * random()))
		edge = self.edges.pop(choice(range(len(self.edges))))
		newE1 = Edge(edge.start, self.highestNode, edge.weight)
		newE2 = Edge(self.highestNode, edge.end, 1)
		self.edges.append(newE1)
		self.edges.append(newE2)
		for dependObj in self.depend:
			if dependObj.nodeNum == edge.end:
				dependObj.dependsOn = [newE2] + [u for u in dependObj.dependsOn if u.start != edge.start]
				dependObj.allDependants[self.highestNode] = True
			elif edge.end in dependObj.allDependants:
				dependObj.allDependants[self.highestNode] = True
		for dependObj in self.depend:
			if dependObj.nodeNum == newE1.start:
				allD = dependObj.allDependants.copy()
				allD[newE1.start] = True
				self.depend.append(DependObj(newE1.end, [newE1], allD))
		self.depend.sort(key=lambda x: len(x.allDependants.keys()))

	def addEdge(self):
		allPairs = []
		for i in range(self.highestNode + 1):
			for j in range(i, self.highestNode + 1):
				if i != j:
					allPairs.append((i, j))
		allPairsAcc = []
		for i in range(len(allPairs)):
			a, b = allPairs[i]
			remove = False
			if a in self.outputs or b in self.inputs:
				remove = True
			if not remove:
				for dependObj in self.depend:
					if dependObj.nodeNum == a and b in dependObj.allDependants:
						remove = True
						break
			if not remove:
				for e in self.edges:
					if a == e.start and b == e.end:
						remove = True
						break
			if not remove:
				allPairsAcc.append((a, b))
		if len(allPairsAcc) == 0:
			self.mutateEdge()
		else:
			start, end = choice(allPairsAcc)
			e = Edge(start, end)
			e.weight = 0
			self.edges.append(e)
			startAllDependants = []
			for dependObj in self.depend:
				if dependObj.nodeNum == start:
					startAllDependants = dependObj.allDependants
					break
			for dependObj in self.depend:
				if dependObj.nodeNum == e.end:
					for toAdd in startAllDependants:
						dependObj.allDependants[toAdd] = True
					dependObj.allDependants[start] = True
					dependObj.dependsOn.append(e)
				elif e.end in dependObj.allDependants:
					for toAdd in startAllDependants:
						dependObj.allDependants[toAdd] = True
					dependObj.allDependants[start] = True
			self.depend.sort(key=lambda x: len(x.allDependants))

	def mutateEdge(self):
		edgeIndex = int(math.floor(len(self.edges) * random()))
		ALPHA = 0.125
		d = choice(self.depend)
		while len(d.dependsOn) == 0:
			d = choice(self.depend)
		choice(d.dependsOn).weight += ((2 * random()) - 1) * ALPHA

	def copy(self):
		out = NeuralNetwork(len(self.inputs), len(self.outputs))
		out.edges = [i.copy() for i in self.edges]
		out.highestNode = self.highestNode
		out.inputs = self.inputs
		out.outputs = self.outputs
		out.depend = [DependObj(a.nodeNum, [i.copy() for i in a.dependsOn], a.allDependants.copy()) for a in self.depend]
		out.depend.sort(key=lambda x: len(x.allDependants))
		return out

	def mutate(self):
		rnJesus = random()
		if rnJesus < 0.10:
			self.addNode()
		elif rnJesus < 0.30:
			self.addEdge()
		else:
			self.mutateEdge()

class Edge:
	def __init__(self, start, end, weight=None):
		self.start = start
		self.end = end
		self.weight = weight
		if weight == None:
			self.weight = (random() * 2) - 1

	#Edge.copy(void): Edge
	def copy(self):
		return Edge(self.start, self.end, self.weight)

	def __str__(self):
		return "<{} to {} with weight {}>".format(self.start, self.end, self.weight)

	def __repr__(self):
		return str(self)

class Player:
	def __init__(self, parent=None):
		global NEXT_PLAYER_ID
		global playerDensity
		global WIDTH
		global HEIGHT
		self.id = NEXT_PLAYER_ID
		NEXT_PLAYER_ID += 1
		if parent == None:
			self.parentId = None
			self.foodForChildren = round(10 + (random() * 10))
			self.food = 40
			self.brain = NeuralNetwork(7, 2)
			self.foodToBirth = round(100 + (random() * 10))
			self.color = (math.floor(random() * 256),math.floor(random() * 256),math.floor(random() * 256))
			self.x = random() * WIDTH
			self.y = random() * HEIGHT
			self.dir = random() * math.pi * 2
		else:
			self.parentId = parent.id
			self.foodForChildren = round(parent.foodForChildren + (random() * 4) - 2)
			self.food = 2.5 * parent.foodForChildren
			copy = parent.brain.copy()
			copy.mutate()
			self.brain = copy
			self.foodToBirth = max(41, round(parent.foodToBirth + (random() * 4) - 2))
			self.color = tuple(map(lambda x: min(255, max(0, round(x + (random() * 20) - 10))), parent.color))
			self.x = min(WIDTH - 1, max(0, parent.x + (random() * 100) - 50))
			self.y = min(HEIGHT - 1, max(0, parent.y + (random() * 100) - 50))
			self.dir = parent.dir
		playerDensity[int(self.x // 20)][int(self.y // 20)] += 1
	def eat(self):
		self.food += 15
		if self.food >= self.foodToBirth:
			self.food -= 20
			child = Player(parent=self)
			global players
			players.append(child)
	def die(self):
		global players
		global playerDensity
		global highlightPlayers
		toRemove = None
		for index in range(len(players)):
			if players[index].id == self.id:
				toRemove = index
		if toRemove == len(players) - 1:
			players = players[:toRemove]
		else:
			players = players[:toRemove] + players[toRemove+1:]
		if self.id in highlightPlayers:
			remIndex = 0
			for idx in range(len(highlightPlayers)):
				if highlightPlayers[idx] == self.id:
					remIndex = idx
					break
			if remIndex == len(highlightPlayers) - 1:
				highlightPlayers = highlightPlayers[:-1]
			else:
				highlightPlayers = highlightPlayers[:remIndex] + highlightPlayers[remIndex + 1:]
		playerDensity[int(self.x // 20)][int(self.y // 20)] -= 1

	def tick(self):
		global foods
		global playerDensity
		global foodDensity
		global HEIGHT
		global WIDTH
		nearestFood = (math.inf, math.inf)
		nFindex = None
		for i in range(len(foods)):
			food = foods[i]
			if ((food[0] - self.x) ** 2) + ((food[1] - self.y) ** 2) < ((nearestFood[0] - self.x) ** 2) + ((nearestFood[1] - self.y) ** 2):
				nearestFood = food
				nFindex = i
		foodDensityInput = 0
		playerDensityInput = 0
		for i in range(max(int(self.x//20) - 3, 0), 1 + min(int(self.x//20) + 3, int((WIDTH - 1)//20))):
			for j in range(max(int(self.y//20) - 3, 0), 1 + min(int(self.y//20) + 3, int((HEIGHT - 1)//20))):
				foodDensityInput += foodDensity[i][j]
				playerDensityInput += playerDensity[i][j]
		speedAndDirection = self.brain.computeOutput([((nearestFood[0] - self.x) ** 2) + ((nearestFood[1] - self.y) ** 2), 100 * math.atan2(nearestFood[1] - self.y, nearestFood[0] - self.x), self.x, self.y, 100 * self.dir, 10 * foodDensityInput, 10 * playerDensityInput])
		speed = max(0, min(math.log(max(0, speedAndDirection[0] / 20)+1), 10))
		self.dir += max(0, min(speedAndDirection[1] / 100, math.pi / 16))
		playerDensity[int(self.x // 20)][int(self.y // 20)] -= 1
		self.x += math.cos(self.dir) * speed
		self.y -= math.sin(self.dir) * speed
		self.x = max(0, min(WIDTH, self.x))
		self.y = max(0, min(HEIGHT, self.y))
		playerDensity[int(self.x // 20)][int(self.y // 20)] += 1
		self.speed = speed
		self.food -= 0.005 + (speed / 1500) + (len(players) / 3000)
		if self.food <= 0:
			self.die()
		if ((nearestFood[0] - self.x) ** 2) + ((nearestFood[1] - self.y) ** 2) < 400:
			if nFindex == len(foods) - 1:
				foods = foods[:nFindex]
			else:
				foods = foods[:nFindex] + foods[nFindex+1:]
			self.eat()
		self.draw()


	def draw(self):
		global highlightPlayers
		if self.id in highlightPlayers:
			SIZE = 30
			highlightColor = (0, 0, 0)
			canvas.create_polygon([
				(self.x + (5 * math.cos(self.dir)), self.y - (5 * math.sin(self.dir))), 
				(self.x + (SIZE * math.cos(self.dir + (3 * math.pi / 4))), self.y - (SIZE * math.sin(self.dir + (3 * math.pi / 4)))), 
				(self.x + (SIZE * (3/4) * math.cos(math.pi / 4) * math.cos(self.dir + math.pi)), self.y - (SIZE * (3/4) * math.cos(math.pi / 4) * math.sin(self.dir + math.pi))),
				(self.x + (SIZE * math.cos(self.dir + (5 * math.pi / 4))), self.y - (SIZE * math.sin(self.dir + (5 * math.pi / 4))))
			], fill="#%02x%02x%02x" % highlightColor)
		SIZE = 20
		canvas.create_polygon([
				(self.x, self.y), 
				(self.x + (SIZE * math.cos(self.dir + (3 * math.pi / 4))), self.y - (SIZE * math.sin(self.dir + (3 * math.pi / 4)))), 
				(self.x + (SIZE * (3/4) * math.cos(math.pi / 4) * math.cos(self.dir + math.pi)), self.y - (SIZE * (3/4) * math.cos(math.pi / 4) * math.sin(self.dir + math.pi))),
				(self.x + (SIZE * math.cos(self.dir + (5 * math.pi / 4))), self.y - (SIZE * math.sin(self.dir + (5 * math.pi / 4))))
			], fill="#%02x%02x%02x" % self.color)

allInfoFrames = []

def onclick(event):
	global highlightPlayers
	global players
	global window
	global allInfoFrames
	mouseX = event.x
	mouseY = event.y
	closest = (math.inf, None)
	for p in players:
		if (p.x - mouseX) ** 2 + (p.y - mouseY) ** 2 < closest[0]:
			closest = (p.x - mouseX) ** 2 + (p.y - mouseY) ** 2, p
	closest = closest[1]
	if closest == None:
		#There are no players on screen :(
		return
	elif closest.id in highlightPlayers:
		remIndex = 0
		for idx in range(len(highlightPlayers)):
			if highlightPlayers[idx] == closest.id:
				remIndex = idx
				break
		if len(highlightPlayers) - 1 == remIndex:
			highlightPlayers = highlightPlayers[:-1]
		else:
			highlightPlayers = highlightPlayers[:remIndex] + highlightPlayers[remIndex + 1:]
		for idx in range(len(allInfoFrames)):
			if allInfoFrames[idx][1].id == closest.id:
				allInfoFrames[idx][0].destroy()
				remIndex = idx
				break
		if len(allInfoFrames) - 1 == remIndex:
			allInfoFrames = allInfoFrames[:-1]
		else:
			allInfoFrames = allInfoFrames[:remIndex] + allInfoFrames[remIndex + 1:]
	else:
		highlightPlayers.append(closest.id)
		frame = tk.Toplevel(window)
		frame.geometry("200x300")
		picOfDude = tk.Canvas(frame, width=200, height=125)
		picOfDude.grid(row=0, columnspan=2, rowspan=3)
		SIZE = 75
		frame.resizable(0,0)
		picOfDude.create_rectangle(0, 0, 200, 125, fill="#%02x%02x%02x" % (255, 255, 255))
		picOfDude.create_polygon([
					(125, 60), 
					(125 + (SIZE * math.cos(3 * math.pi / 4)), 60 - (SIZE * math.sin(3 * math.pi / 4))), 
					(125 + (SIZE * (3/4) * math.cos(math.pi / 4) * math.cos(math.pi)), 60 - (SIZE * (3/4) * math.cos(math.pi / 4) * math.sin(math.pi))),
					(125 + (SIZE * math.cos(5 * math.pi / 4)), 60 - (SIZE * math.sin(5 * math.pi / 4)))
				], fill="#%02x%02x%02x" % closest.color)
		neuralNetPic = tk.Canvas(frame, width=200, height=125)
		neuralNetPic.grid(row=3, columnspan=2, rowspan=3)
		neuralNetPic.create_rectangle(0, 0, 200, 200, fill="#%02x%02x%02x" % (255, 255, 255))
		numNeurons = len(closest.brain.depend)
		dx = int(200 / (numNeurons - (len(closest.brain.inputs) - 2)))
		dy = 20
		neurons = {}
		for i in closest.brain.inputs:
			print(int(i * 200 / len(closest.brain.inputs)))
			neurons[i] = (dx, int((i + 0.5) * 150 / (len(closest.brain.inputs) + 2)), [])

		lastX = -1 * math.inf
		counter = 2
		for dependObj in closest.brain.depend:
			if dependObj.nodeNum in closest.brain.inputs:
				continue
			else:
				neurons[dependObj.nodeNum] = (counter * dx, 10 + ((counter * dy) % 105), dependObj.dependsOn)
				lastX = counter * dx
				counter += 1
		for out in closest.brain.outputs:
			neurons[out] = (lastX, neurons[out][1], neurons[out][2])
		for nodeNum, data in neurons.items():
			for d in data[2]:
				green = int(max(-255, min(255, 255 / (4 * d.weight))))
				red = 0
				if green < 0:
					red = green * -1
					green = 0
				neuralNetPic.create_line(data[0] + 5, data[1] + 5, neurons[d.start][0] + 5, neurons[d.start][1] + 5, fill="#%02x%02x%02x" % (red, green, 0))
		for nodeNum, data in neurons.items():
			neuralNetPic.create_rectangle(data[0]- 1, data[1] - 1, data[0] + 10, data[1] + 10, fill="black")
			box = tk.Canvas(frame, width=10, height=10, highlightthickness=0)
			box.create_rectangle(0, 0, 10, 10, fill="black")
			box.place(x=data[0], y=data[1]+129)
			neurons[nodeNum] = box
		idLabel = tk.Label(frame, text="ID: {}".format(closest.id))
		idLabel.grid(row=6, column=0)
		foodLabel = tk.Label(frame, text="Food: {}".format(int(closest.food)))
		foodLabel.grid(row=6, column=1)
		speedLabel = tk.Label(frame, text="Speed: {}".format(int(closest.speed)))
		speedLabel.grid(row=7, column=0)
		directionLabel = tk.Label(frame, text="Direction: {}".format(int(closest.dir * 180 / math.pi)))
		directionLabel.grid(row=7, column=1)
		frame.attributes('-topmost', 'true')
		def on_closing_info():
			global highlightPlayers
			if closest.id in highlightPlayers:
				remIndex = 0
				for idx in range(len(highlightPlayers)):
					if highlightPlayers[idx] == closest.id:
						remIndex = idx
						break
				if len(highlightPlayers) - 1 == remIndex:
					highlightPlayers = highlightPlayers[:-1]
				else:
					highlightPlayers = highlightPlayers[:remIndex] + highlightPlayers[remIndex + 1:]
			frame.destroy()
		frame.protocol("WM_DELETE_WINDOW", on_closing_info)
		def sigmoid(x):
			if x > 100:
				return 1
			elif x < -100:
				return 0
			else:
				return 1 / (1 + math.exp(-1 *x))
		sums = {}
		for i in neurons.keys():
			sums[i] = 0
		sums[-1] = 0
		def newFrameThread():
			foodLabel["text"] = "Food: {}".format(int(closest.food))
			if closest.food <= 20:
				foodLabel["fg"] = '#%02x%02x%02x' % (255 - int(255 * closest.food / 20), 0, 0)
			speedLabel["text"] = "Speed: {}".format(int(closest.speed))
			directionLabel["text"] = "Direction: {}".format(int((closest.dir * 180 / math.pi) % 360))
			lastCalc = closest.brain.lastCalc
			for nodeNum, value in lastCalc.items():
				sums[nodeNum] += value
			sums[-1] += 1
			for nodeNum, box in neurons.items():
				box.delete("all")
				color = 255 - int(255 * sigmoid((lastCalc[nodeNum] - (sums[nodeNum] / sums[-1])) / 100))
				box.create_rectangle(0, 0, 9, 9, fill='#%02x%02x%02x' % (color, color, color))
			if closest.food <= 0:
				frame.destroy()
			frame.after(10, newFrameThread)
		allInfoFrames.append((frame, closest))
		frame.after(0, newFrameThread)
for i in range(50):
	foods.append((random() * WIDTH, random() * HEIGHT))
for i in range(100):
	players.append(Player())
frameCount = 0
start = datetime.now()
veryStart = datetime.now()
foodMin = 22
def handleOneFrame():
	global frameCount
	global start
	global foodMin
	if frameCount == 100:
		foodMin = max(1, min(22, (60/50) * frameCount / (datetime.now() - start).seconds))
		start = datetime.now()
		frameCount = 0
	else:
		frameCount += 1
	canvas.delete("all")
	for p in players:
		p.tick()
	while len(foods) < foodMin:
		x = random() * WIDTH
		y = random() * HEIGHT
		foods.append((x, y))
		foodDensity[int(x // 20)][int(y // 20)] += 1
	if random() < 0.25:
		x = random() * WIDTH
		y = random() * HEIGHT
		foods.append((x, y))
		foodDensity[int(x // 20)][int(y // 20)] += 1
	for food in foods:
		canvas.create_rectangle(food[0] - 5, food[1] - 5, food[0] + 5, food[1] + 5, fill="yellow")
	if len(players) == 0:
		label['text'] = "Aquarium by Evan Fellman\t\t\tEveryone died. This ran from {} to {}".format(veryStart, datetime.now())
		label['font'] = ("Helvetica", 15)
	else:
		label['text'] = "Aquarium by Evan Fellman\tStarted at {}/{} {}:{}\t\tplayers alive: {}".format(veryStart.day, veryStart.month, veryStart.hour, veryStart.minute, len(players))
		canvas.after(15, handleOneFrame)
canvas.after(0, handleOneFrame)
canvas.bind("<Button-1>", onclick)
window.mainloop()


