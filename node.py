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
        self.id = self.world.get_new_id()

    def __repr__(self):
        return "Node(" + str(self.id) + ")"

    def __str__(self):
        return "Node(" + str(self.id) + ")"

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_edge(self, edge):
        self.edges.append(edge)

    def shares_edge_with(self, other_node):
        for edge in self.edges:
            if edge.connects(other_node):
                return self.edges.index(edge)
        return -1

    def get_adjacent_nodes(self):
        nodes = []
        for edge in self.edges:
            nodes.append(edge.get_other_node(self))
        return nodes
