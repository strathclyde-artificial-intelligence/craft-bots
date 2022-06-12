import random as r
from craftbots.entities.building import Building

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
        self.score = self.__set_score()
        self.start_time = world.tick
        self.deadline = self.__set_deadline()
        self.linked_site = None
        self.completed = False

        self.node.append_task(self)

        self.fields = {"node": self.node.id, "id": self.id, "completed": self.completed, "difficulty": self.difficulty,
                       "needed_resources": self.needed_resources, "site": self.linked_site, 
                       "start_time": self.start_time, "deadline": self.deadline,
                       "score": self.score}

    def __repr__(self):
        return "Task(" + str(self.node) + ", " + str(self.needed_resources) + ")"

    def __str__(self):
        return "Task to build at " + str(self.node) + " with the resource requirements of " + str(self.needed_resources)

    def complete_task(self):
        """
        This function is called when the task is complete (usually by creating the building). It will calculate the
        score provided by the task and added to a total score variable in the simulation
        """
        self.completed = True
        self.fields["completed"] = True
        if self.deadline == -1 or self.world.tick < self.deadline:
            self.world.total_score += self.score

    def __set_score(self):
        a = self.world.task_config["task_score_a"]
        b = self.world.task_config["task_score_b"]
        c = self.world.task_config["task_score_c"]
        n = sum(self.needed_resources)
        return (a * n) + (b * (n ** c))

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
        difficulty = r.choices([Task.EASY, Task.MEDIUM, Task.HARD,], k=1, weights=[
                self.world.task_config["easy_task_weight"],
                self.world.task_config["medium_task_weight"],
                self.world.task_config["hard_task_weight"]
            ])
        return difficulty[0]

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
        resource_types = r.sample(range(5),k=num_of_types)

        if self.difficulty == Task.EASY:
            min_res = self.world.task_config["easy_task_resources"][0]
            max_res = self.world.task_config["easy_task_resources"][1]
        elif self.difficulty == Task.MEDIUM:
            min_res = self.world.task_config["medium_task_resources"][0]
            max_res = self.world.task_config["medium_task_resources"][1]
        else:
            min_res = self.world.task_config["hard_task_resources"][0]
            max_res = self.world.task_config["hard_task_resources"][1]
        resource_amount = max(r.randint(min_res, max_res), num_of_types)
        choices = r.choices(resource_types, k=resource_amount)
        needed_resources = [ choices.count(i) for i in range(5) ]
        return needed_resources

    def set_project(self, project):
        """
        Sets the task's project (the Site / Building associated with the task if there is one) and keeps track of its
        id in the Task's fields

        :param project: The Site / Buildings to be set as the tasks project
        """
        self.linked_site = project
        self.fields.__setitem__("site", self.linked_site.id)

    def __set_deadline(self):
        if r.random() < self.world.task_config["task_deadline_probability"]:
            mining = self.world.resource_config['mine_effort'] / self.world.actor_config['dig_speed']
            travel = 2 * self.world.world_generation_config['roadmap_cast_distance'] / self.world.actor_config['move_speed']
            travel = travel * self.world.world_generation_config['max_nodes'] / 3
            construction = self.world.building_config['build_effort'] / self.world.actor_config['build_speed']
            deadline = sum(self.needed_resources) * (mining + travel + construction)
            return self.world.tick + round(deadline)
        return -1
