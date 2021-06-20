class Building:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.id = self.world.get_new_id()

        self.node.append_building(self)
        
        if colour == 4:
            self.deposited_resources = [0, 0, 0, 0, 0]
            self.needed_resources = self.world.modifiers["NEW_ACTOR_RESOURCES"]
            self.progress = 0
            self.fields = {"node": self.node.id, "colour": self.colour, "id": self.id,
                           "deposited_resources": self.deposited_resources,
                           "needed_resources": self.needed_resources, "progress": self.progress}
        else:
            self.fields = {"node": self.node.id, "colour": self.colour, "id": self.id}

        if self.colour <= 3:
            self.world.building_modifiers[self.colour] += 1

    def __repr__(self):
        return "Building(" + str(self.id) + ", " + self.world.get_colour_string(self.colour) + ", " + str(
            self.node) + ")"

    def __str__(self):
        return self.__repr__()

    def deposit_resources(self, resource):
        if self.colour == 4:
            if resource.location == self.node or resource.location.node == self.node:
                if self.deposited_resources[resource.colour] < self.needed_resources[resource.colour]:
                    resource.set_used(True)
                    self.deposited_resources[resource.colour] += 1
                    self.fields.__setitem__("deposited_resources", self.deposited_resources)
                    resource.location.remove_resource(resource)
                    resource.set_used(True)
                    return True
        return False

    def build(self):
        if self.colour == 4:
            building_progress = self.world.modifiers["BUILD_SPEED"] * (1.05 ** self.world.building_modifiers[2])
            max_progress = sum(self.deposited_resources) / sum(self.needed_resources) * \
                           self.world.modifiers["BUILD_EFFORT"]
            self.set_progress(min(self.progress + building_progress, max_progress))

            if self.progress == max_progress:
                for actor in self.node.actors:
                    if actor.target == self:
                        actor.go_idle()
            if self.progress >= self.world.modifiers["BUILD_EFFORT"]:
                self.world.add_actor(self.node)
                self.ignore_me()

    def max_progress(self):
        if self.colour == 4:
            return sum(self.deposited_resources) / sum(self.needed_resources) * self.world.modifiers["BUILD_EFFORT"]
        return False

    def ignore_me(self):
        if self.colour == 4:
            for actor in self.node.actors:
                if actor.target == self:
                    actor.go_idle()

    def set_progress(self, progress):
        if self.colour == 4:
            self.progress = progress
            self.fields.__setitem__("progress", progress)
