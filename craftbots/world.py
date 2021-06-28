import random as r
import math as m
from entities.node import Node
from entities.edge import Edge
from entities.actor import Actor
from entities.resource import Resource
from entities.site import Site
from entities.building import Building
from entities.mine import Mine
from entities.task import Task


class World:

    def __init__(self, modifiers, world_gen_modifiers, rules):
        self.modifiers = modifiers
        self.world_gen_modifiers = world_gen_modifiers
        self.rules = rules
        """
        0 - Actor Speed
        1 - Actor Mining Speed
        2 - Actor Building Speed
        3 - Actor Inventory Size
        """
        self.building_modifiers = {0: 0, 1: 0, 2: 0, 3: 0}
        
        self.nodes = []
        self.tick = 0
        self.last_id = -1
        self.command_queue = []
        self.command_results = []
        
        self.create_nodes_prm()
        self.tasks = self.generate_tasks()

    def create_nodes_prm(self):
        self.nodes = [Node(self, self.world_gen_modifiers["WIDTH"]/2, self.world_gen_modifiers["HEIGHT"]/2)]
        attempts = 0
        curr_x = self.nodes[0].x
        curr_y = self.nodes[0].y
        for i in range(self.world_gen_modifiers["MAX_NODES"] - 1):
            ok = False
            while not ok:
                ok = True
                rand_angle = r.randint(0, 360)
                rand_deviation = r.randint(-1 * self.world_gen_modifiers["RANDOM_DEVIATION"],
                                           self.world_gen_modifiers["RANDOM_DEVIATION"])
                new_x = m.floor(curr_x + rand_deviation + self.world_gen_modifiers["CAST_DISTANCE"] * m.cos(rand_angle))
                new_y = m.floor(curr_y + rand_deviation + self.world_gen_modifiers["CAST_DISTANCE"] * m.sin(rand_angle))
                for node in self.nodes:
                    if m.dist((new_x, new_y), (node.x, node.y)) <= self.world_gen_modifiers["MIN_DISTANCE"] or\
                            new_x < 0 or new_x > self.world_gen_modifiers["WIDTH"] or new_y < 0 \
                            or new_y > self.world_gen_modifiers["HEIGHT"]:
                        ok = False
                        break
                no_new_edges = True
                if ok:
                    new_node = Node(self, new_x, new_y)
                    new_edges = []
                    for node in self.nodes:
                        if m.dist((new_x, new_y), (node.x, node.y)) <= self.world_gen_modifiers["CONNECT_DISTANCE"]:
                            new_edges.append(Edge(self, new_node, node))
                            no_new_edges = False
                    if not no_new_edges:
                        self.nodes.append(new_node)
                        curr_x = new_x
                        curr_y = new_y
                attempts += 1
                if attempts >= self.world_gen_modifiers["MAX_ATTEMPTS"]:
                    break

    def get_world_info(self):
        actors = {}
        nodes = {}
        edges = {}
        resources = {}
        mines = {}
        sites = {}
        buildings = {}
        tasks = {}
        for actor in self.get_all_actors():
            actors.__setitem__(actor.id, actor.fields)
        for edge in self.get_all_edges():
            edges.__setitem__(edge.id, edge.fields)
        for node in self.nodes:
            nodes.__setitem__(node.id, node.fields)
        for resource in self.get_all_resources():
            resources.__setitem__(resource.id, resource.fields)
        for mine in self.get_all_mines():
            mines.__setitem__(mine.id, mine.fields)
        for site in self.get_all_sites():
            sites.__setitem__(site.id, site.fields)
        for building in self.get_all_buildings():
            buildings.__setitem__(building.id, building.fields)
        for task in self.tasks:
            tasks.__setitem__(task.id, task.fields)
        return {"tick": self.tick, "actors": actors, "nodes": nodes, "edges": edges, "resources": resources, "mines": mines,
                "sites": sites, "buildings": buildings, "tasks": tasks}

    def run_tick(self):
        self.update_all_actors()
        self.update_all_resources()
        self.run_agent_commands()
        if self.tasks_complete():
            pass
            # print("The tasks have been completed")
        self.tick += 1

    def run_agent_commands(self):
        if self.command_queue:
            current_commands = self.command_queue[:]
            self.command_queue = []
            self.command_results = []
            for command in current_commands:
                self.command_results.append((command.id, command.perform()))

    def update_all_actors(self):
        for actor in self.get_all_actors():
            actor.update()
            
    def update_all_resources(self):
        for resource in self.get_all_resources():
            resource.update()

    def tasks_complete(self):
        for task in self.tasks:
            if not task.completed():
                return False
        return True

    def generate_tasks(self):
        tasks = []
        for index in range(3):
            tasks.append(Task(self, self.nodes[r.randint(0, self.nodes.__len__() - 1)], r.randint(0, 4)
                              , r.randint(1, 10)))
        return tasks

    def add_actor(self, node):
        return Actor(self, node)

    def add_resource(self, node, colour):
        return Resource(self, node, colour)

    def add_mine(self, node, colour):
        return Mine(self, node, colour)

    def add_site(self, node, colour):
        return Site(self, node, colour)

    def add_building(self, node, colour):
        return Building(self, node, colour)

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

    def get_all_actor_ids(self):
        actor_ids = []
        for node in self.nodes:
            for actor in node.actors:
                actor_ids.append(actor.id)
        return actor_ids
    
    def get_all_resources(self):
        resources = []
        for node in self.nodes:
            resources.extend(node.resources)
        for actor in self.get_all_actors():
            resources.extend(actor.resources)
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

    def get_new_id(self):
        self.last_id += 1
        return self.last_id

    def get_by_id(self, entity_id, entity_type=None, target_node=None):
        if target_node is None:
            target_node = self.nodes
        else:
            target_node = [target_node]
        for node in target_node:
            if node.id == entity_id and (entity_type == "Node" or entity_type is None):
                return node
            for actor in node.actors:
                if actor.id == entity_id and (entity_type == "Actor" or entity_type is None):
                    return actor
                for resource in actor.resources:
                    if resource.id == entity_id and (entity_type == "Resource" or entity_type is None):
                        return resource
            for resource in node.resources:
                if resource.id == entity_id and (entity_type == "Resource" or entity_type is None):
                    return resource
            for mine in node.mines:
                if mine.id == entity_id and (entity_type == "Mine" or entity_type is None):
                    return mine
            for site in node.sites:
                if site.id == entity_id and (entity_type == "Site" or entity_type is None):
                    return site
            for building in node.buildings:
                if building.id == entity_id and (entity_type == "Building" or entity_type is None):
                    return building
            for edge in node.edges:
                if edge.id == entity_id and (entity_type == "Edge" or entity_type is None):
                    return edge
        return None

    def get_field(self, entity_id, field, entity_type=None, target_node=None):
        entity = self.get_by_id(entity_id, entity_type=entity_type, target_node=target_node)
        return None if entity is None else entity.fields.get(field)
