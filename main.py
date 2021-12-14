import threading

from agents.PDDLAgent.PDDLAgent import PDDLAgent
from agents.PlanningAgent import PlanningAgent
from agents.blank_agent import BlankAgent
from agents.bogo import Bogo
from craftbots.simulation import Simulation
from gui.main_window import CraftBotsGUI

if __name__ == '__main__':

    # agent
    agent = PDDLAgent()

    # Simulation
    sim = Simulation()
    sim.agents.append(agent)

    # GUI
    gui = CraftBotsGUI(sim)
    gui.start_window()