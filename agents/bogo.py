import random
from api import agent_api

"""
Bogo is an agent for the craft bots simulation that only makes (semi)-random moves. 
They are by no means efficient but in most circumstances, Bogo will complete the tasks of 
the simulation.

Bogo's name is a reference to bogosort:
https://en.wikipedia.org/wiki/Bogosort
"""


class Bogo:
    def __init__(self):
        self.api = None
        self.results = []
        self.thinking = False
        self.world_info = None
        self.actors = []
        self.tasks = []
        self.orange_ticks = []

    def receive_results(self, results):
        print(results)
        self.results.extend(results)


    def find_result_by_id(self, result_id):
        for result in self.results:
            if result[0] == result_id:
                return result
        return None

    def at_task_node(self, node):
        for task in self.tasks:
            if (not task["complete"]) and task["node"] == node:
                return True
        return False

    def get_next_commands(self):
        self.api: agent_api.AgentAPI

        if not self.actors:
            for actor_id in self.world_info["actors"]:
                self.actors.append(self.world_info["actors"][actor_id])
                self.orange_ticks.append(0)
        elif self.actors.__len__() < self.world_info["actors"].__len__():
            self.actors = []
            self.orange_ticks = []
            for actor_id in self.world_info["actors"]:
                self.actors.append(self.world_info["actors"][actor_id])
                self.orange_ticks.append(0)

        if not self.tasks:
            for task_id in self.world_info["tasks"]:
                self.tasks.append(self.world_info["tasks"][task_id])

        actor_index = 0
        for actor in self.actors:
            if actor["state"] == 0:
                for task in self.tasks:
                    if (not task["complete"]) and task["node"] == actor["node"]:

                        # Check if there are enough buildings / sites to complete the task
                        num_of_sites_and_builds = 0
                        for site_id in self.api.get_field(actor["node"], "sites"):
                            if self.api.get_field(site_id, "colour") == task["colour"]:
                                num_of_sites_and_builds += 1
                        for building_id in self.api.get_field(actor["node"], "buildings"):
                            if self.api.get_field(building_id, "colour") == task["colour"]:
                                num_of_sites_and_builds += 1
                        if task["amount"] > num_of_sites_and_builds:
                            self.api.start_site(actor["id"], task["colour"])

                        # Deposit resources if needed and possible, and then build
                        for resource_id in actor["resources"]:
                            resource_colour = self.api.get_field(resource_id, "colour", entity_type="Resource")
                            for site_id in self.api.get_field(actor["node"], "sites"):
                                site = self.api.get_by_id(site_id)
                                if site["deposited_resources"][resource_colour] < \
                                        site["needed_resources"][resource_colour]:
                                    self.api.deposit_resources(actor["id"], site_id, resource_id)
                                    self.api.construct_at(actor["id"], site_id)

                # If at a node with a green buildings and holding resources needed to build a new actor, then do so.
                for building_id in self.api.get_field(actor["node"], "buildings"):
                    if self.api.get_field(building_id, "colour") == 4:
                        for resource_id in actor["resources"]:
                            resource_colour = self.api.get_field(resource_id, "colour", entity_type="Resource")
                            building = self.api.get_by_id(building_id)
                            if building["deposited_resources"][resource_colour] < \
                                    building["needed_resources"][resource_colour]:
                                self.api.deposit_resources(actor["id"], building_id, resource_id)
                                self.api.construct_at(actor["id"], building_id)

                # If at a node with resources, pick them up if possible, if not, then drop currently held resources and
                # pick up resources, then move to a random node.
                if self.api.get_field(actor["node"], "resources"):
                    target_resource_id = self.api.get_field(actor["node"], "resources")[0]
                    actor_resource_id = self.api.get_field(actor["id"], "resources")
                    if actor_resource_id:
                        actor_resource_id = actor_resource_id[0]
                    else:
                        actor_resource_id = -1
                    if actor["resources"] and self.api.get_field(actor_resource_id, "colour") == 3:
                        self.api.drop_all_resources(actor["id"])
                        self.api.pick_up_resource(actor["id"], self.world_info["nodes"][actor["node"]]["resources"][0])
                        self.api.move_rand(actor["id"])
                    elif self.api.get_field(target_resource_id, "colour") == 3:
                        self.api.drop_all_resources(actor["id"])
                        self.api.pick_up_resource(actor["id"], self.world_info["nodes"][actor["node"]]["resources"][0])
                        self.api.move_rand(actor["id"])
                    else:
                        self.api.pick_up_resource(actor["id"], target_resource_id)
                        self.api.move_rand(actor["id"])

                # If at a node with a mine, mine at the mine
                if self.api.get_field(actor["node"], "mines"):
                    target_mine = self.api.get_field(actor["node"], "mines")[random.randint(0, self.api.get_field(actor["node"], "mines").__len__() - 1)]
                    self.api.dig_at(actor["id"], target_mine)
                    if self.world_info["mines"][target_mine]["colour"] == 2:
                        self.orange_ticks[actor_index] = self.world_info["tick"]

                # Move randomly if there is nothing else to do
                self.api.move_rand(actor["id"])

            # If waiting at an orange mine for too long, ignore it and move on
            elif actor["state"] == 2:
                actor_target_id = actor["target"]
                if actor["state"] == 2 and self.api.get_field(actor_target_id, "colour") == 2 and \
                        self.api.get_field(actor_target_id, "progress") == 0:
                    if self.orange_ticks[actor_index] + 1200 < self.world_info["tick"]:
                        self.api.cancel_action(actor["id"])
                        self.api.move_rand(actor["id"])
            actor_index += 1
        self.thinking = False


