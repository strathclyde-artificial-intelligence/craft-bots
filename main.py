from agents import test_agent
from craftbots import craft_bots

if __name__ == '__main__':
    craft_bots.start_simulation(agent_class=test_agent.TestAgent)
