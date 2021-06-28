import random as r

class Task:

    EASY = 0
    MEDIUM = 1
    HARD = 2

    def __init__(self, world, node, colour, amount):
        """
        A task in the craftbots simulation. Tasks are randomly generated goals used to give agents something to aim
        towards in the simulation. They ask the agent to create a certain number of buildings of a certain colour.
        :param world: the world which the task is associated with
        :param node: the node which the buildings must be completed at
        :param colour: the colour of buildings to be built
        :param amount: the number of buildings to be built
        """
        self.node = world.nodes[r.randint(0, world.nodes.__len__() - 1)]
        self.colour = colour
        self.amount = amount
        self.world = world
        self.id = self.world.get_new_id()
        self.needed_resources = self.__generate_task()
        self.project = None

        self.fields = {"node": self.node.id, "colour": colour, "amount": amount, "id": self.id,
                       "completed": self.completed, "needed_resources": self.needed_resources, "project": self.project}

    def __repr__(self):
        return "Task(" + str(self.amount) + ", " + self.world.get_colour_string(self.colour) +\
               ", " + str(self.node) + ")"

    def __str__(self):
        if self.amount == 1:
            return "Task to build 1 " + self.world.get_colour_string(self.colour) + " building at " + str(self.node)
        return "Task to build " + str(self.amount) + " " + self.world.get_colour_string(self.colour) \
               + " buildings at " + str(self.node)

    def completed(self):
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

    def complete(self):

    def __generate_task(self):
        """
        Generates a list of needed resources for the Task by determining what difficulty the task should be, and then
        how many different types of resources should be used in the task using the difficulty.

        :return: A list of needed resources for a Site entity to use
        """
        difficulty = self.__get_difficulty()
        num_of_types = self.__get_num_of_types(difficulty)
        return self.__get_num_of_resources(difficulty, num_of_types)

    def __get_difficulty(self):
        """
        Returns the difficulty of the task. This value is determined randomly based on parameters from the
        initialisation files under modifiers.

        :return: The difficulty of the Task
        """
        result = r.randint(1, self.world.modifiers["EASY_TASK_WEIGHT"] + self.world.modifiers["MEDIUM_TASK_WEIGHT"] +
                           self.world.modifiers["HARD_TASK_WEIGHT"])
        if result - self.world.modifiers["EASY_TASK_WEIGHT"] <= 0:
            return Task.EASY
        elif result - self.world.modifiers["EASY_TASK_WEIGHT"] - self.world.modifiers["MEDIUM_TASK_WEIGHT"] <= 0:
            return Task.MEDIUM
        else:
            return Task.HARD
        
    def __get_num_of_types(self, difficulty):
        """
        Returns the number of different resource types to be used in the Task based on the difficulty of the task. This
        value is determined randomly based on parameters from the initialisation files under modifiers.

        :param difficulty: The difficulty of the Task
        :return: The number of different resource types to be used in the Task
        """
        if difficulty == Task.EASY:
            return r.randint(self.world.modifiers["EASY_TASK_MIN_TYPES"], self.world.modifiers["EASY_TASK_MAX_TYPES"])
        elif difficulty == Task.MEDIUM:
            return r.randint(self.world.modifiers["MEDIUM_TASK_MIN_TYPES"], 
                             self.world.modifiers["MEDIUM_TASK_MAX_TYPES"])
        else:
            return r.randint(self.world.modifiers["HARD_TASK_MIN_TYPES"], self.world.modifiers["HARD_TASK_MAX_TYPES"])

    def __get_num_of_resources(self, difficulty, num_of_types):
        """
        Returns a set of needed resources based on the difficulty of the task and the number of resource types to be
        used. These values are determined randomly based on parameters from the initialisation files under modifiers.

        :param difficulty: The difficulty of the Task
        :param num_of_types: The number of different resource types to be used in the Task
        :return: A list of needed resources for a Site entity to use
        """
        available = [0, 1, 2, 3, 4]
        chosen = []
        for _ in range(num_of_types):
            index = r.randint(0, available.__len__() - 1)
            chosen.append(available[index])
            available.remove(available[index])
            
        needed_resources = [0, 0, 0, 0, 0]
        for index in range(needed_resources.__len__()):
            if chosen.__contains__(index):
                if difficulty == Task.EASY:
                    min_res = self.world.modifiers["EASY_TASK_MIN_RESOURCES"]
                    max_res = self.world.modifiers["EASY_TASK_MAX_RESOURCES"]
                elif difficulty == Task.MEDIUM:
                    min_res = self.world.modifiers["MEDIUM_TASK_MIN_RESOURCES"]
                    max_res = self.world.modifiers["MEDIUM_TASK_MAX_RESOURCES"]
                else:
                    min_res = self.world.modifiers["HARD_TASK_MIN_RESOURCES"]
                    max_res = self.world.modifiers["HARD_TASK_MAX_RESOURCES"]
                needed_resources[index] = r.randint(min_res, max_res)
        return needed_resources

    def set_project(self, project):
        """
        Sets the task's project (the Site / Building associated with the task if there is one) and keeps track of its
        id in the Task's fields

        :param project: The Site / Buildings to be set as the tasks project
        """
        self.project = project
        self.fields.__setitem__("project", project.id)
