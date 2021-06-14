from command import Command


class AgentAPI:

    def __init__(self, world, max_commands=10):
        self.world = world
        self.max_commands = max_commands
        self.num_of_current_commands = 0

    def send_command(self, function_id, *args):
        if self.num_of_current_commands < self.max_commands:
            command = Command(self.world, function_id, *args)
            self.num_of_current_commands += 1
            return command.id
        return -1

    def move_to(self, actor_id, node_id):
        return self.send_command(Command.MOVE_TO, actor_id, node_id)

    def move_rand(self, actor_id):
        return self.send_command(Command.MOVE_RAND, actor_id)

    def pick_up_resource(self, actor_id, resource_id):
        return self.send_command(Command.PICK_UP_RESOURCE, actor_id, resource_id)

    def drop_resource(self, actor_id, resource_id):
        return self.send_command(Command.DROP_RESOURCE, actor_id, resource_id)

    def drop_all_resources(self, actor_id):
        return self.send_command(Command.DROP_ALL_RESOURCES, actor_id)

    def dig_at(self, actor_id, mine_id):
        return self.send_command(Command.DIG_AT, actor_id, mine_id)

    def start_site(self, actor_id, site_type):
        return self.send_command(Command.START_SITE, actor_id, site_type)

    def build_at(self, actor_id, site_id):
        return self.send_command(Command.BUILD_AT, actor_id, site_id)

    def deposit_resources(self, actor_id, site_id, resource_id):
        return self.send_command(Command.DEPOSIT_RESOURCES, actor_id, site_id, resource_id)

    def no_commands(self):
        return self.send_command(Command.NO_COMMAND)

    def cancel_action(self, actor_id):
        return self.send_command(Command.CANCEL_ACTION, actor_id)

    def get_by_id(self, entity_id, entity_type=None, target_node=None):
        result = self.world.get_by_id(entity_id, entity_type=entity_type, target_node=target_node)
        if result is None:
            return None
        else:
            return result.fields

    def get_field(self, entity_id, field, entity_type=None, target_node=None):
        return self.world.get_field(entity_id, field, entity_type=entity_type, target_node=target_node)
