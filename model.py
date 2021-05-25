import random as r
import math as m
import numpy.random as nr


class Edge:
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
        self.node_a.add_edge(self)
        self.node_b.add_edge(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.node_a == other.node_a and self.node_b == other.node_b or self.node_a == other.node_b and\
                    self.node_b == other.node_a:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Edge" + self.__str__()

    def __str__(self):
        return "(" + str(self.node_a) + ", " + str(self.node_b) + ", " + str(self.length()) + ")"

    def length(self):
        return m.dist((self.node_a.x, self.node_a.y), (self.node_b.x, self.node_b.y))

    def connects(self, node):
        return node == self.node_a or node == self.node_b


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.edges = []
        self.actors = []
        self.mines = []

    def __repr__(self):
        return "Node()"

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def add_edge(self, edge):
        self.edges.append(edge)


class World:
    def __init__(self):
        self.nodes = []
        self.map = []
        self.edges = []
        self.actors = []
        self.create_nodes_prm(max_nodes=30, min_dist=10, cast_dist=20, connect_dist=25)

    def create_nodes_prm(self, cast_dist=15, min_dist=5, connect_dist=20, max_nodes=10, max_attempts=50, deviation=5):
        self.nodes = [Node(50, 50)]
        attempts = 0
        curr_x = 50
        curr_y = 50
        for i in range(max_nodes):
            ok = False
            while not ok:
                ok = True
                rand_angle = r.randint(0, 360)
                rand_deviation = r.randint(-1 * deviation, deviation)
                new_x = m.floor(curr_x + rand_deviation + cast_dist * m.cos(rand_angle))
                new_y = m.floor(curr_y + rand_deviation + cast_dist * m.sin(rand_angle))
                for node in self.nodes:
                    if (node.x == new_x and node.y == new_y) or m.dist((new_x, new_y), (node.x, node.y)) <= min_dist or\
                            new_x < 0 or new_x > 100 or new_y < 0 or new_y > 100:
                        ok = False
                        break
                no_new_edges = True
                if ok:
                    new_node = Node(new_x, new_y)
                    for node in self.nodes:
                        if m.dist((new_x, new_y), (node.x, node.y)) <= connect_dist and\
                                not self.edges.__contains__(Edge(new_node, node)):
                            self.edges.append(Edge(new_node, node))
                            no_new_edges = False
                if no_new_edges:
                    ok = False
                if ok:
                    self.nodes.append(Node(new_x, new_y))
                    curr_x = new_x
                    curr_y = new_y
                attempts += 1
                if attempts >= max_attempts:
                    break

    def create_nodes_normal_dis(self):
        self.nodes = []
        for i in range(10):
            unique = False
            while not unique:
                unique = True
                new_x = int(nr.normal(loc=5, scale=2))
                new_y = int(nr.normal(loc=5, scale=2))
                new_x = min(max(0, new_x), 9)
                new_y = min(max(0, new_y), 9)
                for node in self.nodes:
                    if node.x == new_x and node.y == new_y:
                        unique = False
                        continue
            self.nodes.append(Node(new_x, new_y))
            self.map[new_x][new_y] = "N"
        for current_node in self.nodes:
            distance_map = []
            for other_node in self.nodes:
                if current_node != other_node:
                    distance = m.ceil(((current_node.x - other_node.x)**2 + (current_node.y - other_node.y)**2) ** 0.5)
                    distance_map.append((other_node, distance))
            distance_map.sort(key=lambda x: x[1])
            for edge in distance_map[:3]:
                if not self.edges.__contains__(Edge(current_node, edge[0])):
                    self.edges.append(Edge(current_node, edge[0]))

    def print_nodes(self):
        print(self.nodes)

    def print_edges(self):
        print(self.edges)


class Actor:
    def __init__(self, world):
        self.world = world
        self.node = self.world.nodes[0]
        self.node.actors.append(self)
        self.world.actors.append(self)

    def move_to(self, target_node):
        moved = False
        index = 0
        while not moved:
            if index == self.node.edges.__len__():
                return False
            if self.node.edges[index].connects(target_node):
                self.node.actors.remove(self)
                self.node = target_node
                self.node.actors.append(self)
                return True
            index += 1

    def move_rand(self):
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            self.move_to(target_edge.node_b)
        else:
            self.move_to(target_edge.node_a)
