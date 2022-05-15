from agents.test_agent import TestAgent
from craftbots.simulation import Simulation
from gui.main_window import CraftBotsGUI

if __name__ == '__main__':

    # Simulation
    sim = Simulation()

    # agent
    agent = TestAgent()
    sim.agents.append(agent)

    # GUI
    gui = CraftBotsGUI(sim)
    gui.start_window()

