from agents.agent import Agent
from craftbots.entities.actor import Actor
from craftbots.log_manager import Logger

class TestAgent(Agent):

    def __init__(self):
        super().__init__()            

    def get_next_commands(self):

        Logger.info("Agent", "Starting random moves.")

        while not self.simulation_complete:
            for actor_id in self.api.actors:
                if self.api.get_field(actor_id, "state") == Actor.IDLE:
                    self.api.move_rand(actor_id)

        Logger.info("Agent", "Finished.")