from api import agent_api


class TestAgent:
    def __init__(self):
        self.api = None
        self.thinking = False
        self.world_info = None

    def receive_results(self, results):
        print(results)

    def get_next_commands(self):
        self.api: agent_api.AgentAPI
        for actor_id in self.world_info["actors"]:
            if self.api.get_field(actor_id, "state") == 0:
                self.api.move_rand(actor_id)
        self.thinking = False
