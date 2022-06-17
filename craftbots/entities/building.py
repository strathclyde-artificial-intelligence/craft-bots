import numpy.random as nr
import random as r
import math as m

from craftbots.log_manager import Logger

class Building:

    BUILDING_TASK         = 0
    BUILDING_SPEED        = 1
    BUILDING_MINE         = 2
    BUILDING_CONSTRUCTION = 3
    BUILDING_INVENTORY    = 4
    BUILDING_ACTOR_SPAWN  = 5

    BUILDING_NAMES = {
        0: "task",
        1: "actor_speed",
        2: "mining_speed",
        3: "constructing_speed",
        4: "inventory_size",
        5: "actor_spawn"
    }

    def __init__(self, world, node, building_type=0):
        """
        A completed building in the craftbots simulation. It takes a certain amount of work and resources gathered into
        a site by actors to create a building. Different buildings require different amount of resources. Each type of
        building will provide a different positive effect for the actors in the simulation.

        :param world: the world the in which the building exists
        :param node: the node the building is located at
        :param building_type: the colour of the building (this determines the effect it provides)
        """
        self.world = world
        self.node = node
        self.building_type = building_type
        self.id = self.world.get_new_id()

        self.node.append_building(self)

        # If the building is green then create other fields needed to keep track of new actor construction
        if building_type == Building.BUILDING_ACTOR_SPAWN:
            self.deposited_resources = [0, 0, 0, 0, 0]
            self.needed_resources = self.world.building_config["new_actor_resources"]
            self.progress = 0
            self.fields = {"node": self.node.id, "building_type": self.building_type, "id": self.id,
                           "deposited_resources": self.deposited_resources,
                           "needed_resources": self.needed_resources, "progress": self.progress}
        else:
            self.fields = {"node": self.node.id, "building_type": self.building_type, "id": self.id}

        # Keep track of the bonuses the building provides in the simulation
        if self.building_type != Building.BUILDING_TASK:
            max_var_name = Building.BUILDING_NAMES[self.building_type] + "_building_maximum"
            if self.world.building_config[max_var_name] > 0:
                # Limited positive capacity for this kind of building
                self.world.building_modifiers[self.building_type] = min(self.world.building_config[max_var_name], self.world.building_modifiers[self.building_type] + 1)
            elif self.world.building_config[max_var_name] == -1:
                # Unlimited capacity for this kind of building
                self.world.building_modifiers[self.building_type] += 1

    def __repr__(self):
        return "Building(" + str(self.id) + ", " + Building.BUILDING_NAMES[self.building_type] + ", " + str(self.node) + ")"

    def __str__(self):
        return self.__repr__()

    def deposit_resources(self, resource):
        """
        Deposit a resource into the building if it is green. This consumes the resource.

        :param resource: The resource to be added
        :return: True if the resource was deposited and false if it wasn't
        """
        if self.building_type == Building.BUILDING_ACTOR_SPAWN:
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
        Called to provide progress on the construction of a new bot. This can only be done up to a certain point based
        on how many resources have been deposited so far.
        """
        if self.world.nondeterminism_config["construction_non_deterministic"] and r.random() < self.world.nondeterminism_config["construction_non_deterministic"]:
            Logger.info("building" + str(self.id), "Constructing failed.")
            self.fail_construction()
            return

        if self.building_type == Building.BUILDING_ACTOR_SPAWN:

            build_speed = self.world.actor_config["build_speed"]
            if self.world.temporal_config["build_duration_uncertain"]:
                deviation = nr.normal(deviation, self.world.temporal_config["build_per_tick_stddev"])
                deviation = max(self.world.temporal_config["build_deviation_bounds"][0], deviation)
                deviation = min(self.world.temporal_config["build_deviation_bounds"][1], deviation)
                build_speed = build_speed + deviation

            building_progress = build_speed * (
                        (1 + self.world.building_config["constructing_speed_building_modifier_strength"]) **
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
                    Logger.info("building" + str(self.id), "Agent construction completion failed.")
                    self.fail_construction()
                    return
                self.world.add_actor(self.node)
                self.ignore_me()

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
        Gets the currently possible maximum progress based on how many resources have been deposited, if the building is
        green

        :return: The maximum progress, or False if the building is not green
        """
        if self.building_type == Building.BUILDING_ACTOR_SPAWN:
            return sum(self.deposited_resources) / sum(self.needed_resources) * self.world.building_config["build_effort"]
        return False

    def ignore_me(self):
        """
        Gets all the actors that have targeted the building and sets them to become idle
        """
        if self.building_type == Building.BUILDING_ACTOR_SPAWN:
            for actor in self.node.actors:
                if actor.target == self:
                    actor.go_idle()

    def set_progress(self, progress):
        """
        Sets the progress of the new actor in the building and keeps track of this in the Buildings fields.

        :param progress:
        """
        if self.building_type == Building.BUILDING_ACTOR_SPAWN:
            self.progress = progress
            self.fields.__setitem__("progress", progress)
