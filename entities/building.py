class Building:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.id = self.world.get_new_id()

        self.node.buildings.append(self)

        self.fields = {"node": self.node.id, "colour": self.colour, "id": self.id}

    def __repr__(self):
        return "Building(" + str(self.id) + ", " + self.world.get_colour_string(self.colour) + ", " + str(
            self.node) + ")"

    def __str__(self):
        return self.__repr__()
