import random as r
import math as m

from craftbots.config.config_manager import Configuration
from craftbots.entities.node import Node
from craftbots.entities.edge import Edge
from craftbots.entities.actor import Actor
from craftbots.entities.resource import Resource
from craftbots.entities.site import Site
from craftbots.entities.building import Building
from craftbots.entities.mine import Mine
from craftbots.entities.task import Task
from craftbots.log_manager import Logger


class World:

    def __init__(self, config):

        # Flatten nested config into dictionaries for easy access
        self.config = config
        self.world_generation_config = Configuration.flatten(self.config['World Setup'])
        self.task_config = Configuration.flatten(self.config['Tasks'])
        self.actor_config = Configuration.flatten(self.config['Actors'])
        self.resource_config = Configuration.flatten(self.config['Resources'])
        self.building_config = Configuration.flatten(self.config['Buildings'])
        self.partial_observability_config = Configuration.flatten(self.config["Partial Observability"])
        self.nondeterminism_config = Configuration.flatten(self.config["Nondeterminism"])
        self.temporal_config = Configuration.flatten(self.config["Temporal Uncertainty"])

        # Set random seed before any other calls
        if Configuration.get_value(config, "use_random_seed"):
            r.seed(Configuration.get_value(config, "random_seed"))

        self.building_modifiers = {
            Building.BUILDING_SPEED:        0,
            Building.BUILDING_MINE:         0,
            Building.BUILDING_INVENTORY:    0,
            Building.BUILDING_CONSTRUCTION: 0
        }

        self.nodes = []
        self.tick = 0
        self.last_id = -1
        self.command_queue = []
        self.all_commands = []
        self.total_score = 0
        self.max_possible_score = 0

        self.create_nodes_prm()
        self.tasks = self.generate_tasks(int(self.task_config["initial_tasks"]))

    # ===================== #
    # Probabilistic Roadmap #
    # ===================== #

    def create_nodes_prm(self):

        self.nodes = [Node(self, int(self.world_generation_config["width"])/2, int(self.world_generation_config["height"])/2)]
        attempts = 0
        curr_x = self.nodes[0].x
        curr_y = self.nodes[0].y
        for i in range(int(self.world_generation_config["max_nodes"]) - 1):
            ok = False
            while not ok:
                ok = True
                rand_angle = r.randint(0, 360)
                rand_deviation = r.randint(-1 * self.world_generation_config["roadmap_random_deviation"],
                                           self.world_generation_config["roadmap_random_deviation"])
                new_x = m.floor(curr_x + rand_deviation + self.world_generation_config["roadmap_cast_distance"] * m.cos(rand_angle))
                new_y = m.floor(curr_y + rand_deviation + self.world_generation_config["roadmap_cast_distance"] * m.sin(rand_angle))
                for node in self.nodes:
                    if m.dist((new_x, new_y), (node.x, node.y)) <= self.world_generation_config["roadmap_min_distance"] or\
                            new_x < 0 or new_x > self.world_generation_config["width"] or new_y < 0 \
                            or new_y > self.world_generation_config["height"]:
                        ok = False
                        break
                no_new_edges = True
                if ok:
                    new_node = Node(self, new_x, new_y)
                    new_edges = []
                    for node in self.nodes:
                        if m.dist((new_x, new_y), (node.x, node.y)) <= float(self.world_generation_config["roadmap_connect_distance"]):
                            new_edges.append(Edge(self, new_node, node))
                            no_new_edges = False
                    if not no_new_edges:
                        self.nodes.append(new_node)
                        curr_x = new_x
                        curr_y = new_y
                attempts += 1
                if attempts >= self.world_generation_config["roadmap_max_attempts"]:
                    break

    # ===================== #
    # World Info Dictionary #
    # ===================== #

    def get_world_info(self, target_actors=None):
        if target_actors is None:
            actors = self.get_all_actors()
        else:
            actors = []
            for actor_index in range(target_actors.__len__()):
                actors.append(self.get_by_id(target_actors[actor_index], entity_type="Actor"))

        look_effort = Configuration.get_value(self.config, "look_effort")

        edges_info = self.get_edges_info(actors)
        resources_info = self.get_resources_info(actors)
        mines_info = self.get_mines_info(actors)
        sites_info = self.get_sites_info(actors)
        buildings_info = self.get_buildings_info(actors)
        tasks_info = self.get_tasks_info(actors)
        actors_info = self.get_actor_info(actors)

        nodes_info = {}
        if self.partial_observability_config["node_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    if nodes_info.__contains__(actor.node.id):
                        nodes_info.get(actor.node.id)["observers"].append(actor.id)
                    else:
                        nodes_info.__setitem__(actor.node.id, actor.node.fields)
                        nodes_info.get(actor.node.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node_id in node_stack:
                        if nodes_info.__contains__(node_id):
                            nodes_info.get(node_id)["observers"].append(actor.id)
                        else:
                            nodes_info.__setitem__(node_id, node_stack[node_id].fields)
                            nodes_info.get(node_id).__setitem__("observers", [actor.id])
        else:
            for node in self.nodes:
                nodes_info.__setitem__(node.id, node.fields)
                if self.partial_observability_config["edge_po"]:
                    nodes_info[node.id].__setitem__("edges", [])
                    for edge_id in edges_info:
                        if edges_info[edge_id]["node_a"] == node.id or edges_info[edge_id]["node_b"] == node.id:
                            nodes_info.get(node.id)["edges"].append(edge_id)
                if self.partial_observability_config["resource_po"]:
                    nodes_info[node.id].__setitem__("resources", [])
                    for resource_id in resources_info:
                        if resources_info[resource_id]["location"] == node.id:
                            nodes_info.get(node.id)["resources"].append(resource_id)
                if self.partial_observability_config["mine_po"]:
                    nodes_info[node.id].__setitem__("mines", [])
                    for mine_id in mines_info:
                        if mines_info[mine_id]["node"] == node.id:
                            nodes_info.get(node.id)["mines"].append(mine_id)
                if self.partial_observability_config["site_po"]:
                    nodes_info[node.id].__setitem__("sites", [])
                    for site_id in sites_info:
                        if sites_info[site_id]["node"] == node.id:
                            nodes_info.get(node.id)["sites"].append(site_id)
                if self.partial_observability_config["building_po"]:
                    nodes_info[node.id].__setitem__("buildings", [])
                    for building_id in buildings_info:
                        if buildings_info[building_id]["node"] == node.id:
                            nodes_info.get(node.id)["buildings"].append(building_id)
                if self.partial_observability_config["task_po"]:
                    nodes_info[node.id].__setitem__("tasks", [])
                    for task_id in tasks_info:
                        if tasks_info[task_id]["node"] == node.id:
                            nodes_info.get(node.id)["tasks"].append(task_id)

        commands_info = {}
        for command in self.all_commands:
            if actors_info.__contains__(command.args[0]):
                commands_info.__setitem__(command.id, command.fields)

        return {"tick": self.tick, "actors": actors_info, "nodes": nodes_info, "edges": edges_info, "resources": resources_info,
                "mines": mines_info, "sites": sites_info, "buildings": buildings_info, "tasks": tasks_info, "commands": commands_info,
                "score": self.total_score}
    
    def get_actor_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        actor_info = {}
        if self.partial_observability_config["actor_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for actor_at_node in actor.node.actors:
                        if actor_at_node.id in actor_info:
                            actor_info.get(actor_at_node.id)["observers"].append(actor.id)
                        else:
                            actor_info.__setitem__(actor_at_node.id, actor_at_node.fields)
                            actor_info.get(actor_at_node.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for actor_at_node in node_stack[node].actors:
                            if actor_at_node.id in actor_info:
                                actor_info.get(actor_at_node.id)["observers"].append(actor.id)
                            else:
                                actor_info.__setitem__(actor_at_node.id, actor_at_node.fields)
                                actor_info.get(actor_at_node.id).__setitem__("observers", [actor.id])
        else:
            for actor in self.get_all_actors():
                actor_info.__setitem__(actor.id, actor.fields)
        return actor_info

    def get_tasks_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        tasks = {}
        if self.partial_observability_config["task_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for task in actor.node.tasks:
                        if tasks.__contains__(task.id):
                            tasks.get(task.id)["observers"].append(actor.id)
                        else:
                            tasks.__setitem__(task.id, task.fields)
                            tasks.get(task.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for task in node_stack[node].tasks:
                            if tasks.__contains__(task.id):
                                tasks.get(task.id)["observers"].append(actor.id)
                            else:
                                tasks.__setitem__(task.id, task.fields)
                                tasks.get(task.id).__setitem__("observers", [actor.id])
        else:
            for task in self.tasks:
                tasks.__setitem__(task.id, task.fields)
        return tasks

    def get_buildings_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        buildings = {}
        if self.partial_observability_config["building_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for building in actor.node.buildings:
                        if buildings.__contains__(building.id):
                            buildings.get(building.id)["observers"].append(actor.id)
                        else:
                            buildings.__setitem__(building.id, building.fields)
                            buildings.get(building.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for building in node_stack[node].buildings:
                            if buildings.__contains__(building.id):
                                buildings.get(building.id)["observers"].append(actor.id)
                            else:
                                buildings.__setitem__(building.id, building.fields)
                                buildings.get(building.id).__setitem__("observers", [actor.id])
        else:
            for building in self.get_all_buildings():
                buildings.__setitem__(building.id, building.fields)
        return buildings

    def get_sites_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        sites = {}
        if self.partial_observability_config["site_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for site in actor.node.sites:
                        if sites.__contains__(site.id):
                            sites.get(site.id)["observers"].append(actor.id)
                        else:
                            sites.__setitem__(site.id, site.fields)
                            sites.get(site.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for site in node_stack[node].sites:
                            if sites.__contains__(site.id):
                                sites.get(site.id)["observers"].append(actor.id)
                            else:
                                sites.__setitem__(site.id, site.fields)
                                sites.get(site.id).__setitem__("observers", [actor.id])
        else:
            for site in self.get_all_sites():
                sites.__setitem__(site.id, site.fields)
        return sites

    def get_mines_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        mines = {}
        if self.partial_observability_config["mine_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for mine in actor.node.mines:
                        if mines.__contains__(mine.id):
                            mines.get(mine.id)["observers"].append(actor.id)
                        else:
                            mines.__setitem__(mine.id, mine.fields)
                            mines.get(mine.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for mine in node_stack[node].mines:
                            if mines.__contains__(mine.id):
                                mines.get(mine.id)["observers"].append(actor.id)
                            else:
                                mines.__setitem__(mine.id, mine.fields)
                                mines.get(mine.id).__setitem__("observers", [actor.id])
        else:
            for mine in self.get_all_mines():
                mines.__setitem__(mine.id, mine.fields)
        return mines

    def get_resources_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        resources = {}
        if self.partial_observability_config["resource_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for resource in actor.node.resources:
                        if resources.__contains__(resource.id):
                            resources.get(resource.id)["observers"].append(actor.id)
                        else:
                            resources.__setitem__(resource.id, resource.fields)
                            resources.get(resource.id).__setitem__("observers", [actor.id])
                    for node_actor in actor.node.actors:
                        for resource in node_actor.resources:
                            if resources.__contains__(resource.id):
                                resources.get(resource.id)["observers"].append(actor.id)
                            else:
                                resources.__setitem__(resource.id, resource.fields)
                                resources.get(resource.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for resource in node_stack[node].resources:
                            if resources.__contains__(resource.id):
                                resources.get(resource.id)["observers"].append(actor.id)
                            else:
                                resources.__setitem__(resource.id, resource.fields)
                                resources.get(resource.id).__setitem__("observers", [actor.id])
                        for node_actor in node_stack[node].actors:
                            for resource in node_actor.resources:
                                if resources.__contains__(resource.id):
                                    resources.get(resource.id)["observers"].append(actor.id)
                                else:
                                    resources.__setitem__(resource.id, resource.fields)
                                    resources.get(resource.id).__setitem__("observers", [actor.id])
        else:
            for resource in self.get_all_resources():
                resources.__setitem__(resource.id, resource.fields)
        return resources

    def get_edges_info(self, actors):
        look_effort = Configuration.get_value(self.config, "look_effort")
        edges = {}
        if self.partial_observability_config["edge_po"]:
            for actor in actors:
                if actor.state != actor.LOOKING and actor.state != actor.MOVING and actor.state != actor.RECOVERING:
                    for edge in actor.node.edges:
                        if edges.__contains__(edge.id):
                            if not edges.get(edge.id)["observers"].__contains__(actor.id):
                                edges.get(edge.id)["observers"].append(actor.id)
                        else:
                            edges.__setitem__(edge.id, edge.fields)
                            edges.get(edge.id).__setitem__("observers", [actor.id])
                elif actor.state == actor.LOOKING:
                    node_stack = {actor.node.id: actor.node}
                    got_new_nodes = True
                    layer = 0
                    new_nodes = []
                    while got_new_nodes and layer < actor.progress / look_effort:
                        got_new_nodes = False
                        layer += 1
                        for node_id in node_stack:
                            for edge in node_stack[node_id].edges:
                                new_node = edge.get_other_node(node_stack[node_id])
                                if not node_stack.__contains__(new_node.id):
                                    new_nodes.append(new_node)
                                    got_new_nodes = True
                        if got_new_nodes:
                            for new_node in new_nodes:
                                node_stack.__setitem__(new_node.id, new_node)
                    for node in node_stack:
                        for edge in node_stack[node].edges:
                            if edges.__contains__(edge.id):
                                if not edges.get(edge.id)["observers"].__contains__(actor.id):
                                    edges.get(edge.id)["observers"].append(actor.id)
                            else:
                                edges.__setitem__(edge.id, edge.fields)
                                edges.get(edge.id).__setitem__("observers", [actor.id])
        else:
            for edge in self.get_all_edges():
                edges.__setitem__(edge.id, edge.fields)
        return edges

    # ====== #
    # Update #
    # ====== #

    def run_tick(self):

        # update all actors
        for actor in self.get_all_actors():
            actor.update()

        # decay green resource
        for resource in self.get_all_resources():
            if resource.colour == Resource.GREEN:
                resource.update()
        
        # process new commands
        if self.command_queue:
            self.all_commands.extend(self.command_queue)
            for command in self.command_queue:
                command.perform()
            self.command_queue = []
            
        # check task deadlines
        for task in self.tasks:
            if task.deadline > 0 and task.deadline < self.tick:
                task.complete_task()

        # generate new tasks
        if self.all_tasks_complete() and self.task_config["refresh_tasks"]:
            self.tasks.extend(self.generate_tasks(int(self.task_config["initial_tasks"])))
        if r.random() < self.task_config["new_task_chance"]:
            Logger.info("world","New task generated")
            self.tasks.extend(self.generate_tasks())

        # update tick
        self.tick += 1

    def all_tasks_complete(self):
        for task in self.tasks:
            if not task.completed:
                return False
        return True

    def generate_tasks(self, amount=1):
        tasks = []
        for index in range(amount):
            new_task = Task(self)
            self.max_possible_score += new_task.score
            tasks.append(new_task)
        return tasks

    # =============== # 
    # adding entities #
    # =============== # 

    def add_actor(self, node):
        return Actor(self, node)

    def add_resource(self, location, colour):
        return Resource(self, location, colour)

    def add_mine(self, node, colour):
        return Mine(self, node, colour)

    def add_site(self, node, task_id):
        return Site(self, node, task_id)

    def add_building(self, node, building_type):
        return Building(self, node, building_type)

    # =============== # 
    # setters/getters #
    # =============== # 

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

    def get_by_id(self, entity_id, target_actors=None, entity_type=None, target_node=None):
        if target_actors is not None:
            visible_world = self.get_world_info(target_actors=target_actors)
            if entity_id not in visible_world["actors"] and entity_id not in visible_world["sites"] and \
                    entity_id not in visible_world["buildings"] and entity_id not in visible_world["edges"] and \
                    entity_id not in visible_world["mines"] and entity_id not in visible_world["nodes"] and \
                    entity_id not in visible_world["resources"] and entity_id not in visible_world["tasks"] and \
                    entity_id not in visible_world["commands"]:
                return None
        if target_node is None:
            target_node = self.nodes
        else:
            target_node = [target_node]

        if entity_type == "Command" or entity_type is None:
            for command in self.all_commands:
                if command.id == entity_id:
                    return command
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
            for task in node.tasks:
                if task.id == entity_id and (entity_type == "Task" or entity_type is None):
                    return task
        return None

    def get_field(self, entity_id, field, target_actors=None, entity_type=None, target_node=None):
        entity = self.get_by_id(entity_id, target_actors=target_actors, entity_type=entity_type, target_node=target_node)
        return None if entity is None else entity.fields.get(field)
