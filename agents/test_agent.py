from api import agent_api
from api.command import Command
from craftbots.entities.actor import Actor
from craftbots.log_manager import Logger

class Agent:

    def __init__(self):

        # simulation status flags
        self.simulation_complete = False
        self.simulation_paused = False

        # simulation interface
        self.api = None
        self.world_info = None

        # agent status flag
        self.thinking = False                

    def get_next_commands(self):
        
        self.api: agent_api.AgentAPI
        self.world_info : dict

        Logger.info("Agent", "Starting random moves.")
        while not self.simulation_complete:
            for actor_id in self.api.actors:
                if self.api.get_field(actor_id, "state") == Actor.IDLE:
                    self.api.move_rand(actor_id)

        Logger.info("Agent", "Finished.")