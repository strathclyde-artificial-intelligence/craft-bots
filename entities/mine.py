class Mine:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.progress = 0
        self.id = self.world.get_new_id()

        self.node.append_mine(self)

        self.fields = {"node": self.node.id, "colour": self.colour, "id": self.id, "progress": self.progress}

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
        self.set_progress(0)
        self.world.add_resource(self.node, self.colour)

    def dig(self):
        digging_progress = self.world.modifiers["MINE_SPEED"] * \
                           ((1 + self.world.modifiers["ORANGE_BUILDING_MODIFIER_STRENGTH"])
                            ** self.world.building_modifiers[1])

        # If mine is red, ensure that it is within red mining intervals
        if self.colour == 0:
            index = 0
            bad_time = True
            while index < self.world.modifiers["RED_COLLECTION_INTERVALS"].__len__():
                if self.world.modifiers["RED_COLLECTION_INTERVALS"][index] <= self.world.tick % \
                        self.world.modifiers["CYCLE_LENGTH"] <= \
                        self.world.modifiers["RED_COLLECTION_INTERVALS"][index + 1]:
                    self.set_progress(self.progress + digging_progress)
                    bad_time = False
                    break
                index += 2
            if bad_time:
                return False

        # If mine is orange, make sure 2+ actors are currently mining
        elif self.colour == 2:
            num_of_miners = 0
            for actor in self.node.actors:
                if actor.target == self:
                    num_of_miners += 1
            if num_of_miners >= self.world.modifiers["ORANGE_ACTORS_TO_MINE"]:
                self.set_progress(self.progress + digging_progress)
            else:
                return False

        # If mine is blue, slow down mining speed
        elif self.colour == 1:
            self.set_progress(self.progress + (digging_progress / self.world.modifiers["BLUE_EXTRA_EFFORT"]))
        else:
            self.set_progress(self.progress + digging_progress)

        # Check if mining yields resources, and stop mining
        if self.progress >= self.world.modifiers["MINE_EFFORT"]:
            self.provide()
            self.ignore_me()

    # Make all actors mining at this mine stop
    def ignore_me(self):
        for actor in self.node.actors:
            if actor.target == self:
                actor.go_idle()

    def set_progress(self, progress):
        self.progress = progress
        self.fields.__setitem__("progress", progress)
