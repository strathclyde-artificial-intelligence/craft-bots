import random as r
import math as m
from node import Node
from edge import Edge
from actor import Actor
from resource import Resource
from site import Site
from building import Building
from mine import Mine
from task import Task


class World:

    def __init__(self, build_speed=3, build_effort=100, mine_speed=3, mine_effort=100, green_decay_time=300,
                 blue_extra_effort=12, cycle_length=1200, red_collection_intervals=None, actor_speed=1,
                 width=600, height=600):
        if red_collection_intervals is None:
            red_collection_intervals = [0, 600]
        self.modifiers = {
            "BUILD_SPEED": build_speed,
            "BUILD_EFFORT": build_effort,
            "MINE_SPEED": mine_speed,
            "MINE_EFFORT": mine_effort,
            "GREEN_DECAY_TIME": green_decay_time,
            "BLUE_EXTRA_EFFORT": blue_extra_effort,
            "CYCLE_LENGTH": cycle_length,
            "RED_COLLECTION_INTERVALS": red_collection_intervals,
            "ACTOR_SPEED": actor_speed,
            "WIDTH": width,
            "HEIGHT": height
        }
        
        self.nodes = []
        self.tick = 0
        self.next_id = -1
        
        self.create_nodes_prm()
        self.tasks = self.generate_tasks()

    def create_nodes_prm(self, cast_dist=80, min_dist=40, connect_dist=100, max_nodes=50, max_attempts=100, deviation=0):
        self.nodes = [Node(self, self.modifiers["WIDTH"]/2, self.modifiers["HEIGHT"]/2)]
        attempts = 0
        curr_x = self.nodes[0].x
        curr_y = self.nodes[0].y
        for i in range(max_nodes - 1):
            ok = False
            while not ok:
                ok = True
                rand_angle = r.randint(0, 360)
                rand_deviation = r.randint(-1 * deviation, deviation)
                new_x = m.floor(curr_x + rand_deviation + cast_dist * m.cos(rand_angle))
                new_y = m.floor(curr_y + rand_deviation + cast_dist * m.sin(rand_angle))
                for node in self.nodes:
                    if m.dist((new_x, new_y), (node.x, node.y)) <= min_dist or\
                            new_x < 0 or new_x > self.modifiers["WIDTH"] or new_y < 0 \
                            or new_y > self.modifiers["HEIGHT"]:
                        ok = False
                        break
                no_new_edges = True
                if ok:
                    new_node = Node(self, new_x, new_y)
                    new_edges = []
                    for node in self.nodes:
                        if m.dist((new_x, new_y), (node.x, node.y)) <= connect_dist:
                            new_edges.append(Edge(new_node, node))
                            no_new_edges = False
                    if not no_new_edges:
                        self.nodes.append(new_node)
                        curr_x = new_x
                        curr_y = new_y
                attempts += 1
                if attempts >= max_attempts:
                    break

    def run_tick(self):
        self.update_all_actors()
        self.update_all_resources()
        if self.tasks_complete():
            print("The tasks have been completed")
        self.tick += 1
        
    def update_all_actors(self):
        for actor in self.get_all_actors():
            actor.update()
            
    def update_all_resources(self):
        for resource in self.get_all_resources():
            resource.update()

    def tasks_complete(self):
        for task in self.tasks:
            if not task.complete():
                return False
        return True

    def generate_tasks(self):
        tasks = []
        for index in range(3):
            tasks.append(Task(self.nodes[r.randint(0, self.nodes.__len__() - 1)], r.randint(0, 4), r.randint(1, 10)))
        return tasks

    def add_actor(self, node):
        Actor(self, node)

    def add_resource(self, node, colour):
        Resource(self, node, colour)

    def add_mine(self, node, colour):
        Mine(self, node, colour)

    def add_site(self, node, colour):
        Site(self, node, colour)

    def add_building(self, node, colour):
        Building(self, node, colour)

    def get_colour_string(self, colour):
        if colour == 0:
            return "red"
        elif colour == 1:
            return "blue"
        elif colour == 2:
            return "orange"
        elif colour == 3:
            return "black"
        elif colour == 4:
            return "green"

    def get_all_mines(self):
        mines = []
        for node in self.nodes:
            mines.extend(node.mines)
        return mines
    
    def get_all_actors(self):
        actors = []
        for node in self.nodes:
            actors.extend(node.actors)
        return actors
    
    def get_all_resources(self):
        resources = []
        for node in self.nodes:
            resources.extend(node.resources)
        return resources
    
    def get_all_sites(self):
        sites = []
        for node in self.nodes:
            sites.extend(node.sites)
        return sites
    
    def get_all_buildings(self):
        buildings = []
        for node in self.nodes:
            buildings.extend(node.buildings)
        return buildings

    def get_all_edges(self):
        edges = []
        for node in self.nodes:
            for edge in node.edges:
                if not edges.__contains__(edge):
                    edges.append(edge)
        return edges
