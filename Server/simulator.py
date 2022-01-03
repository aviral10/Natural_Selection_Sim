import numpy as np
import random
random.seed(200)

import time
from math import tanh
from Simulator.PARAMETERS import WORLD_SIZE
from Simulator.PARAMETERS import BRAIN_SIZE
from Simulator.PARAMETERS import INTERNAL_NEURONS
# WORLD_SIZE = 128
# BRAIN_SIZE = 5

class Node:
    def __init__(self, x, y, isOcc=False):
        self.x = x
        self.y = y
        self.isOccupied = isOcc

    def dumps(self):
        return f"{{x: {self.x}, y: {self.y}, isOcc: {self.isOccupied} }}"

    def __repr__(self):
        return f"{self.__dict__}"


ALL_CELLS = [{'x': i, 'y': j} for i in range(WORLD_SIZE) for j in range(WORLD_SIZE)]


class Grid:

    def __init__(self, world):
        self.world_size = world
        self.GRID_CELLS = [[Node(i, j) for j in range(world)] for i in range(world)]

    def dumps(self):
        return [bele.dumps() for ele in self.GRID_CELLS for bele in ele]


grid = Grid(WORLD_SIZE)


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
        return f"name: {self.name}"

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
        self.genomeCol = self.randColor()
        self.genome = self.cleanGenome(gen)
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
            curr.parentweights = np.array(par, dtype=np.float)

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

            curr.parentweights = np.array(par, dtype=np.float)

        eps = Neuron("none", 'a', self.epsFunc)
        g[2].append(eps)
        self.brain_graph = g

    def cleanGenome(self, gen):
        if gen is None:
            return None
        gen = list(set(gen))
        return gen

    # def output_action(self, probabilities):
    #     return

    def sampleFunc(self):
        print("PP")

    def think(self):
        for idx in range(3):
            for neu in self.brain_graph[idx]:
                neu.think()
        probs = [max(0, entity.value) for entity in self.brain_graph[2]]
        chc = random.choices(self.brain_graph[2], weights=probs, k=1)
        chc[0].execute()

    def thinks(self):
        for idx in range(3):
            for neu in self.brain_graph[idx]:
                neu.think()
        probs = [max(0, entity.value) for entity in self.brain_graph[2]]
        sm = sum(probs)
        if sm == 0:
            probs[-1] = 1 - sm
            sm = 1
        norm = [float(i)/sm for i in probs]
        ret = np.random.choice(self.brain_graph[2], size=1, replace=False, p=norm)
        # ret = random.choices(population=self.brain_graph[2], weights=norm, k=1)
        # print(ret)
        ret[0].execute()

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
            if not grid.GRID_CELLS[self.x + dx][self.y + dy].isOccupied:
                grid.GRID_CELLS[self.x][self.y].isOccupied = False
                self.x += dx
                self.y += dy
                grid.GRID_CELLS[self.x][self.y].isOccupied = True
                self.prev = (dx, dy)
                return True
            else:
                if dy == 0:
                    dy = 1
                    if isValidCell(self.x + dx, self.y + dy):
                        grid.GRID_CELLS[self.x][self.y].isOccupied = False
                        self.x += dx
                        self.y += dy
                        grid.GRID_CELLS[self.x][self.y].isOccupied = True
                        self.prev = (dx, 0)
                        return True
                    dy = -1
                    if isValidCell(self.x + dx, self.y + dy):
                        grid.GRID_CELLS[self.x][self.y].isOccupied = False
                        self.x += dx
                        self.y += dy
                        grid.GRID_CELLS[self.x][self.y].isOccupied = True
                        self.prev = (dx, 0)
                        return True
                else:
                    dx = 1
                    if isValidCell(self.x + dx, self.y + dy):
                        grid.GRID_CELLS[self.x][self.y].isOccupied = False
                        self.x += dx
                        self.y += dy
                        grid.GRID_CELLS[self.x][self.y].isOccupied = True
                        self.prev = (0, dy)
                        return True
                    dx = -1
                    if isValidCell(self.x + dx, self.y + dy):
                        grid.GRID_CELLS[self.x][self.y].isOccupied = False
                        self.x += dx
                        self.y += dy
                        grid.GRID_CELLS[self.x][self.y].isOccupied = True
                        self.prev = (0, dy)
                        return True

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

    def searchForw(self):
        if self.prev == (0,0):
            rfunc = random.choice([self.density_north, self.density_east, self.density_south, self.density_west])
            return rfunc()
        if self.prev == (0,1):
            return self.density_east()
        if self.prev == (1,0):
            return self.density_south()
        if self.prev == (0,-1):
            return self.density_west()
        if self.prev == (-1,0):
            return self.density_north()

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







from flask import Flask, jsonify, make_response
from flask_cors import CORS
import json
import gzip

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"



def generate_population(sz):
    choices = np.random.choice(ALL_CELLS, size=sz, replace=False)
    arr = [Creature(ele['x'], ele['y'], [random.randint(1, int("ffffffff",16)) for _ in range(BRAIN_SIZE)]) for ele in choices]
    for ele in arr:
        grid.GRID_CELLS[ele.x][ele.y].isOccupied = True
    return arr


def condition(ele):
    # val = 40
    # return (ele.x <= val or ele.x >= 128-val) and (ele.y <= val or ele.y >= 128-val)
    return ele.x > 64

def mutation(probability):
    # val = random.random()
    # if val <= probability:
    #     print("Prob: ", val)
    #     return True
    # return False
    return random.random() < probability

def run_natural_selection():
    global creatures, ALL_CELLS


    # for iterate in range(gens):
    choices = np.random.choice(ALL_CELLS, size=len(creatures), replace=False)
    for ele in grid.GRID_CELLS:
        for bele in ele:
            bele.isOccupied = False
    # choices = random.sample(ALL_CELLS, k=len(creatures))
    brr = []

    for ele in creatures:
        if condition(ele):
            mutate = False
            for _ in range(random.randint(1,2)):
                gene = ele.genome[:]
                if mutation(1/ 1000):
                    mutate = True
                    # print("Mutated because genome was copied", ele.genome_copied, "times")
                    ch = random.choice(gene)
                    # print("Old Gene: ", ch)
                    ch ^= ( (1<<(random.randint(0,32))) -1)
                    # print("New Gene: ", ch)
                brr.append(Creature(ele.x, ele.y, gene))
                brr[-1].genome_copied = ele.genome_copied+1
                if mutate: brr[-1].genome_copied = 0
    while len(brr) < len(creatures):
        brr.append(Creature(1,1,[random.randint(1, int("ffffffff",16)) for _ in range(BRAIN_SIZE)]))
    random.shuffle(brr)
    if len(brr) > len(creatures):
        brr = brr[:len(creatures)]
    for i,ele in enumerate(brr):
        ele.x = choices[i]['x']
        ele.y = choices[i]['y']
        # print(ele.genome)
    creatures = brr


creatures = generate_population(100)
subsequent = False
@app.route("/test", methods=['POST'])
def test():
    global subsequent
    arr = []
    n = 1
    # if subsequent: n = 1
    itera = 0
    while itera < n:
        for i in range(300):
            temp = []
            if itera == n-1:
                for elem in creatures:
                    temp.append({'x': elem.x, 'y': elem.y, 'g': elem.genomeCol})

                arr.append(temp)
            for elem in creatures:
                elem.think()
        run_natural_selection()
        subsequent = True

        itera+=1


    content = gzip.compress(json.dumps(arr).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response




if __name__ == '__main__':


    app.run(debug=True)




