class Node:
    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.edges = []
        self.actors = []
        self.resources = []
        self.mines = []
        self.sites = []
        self.buildings = []

    def __repr__(self):
        return "Node(" + str(self.x) + ", " + str(self.x) + ")"

    def __str__(self):
        return "Node(" + str(self.x) + ", " + str(self.x) + ")"

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_edge(self, edge):
        self.edges.append(edge)
