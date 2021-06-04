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
        """
        The actor of the world. With this object, your agent will be able to manipulate the world.
        The actor lets the node it should be in know that it exists, so it can be tracked. The actor also has
        several states which indicate what it is currently doing. It initially starts idle (0)
        :param world: The world in which the actor should exist
        :param node: The node in which to spawn the actor. If none is given then the actor spawns at the first node
        created in the world.
        """
        self.world = world
        self.node = node
        self.node.actors.append(self)
        self.state = 0
        self.progress = -1
        self.id = self.world.get_new_id()
        self.target = None
        self.resources = []

    def __repr__(self):
        return "Actor(" + str(self.id) + ")"

    def warp_to(self, target_node):
        """
        "Warps" the actor instantly to the selected node. This method is for testing purposes only and should not be
        used in a competition setting.
        :param target_node: Node object to warp the actor to. Must share an edge with node the actor is currently in
        :return: True if successful and False otherwise
        """
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
        """
        "Warps" the actor instantly to a random node that shares an edge with its current node.
        This method is for testing purposes only and should not be used in a competition setting.
        :return: True if successful and False otherwise
        """
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            return self.warp_to(target_edge.node_b)
        else:
            return self.warp_to(target_edge.node_a)

    def travel_to(self, target_node):
        """
        Tells the actor to begin moving to the targeted node. Whenever the actor is updated via update(), it will make
        a certain amount of progress based on the ACTOR_SPEED modifier. Actor must be idle before beginning to travel.
        :param target_node: Node object to send the actor to. Must share an edge with node the actor is currently in
        :return: True if successful and False otherwise
        """
        if self.state:
            # print("Error: Must be idle to begin travelling to another node!")
            return False
        node_index = self.node.shares_edge_with(target_node)
        if node_index != -1:
            self.target = (self.node.edges[node_index], target_node)
            self.state = 1
            self.progress = 0
            return True
        return False

    def travel_rand(self):
        """
        Tells the actor to begin travelling towards a random node that shares an edge with the node it is currently in
        :return: True if successful and False otherwise
        """
        target_edge = self.node.edges[r.randint(0, self.node.edges.__len__() - 1)]
        if target_edge.node_a == self.node:
            return self.travel_to(target_edge.node_b)
        else:
            return self.travel_to(target_edge.node_a)

    def update(self):
        """
        Called to simulate the actor performing actions for 1 tick. Depends on what the actor is currently doing via the
        state.
        """
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
        """
        Has the actor attempt to pick up the resource and place it in its inventory. Resource must be in the same node
        as the actor, and actor must be idle. If the resource is black, the actor must have an empty inventory.
        Otherwise, the actor must not already be holding a black resource.
        :param resource: Resource object to be picked up
        :return: True if successful and False otherwise
        """
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
        """
        Has the actor drop the resource into the node it is currently in. Actor must be idle to do so, and the resource
        should be inside the actor's inventory.
        :param resource: Resource object to be dropped
        :return: True if successful and False otherwise
        """
        if self.state == 0 and self.resources.__contains__(resource):
            resource.location = self.node
            self.resources.remove(resource)
            self.node.resources.append(resource)
            return True
        return False

    def drop_everything(self):
        """
        Has the actor drop everything in it's inventory into the actor's current node, leaving it holding nothing.
        Actor must be idle to do this
        :return: True if successful and False otherwise
        """
        if self.state == 0:
            for resource in self.resources:
                resource.location = self.node
                self.resources.remove(resource)
                self.node.resources.append(resource)
            return True
        return False

    def mine_at(self, mine):
        """
        Tells the actor to start mining at the selected mine. Actor must be idle to start mining and the mine should
        be at the same node as the actor. When the actor is updated via update(), the actor makes progress towards
        mining.
        :param mine: The mine object the actor should start mining at.
        :return: True if successful and otherwise False
        """
        if not self.state and mine.node == self.node:
            self.state = 2
            self.target = mine
            return True
        return False

    def start_site(self, colour):
        """
        Has the actor create a new "construction" site to create a building. Site is created in the same node as the
        actor. Actor must be idle to do this.
        :param colour: The colour of the construction site to make
        :return True if successful and False otherwise
        """
        if not self.state:
            self.world.add_site(self.node, colour)
            return True
        return False

    def build_at(self, site):
        """
        Tells the actor to begin building at the construction site. The site must be in the same node as the actor, and
        the actor must be idle. The actor will automatically stop building when it cannot build anymore due to a lack of
        materials or if the building is complete. When the actor is updated via update(), the actor makes progress
        towards building
        :param site: The site the actor should start building at.
        :return: True if successful and otherwise False
        """
        if not self.state and self.node == site.node:
            self.state = 3
            self.target = site
            return True
        return False

    def deposit(self, site, resource):
        """
        Tells the actor to deposit a resource object into a construction site. The site must be in the same node as the
        actor, the actor must be idle, the resource should be in the actors inventory or in the same node as the site
        and the actor, and the site should still need that type of resource.
        :param site: The site in which to drop off the resource
        :param resource: The resource to drop off
        :return: True if successful and False otherwise
        """
        return site.deposit_resources(resource)
