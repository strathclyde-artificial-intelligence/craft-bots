class Command:
    def __init__(self, world, function_id, *args):
        self.world = world
        self.id = self.world.get_new_id()
        self.world.command_queue.append(self)
        self.function_id = function_id
        self.args = args

    def perform(self):
        if self.function_id == 0 and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            target_node = self.world.get_by_id(self.args[1], entity_type="Node")
            return actor.travel_to(target_node)
        elif self.function_id == 1 and self.args.__len__() == 1:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            return actor.travel_rand()
        elif self.function_id == 10 and self.args.__len__() == 0:
            return self.world.get_all_actors()
        else:
            return False
