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
			self.brain = NeuralNetwork(6, 2)
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
		self.food += 10
		if self.food >= self.foodToBirth:
			self.food -= 20 + self.foodForChildren
			child = Player(parent=self)
			global players
			players.append(child)
	def die(self):
		global players
		global playerDensity
		toRemove = None
		for index in range(len(players)):
			if players[index].id == self.id:
				toRemove = index
		if index == len(players) - 1:
			players = players[:index]
		else:
			players = players[:index] + players[index+1:]
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
		speedAndDirection = self.brain.computeOutput([((nearestFood[0] - self.x) ** 2) + ((nearestFood[1] - self.y) ** 2), 100 * math.atan2(nearestFood[1] - self.y, nearestFood[0] - self.x), self.x, self.y, 10 * foodDensityInput, 10 * playerDensityInput])
		speed = max(0, min(math.log(max(0, speedAndDirection[0] / 20)+1), 10))
		self.dir += max(0, min(speedAndDirection[1] / 100, math.pi / 16))
		playerDensity[int(self.x // 20)][int(self.y // 20)] -= 1
		self.x += math.cos(self.dir) * speed
		self.y -= math.sin(self.dir) * speed
		self.x = max(0, min(WIDTH, self.x))
		self.y = max(0, min(HEIGHT, self.y))
		playerDensity[int(self.x // 20)][int(self.y // 20)] += 1
		self.food -= 0.001 + (speed / 1500)
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
		SIZE = 20
		canvas.create_polygon([
				(self.x, self.y), 
				(self.x + (SIZE * math.cos(self.dir + (3 * math.pi / 4))), self.y - (SIZE * math.sin(self.dir + (3 * math.pi / 4)))), 
				(self.x + (SIZE * (3/4) * math.cos(math.pi / 4) * math.cos(self.dir + math.pi)), self.y - (SIZE * (3/4) * math.cos(math.pi / 4) * math.sin(self.dir + math.pi))),
				(self.x + (SIZE * math.cos(self.dir + (5 * math.pi / 4))), self.y - (SIZE * math.sin(self.dir + (5 * math.pi / 4))))
			], fill="#%02x%02x%02x" % self.color)
for i in range(20):
	foods.append((random() * WIDTH, random() * HEIGHT))
for i in range(50):
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
		foodMin = max(1, min(22, (30/50) * frameCount / (datetime.now() - start).seconds))
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
	if random() < 0.125:
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
		label['text'] = "Aquarium by Evan Fellman\t\t\tplayers alive: {}".format(len(players))
		canvas.after(15, handleOneFrame)
canvas.after(0, handleOneFrame)
window.mainloop()


