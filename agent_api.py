from command import Command


class AgentAPI:

    def __init__(self, world, max_commands=10):
        self.world = world
        self.max_commands = 3
        self.num_of_current_commands = 0

    def send_command(self, function_id, *args):
        if self.num_of_current_commands < self.max_commands:
            command = Command(self.world, function_id, *args)
            self.num_of_current_commands += 1
            return command.id
        return -1

    def move_to(self, actor_id, node_id):
        return self.send_command(0, actor_id, node_id)

    def move_rand(self, actor_id):
        return self.send_command(1, actor_id)

    def pick_up_resource(self, actor_id, resource_id):
        pass

    def drop_resource(self, actor_id, resource_id):
        pass

    def drop_all_resources(self, actor_id):
        pass

    def mine_at(self, actor_id, mine_id):
        pass

    def start_site(self, actor_id, site_type):
        pass

    def build_at(self, actor_id, site_id):
        pass

    def deposit_resources(self, actor_id, resource_id):
        pass

    def get_adjacent_nodes(self, node_id):
        pass

    def get_actors_at(self, node_id):
        pass

    def get_all_actors(self):
        return self.send_command(10)

    def get_resources_at(self, node_id):
        pass

    def get_mines_at(self, node_id):
        pass

    def get_sites_at(self, node_id):
        pass

    def get_buildings_at(self, node_id):
        pass

    def get_tasks(self):
        pass

