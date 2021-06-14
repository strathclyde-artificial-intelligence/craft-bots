import random
import agent_api

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
        self.results.extend(results)
        self.thinking = False

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

        if not self.tasks:
            for task_id in self.world_info["tasks"]:
                self.tasks.append(self.world_info["tasks"][task_id])

        actor_index = 0
        for actor in self.actors:
            if actor["state"] == 0:
                for task in self.tasks:
                    if (not task["complete"]) and task["node"] == actor["node"]:
                        num_of_sites_and_builds = 0
                        for site_id in self.world_info["nodes"][actor["node"]]["sites"]:
                            if self.world_info["sites"][site_id]["colour"] == task["colour"]:
                                num_of_sites_and_builds += 1
                        for building_id in self.world_info["nodes"][actor["node"]]["buildings"]:
                            if self.world_info["buildings"][building_id]["colour"] == task["colour"]:
                                num_of_sites_and_builds += 1
                        for _ in range(task["amount"] - num_of_sites_and_builds):
                            self.api.start_site(actor["id"], task["colour"])
                        for resource_id in actor["resources"]:
                            resource_colour = self.world_info["resources"][resource_id]["colour"]
                            for site_id in self.world_info["nodes"][actor["node"]]["sites"]:
                                site = self.world_info["sites"][site_id]
                                if site["deposited_resources"][resource_colour] < \
                                        site["needed_resources"][resource_colour]:
                                    self.api.deposit_resources(actor["id"], site_id, resource_id)
                                    self.api.build_at(actor["id"], site_id)
                if self.world_info["nodes"][actor["node"]]["resources"]:
                    target_resource_id = self.world_info["nodes"][actor["node"]]["resources"][0]
                    if actor["resources"] and self.world_info["resources"][actor["resources"][0]]["colour"] == 3:
                        self.api.drop_all_resources(actor["id"])
                        self.api.pick_up_resource(actor["id"], self.world_info["nodes"][actor["node"]]["resources"][0])
                        self.api.move_rand(actor["id"])
                    elif self.world_info["resources"][target_resource_id]["colour"] == 3:
                        self.api.drop_all_resources(actor["id"])
                        self.api.pick_up_resource(actor["id"], self.world_info["nodes"][actor["node"]]["resources"][0])
                        self.api.move_rand(actor["id"])
                    else:
                        self.api.pick_up_resource(actor["id"], target_resource_id)
                        self.api.move_rand(actor["id"])
                if self.world_info["nodes"][actor["node"]]["mines"]:
                    target_mine = self.world_info["nodes"][actor["node"]]["mines"][random.randint(0, self.world_info["nodes"][actor["node"]]["mines"].__len__() - 1)]
                    self.api.dig_at(actor["id"], target_mine)
                    if self.world_info["mines"][target_mine]["colour"] == 2:
                        self.orange_ticks[actor_index] = self.world_info["tick"]
                self.api.move_rand(actor["id"])
            elif actor["state"] == 2:
                actor_target_id = actor["target"]
                if actor["state"] == 2 and self.world_info["mines"][actor_target_id]["colour"] == 2 and \
                        self.world_info["mines"][actor_target_id]["progress"] == 0:
                    if self.orange_ticks[actor_index] + 1200 < self.world_info["tick"]:
                        self.api.cancel_action(actor["id"])
                        self.api.move_rand(actor["id"])
            actor_index += 1
        self.api.no_commands()

        """
                    if actor.node.resources:
                        if actor.resources and actor.resources[0].colour == 3:
                            self.api.drop_all_resources(actor.id)
                            self.api.pick_up_resource(actor.id, actor.node.resources[0].id)
                            self.api.move_rand(actor.id)
                            return
                        elif actor.node.resources[0].colour == 3:
                            self.api.drop_all_resources(actor.id)
                            self.api.pick_up_resource(actor.id, actor.node.resources[0].id)
                            self.api.move_rand(actor.id)
                        else:
                            self.api.pick_up_resource(actor.id, actor.node.resources[0].id)
                            self.api.move_rand(actor.id)
                            return
                    if actor.node.mines:
                        target_mine = actor.node.mines[random.randint(0, actor.node.mines.__len__() - 1)]
                        self.api.dig_at(actor.id, target_mine.id)
                        if target_mine.colour == 2:
                            self.orange_ticks[actor_index] = actor.world.tick
                        return
                    self.api.move_rand(actor.id)
                    return
                else:
                    if actor.state == 2 and actor.target.colour == 2 and actor.target.progress == 0:
                        if self.orange_ticks[actor_index] + 1200 < actor.world.tick:
                            self.api.cancel_action(actor.id)
                            self.api.move_rand(actor.id)
                            return
            actor_index += 1
        self.api.no_commands()
        """
