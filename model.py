import random as r
import math as m
import numpy.random as nr

ACTOR_SPEED = 1
MINE_SPEED = 3
MINE_EFFORT = 100

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
        return m.ceil(m.dist((self.node_a.x, self.node_a.y), (self.node_b.x, self.node_b.y)))

    def connects(self, node):
        return node == self.node_a or node == self.node_b


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.edges = []
        self.actors = []
        self.resources = []
        self.mines = []

    def __repr__(self):
        return "Node(" + str(self.x) + ", " + str(self.y) + ")"

    def __str__(self):
        return "Node(" + str(self.x) + ", " + str(self.y) + ")"

    def add_edge(self, edge):
        self.edges.append(edge)


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.nodes = []
        self.map = []
        self.edges = []
        self.actors = []
        self.resources = []
        self.mines = []
        self.create_nodes_prm()
        self.tick = 0

    def create_nodes_prm(self, cast_dist=80, min_dist=40, connect_dist=75, max_nodes=2, max_attempts=100, deviation=15):
        self.nodes = [Node(self.width/2, self.height/2)]
        attempts = 0
        curr_x = self.nodes[0].x
        curr_y = self.nodes[0].y
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
                            new_x < 0 or new_x > self.width or new_y < 0 or new_y > self.height:
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

    def run_tick(self):
        for actor in self.actors:
            actor.update()
        self.tick += 1
        # print("Tick: " + str(self.tick))


class Actor:
    """
    States:
    0 - Idle
    1 - Moving
    2 - Mining
    """
    def __init__(self, world):
        self.world = world
        self.node = self.world.nodes[0]
        self.node.actors.append(self)
        self.world.actors.append(self)
        self.state = 0
        self.progress = -1
        self.target = None
        self.inventory = []

    def warp_to(self, target_node):
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

    def warp_rand(self):
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            self.warp_to(target_edge.node_b)
        else:
            self.warp_to(target_edge.node_a)

    def travel_to(self, target_node):
        if self.state:
            print("Error: Must be idle to begin travelling to another node!")
            return False
        moved = False
        index = 0
        while not moved:
            if index == self.node.edges.__len__():
                return False
            if self.node.edges[index].connects(target_node):
                self.target = (self.node.edges[index], target_node)
                self.state = 1
                self.progress = 0
                return True
            index += 1

    def travel_rand(self):
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            self.travel_to(target_edge.node_b)
        else:
            self.travel_to(target_edge.node_a)

    def update(self):
        if self.state == 1:
            self.progress += ACTOR_SPEED
            if self.target[0].length() <= self.progress:
                self.node.actors.remove(self)
                self.node = self.target[1]
                self.node.actors.append(self)
                self.state = 0
                self.progress = -1
                self.target = None
        if self.state == 2:
            self.progress += MINE_SPEED
            if self.progress >= MINE_EFFORT:
                self.progress = -1
                self.state = 0
                self.target.mine()
                self.target = None

    def pick_up_resource(self, resource):
        if self.state == 0 and resource.location is self.node:
            if resource.colour == 3 and self.inventory:
                return False
            resource.location = self
            self.inventory.append(resource)
            self.node.resources.remove(resource)
            return True
        return False

    def drop_resource(self, resource):
        if self.state == 0 and self.inventory.__contains__(resource):
            resource.location == self.node
            self.inventory.remove(resource)
            self.node.resources.append(resource)
            return True
        return False

    def drop_everything(self):
        if self.state == 0:
            for resource in self.inventory:
                resource.location = self.node
                self.inventory.remove(resource)
                self.node.resources.append(resource)
            return True
        return False

    def mine_at(self, mine):
        if not self.state and mine.node == self.node:
            self.state = 2
            self.target = mine
            self.progress = 0


class Resource:
    def __init__(self, world, location, colour=0):
        self.world = world
        self.colour = colour
        self.location = location
        if isinstance(self.location, Actor):
            location.inventory.append(self)
        if isinstance(self.location, Node):
            location.resources.append(self)
        self.world.resources.append(self)

    def get_colour_string(self):
        if self.colour == 0:
            return "red"
        elif self.colour == 1:
            return "blue"
        elif self.colour == 2:
            return "orange"
        elif self.colour == 3:
            return "black"
        elif self.colour == 4:
            return "green"


class Mine:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour

        self.world.mines.append(self)
        self.node.mines.append(self)

    def mine(self):
        Resource(self.world, self.node, self.colour)

    def get_colour_string(self):
        if self.colour == 0:
            return "red"
        elif self.colour == 1:
            return "blue"
        elif self.colour == 2:
            return "orange"
        elif self.colour == 3:
            return "black"
        elif self.colour == 4:
            return "green"
