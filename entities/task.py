import random as r
from entities.building import Building


class Task:

    EASY    = 0
    MEDIUM  = 1
    HARD    = 2

    def __init__(self, world):
        """
        A task in the craftbots simulation. Tasks are randomly generated goals used to give agents something to aim
        towards in the simulation. They ask the agent to create a purple building (a goal building) that has randomly
        generated resource requirements.
        :param world: the world which the task is associated with
        """
        self.node = world.nodes[r.randint(0, world.nodes.__len__() - 1)]
        self.world = world
        self.id = self.world.get_new_id()
        self.difficulty = self.__decide_difficulty()
        self.needed_resources = self.__generate_task()
        self.deadline = self.__set_dead_line()
        self.project = None

        self.node.append_task(self)

        self.fields = {"node": self.node.id, "id": self.id, "completed": self.completed, "difficulty": self.difficulty,
                       "needed_resources": self.needed_resources, "project": self.project, "deadline": self.deadline}

    def __repr__(self):
        return "Task(" + str(self.node) + ", " + str(self.needed_resources) + ")"

    def __str__(self):
        return "Task to build at " + str(self.node) + " with the resource requirements of " + str(self.needed_resources)

    def completed(self):
        """
        Checks if the deadline had passed, and then checks if the tasks project is a Building entity. If it is then it
        implies that the building is complete and as such the task is complete. If the project is None or a Site entity,
        then it implies that there is still work to do before the task is complete. If the deadline has passed then the
        task is considered completed, but the agent will not have received any rewards for it.
        :return: True if the task is completed, and False if not
        """

        return isinstance(self.project, Building) if self.deadline >= self.world.tick or self.deadline == -1 else True

    def complete_task(self):
        """
        This function is called when the task is complete (usually by creating the building). It will calculate the
        score provided by the task and added to a total score variable in the simulation
        """

        self.world.total_score += (sum(self.needed_resources) * self.world.task_config["task_score_a"]) + \
                                  (self.world.task_config["task_score_b"] *
                                   (sum(self.needed_resources) ** self.world.task_config["task_score_c"]))

    def __generate_task(self):
        """
        Generates a list of needed resources for the Task by determining what difficulty the task should be, and then
        how many different types of resources should be used in the task using the difficulty.

        :return: A list of needed resources for a Site entity to use
        """

        return self.__get_num_of_resources(self.__get_num_of_types())

    def __decide_difficulty(self):
        """
        Returns the difficulty of the task. This value is determined randomly based on parameters from the
        initialisation files under modifiers.

        :return: The difficulty of the Task
        """
        result = r.randint(1, self.world.task_config["easy_task_weight"] + self.world.task_config["medium_task_weight"] +
                           self.world.task_config["hard_task_weight"])
        if result - self.world.task_config["easy_task_weight"] <= 0:
            return Task.EASY
        elif result - self.world.task_config["easy_task_weight"] - self.world.task_config["medium_task_weight"] <= 0:
            return Task.MEDIUM
        else:
            return Task.HARD
        
    def __get_num_of_types(self):
        """
        Returns the number of different resource types to be used in the Task based on the difficulty of the task. This
        value is determined randomly based on parameters from the initialisation files under modifiers.

        :return: The number of different resource types to be used in the Task
        """
        if self.difficulty == Task.EASY:
            return r.randint(self.world.task_config["easy_task_types"][0], self.world.task_config["easy_task_types"][1])
        elif self.difficulty == Task.MEDIUM:
            return r.randint(self.world.task_config["medium_task_types"][0], self.world.task_config["medium_task_types"][1])
        else:
            return r.randint(self.world.task_config["hard_task_types"][0], self.world.task_config["hard_task_types"][1])

    def __get_num_of_resources(self, num_of_types):
        """
        Returns a set of needed resources based on the difficulty of the task and the number of resource types to be
        used. These values are determined randomly based on parameters from the initialisation files under modifiers.

        :param num_of_types: The number of different resource types to be used in the Task
        :return: A list of needed resources for a Site entity to use
        """
        available = [0, 1, 2, 3, 4]
        chosen = []
        for _ in range(min(num_of_types,len(available))):
            index = r.randint(0, len(available) - 1)
            chosen.append(available[index])
            available.remove(available[index])
            
        needed_resources = [0, 0, 0, 0, 0]
        for index in range(len(needed_resources)):
            if chosen.__contains__(index):
                if self.difficulty == Task.EASY:
                    min_res = self.world.task_config["easy_task_resources"][0]
                    max_res = self.world.task_config["easy_task_resources"][1]
                elif self.difficulty == Task.MEDIUM:
                    min_res = self.world.task_config["medium_task_resources"][0]
                    max_res = self.world.task_config["medium_task_resources"][1]
                else:
                    min_res = self.world.task_config["hard_task_resources"][0]
                    max_res = self.world.task_config["hard_task_resources"][1]
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

    def __set_dead_line(self):
        if r.random() < self.world.task_config["task_deadline_probability"]:
            sum_of_res = sum(self.needed_resources) * self.world.task_config["RESOURCE_COMP_MODIFIER"]
            mining_compensation = sum_of_res * self.world.task_config["MINE_EFFORT"]
            travel_compensation = sum_of_res * self.world.world_gen_modifiers["CAST_DISTANCE"] * \
                                  self.world.get_all_edges().__len__() * 0.2 / self.world.task_config["ACTOR_MOVE_SPEED"]
            construction_compensation = sum_of_res * self.world.task_config["BUILD_EFFORT"]

            mining_compensation *= self.world.task_config["MINING_COMP_MODIFIER"]
            travel_compensation *= self.world.task_config["TRAVEL_COMP_MODIFIER"]
            construction_compensation *= self.world.task_config["CONSTRUCT_COMP_MODIFIER"]

            compensation = (mining_compensation + travel_compensation + construction_compensation) \
                           * self.world.task_config["COMP_MODIFIER"]
            return self.world.tick + compensation
        return -1
