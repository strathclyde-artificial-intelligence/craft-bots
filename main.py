import threading

from agents.blank_agent import BlankAgent
from agents.bogo import Bogo
from craftbots.simulation import Simulation
from gui.main_window import CraftBotsGUI

if __name__ == '__main__':

    # Simulation
    sim = Simulation()

    # agent
    agent = Bogo()
    sim.agents.append(agent)

    # GUI
    gui = CraftBotsGUI(sim)
    gui.start_window()

