class Building:
    def __init__(self, world, node, colour=0):
        self.world = world
        self.node = node
        self.colour = colour
        self.id = self.world.get_new_id()

        self.node.buildings.append(self)
