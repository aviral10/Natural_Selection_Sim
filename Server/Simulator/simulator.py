# import numpy as np
# import random
# random.seed(200)
#
# from random import randint, random
# from math import tanh
# from Simulator.PARAMETERS import WORLD_SIZE
#
#
# class Node:
#     def __init__(self, x, y, isOcc=False):
#         self.x = x
#         self.y = y
#         self.isOccupied = isOcc
#
#     def dumps(self):
#         return f"{{x: {self.x}, y: {self.y}, isOcc: {self.isOccupied} }}"
#
#     def __repr__(self):
#         return f"{self.__dict__}"
#
#
# ALL_CELLS = [{'x': i, 'y': j} for i in range(WORLD_SIZE) for j in range(WORLD_SIZE)]
#
#
# class Grid:
#
#     def __init__(self, world):
#         self.world_size = world
#         self.GRID_CELLS = [[Node(i, j) for j in range(world)] for i in range(world)]
#
#     def dumps(self):
#         return [bele.dumps() for ele in self.GRID_CELLS for bele in ele]
#
#
# grid = Grid(WORLD_SIZE)
#
#
# inNames = ['Lx', 'Ly', 'Srf', 'Rnd']
# outNames = ['me', 'mw', 'mn', 'ms', 'mf', 'mrd', 'stRad']
#
#
# class Neuron:
#     def __init__(self, name="", neuron_type="i",func=None):
#         self.name = name
#         self.ntype = neuron_type
#         self.func = func
#         self.value = 0
#         self.parents = []
#         self.pointingTo = []
#
#     def think(self):
#         if self.ntype == 's':
#             self.value = self.func()
#             return self.value
#         elif self.ntype == 'i' or self.ntype == 'a':
#             nval = 0
#             for conn in self.parents:
#                 nval += conn[0].value*conn[1]
#             nval = tanh(nval)
#             self.value = nval
#             return self.value
#
#     def execute(self):
#         return self.func()
#
#     def __repr__(self):
#         return f"name: {self.name}"
#
#     def dumps(self):
#         return f"name: {self.name}, parents: {self.parents}, pointing: {self.pointingTo}"
#
#
# def isValidCell(px, py):
#     if grid.world_size > px >= 0:
#         if grid.world_size > py >= 0:
#             return True
#     return False
#
#
# def extractData(genome):
#     weight = int("00000000000000001111111111111111", 2) & genome
#     sink_id = (int("00000000011111110000000000000000", 2) & genome) >> 16
#     sink_type = (int("00000000100000000000000000000000", 2) & genome) >> 23
#     source_id = (int("01111111000000000000000000000000", 2) & genome) >> 24
#     source_type = (int("10000000000000000000000000000000", 2) & genome) >> 31
#     # print([source_type, source_id, sink_type, sink_id, weight])
#     if weight & (1 << 15):
#         weight = weight ^ int("1111111111111111", 2)
#         weight += 1
#         weight = -weight
#     return source_type, source_id, sink_type, sink_id, weight / 8192
#
#
# class Brain:
#     SENS_LIM = 4
#     ACT_LIM = 7
#
#     def __init__(self, px, py, gen=None, internalNeuronSize = 2):
#
#         self.x = px
#         self.y = py
#
#         self.sensory = [Neuron(inNames[_]) for _ in range(self.SENS_LIM)]
#         self.action = [Neuron(outNames[_]) for _ in range(self.ACT_LIM)]
#         self.brain_graph = [[], [], []]
#         self.internal_Neurons = []
#         self.genomeCol = self.randColor()
#         self.genome = self.cleanGenome(gen)
#         self.prev = (0,0)
#         self.internal_Neurons = [Neuron(str(i), "i") for i in range(internalNeuronSize)]
#         self.search_radius = 1
#
#         self.attach_functions()
#         if self.genome is not None:
#             for gene in self.genome:
#                 source_type, source_id, sink_type, sink_id, weight = extractData(gene)
#                 if source_type == 0:
#                     source_id %= self.SENS_LIM
#                 else:
#                     source_id %= internalNeuronSize
#
#                 if sink_type == 0:
#                     sink_id %= self.ACT_LIM
#                 else:
#                     sink_id %= internalNeuronSize
#
#                 # print(source_type, source_id, sink_type, sink_id, weight)
#                 # Make brain graph here
#                 if source_type == 0:
#                     left_node = self.sensory[source_id]
#                     left_node.ntype = 's'
#                     self.brain_graph[0].append(left_node)
#                     right_node = None
#                     if sink_type == 0:
#                         right_node = self.action[sink_id]
#                         right_node.ntype = 'a'
#                         self.brain_graph[2].append(right_node)
#                     else:
#                         right_node = self.internal_Neurons[sink_id]
#                         right_node.ntype = 'i'
#                         self.brain_graph[1].append(right_node)
#
#                     right_node.parents.append([left_node, weight])
#                     left_node.pointingTo.append([right_node, weight])
#                 else:
#                     left_node = self.internal_Neurons[source_id]
#                     left_node.ntype = 'i'
#                     self.brain_graph[1].append(left_node)
#                     right_node = None
#                     if sink_type == 0:
#                         right_node = self.action[sink_id]
#                         right_node.ntype = 'a'
#                         self.brain_graph[2].append(right_node)
#                     else:
#                         right_node = self.internal_Neurons[sink_id]
#                         right_node.ntype = 'i'
#                         self.brain_graph[1].append(right_node)
#
#                     right_node.parents.append([left_node, weight])
#                     left_node.pointingTo.append([right_node, weight])
#         self.clean_brain_graph()
#         # print("New Creature")
#         # print(self.brain_graph)
#
#     def clean_brain_graph(self):
#         visited = {}
#         g = [[],[],[]]
#         for neu in self.brain_graph[2]:
#             if id(neu) not in visited:
#                 visited[id(neu)] = 1
#                 g[2].append(neu)
#
#         for curr in g[2]:
#             for element in curr.parents:
#                 neu = element[0]
#                 if id(neu) not in visited:
#                     visited[id(neu)] = 1
#                     if neu.ntype == 'i':
#                         g[1].append(neu)
#                     elif neu.ntype == 's':
#                         g[0].append(neu)
#
#         for curr in g[1]:
#             for element in curr.parents:
#                 neu = element[0]
#                 if id(neu) not in visited:
#                     visited[id(neu)] = 1
#                     if neu.ntype == 'i':
#                         g[1].append(neu)
#                     elif neu.ntype == 's':
#                         g[0].append(neu)
#         eps = Neuron("none", 'a', self.epsFunc)
#         g[2].append(eps)
#         self.brain_graph = g
#
#     def cleanGenome(self, gen):
#         if gen is None:
#             return None
#         gen = list(set(gen))
#         return gen
#
#     def output_action(self, probabilities):
#         return np.random.choice(self.brain_graph[2], size=1, replace=False, p=probabilities)
#
#     def think(self):
#         for idx in range(3):
#             for neu in self.brain_graph[idx]:
#                 neu.think()
#         probs = [max(0, entity.value) for entity in self.brain_graph[2]]
#         sm = sum(probs)
#         if sm == 0: sm = 1
#         norm = [float(i)/sm for i in probs]
#         sm = sum(norm)
#         if sum(norm) == 0:
#             norm[-1] = 1-sm
#         ret = self.output_action(norm)
#         # print(ret)
#         ret[0].execute()
#
#     def attach_functions(self):
#         for i in range(len(inNames)):
#             ele = self.sensory[i]
#             if inNames[i] == 'Lx':
#                 ele.func = self.lx
#                 ele.name = 'Lx'
#             elif inNames[i] == 'Ly':
#                 ele.func = self.ly
#                 ele.name = 'Ly'
#             elif inNames[i] == 'Srf':
#                 ele.func = self.searchForw
#                 ele.name = 'Srf'
#             elif inNames[i] == 'Rnd':
#                 ele.func = self.rand
#                 ele.name = 'Rnd'
#         for i in range(len(outNames)):
#             ele = self.action[i]
#             if outNames[i] == 'me':
#                 ele.func = self.me
#                 ele.name = 'me'
#             elif outNames[i] == 'mw':
#                 ele.func = self.mw
#                 ele.name = 'mw'
#             elif outNames[i] == 'mn':
#                 ele.func = self.mn
#                 ele.name = 'mn'
#             elif outNames[i] == 'ms':
#                 ele.func = self.ms
#                 ele.name = 'ms'
#             elif outNames[i] == 'mf':
#                 ele.func = self.mf
#                 ele.name = 'mf'
#             elif outNames[i] == 'mrd':
#                 ele.func = self.mrd
#                 ele.name = 'mrd'
#             elif outNames[i] == 'stRad':
#                 ele.func = self.setRadius
#                 ele.name = 'stRad'
#
#     def isValid(self, dx, dy):
#         px = self.x + dx
#         py = self.y + dy
#         if grid.world_size > px >= 0:
#             if grid.world_size > py >= 0:
#                 return True
#         return False
#
#     def epsFunc(self):
#         return self.move(0,0)
#
#     def move(self, dx, dy):
#         if self.isValid(dx, dy) and not grid.GRID_CELLS[self.x + dx][self.y + dy].isOccupied:
#             grid.GRID_CELLS[self.x][self.y].isOccupied = False
#             self.x += dx
#             self.y += dy
#             grid.GRID_CELLS[self.x][self.y].isOccupied = True
#             self.prev = (dx, dy)
#             return True
#         self.prev = (0, 0)
#         return False
#
#     def lx(self):
#         return self.x/WORLD_SIZE
#
#     def ly(self):
#         return self.y/WORLD_SIZE
#
#     def density_east(self):
#         length = 3
#         cx = self.x
#         cy = self.y
#         total_cells_covered = 0
#         cells_occupied = 0
#         for i in range(self.search_radius):
#             cx -= 1
#             cy += 1
#             for j in range(length):
#
#                 if isValidCell(cx, cy):
#                     if grid.GRID_CELLS[cx][cy].isOccupied:
#                         cells_occupied += 1
#                 total_cells_covered += 1
#                 cx += 1
#             cx -= length
#             length += 2
#         return cells_occupied/total_cells_covered
#
#     def density_west(self):
#         length = 3
#         cx = self.x
#         cy = self.y
#         total_cells_covered = 0
#         cells_occupied = 0
#         for i in range(self.search_radius):
#             cx -= 1
#             cy -= 1
#             for j in range(length):
#
#                 if isValidCell(cx, cy):
#                     if grid.GRID_CELLS[cx][cy].isOccupied:
#                         cells_occupied += 1
#                 total_cells_covered += 1
#                 cx += 1
#             cx -= length
#             length += 2
#         return cells_occupied/total_cells_covered
#
#     def density_north(self):
#         length = 3
#         cx = self.x
#         cy = self.y
#         total_cells_covered = 0
#         cells_occupied = 0
#         for i in range(self.search_radius):
#             cx -= 1
#             cy -= 1
#             for j in range(length):
#
#                 if isValidCell(cx, cy):
#                     if grid.GRID_CELLS[cx][cy].isOccupied:
#                         cells_occupied += 1
#                 total_cells_covered += 1
#                 cy += 1
#             cy -= length
#             length += 2
#         return cells_occupied / total_cells_covered
#
#     def density_south(self):
#         length = 3
#         cx = self.x
#         cy = self.y
#         total_cells_covered = 0
#         cells_occupied = 0
#         for i in range(self.search_radius):
#             cx += 1
#             cy -= 1
#             for j in range(length):
#
#                 if isValidCell(cx, cy):
#                     if grid.GRID_CELLS[cx][cy].isOccupied:
#                         cells_occupied += 1
#                 total_cells_covered += 1
#                 cy += 1
#             cy -= length
#             length += 2
#         return cells_occupied / total_cells_covered
#
#     def searchForw(self):
#         if self.prev == (0,0):
#             return self.density_east()
#         if self.prev == (0,1):
#             return self.density_east()
#         if self.prev == (1,0):
#             return self.density_south()
#         if self.prev == (0,-1):
#             return self.density_west()
#         if self.prev == (-1,0):
#             return self.density_north()
#
#     def searchAll(self):
#         arr = [self.density_north(), self.density_east(), self.density_south(), self.density_west()]
#
#     def rand(self):
#         return random()
#
#     def randColor(self):
#         return f"#{hex(randint(0,255))[2:]}{hex(randint(0,255))[2:]}{hex(randint(0,255))[2:]}"
#
#     def me(self):
#         return self.move(0, 1)
#
#     def mw(self):
#         return self.move(0, -1)
#
#     def mn(self):
#         return self.move(-1, 0)
#
#     def ms(self):
#         return self.move(1, 0)
#
#     def mf(self):
#         self.move(*self.prev)
#
#     def mrd(self):
#         arr = [randint(-1,1),0]
#         if arr[0] == 0:
#             arr[1] = randint(-1,1)
#         return self.move(arr[0],arr[1])
#
#     def setRadius(self):
#         self.search_radius += 2
#         self.search_radius = max(1, self.search_radius%10)
#         return 1
#
#
# class Creature(Brain):
#
#     def __init__(self, px, py, gen=None, world=128):
#         Brain.__init__(self, px, py, gen)
#         self.world_size = world
#         self.boundary = world
#
#     def dumps(self):
#         ret = {
#             'x': self.x,
#             'y': self.y,
#             'g': self.genomeCol
#         }
#         return ret
#
#
# def generate_population(sz):
#     choices = np.random.choice(ALL_CELLS, size=sz, replace=False)
#     arr = [Creature(ele['x'], ele['y'], [randint(1, int("ffffffff",16)) for _ in range(4)]) for ele in choices]
#     for ele in arr:
#         grid.GRID_CELLS[ele.x][ele.y].isOccupied = True
#     return arr
#
#
# creatures = generate_population(100)
#
# for elem in creatures:
#     print(elem.brain_graph)
#     print("Before: ", elem.x, elem.y)
#     elem.think()
#     print("After : ", elem.x, elem.y)
#     elem.think()
#     print("After2: ", elem.x, elem.y)
#     print()