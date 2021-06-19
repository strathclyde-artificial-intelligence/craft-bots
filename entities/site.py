class Site:
    
    NEEDED_RESOURCES = [
        [0, 2, 0, 2, 2],
        [1, 4, 1, 0, 0],
        [1, 3, 0, 0, 1],
        [4, 2, 0, 2, 0],
        [0, 0, 2, 2, 3]
    ]
    
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.deposited_resources = [0, 0, 0, 0, 0]
        self.needed_resources = Site.NEEDED_RESOURCES[colour]
        self.progress = 0
        self.id = self.world.get_new_id()

        self.node.append_site(self)
        
        self.fields = {"node": self.node.id, "colour": self.colour, "deposited_resources": self.deposited_resources,
                       "needed_resources": self.needed_resources, "progress": self.progress, "id": self.id}

    def __repr__(self):
        return "Site(" + str(self.id) + ", " + str(self.node) + ")"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, Site):
            if self.node == other.node and self.colour == other.colour:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def deposit_resources(self, resource):
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
        max_progress = sum(self.deposited_resources) / sum(self.needed_resources) * self.world.modifiers["BUILD_EFFORT"]
        self.set_progress(min(self.progress + self.world.modifiers["BUILD_SPEED"], max_progress))

        if self.progress == max_progress:
            for actor in self.node.actors:
                if actor.target == self:
                    actor.go_idle()
        if self.progress >= self.world.modifiers["BUILD_EFFORT"]:
            self.world.add_building(self.node, self.colour)
            self.node.remove_site(self)
            self.ignore_me()
            del self

    def max_progress(self):
        return sum(self.deposited_resources) / sum(self.needed_resources) * self.world.modifiers["BUILD_EFFORT"]

    def ignore_me(self):
        for actor in self.node.actors:
            if actor.target == self:
                actor.go_idle()

    def set_progress(self, progress):
        self.progress = progress
        self.fields.__setitem__("progress", progress)
