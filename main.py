from craftbots import craft_bots
from agents import bogo
from agents import blank_agent
from agents import test_agent

if __name__ == '__main__':
    # craft_bots.start_simulation(agent=bogo.Bogo())
    print(craft_bots.start_simulation(agent=blank_agent.BlankAgent()))
    # craft_bots.start_simulation(agent=test_agent.TestAgent())
