from api.command import Command


class AgentAPI:

    def __init__(self, world, max_commands=10):
        """
        The API for the craftbots simulation. It is given to the agent and the agent can make calls to this to perform
        actions on the simulation or to gather information.

        :param world: The world used to be affected by the API/agent
        :param max_commands: The maximum number of commands that can be sent to the world in one tick. If set to 0 then
        there is no limit
        """
        self.__world = world
        self.__max_commands = max_commands
        self.num_of_current_commands = 0

    def __send_command(self, function_id, *args):
        """
        This function creates a Command object that sends itself to the world, and at the start of a tick all of the
        commands are executed. This then returns a unique ID that can be used to find the outcome of the command. This
        will most often be True if the action is done/started successfully or False if for some reason the action could
        not be performed. This will return -1 if the max_commands limit has been reached for the tick

        The result is given to the agent in a tuple with the command's id when the craft bots
        simulation calls the receive_results method in the Agent.

        :param function_id: the ID of the action to be performed
        :param args: an array of parameters to be passed to the command.
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        if self.num_of_current_commands < self.__max_commands or self.__max_commands == 0:
            command = Command(self.__world, function_id, *args)
            self.num_of_current_commands += 1
            return command.id
        return -1

    def move_to(self, actor_id, node_id):
        """
        Send the actor to the given node.

        To do this, the agent must be idle, and the target node must be adjacent to the node the actor is currently at.

        :param actor_id: The ID of the actor to be moved
        :param node_id: The ID of the node the actor should move to.
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.MOVE_TO, actor_id, node_id)

    def move_rand(self, actor_id):
        """
        Send the actor to a randomly chosen adjacent node.

        To do this, the agent must be idle.

        :param actor_id: The ID of the actor to be moved
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.MOVE_RAND, actor_id)

    def pick_up_resource(self, actor_id, resource_id):
        """
        Tell an actor to pick a a specific resource off of the ground.

        To do this, the actor must be idle, the resource must be in the same node as the actor, the resource must not
        held by another actor, and the actor should have space in it's inventory to store the resource.

        If the resource is black then the actor should not be holding any other resources. The actor should also not be
        holding a black resource already.

        :param actor_id: The ID of the actor to pick up the resource
        :param resource_id: The ID of the resource to be picked up
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.PICK_UP_RESOURCE, actor_id, resource_id)

    def drop_resource(self, actor_id, resource_id):
        """
        Tell an actor to drop a specific resource from its inventory. The resource will be dropped at the node the actor
        is at.

        To do this, the actor must be idle and the resource must be in the actors inventory.

        :param actor_id: The ID of the actor to drop the resource
        :param resource_id: The ID of the resource to be dropped
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.DROP_RESOURCE, actor_id, resource_id)

    def drop_all_resources(self, actor_id):
        """
        Tell an actor to drop all of the resources it is currently holding. This will drop all of the resources it is
        currently holding into the node the actor is currently at.

        To do this, the actor must be idle.

        :param actor_id: The ID of the actor to drop all of its resources
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.DROP_ALL_RESOURCES, actor_id)

    def dig_at(self, actor_id, mine_id):
        """
        Tell an actor to begin digging at a mine. Assuming the special mining conditions of the mines resource are met,
        after a certain amount of time, a new resource will be placed on the node the mine and actor are at and then the
        actor will stop digging.

        To do this, the actor must be idle, and the actor should be at the same node as the mine.

        :param actor_id: The ID of the actor to dig at the mine
        :param mine_id: The ID of the mine the actor should dig at
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.DIG_AT, actor_id, mine_id)

    def start_site(self, actor_id, site_type):
        """
        Tell an actor to start a site of the specified type. A site will be placed on the node that the actor is at.

        To do this the actor must be idle.

        :param actor_id: The ID of the actor to create a site
        :param site_type: The type of site to be built (0: red, 1: blue, 2: orange, 3: black, 4: green)
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.START_SITE, actor_id, site_type)

    def construct_at(self, actor_id, site_id):
        """
        Tell the actor to begin constructing at the specified site. The actor will construct up to a percentage equal to
        the deposited resources / needed resources at the site. If the actor completes construction then the site will
        become a building at the same node, and the actor will become idle. Actors can also construct at green buildings
        in the same manner in order to create new actors.

        To do this, the actor must be idle and the actor must be at the same node as the site.

        :param actor_id: The ID of the actor to construct at the site
        :param site_id: The ID of the site / building the actor should construct at.
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.CONSTRUCT_AT, actor_id, site_id)

    def deposit_resources(self, actor_id, site_id, resource_id):
        """
        Tell the actor deposit a resource into the site. This will increase the maximum progress that can be done on the
        site. Actors can also do this on green buildings to commit resources towards creating new actors.

        To do this, the actor must be at the same node as the site, the resource must be in the actor's inventory, and
        the site should still need the type of the resource.

        :param actor_id: The ID of the actor to deposit a resource at the site
        :param site_id: The ID of the site the resources should be deposited in
        :param resource_id: The ID of the resource to be deposited
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.DEPOSIT_RESOURCES, actor_id, site_id, resource_id)

    def get_world_info(self):
        """
        This gets an up to date version of the world_info dictionary instantly. This is to be used if your agent takes a
        long time to deliberate actions or is waiting for something to change, and the agent needs up to date
        information immediately.

        This does not need to be called at the start of get_next_commands because the world info is updated each time
        before the function is called.

        :return: The world_info dictionary
        """
        return self.__world.get_world_info()

    def cancel_action(self, actor_id):
        """
        Tells the actor to stop any ongoing action it is currently performing. Depending on what the actor is currently
        doing depends on what the actor does. If the actor is moving between two nodes, then the actor will turn around
        attempt to return to the node it started at. If the actor is digging, then it will become idle, and if no other
        actors are digging at the node, then the progress towards a new resource is lost. If the actor is constructing,
        then the actor becomes idle, and the progress in the site stops at the amount it is at.

        To do this, the actor must not be idle.

        :param actor_id: The ID of the actor to cancel its action
        :return: The ID of the command or -1 if the max command limit has been reached
        """
        return self.__send_command(Command.CANCEL_ACTION, actor_id)

    def get_by_id(self, entity_id, entity_type=None, target_node=None):
        """
        This command instantly returns the fields of an entity. The fields are stored in a dictionary and are updated
        every tick.

        Optionally, the type of the entity can be passed in as a string to stop the function from searching other types
        of entities and the ID of the node that should be searched can also be chosen to only search one node for the
        specified entity.

        :param entity_id: The ID of the entity that should be found
        :param entity_type: (optional) The type of entity to be found
        (Node, Edge, Actor, Resource, Mine, Site, Building)
        :param target_node: (optional) the ID of the node that should be checked
        :return: A dictionary of the fields the entity has, or None if the entity is not found
        """
        result = self.__world.get_by_id(entity_id, entity_type=entity_type, target_node=self.__world.get_by_id(target_node))
        return None if result is None else result.fields

    def get_field(self, entity_id, field, entity_type=None, target_node=None):
        """
        This command instantly returns the specified field of an entity. The field should be stored in the fields of the
        entity.

        Optionally, the type of the entity can be passed in as a string to stop the function from searching other types
        of entities and the ID of the node that should be searched can also be chosen to only search one node for the
        specified entity.

        :param entity_id: The ID of the entity that should be found
        :param field: The field of the entity that should be returned
        :param entity_type: (optional) The type of entity to be found
        (Node, Edge, Actor, Resource, Mine, Site, Building)
        :param target_node: (optional) the ID of the node that should be checked
        :return: The field from the entity, or None if the entity is not found or the entity does not have the field.
        """
        return self.__world.get_field(entity_id, field, entity_type=entity_type, target_node=target_node)
