from api import agent_api
from api.command import Command


class TestAgent:
    def __init__(self):
        self.api = None
        self.thinking = False
        self.world_info = None
        self.pending = []

    def get_next_commands(self):
        self.api: agent_api.AgentAPI
        for actor_id in self.api.actors:
            if self.api.get_field(actor_id, "state") == 0:
                self.pending.append(self.api.move_rand(actor_id))
        self.thinking = False

        for command_id in self.pending:
            if self.api.get_field(command_id, "state") == Command.COMPLETED:
                self.pending.remove(command_id)
