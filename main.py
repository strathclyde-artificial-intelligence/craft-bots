from craftbots import craft_bots
from agents import bogo
from agents import blank_agent

if __name__ == '__main__':
    craft_bots.start_simulation(agent=bogo.Bogo())
    # craft_bots.start_simulation(agent=blank_agent.BlankAgent())
