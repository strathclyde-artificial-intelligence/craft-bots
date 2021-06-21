class Task:
    def __init__(self, world, node, colour, amount):
        """
        A task in the craftbots simulation. Tasks are randomly generated goals used to give agents something to aim
        towards in the simulation. They ask the agent to create a certain number of buildings of a certain colour.
        :param world: the world which the task is associated with
        :param node: the node which the buildings must be completed at
        :param colour: the colour of buildings to be built
        :param amount: the number of buildings to be built
        """
        self.node = node
        self.colour = colour
        self.amount = amount
        self.world = world
        self.id = self.world.get_new_id()

        self.fields = {"node": node.id, "colour": colour, "amount": amount, "id": self.id, "complete": False}

    def __repr__(self):
        return "Task(" + str(self.amount) + ", " + self.world.get_colour_string(self.colour) +\
               ", " + str(self.node) + ")"

    def __str__(self):
        if self.amount == 1:
            return "Task to build 1 " + self.world.get_colour_string(self.colour) + " building at " + str(self.node)
        return "Task to build " + str(self.amount) + " " + self.world.get_colour_string(self.colour) \
               + " buildings at " + str(self.node)

    def complete(self):
        """
        Checks if the minimum amount of buildings of the right colour have been built and return True or False if that
        has been fulfilled yet or not
        :return: True if the task is completed, and False if not
        """
        current_amount = 0
        for building in self.node.buildings:
            if building.colour == self.colour:
                current_amount += 1
                if current_amount >= self.amount:
                    self.fields.__setitem__("complete", True)
                    return True
        return False
