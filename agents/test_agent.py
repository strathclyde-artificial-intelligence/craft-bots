from api import agent_api


class TestAgent:
    def __init__(self):
        self.api = None
        self.thinking = False
        self.world_info = None

    def receive_results(self, results):
        pass
        # print(results)

    def get_next_commands(self):
        self.api: agent_api.AgentAPI
        for actor_id in self.api.actors:
            if self.api.get_field(actor_id, "state") == 0:
                if self.world_info["actors"].__len__() > 1:
                    for current_actor_id in self.world_info["actors"]:
                        if current_actor_id != actor_id:
                            self.api.start_sending(actor_id, "hello friend!")
                self.api.move_rand(actor_id)
            if self.api.get_field(actor_id, "state") == 6:
                for current_actor_id in self.world_info["actors"]:
                    if current_actor_id > actor_id:
                        self.api.cancel_action(actor_id)
                        self.api.start_receiving(actor_id)

        if self.world_info["tick"] % 10 == 0:
            for actor_id in self.world_info["actors"]:
                print(self.api.get_field(actor_id, "target"))
        self.thinking = False
