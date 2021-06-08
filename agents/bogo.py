import random
from agents import agent_api

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

    def get_next_commands(self):
        self.api: agent_api.AgentAPI
        if not self.actors:
            self.actors = self.api.get_all_actors()
        elif isinstance(self.actors, int):
            self.actors = self.find_result_by_id(self.actors)[1]
            for _ in self.actors:
                self.orange_ticks.append(0)
        elif not self.tasks:
            self.tasks = self.api.get_tasks()
        elif isinstance(self.tasks, int):
            self.tasks = self.find_result_by_id(self.tasks)[1]
        else:
            actor_index = 0
            for actor in self.actors:
                at_task_node = False
                for task in self.tasks:
                    if task.node == actor.node:
                        at_task_node = True
                if not actor.state:
                    if at_task_node:
                        for task in self.tasks:
                            if (not task.complete()) and task.node == actor.node:
                                num_of_sites_and_builds = 0
                                for site in actor.node.sites:
                                    if site.colour == task.colour:
                                        num_of_sites_and_builds += 1
                                for building in actor.node.buildings:
                                    if building.colour == task.colour:
                                        num_of_sites_and_builds += 1
                                if num_of_sites_and_builds < task.amount:
                                    self.api.start_site(actor.id, task.colour)
                                    return
                                else:
                                    for resource in actor.resources:
                                        for site in actor.node.sites:
                                            if site.deposited_resources[resource.colour] < site.needed_resources[resource.colour]:
                                                self.api.deposit_resources(actor.id, site.id, resource.id)
                                                self.api.build_at(actor.id, site.id)
                                                return
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
                        self.api.mine_at(actor.id, target_mine.id)
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
