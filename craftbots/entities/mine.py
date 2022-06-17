import numpy.random as nr
import random as r

from craftbots.entities.building import Building
from craftbots.log_manager import Logger


class Mine:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.progress = 0
        self.id = self.world.get_new_id()

        self.node.append_mine(self)

        self.fields = {"node": self.node.id, "colour": self.colour, "id": self.id, "progress": self.progress, "max_progress": self.world.resource_config["mine_effort"]}

    def __repr__(self):
        return "Mine(" + str(self.id) + ", " + self.world.get_colour_string(self.colour) + ", " + str(
            self.node) + ")"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return isinstance(other, Mine) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def provide(self):
        """
        Creates a resource at the node the mine is at, and resets the progress
        """
        self.set_progress(0)
        self.world.add_resource(self.node, self.colour)

    def dig(self, deviation):
        """
        Called when an actor digs at this mine, checking if the requirements (if any) are met before progress is made.

        :return: True if digging can begin and false otherwise.
        """

        if self.world.nondeterminism_config["digging_non_deterministic"] and r.random() < self.world.nondeterminism_config["digging_non_deterministic"]:
            Logger.info("mine" + str(self.id), "Mining failed.")
            self.set_progress(0)
            self.ignore_me()
            return False

        dig_speed = self.world.actor_config["dig_speed"]
        if self.world.temporal_config["mine_duration_uncertain"]:
            deviation = nr.normal(deviation, self.world.temporal_config["mine_per_tick_stddev"])
            deviation = max(self.world.temporal_config["mine_deviation_bounds"][0], deviation)
            deviation = min(self.world.temporal_config["mine_deviation_bounds"][1], deviation)
            dig_speed = dig_speed + deviation

        digging_progress = dig_speed * ((1 + self.world.building_config["mining_speed_building_modifier_strength"]) **
                                        self.world.building_modifiers[Building.BUILDING_MINE])

        # If mine is red, ensure that it is within red mining intervals
        # TODO fix resource colour references (and mine) so that they are human readable.
        if self.colour == 0:
            time_now = self.world.tick % self.world.resource_config["cycle_length"]
            if self.world.resource_config["red_collection_intervals"][0] < time_now < self.world.resource_config["red_collection_intervals"][1]:
                self.set_progress(self.progress + digging_progress)
            else: return False

        # If mine is orange, make sure 2+ actors are currently mining
        # TODO fix resource colour references (and mine) so that they are human readable.
        elif self.colour == 2:
            num_of_miners = 0
            num_of_miners = len([ actor for actor in self.node.actors if actor.target == self])
            if num_of_miners >= self.world.resource_config["orange_actors_to_mine"]:
                self.set_progress(self.progress + digging_progress)
            else: return False

        # If mine is blue, slow down mining speed
        # TODO fix resource colour references (and mine) so that they are human readable.
        elif self.colour == 1:
            self.set_progress(self.progress + (digging_progress / self.world.resource_config["blue_extra_effort"]))

        # Otherwise increase progress
        else: self.set_progress(self.progress + digging_progress)

        # Check if mining yields resources, and stop mining
        if self.progress >= self.world.resource_config["mine_effort"]:
            if self.world.nondeterminism_config["digging_completion_non_deterministic"] and \
                    r.random() < self.world.nondeterminism_config["digging_completion_non_deterministic"]:
                Logger.info("mine" + str(self.id), "Mining completion failed.")
                self.set_progress(0)
                self.ignore_me()
                return False
            self.provide()
            self.ignore_me()
            # TODO check if FALSE should be returned

        return True

    def ignore_me(self):
        """
        Gets all the actors that have targeted the mine and sets them to become idle
        """
        for actor in self.node.actors:
            if actor.target == self:
                actor.go_idle()

    def set_progress(self, progress):
        """
        Sets the progress of the mine and keeps track of this in the mines fields

        :param progress:
        """
        self.progress = progress
        self.fields.__setitem__("progress", progress)
