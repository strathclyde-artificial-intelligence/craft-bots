import random as r


class Actor:
    """
    States:
    0 - Idle
    1 - Moving
    2 - Mining
    3 - Building
    """
    def __init__(self, world, node):
        self.world = world
        self.node = node
        self.node.actors.append(self)
        self.state = 0
        self.progress = -1
        self.target = None
        self.resources = []

    def warp_to(self, target_node):
        moved = False
        index = 0
        while not moved:
            if index == self.node.edges.__len__():
                return False
            if self.node.edges[index].connects(target_node):
                self.node.actors.remove(self)
                self.node = target_node
                self.node.actors.append(self)
                return True
            index += 1

    def warp_rand(self):
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            self.warp_to(target_edge.node_b)
        else:
            self.warp_to(target_edge.node_a)

    def travel_to(self, target_node):
        if self.state:
            # print("Error: Must be idle to begin travelling to another node!")
            return False
        moved = False
        index = 0
        while not moved:
            if index == self.node.edges.__len__():
                print("Error: Could not find connected edge")
                return False
            if self.node.edges[index].connects(target_node):
                self.target = (self.node.edges[index], target_node)
                self.state = 1
                self.progress = 0
                return True
            index += 1

    def travel_rand(self):
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            self.travel_to(target_edge.node_b)
        else:
            self.travel_to(target_edge.node_a)

    def update(self):
        if self.state == 1:
            self.progress += self.world.modifiers["ACTOR_SPEED"]
            if self.target[0].length() <= self.progress:
                self.node.actors.remove(self)
                self.node = self.target[1]
                self.node.actors.append(self)
                self.state = 0
                self.progress = -1
                self.target = None
        if self.state == 2:
            self.target.mine()
        if self.state == 3:
            self.target.build()

    def pick_up_resource(self, resource):
        if self.state == 0 and resource.location is self.node:
            if resource.colour == 3 and self.resources or self.resources and self.resources[0].colour == 3:
                print("can hold one black and nothing else")
                return False
            resource.location = self
            self.resources.append(resource)
            self.node.resources.remove(resource)
            return True
        return False

    def drop_resource(self, resource):
        if self.state == 0 and self.resources.__contains__(resource):
            resource.location = self.node
            self.resources.remove(resource)
            self.node.resources.append(resource)
            return True
        return False

    def drop_everything(self):
        if self.state == 0:
            for resource in self.resources:
                resource.location = self.node
                self.resources.remove(resource)
                self.node.resources.append(resource)
            return True
        return False

    def mine_at(self, mine):
        if not self.state and mine.node == self.node:
            self.state = 2
            self.target = mine
            self.progress = 0

    def start_site(self, colour):
        if not self.state:
            self.world.add_site(self.node, colour)

    def build_at(self, site):
        if not self.state and self.node == site.node:
            self.state = 3
            self.target = site

    def deposit(self, site, resource):
        if self.resources.__contains__(resource):
            return site.deposit_resources(resource)
