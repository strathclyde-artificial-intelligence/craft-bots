class Site:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.deposited_resources = [0, 0, 0, 0, 0]
        self.needed_resources = self.get_needed_resources()
        self.progress = 0

        self.node.sites.append(self)

    def __repr__(self):
        return "Site(" + str(self.node.x) + ", " + str(self.node.y) + ")"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, Site):
            if self.node == other.node and self.colour == other.colour:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_needed_resources(self):
        if self.colour == 0:
            return [5, 0, 0, 0, 0]
        elif self.colour == 1:
            return [0, 5, 0, 0, 0]
        elif self.colour == 2:
            return [0, 0, 5, 0, 0]
        elif self.colour == 3:
            return [0, 0, 0, 5, 0]
        elif self.colour == 4:
            return [0, 0, 0, 0, 5]

    def deposit_resources(self, resource):
        if resource.location == self.node or resource.location.node == self.node:
            if self.deposited_resources[resource.colour] < self.needed_resources[resource.colour]:
                resource.used = True
                self.deposited_resources[resource.colour] += 1
                resource.location.resources.remove(resource)
                self.world.resources.remove(resource)
                resource.used = True
                return True
        return False

    def build(self):
        max_progress = sum(self.deposited_resources) / sum(self.needed_resources) * self.world.modifiers["BUILD_EFFORT"]
        self.progress = min(self.progress + self.world.modifiers["BUILD_SPEED"], max_progress)

        if self.progress == max_progress:
            for actor in self.node.actors:
                if actor.target == self:
                    actor.state = 0
                    actor.target = None
        if self.progress >= self.world.modifiers["BUILD_EFFORT"]:
            self.world.add_building(self.node, self.colour)
            # for actor in self.node.actors:
            #     if actor.target == self:
            #         actor.state = 0
            #         actor.target = None
            self.node.sites.remove(self)
            self.world.sites.remove(self)
            del self

    def max_progress(self):
        return sum(self.deposited_resources) / sum(self.needed_resources) * self.world.modifiers["BUILD_EFFORT"]
