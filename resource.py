class Resource:
    def __init__(self, world, location, colour=0):
        self.world = world
        self.colour = colour
        self.location = location
        self.tick_created = self.world.tick
        self.used = False
        self.id = self.world.get_new_id()

        self.location.append_resource(self)

        self.fields = {"id": self.id, "location": self.location.id, "tick_created": self.tick_created, "used": self.used}

    def __repr__(self):
        return "Resource(" + str(self.id) + ", " + self.world.get_colour_string(self.colour) + ", " + str(
            self.location) + ")"

    def __str__(self):
        return self.__repr__()

    def update(self):
        if self.colour == 4 and self.world.tick - self.tick_created >= self.world.modifiers["GREEN_DECAY_TIME"]:
            self.set_used(True)
            self.location.remove_resource(self)

    def set_location(self, location):
        self.location = location
        self.fields.__setitem__("location", location.id)

    def set_used(self, used):
        self.used = used
        self.fields.__setitem__("used", used)
