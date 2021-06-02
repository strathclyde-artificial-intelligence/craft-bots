class Resource:
    def __init__(self, world, location, colour=0):
        self.world = world
        self.colour = colour
        self.location = location
        self.location.resources.append(self)
        if self.colour == 4:
            self.tick_created = self.world.tick
        self.used = False

    def get_colour_string(self):
        if self.colour == 0:
            return "red"
        elif self.colour == 1:
            return "blue"
        elif self.colour == 2:
            return "orange"
        elif self.colour == 3:
            return "black"
        elif self.colour == 4:
            return "green"

    def update(self):
        if self.colour == 4 and self.world.tick - self.tick_created >= self.world.modifiers["GREEN_DECAY_TIME"]:
            self.used = True
            self.location.resources.remove(self)
