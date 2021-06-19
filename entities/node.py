class Node:
    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.edges = []
        self.actors = []
        self.resources = []
        self.mines = []
        self.sites = []
        self.buildings = []
        self.id = self.world.get_new_id()
        
        self.fields = {"x": self.x, "y": self.y, "edges": [], "actors": [], "resources": [], "mines": [], "sites": [], 
                       "buildings": [], "id": self.id}

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

    def add_edge(self, edge):
        self.edges.append(edge)

    def shares_edge_with(self, other_node):
        for edge in self.edges:
            if edge.connects(other_node):
                return self.edges.index(edge)
        return -1

    def get_adjacent_nodes(self):
        nodes = []
        for edge in self.edges:
            nodes.append(edge.get_other_node(self))
        return nodes

    def append_edge(self, edge):
        self.edges.append(edge)
        self.fields.get("edges").append(edge.id)

    def append_actor(self, actor):
        self.actors.append(actor)
        self.fields.get("actors").append(actor.id)

    def remove_actor(self, actor):
        self.actors.remove(actor)
        self.fields.get("actors").remove(actor.id)

    def append_resource(self, resource):
        self.resources.append(resource)
        self.fields.get("resources").append(resource.id)

    def remove_resource(self, resource):
        self.resources.remove(resource)
        self.fields.get("resources").remove(resource.id)

    def append_mine(self, mine):
        self.mines.append(mine)
        self.fields.get("mines").append(mine.id)

    def append_site(self, site):
        self.sites.append(site)
        self.fields.get("sites").append(site.id)

    def remove_site(self, site):
        self.sites.remove(site)
        self.fields.get("sites").remove(site.id)

    def append_building(self, building):
        self.buildings.append(building)
        self.fields.get("buildings").append(building.id)
