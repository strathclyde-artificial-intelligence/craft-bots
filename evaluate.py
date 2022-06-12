import argparse
import time
from craftbots.log_manager import Logger
from progress.bar import ShadyBar
from agents.rule_based_agent import RBAgent
from craftbots.config.config_manager import Configuration
from craftbots.simulation import Simulation

def reset_simulation(sim : Simulation):
    sim.agents.clear()
    agent = RBAgent()
    sim.agents.append(agent)
    sim.reset_simulation()

if __name__ == '__main__':

    # parse command line arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", help="set number of simulation runs (default 1)", type=int, default=1)
    arg_parser.add_argument("-f", help="configuration file", type=str)
    arg_parser.add_argument("-o", help="output file", type=str, default="evaluation_output.csv")
    arg_parser.add_argument("-r", help="override config simulation rate (default -1, no override)", type=int, default=-1)
    args = arg_parser.parse_args()
    
    # ensure logging is not printing to screen
    Logger.log_to_screen = False

    # create output file
    with open(args.o,'w') as ofile:
        ofile.write("seed,score,max_score\n")

    # create simulation
    if args.f:
        print("Starting simulation with config file: "+ args.f)
        sim : Simulation = Simulation(args.f)
    else:
        print("Starting simulation with default config file: craftbots/config/simple_configuration.yaml")
        sim : Simulation = Simulation(configuration_file="craftbots/config/simple_configuration.yaml")

    # make sure to use random seed
    Configuration.set_value(sim.config, "use_random_seed", True)
    initial_seed = Configuration.get_value(sim.config, "random_seed")

    # check simulation rate
    if args.r > 0: Configuration.set_value(sim.config, "simulation_rate", args.r)

    # set up progress bar
    sim_length = Configuration.get_value(sim.config, "sim_length")
    bar : ShadyBar = ShadyBar('Running simulations', max=args.n*sim_length)

    # run simulations
    for n in range(args.n):

        Configuration.set_value(sim.config, "random_seed", initial_seed+n)
        reset_simulation(sim)
        sim.start_simulation()

        while not sim.simulation_finished:
            bar.goto(n*sim_length + sim.world.tick)
            time.sleep(0.1)

        with open(args.o,'a') as ofile:
            ofile.write(str(Configuration.get_value(sim.config, "random_seed"))+","+str(sim.world.total_score)+","+str(sim.world.max_possible_score)+"\n")
    bar.finish()
