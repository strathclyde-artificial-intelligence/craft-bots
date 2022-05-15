import time
import threading

from api.agent_api import AgentAPI
from craftbots.log_manager import Logger
from craftbots.world_factory import WorldFactory
from craftbots.config.config_manager import Configuration


class Simulation:

    def __init__(self, configuration_file = "craftbots/config/simulation_configuration.yaml"):

        # simulation loop properties
        self.config = Configuration.read_ini_file(configuration_file)
        self.simulation_paused = False
        self.simulation_running = False
        self.simulation_finished = False

        # world model
        self.world = None

        # agent references
        self.agents = []

        # logging
        Logger.setup_logger(self.config, self.world)

    # ================== #
    # simulation methods #
    # ================== #

    def reset_simulation(self):
        self.world = WorldFactory.generate_world(self.config)
        Logger.setup_logger(self.config, self.world)
        for agent in self.agents:
            actor_ids = self.world.get_all_actor_ids()
            agent.api = AgentAPI(self.world, actor_ids)
            agent.world_info = agent.api.get_world_info()

        self.simulation_finished = False

    def pause_simulation(self):
        self.simulation_paused = not self.simulation_paused

    def start_simulation(self):

        # simulation not prepped
        if not self.world: return

        # start new simulation run
        if not self.simulation_running and not self.simulation_finished:
            self.simulation_running = True
            sim_thread = threading.Thread(target=self.run_simulation)
            sim_thread.start()

        # restart paused simulation
        elif self.simulation_running and self.simulation_paused:
            # unpause existing simulation
            self.simulation_paused = False

    def run_simulation(self):

        while not self.simulation_finished:

            loop_start = time.time()

            if not self.simulation_paused:

                # poll agents
                for agent in self.agents:
                    agent.world_info = agent.api.get_world_info()
                    # blocking request for agent commands
                    if Configuration.get_value(self.config, "lockstep"):
                        agent.get_next_commands()
                    # non-blocking request
                    elif not agent.thinking:
                        threading.Thread(target=agent.get_next_commands).start()

                # update world
                self.simulation_finished = self.world.run_tick()

                # reset agent command queues
                for agent in self.agents:
                    agent.api.num_of_current_commands = 0

                # check if finished
                if self.world.tick > Configuration.get_value(self.config, "sim_length"):
                    self.simulation_finished = True

            # simulation rate
            period = 1 / Configuration.get_value(self.config, "simulation_rate")
            wait = period - (time.time() - loop_start)
            if wait > 0.01:
                print(wait)
                time.sleep(wait)

        # simulation complete
        self.simulation_running = False
