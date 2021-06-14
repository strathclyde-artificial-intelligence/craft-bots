
import craft_bots
import test_agent
from agents import human_agent
from agents import bogo

if __name__ == '__main__':
    craft_bots.start_simulation(agent=bogo.Bogo())
