import argparse
import time
from agents.bogo import Bogo
from craftbots.simulation import Simulation


def reset_simulation(sim : Simulation):
    sim.agents.clear()
    agent = Bogo()
    sim.agents.append(agent)
    sim.reset_simulation()

if __name__ == '__main__':

    # parse command line arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", help="set number of simulation runs (default 1)", type=int, default=1)
    arg_parser.add_argument("-c", help="configuration file", type=str)
    args = arg_parser.parse_args()
    
    # Simulation
    if args.c:
        print("Starting simulation with config file: "+ args.c)
        sim = Simulation(args.c)
    else:
        print("Starting simulation with config file: craftbots/config/simulation_configuration.yaml")
        sim = Simulation()

    for n in range(args.n):
        reset_simulation(sim)
        sim.start_simulation()

        while not sim.simulation_finished:
            time.sleep(0.1)
        print("sim score: ", sim.world.total_score)



