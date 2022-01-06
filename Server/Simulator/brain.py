import numpy as np
import random
import pickle
import time
from math import tanh
from Simulator.grid import *

grid = Grid(WORLD_SIZE)

# implement: popGradient
inNames = ['Lx', 'Ly', 'Srf', 'Rnd']
outNames = ['me', 'mw', 'mn', 'ms', 'mf', 'mrd', 'stRad']


class Neuron:
    def __init__(self, name="", neuron_type="i",func=None):
        self.name = name
        self.ntype = neuron_type
        self.func = func
        self.value = 0
        self.parents = []
        self.pointingTo = []
        self.parentweights = None
        self.isDeactivated = False

    def think(self):
        if self.isDeactivated: return 0
        if self.ntype == 's':
            self.value = self.func()
            return self.value
        else:
            nval = 0
            for conn in self.parents:
                nval += conn[0].value*conn[1]
            nval = tanh(nval)
            self.value = nval
            return self.value

    def thinks(self):
        if self.isDeactivated: return 0
        if self.ntype == 's':
            self.value = self.func()
            return self.value
        else:
            ca = np.array([conn[0].value for conn in self.parents], dtype=np.float)
            # cb = self.parentweights
            cc = np.array([conn[1] for conn in self.parents], dtype=np.float)
            # print("none", cb, cc)
            nval = np.dot(ca,cc)
            nval = tanh(nval)
            self.value = nval
            return self.value

    def execute(self):
        return self.func()

    def __repr__(self):
        return f"name: {self.name}, VALUE: {self.value}"

    def dumps(self):
        return f"name: {self.name}, parents: {self.parents}, pointing: {self.pointingTo}"


def isValidCell(px, py):
    if grid.world_size > px >= 0:
        if grid.world_size > py >= 0:
            if grid.GRID_CELLS[px][py].isOccupied == False:
                return True
    return False


def extractData(genome):
    weight = int("00000000000000001111111111111111", 2) & genome
    sink_id = (int("00000000011111110000000000000000", 2) & genome) >> 16
    sink_type = (int("00000000100000000000000000000000", 2) & genome) >> 23
    source_id = (int("01111111000000000000000000000000", 2) & genome) >> 24
    source_type = (int("10000000000000000000000000000000", 2) & genome) >> 31
    # print([source_type, source_id, sink_type, sink_id, weight])
    if weight & (1 << 15):
        weight = weight ^ int("1111111111111111", 2)
        weight += 1
        weight = -weight
    return source_type, source_id, sink_type, sink_id, weight / 8192


def binSearch(arr, key):
    low = 0
    high = len(arr) - 1
    ans = -1
    while low < high:
        mid = (low + high) // 2
        if arr[mid] <= key:
            ans = mid
            low = mid + 1
        else:
            high = mid - 1
    return ans

def prob2bool(factor):
    # assert(factor >= 0.0 && factor <= 1.0);
    return random.random() < factor

class Brain:
    SENS_LIM = len(inNames)
    ACT_LIM = len(outNames)

    def __init__(self, px, py, gen=None, internalNeuronSize = INTERNAL_NEURONS):

        self.x = px
        self.y = py

        self.sensory = [Neuron(inNames[_]) for _ in range(self.SENS_LIM)]

        self.action = [Neuron(outNames[_]) for _ in range(self.ACT_LIM)]
        self.brain_graph = [[], [], []]
        self.internal_Neurons = []
        # self.genomeCol = self.randColor()
        self.genome = self.cleanGenome(gen)
        self.genomeCol = self.genomeColor()

        self.genome_copied = 0
        self.prev = (0,0)
        self.internal_Neurons = [Neuron(str(i), "i") for i in range(internalNeuronSize)]
        self.search_radius = 1

        self.attach_functions()
        if self.genome is not None:
            self.brain_graph = [[], [], []]
            for gene in self.genome:
                source_type, source_id, sink_type, sink_id, weight = extractData(gene)
                if source_type == 0:
                    source_id %= self.SENS_LIM
                else:
                    source_id %= internalNeuronSize

                if sink_type == 0:
                    sink_id %= self.ACT_LIM
                else:
                    sink_id %= internalNeuronSize

                # print(source_type, source_id, sink_type, sink_id, weight)
                # Make brain graph here
                if source_type == 0:
                    left_node = self.sensory[source_id]
                    left_node.ntype = 's'
                    self.brain_graph[0].append(left_node)
                    right_node = None
                    if sink_type == 0:
                        right_node = self.action[sink_id]
                        right_node.ntype = 'a'
                        self.brain_graph[2].append(right_node)
                    else:
                        right_node = self.internal_Neurons[sink_id]
                        right_node.ntype = 'i'
                        self.brain_graph[1].append(right_node)

                    right_node.parents.append([left_node, weight])
                    left_node.pointingTo.append([right_node, weight])
                else:
                    left_node = self.internal_Neurons[source_id]
                    left_node.ntype = 'i'
                    self.brain_graph[1].append(left_node)
                    right_node = None
                    if sink_type == 0:
                        right_node = self.action[sink_id]
                        right_node.ntype = 'a'
                        self.brain_graph[2].append(right_node)
                    else:
                        right_node = self.internal_Neurons[sink_id]
                        right_node.ntype = 'i'
                        self.brain_graph[1].append(right_node)

                    right_node.parents.append([left_node, weight])
                    left_node.pointingTo.append([right_node, weight])
        self.clean_brain_graph()
        # print("New Creature")
        # print(self.brain_graph)

    def genomeColorS(self):
        tup = [[*extractData(ele)] for ele in self.genome]
        for ele in tup:
            ele[-1] = int(ele[-1])
        tup = tuple(tuple(ele) for ele in tup)
        val = hash(tup) % int("ffffff", 16)
        # print(self.genomeColorS())
        return "#"+hex(val)[2:]

    def genomeColor(self):
        tup = [[*extractData(ele)] for ele in self.genome]
        for idx,ele in enumerate(tup):
            ele[-1] = ele[-1]*8192
            ele[1] %= self.SENS_LIM
            ele[3] %= self.ACT_LIM
            tup[idx] = int(str(ele[0]) + f"{ele[1]:07b}" + str(ele[2]) + f"{ele[2]:07b}" + f"{ele[3]:016b}", 16)
        tup = tuple(tup)
        val = hash(tup) % int("ffffff", 16)
        return "#" + hex(val)[2:]


    def clean_brain_graph(self):
        visited = {}
        g = [[],[],[]]
        for neu in self.brain_graph[2]:
            if id(neu) not in visited:
                visited[id(neu)] = 1
                g[2].append(neu)

        for curr in g[2]:
            par = []
            for element in curr.parents:
                neu = element[0]
                if id(neu) not in visited:
                    visited[id(neu)] = 1
                    if neu.ntype == 'i':
                        g[1].append(neu)
                    elif neu.ntype == 's':
                        g[0].append(neu)
                    par.append(element[1])
            # curr.parentweights = np.array(par, dtype=np.float)

        for curr in g[1]:
            par = []
            for element in curr.parents:
                neu = element[0]
                if id(neu) not in visited:
                    visited[id(neu)] = 1
                    if neu.ntype == 'i':
                        g[1].append(neu)
                    elif neu.ntype == 's':
                        g[0].append(neu)
                    par.append(element[1])

            # curr.parentweights = np.array(par, dtype=np.float)

        eps = Neuron("none", 'a', self.epsFunc)
        g[2].append(eps)
        self.brain_graph = g

    def cleanGenome(self, gen):
        if gen is None:
            return None
        gen = list(sorted(set(gen)))
        return gen

    # def output_action(self, probabilities):
    #     return


    def thinks(self):
        for idx in range(3):
            for neu in self.brain_graph[idx]:
                neu.think()
        probs = [max(0, entity.value) for entity in self.brain_graph[2]]
        chc = random.choices(self.brain_graph[2], weights=probs, k=1)
        chc[0].execute()

    def think(self):
        for idx in range(3):
            for neu in self.brain_graph[idx]:
                neu.think()

        if random.randint(0,1) == 1:
            entities = [entity for entity in self.brain_graph[2] if entity.name[0] != 'm']
            if len(entities) != 0:
                probs = [max(0, entity.value) for entity in entities]
                chc = random.choices(entities, weights=probs, k=1)
                chc[0].execute()
                return None
        #
        px, py = 0,0
        for ele in self.brain_graph[2]:
            if ele.name == 'me':
                py += ele.value
            elif ele.name == 'mw':
                py -= ele.value
            elif ele.name == 'mn':
                px -= ele.value
            elif ele.name == 'ms':
                px += ele.value
            elif ele.name == 'mf':
                px += self.prev[0]*ele.value
                py += self.prev[1]*ele.value
            elif ele.name == 'mr':
                px -= self.prev[0] * ele.value
                py -= self.prev[1] * ele.value
            elif ele.name == 'mrd':
                rx = random.randint(-1,1)
                ry = random.randint(-1,1)
                px += rx * ele.value
                py += ry * ele.value

        px = tanh(px)
        py = tanh(py)
        probx = random.random() < abs(px)
        proby = random.random() < abs(py)
        sigX = -1 if px < 0 else 1
        sigY = -1 if py < 0 else 1
        px = probx*sigX
        py = proby*sigY
        self.move(px, py)




    def attach_functions(self):
        for i in range(len(inNames)):
            ele = self.sensory[i]
            if inNames[i] == 'Lx':
                ele.func = self.lx
                ele.name = 'Lx'
            elif inNames[i] == 'Ly':
                ele.func = self.ly
                ele.name = 'Ly'
            elif inNames[i] == 'Srf':
                ele.func = self.searchForw
                ele.name = 'Srf'
            elif inNames[i] == 'Rnd':
                ele.func = self.rand
                ele.name = 'Rnd'
        for i in range(len(outNames)):
            ele = self.action[i]
            if outNames[i] == 'me':
                ele.func = self.me
                ele.name = 'me'
            elif outNames[i] == 'mw':
                ele.func = self.mw
                ele.name = 'mw'
            elif outNames[i] == 'mn':
                ele.func = self.mn
                ele.name = 'mn'
            elif outNames[i] == 'ms':
                ele.func = self.ms
                ele.name = 'ms'
            elif outNames[i] == 'mf':
                ele.func = self.mf
                ele.name = 'mf'
            elif outNames[i] == 'mrd':
                ele.func = self.mrd
                ele.name = 'mrd'
            elif outNames[i] == 'stRad':
                ele.func = self.setRadius
                ele.name = 'stRad'

    def isValid(self, dx, dy):
        px = self.x + dx
        py = self.y + dy
        if grid.world_size > px >= 0:
            if grid.world_size > py >= 0:
                return True
        return False

    def epsFunc(self):
        return False

    def move(self, dx, dy):
        if self.isValid(dx, dy):
            px = self.x + dx
            py = self.y + dy
            if not grid.GRID_CELLS[px][py].isOccupied:
                grid.GRID_CELLS[self.x][self.y].isOccupied = False
                self.x = px
                self.y = py
                grid.GRID_CELLS[self.x][self.y].isOccupied = True
                self.prev = (dx, dy)
                return True
            else:
                # if dy == 0:
                #     dy = 1
                #     if isValidCell(self.x + dx, self.y + dy):
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = False
                #         self.x += dx
                #         self.y += dy
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = True
                #         self.prev = (dx, 0)
                #         return True
                #     dy = -1
                #     if isValidCell(self.x + dx, self.y + dy):
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = False
                #         self.x += dx
                #         self.y += dy
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = True
                #         self.prev = (dx, 0)
                #         return True
                # else:
                #     dx = 1
                #     if isValidCell(self.x + dx, self.y + dy):
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = False
                #         self.x += dx
                #         self.y += dy
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = True
                #         self.prev = (0, dy)
                #         return True
                #     dx = -1
                #     if isValidCell(self.x + dx, self.y + dy):
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = False
                #         self.x += dx
                #         self.y += dy
                #         grid.GRID_CELLS[self.x][self.y].isOccupied = True
                #         self.prev = (0, dy)
                #         return True
                self.prev = (0,0)
                return False
        self.prev = (0, 0)
        return False

    def lx(self):
        return self.x/WORLD_SIZE

    def ly(self):
        return self.y/WORLD_SIZE

    def density_east(self):
        length = 3
        cx = self.x
        cy = self.y
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cx -= 1
            cy += 1
            for j in range(length):

                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
                cx += 1
            cx -= length
            length += 2
        return cells_occupied/total_cells_covered

    def density_west(self):
        length = 3
        cx = self.x
        cy = self.y
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cx -= 1
            cy -= 1
            for j in range(length):

                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
                cx += 1
            cx -= length
            length += 2
        return cells_occupied/total_cells_covered

    def density_north(self):
        length = 3
        cx = self.x
        cy = self.y
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cx -= 1
            cy -= 1
            for j in range(length):

                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
                cy += 1
            cy -= length
            length += 2
        return cells_occupied / total_cells_covered

    def density_south(self):
        length = 3
        cx = self.x
        cy = self.y
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cx += 1
            cy -= 1
            for j in range(length):

                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
                cy += 1
            cy -= length
            length += 2
        return cells_occupied / total_cells_covered

    def density_northeast(self):
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cy = self.y + i
            for j in range(self.search_radius):
                cx = self.x - j
                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
        return cells_occupied / total_cells_covered

    def density_northwest(self):
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cy = self.y - i
            for j in range(self.search_radius):
                cx = self.x - j
                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
        return cells_occupied / total_cells_covered

    def density_southeast(self):
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cy = self.y + i
            for j in range(self.search_radius):
                cx = self.x + j
                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
        return cells_occupied / total_cells_covered

    def density_southwest(self):
        total_cells_covered = 0
        cells_occupied = 0
        for i in range(self.search_radius):
            cy = self.y - i
            for j in range(self.search_radius):
                cx = self.x + j
                if isValidCell(cx, cy):
                    if grid.GRID_CELLS[cx][cy].isOccupied:
                        cells_occupied += 1
                total_cells_covered += 1
        return cells_occupied / total_cells_covered

    def searchForw(self):
        if self.prev == (0,0):
            rfid = random.randint(1,4)
            if rfid == 1:
                return self.density_east()
            elif rfid == 2:
                return self.density_south()
            elif rfid == 3:
                return self.density_west()
            else:
                return self.density_north()
        if self.prev == (0,1):
            return self.density_east()
        if self.prev == (1,0):
            return self.density_south()
        if self.prev == (0,-1):
            return self.density_west()
        if self.prev == (-1,0):
            return self.density_north()
        if self.prev == (1,1):
            return self.density_southeast()
        if self.prev == (1,-1):
            return self.density_southwest()
        if self.prev == (-1,1):
            return self.density_northeast()
        if self.prev == (-1,-1):
            return self.density_northwest()

    def searchAll(self):
        arr = [self.density_north(), self.density_east(), self.density_south(), self.density_west()]

    def rand(self):
        return random.random()

    def randColor(self):
        return f"#{hex(random.randint(0,255))[2:]}{hex(random.randint(0,255))[2:]}{hex(random.randint(0,255))[2:]}"

    def me(self):
        return self.move(0, 1)

    def mw(self):
        return self.move(0, -1)

    def mn(self):
        return self.move(-1, 0)

    def ms(self):
        return self.move(1, 0)

    def mf(self):
        self.move(*self.prev)

    def mrd(self):
        arr = [random.randint(-1,1),0]
        if arr[0] == 0:
            arr[1] = random.randint(-1,1)
        return self.move(arr[0],arr[1])

    def setRadius(self):
        self.search_radius += 2
        self.search_radius = max(1, self.search_radius%10)
        return 1


class Creature(Brain):

    def __init__(self, px, py, gen=None, world=128):
        Brain.__init__(self, px, py, gen)
        self.world_size = world
        self.boundary = world

    def dumps(self):
        ret = {
            'x': self.x,
            'y': self.y,
            'g': self.genomeCol
        }
        return ret

    def __repr__(self):
        return f"x: {self.x}, y: {self.y}, g: {self.genome}"


