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
        elif self.function_id == 2 and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            resource = self.world.get_by_id(self.args[1], entity_type="Resource")
            return actor.pick_up_resource(resource)
        elif self.function_id == 3 and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            resource = self.world.get_by_id(self.args[1], entity_type="Resource")
            return actor.drop_resource(resource)
        elif self.function_id == 4 and self.args.__len__() == 1:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            return actor.drop_everything()
        elif self.function_id == 5 and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            mine = self.world.get_by_id(self.args[1], entity_type="Mine")
            return actor.mine_at(mine)
        elif self.function_id == 6 and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            return actor.start_site(self.args[1])
        elif self.function_id == 7 and self.args.__len__() == 2:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            site = self.world.get_by_id(self.args[1], entity_type="Site")
            return actor.build_at(site)
        elif self.function_id == 8 and self.args.__len__() == 3:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            site = self.world.get_by_id(self.args[1], entity_type="Site")
            resource = self.world.get_by_id(self.args[2], entity_type="Resource")
            print(resource)
            return actor.deposit(site, resource)
        elif self.function_id == 9 and self.args.__len__() == 1:
            node = self.world.get_by_id(self.args[0], entity_type="Node")
            return node.get_adjacent_nodes()
        elif self.function_id == 10 and self.args.__len__() == 1:
            node = self.world.get_by_id(self.args[0], entity_type="Node")
            return node.actors
        elif self.function_id == 11 and self.args.__len__() == 0:
            return self.world.get_all_actors()
        elif self.function_id == 12 and self.args.__len__() == 1:
            node = self.world.get_by_id(self.args[0], entity_type="Node")
            return node.resources
        elif self.function_id == 13 and self.args.__len__() == 0:
            return self.world.get_all_mines()
        elif self.function_id == 14 and self.args.__len__() == 1:
            node = self.world.get_by_id(self.args[0], entity_type="Node")
            return node.mines
        elif self.function_id == 15 and self.args.__len__() == 0:
            return self.world.get_all_resources()
        elif self.function_id == 16 and self.args.__len__() == 1:
            node = self.world.get_by_id(self.args[0], entity_type="Node")
            return node.sites
        elif self.function_id == 17 and self.args.__len__() == 0:
            return self.world.get_all_sites()
        elif self.function_id == 18 and self.args.__len__() == 1:
            node = self.world.get_by_id(self.args[0], entity_type="Node")
            return node.buildings
        elif self.function_id == 19 and self.args.__len__() == 0:
            return self.world.get_all_buildings()
        elif self.function_id == 20 and self.args.__len__() == 0:
            return self.world.tasks
        elif self.function_id == 21 and self.args.__len__() == 0:
            return self.world.nodes
        elif self.function_id == 22 and self.args.__len__() == 0:
            return None
        elif self.function_id == 23 and self.args.__len__() == 1:
            actor = self.world.get_by_id(self.args[0], entity_type="Actor")
            return actor.cancel_action()
        else:
            return False
