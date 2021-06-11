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
        return self.send_command(2, actor_id, resource_id)

    def drop_resource(self, actor_id, resource_id):
        return self.send_command(3, actor_id, resource_id)

    def drop_all_resources(self, actor_id):
        return self.send_command(4, actor_id)

    def mine_at(self, actor_id, mine_id):
        return self.send_command(5, actor_id, mine_id)

    def start_site(self, actor_id, site_type):
        return self.send_command(6, actor_id, site_type)

    def build_at(self, actor_id, site_id):
        return self.send_command(7, actor_id, site_id)

    def deposit_resources(self, actor_id, site_id, resource_id):
        return self.send_command(8, actor_id, site_id, resource_id)

    def get_adjacent_nodes(self, node_id):
        return self.send_command(9, node_id)

    def get_actors_at(self, node_id):
        return self.send_command(10, node_id)

    def get_all_actors(self):
        return self.send_command(11)

    def get_resources_at(self, node_id):
        return self.send_command(12, node_id)

    def get_all_mines(self):
        return self.send_command(13)

    def get_mines_at(self, node_id):
        return self.send_command(14, node_id)

    def get_all_resources(self):
        return self.send_command(15)

    def get_sites_at(self, node_id):
        return self.send_command(16, node_id)

    def get_all_sites(self):
        return self.send_command(17)

    def get_buildings_at(self, node_id):
        return self.send_command(18, node_id)

    def get_all_buildings(self):
        return self.send_command(19)

    def get_tasks(self):
        return self.send_command(20)

    def get_all_nodes(self):
        return self.send_command(21)

    def no_commands(self):
        return self.send_command(22)

    def cancel_action(self, actor_id):
        return self.send_command(23, actor_id)
