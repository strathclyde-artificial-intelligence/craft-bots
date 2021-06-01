class Task:
    def __init__(self, node, colour, amount):
        self.node = node
        self.colour = colour
        self.amount = amount

    def __repr__(self):
        return "Task(" + str(self.amount) + ", " + self.get_colour_string() + ", " + str(self.node) + ")"

    def __str__(self):
        if self.amount == 1:
            return "Task to build 1 " + self.get_colour_string() + " building at " + str(self.node)
        return "Task to build " + str(self.amount) + " " + self.get_colour_string() + " buildings at " + str(self.node)

    def complete(self):
        current_amount = 0
        for building in self.node.buildings:
            if building.colour == self.colour:
                current_amount += 1
                if current_amount >= self.amount:
                    return True
        return False

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
