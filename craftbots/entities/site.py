import numpy.random as nr
import random as r
from craftbots.entities.building import Building
from craftbots.log_manager import Logger


class Site:

    def __init__(self, world, node, task_id=None):
        """
        A site in the craftbots simulation. It allows actors to deposit resources and construct at it to create
        buildings. These buildings provide bonuses to the actors

        :param world: the world in which the site exists
        :param node: the node the site is located at
        :param building_type: the colour of the site (this will produce a building of that type)
        :param target_task: the task entity that is chosen if the site is purple. If it is None then one at the sites node is chosen at random (if a free task is available)
        """
        self.world = world
        self.node = node
        self.building_type = Building.BUILDING_TASK
        self.deposited_resources = [0, 0, 0, 0, 0]
        self.progress = 0
        self.id = self.world.get_new_id()
        self.needed_resources = []
        if self.building_type == Building.BUILDING_TASK:
            if task_id is None:
                for task in self.world.tasks:
                    if task.node == self.node and task.project is None:
                        task.set_project(self)
                        self.task = task
                        self.needed_resources = task.needed_resources
                        break
            else:
                target_task = self.world.get_by_id(task_id, target_node=self.node)
                if target_task.linked_site is None and target_task.node == self.node:
                    target_task.set_project(self)
                    self.task = target_task
                    self.needed_resources = target_task.needed_resources
        else:
            resources_key = Building.BUILDING_NAMES[self.building_type] + "_building_resources"
            self.needed_resources = self.world.building_config[resources_key]

        # If needed resources cannot be found, then do not inform anything that this Site exists
        if self.needed_resources:
            self.node.append_site(self)
            self.fields = {"node": self.node.id, "building_type": self.building_type,
                           "deposited_resources": self.deposited_resources, "needed_resources": self.needed_resources,
                           "progress": self.progress, "max_progress": self.max_progress(),
                           "needed_effort": self.world.building_config["build_effort"] * sum(self.needed_resources),
                           "id": self.id}

    def __repr__(self):
        return "Site(" + str(self.id) + ", " + str(self.node) + ")"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, Site):
            if self.node == other.node and self.building_type == other.building_type:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def deposit_resources(self, resource):
        """
        Deposit a resource into the site. This consumes the resource.
        :param resource: The resource to be added
        :return: True if the resource was deposited and false if it wasn't
        """
        if resource.location == self.node or resource.location.node == self.node:
            if self.deposited_resources[resource.colour] < self.needed_resources[resource.colour]:
                resource.set_used(True)
                self.deposited_resources[resource.colour] += 1
                self.fields.__setitem__("deposited_resources", self.deposited_resources)
                resource.location.remove_resource(resource)
                resource.set_used(True)
                return True
        return False

    def construct(self, deviation):
        """
        Called to provide progress on the construction of a building. This can only be done up to a certain point based
        on how many resources have been deposited so far.
        """

        if self.world.nondeterminism_config["construction_non_deterministic"] \
                and r.random() < self.world.nondeterminism_config["construction_non_deterministic"]:
            Logger.info("site" + str(self.id), "Constructing failed.")
            self.fail_construction()
            return

        build_speed = self.world.actor_config["build_speed"]
        if self.world.temporal_config["build_duration_uncertain"]:
            deviation = nr.normal(deviation, self.world.temporal_config["build_per_tick_stddev"])
            deviation = max(self.world.temporal_config["build_deviation_bounds"][0] + build_speed, deviation)
            deviation = min(self.world.temporal_config["build_deviation_bounds"][1] + build_speed, deviation)
            build_speed = deviation

        building_progress = build_speed * ((1 + self.world.building_config["constructing_speed_building_modifier_strength"]) **
                                           self.world.building_modifiers[Building.BUILDING_CONSTRUCTION])

        max_progress = self.max_progress()
        self.set_progress(min(self.progress + building_progress, max_progress))

        if self.progress == max_progress:
            for actor in self.node.actors:
                if actor.target == self:
                    actor.go_idle()
                    
        if self.progress >= self.world.building_config["build_effort"] * sum(self.needed_resources):
            if self.world.nondeterminism_config["construction_completion_non_deterministic"] \
                    and r.random() < self.world.nondeterminism_config["construction_completion_non_deterministic"]:
                Logger.info("site" + str(self.id), "Construction completion failed.")
                self.fail_construction()
                return
            new_building = self.world.add_building(self.node, self.building_type)
            self.node.remove_site(self)
            self.ignore_me()
            if self.building_type == Building.BUILDING_TASK:
                self.task.set_project(new_building)
                self.task.complete_task()
            del self

    def fail_construction(self):

        penalty = r.uniform(self.world.nondeterminism_config["construction_failure_penalty"][0],
                            self.world.nondeterminism_config["construction_failure_penalty"][1])
        resources_lost = int(len(self.deposited_resources) * penalty)
        resources_lost = min(len(self.deposited_resources), max(0,resources_lost))

        for _ in range(resources_lost):
            self.deposited_resources[self.deposited_resources.index(max(self.deposited_resources))] -= 1
            self.set_progress(max(self.progress - self.world.building_config["build_effort"], 0))

        self.ignore_me()

    def max_progress(self):
        """
        Gets the currently possible maximum progress based on how many resources have been deposited

        :return: The maximum progress
        """
        return self.world.building_config["build_effort"] * sum(self.needed_resources) * sum(self.deposited_resources) / sum(self.needed_resources)

    def ignore_me(self):
        """
        Gets all the actors that have targeted the building and sets them to become idle
        """
        for actor in self.node.actors:
            if actor.target == self:
                actor.go_idle()

    def set_progress(self, progress):
        """
        Sets the progress of the site and keeps track of this in the sites fields.
        :param progress:
        """
        self.progress = progress
        self.fields.__setitem__("progress", progress)
