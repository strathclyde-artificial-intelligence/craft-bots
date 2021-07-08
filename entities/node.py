class Node:
    def __init__(self, world, x, y):
        """
        A node in the craftbots simulation. Nodes can contain actors, resources, mines, sites, and buildings. They are
        connected to other nodes via edges, which actors can move between.
        :param world: the world in which the node exists.
        :param x: The nodes x position in the world
        :param y: The nodes y position in the world
        """
        self.world = world
        self.x = x
        self.y = y
        self.edges = []
        self.actors = []
        self.resources = []
        self.mines = []
        self.sites = []
        self.buildings = []
        self.tasks = []
        self.id = self.world.get_new_id()
        
        self.fields = {"x": self.x, "y": self.y, "edges": [], "actors": [], "resources": [], "mines": [], "sites": [], 
                       "buildings": [], "tasks": [], "id": self.id}

    def __repr__(self):
        return "Node(" + str(self.id) + ")"

    def __str__(self):
        return "Node(" + str(self.id) + ")"

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def shares_edge_with(self, other_node):
        """
        Returns the index of the edge in the edge field of this node the connects it to the passed in node.
        :param other_node: the other node to be checked
        :return: Index of the edge in the edges field of the Node, or -1 if it is not connected
        """
        for edge in self.edges:
            if edge.connects(other_node):
                return self.edges.index(edge)
        return -1

    def get_adjacent_nodes(self):
        """
        Returns a list of all of the adjacent nodes to the node connected via edges
        :return: List of all of the nodes connected via edges to this node
        """
        nodes = []
        for edge in self.edges:
            nodes.append(edge.get_other_node(self))
        return nodes

    def append_edge(self, edge):
        """
        Adds a edge to the node and keeps its id in the nodes fields
        :param edge: the edge to be added
        """
        self.edges.append(edge)
        self.fields.get("edges").append(edge.id)

    def append_actor(self, actor):
        """
        Adds a actor to the node and keeps its id in the nodes fields
        :param actor: the actor to be added
        """
        self.actors.append(actor)
        self.fields.get("actors").append(actor.id)

    def remove_actor(self, actor):
        """
        Removes the actor at the node and removes its id in the nodes fields
        :param actor: the actor to be removed
        """
        self.actors.remove(actor)
        self.fields.get("actors").remove(actor.id)

    def append_resource(self, resource):
        """
        Adds a resource to the node and keeps its id in the nodes fields
        :param resource: the resource to be added
        """
        self.resources.append(resource)
        self.fields.get("resources").append(resource.id)

    def remove_resource(self, resource):
        """
        Removes the resource at the node and removes its id in the nodes fields
        :param resource: the resource to be removed
        """
        self.resources.remove(resource)
        self.fields.get("resources").remove(resource.id)

    def append_mine(self, mine):
        """
        Adds a mine to the node and keeps its id in the nodes fields
        :param mine: the mine to be added
        """
        self.mines.append(mine)
        self.fields.get("mines").append(mine.id)

    def append_site(self, site):
        """
        Adds a site to the node and keeps its id in the nodes fields
        :param site: the site to be added
        """
        self.sites.append(site)
        self.fields.get("sites").append(site.id)

    def remove_site(self, site):
        """
        Removes the site at the node and removes its id in the nodes fields
        :param site: the site to be removes
        """
        self.sites.remove(site)
        self.fields.get("sites").remove(site.id)

    def append_building(self, building):
        """
        Adds a building to the node and keeps its id in the nodes fields
        :param building: the building to be added
        """
        self.buildings.append(building)
        self.fields.get("buildings").append(building.id)

    def append_task(self, task):
        """
        Adds a task to the node and keeps its id in the nodes fields
        :param task: the task to be added
        """
        self.tasks.append(task)
        self.fields.get("tasks").append(task.id)
