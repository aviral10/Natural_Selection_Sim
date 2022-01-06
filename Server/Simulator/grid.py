from Simulator.PARAMETERS import *


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

