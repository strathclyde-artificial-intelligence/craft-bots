from craftbots import craft_bots
from agents import bogo
from agents import blank_agent
from agents import test_agent
from agents import human_agent

if __name__ == '__main__':
    craft_bots.start_simulation(agent_class=bogo.Bogo)
    # craft_bots.start_simulation(agent_class=blank_agent.BlankAgent)
    # craft_bots.start_simulation(agent_class=test_agent.TestAgent)
    # craft_bots.start_simulation(agent_class=human_agent.HumanAgent)
