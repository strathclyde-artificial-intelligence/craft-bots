from agents.rule_based_agent import RBAgent
from agents.test_agent import Agent
from craftbots.simulation import Simulation
from gui.main_window import CraftBotsGUI

if __name__ == '__main__':

    # Simulation
    sim = Simulation(configuration_file='craftbots/config/simple_configuration.yaml')

    # agent
    agent = RBAgent()
    sim.agents.append(agent)

    # GUI
    gui = CraftBotsGUI(sim)
    gui.start_window()

