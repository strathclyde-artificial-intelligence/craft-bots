class Command:

    MOVE_TO = 0
    MOVE_RAND = 1
    PICK_UP_RESOURCE = 2
    DROP_RESOURCE = 3
    DROP_ALL_RESOURCES = 4
    DIG_AT = 5
    START_SITE = 6
    BUILD_AT = 7
    DEPOSIT_RESOURCES = 8
    NO_COMMAND = 9
    CANCEL_ACTION = 10

    def __init__(self, world, function_id, *args):
        self.world = world
        self.id = self.world.get_new_id()
        self.world.command_queue.append(self)
        self.function_id = function_id
        self.args = args

    def perform(self):
        if self.function_id == Command.MOVE_TO and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            target_node = self.world.get_by_id(self.args[1], entity_type="Node")
            if actor is not None and target_node is not None:
                return actor.travel_to(target_node)
            return False
        elif self.function_id == Command.MOVE_RAND and self.args.__len__() == 1:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            if actor is not None:
                return actor.travel_rand()
            return False
        elif self.function_id == Command.PICK_UP_RESOURCE and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            resource = self.world.get_by_id(self.args[1], entity_type="Resource")
            if actor is not None and resource is not None:
                return actor.pick_up_resource(resource)
            return False
        elif self.function_id == Command.DROP_RESOURCE and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            resource = self.world.get_by_id(self.args[1], entity_type="Resource")
            if actor is not None and resource is not None:
                return actor.drop_resource(resource)
            return False
        elif self.function_id == Command.DROP_ALL_RESOURCES and self.args.__len__() == 1:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            if actor is not None:
                return actor.drop_everything()
            return False
        elif self.function_id == Command.DIG_AT and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            mine = self.world.get_by_id(self.args[1], entity_type="Mine")
            if actor is not None and mine is not None:
                return actor.dig_at(mine)
            return False
        elif self.function_id == Command.START_SITE and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            if actor is not None:
                return actor.start_site(self.args[1])
            return False
        elif self.function_id == Command.BUILD_AT and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            site = self.world.get_by_id(self.args[1], entity_type="Site")
            if site is None:
                site = self.world.get_by_id(self.args[1], entity_type="Building")
            if actor is not None and site is not None:
                return actor.build_at(site)
            return False
        elif self.function_id == Command.DEPOSIT_RESOURCES and self.args.__len__() == 3:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            site = self.world.get_by_id(self.args[1], entity_type="Site")
            if site is None:
                site = self.world.get_by_id(self.args[1], entity_type="Building")
            resource = self.world.get_by_id(self.args[2], entity_type="Resource")
            if actor is not None and site is not None and resource is not None:
                return actor.deposit(site, resource)
            return False
        elif self.function_id == Command.NO_COMMAND and self.args.__len__() == 0:
            return None
        elif self.function_id == Command.CANCEL_ACTION and self.args.__len__() == 1:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            if actor is not None:
                return actor.cancel_action()
            return False
        else:
            return False
