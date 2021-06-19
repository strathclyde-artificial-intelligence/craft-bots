from craftbots import craft_bots
from agents import bogo

if __name__ == '__main__':
    craft_bots.start_simulation(agent=bogo.Bogo())
