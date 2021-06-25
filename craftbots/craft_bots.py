from craftbots.world import World
from api.agent_api import AgentAPI
from agents.blank_agent import BlankAgent
import craftbots.view as view
import threading
import random as r
import math
import time

PADDING = 25
NODE_SIZE = 20

simulation_stop = None
sim_stopped = False
gui_updating = False
root = None
start_time = time.time()


def default_scenario(world, modifiers, world_gen_modifiers):
    for _ in range(modifiers["NUM_OF_ACTORS"]):
        world.add_actor(world.nodes[r.randint(0, world.nodes.__len__() - 1)])
        
    for _ in range(world_gen_modifiers["NUM_OF_RED_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
        
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
        
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
        
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
        
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_SITES"]):
        world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_BUILDINGS"]):
        world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)


def start_simulation(agent=None, use_gui=True, scenario=default_scenario):
    world_gen_modifiers = get_world_gen_modifiers()
    modifiers = get_modifiers()
    rules = get_rules()
    world = World(modifiers, world_gen_modifiers, rules)
    scenario(world, modifiers, world_gen_modifiers)

    if agent is not None:
        agent.api = AgentAPI(world)
        agent.world_info = world.get_world_info()
    else:
        agent = BlankAgent()
        agent.api = AgentAPI(world)
        agent.world_info = world.get_world_info()

    global simulation_stop
    simulation_stop = call_repeatedly(1 / rules["TICK_HZ"], refresh_world, world, agent)

    if use_gui:
        gui = init_gui(world)
        refresh_gui(gui, rules["TICK_HZ"])
        gui.mainloop()


def refresh_gui(gui, tick_hz):

    def refresh_gui_wrapper():
        if not sim_stopped:
            gui.update_model()
            refresh_gui(gui, tick_hz)

    gui.after(math.ceil(1000 / tick_hz), refresh_gui_wrapper)


def refresh_world(world, agent):
    if not agent.thinking:
        agent.thinking = True
        agent.world_info = world.get_world_info()
        agent_thread = threading.Thread(target=agent.get_next_commands)
        agent_thread.start()
    world.run_tick()
    if world.command_results:
        agent.receive_results(world.command_results)
        world.command_results = []
    agent.api.num_of_current_commands = 0
    if world.rules["TIME_LENGTH_TYPE"] == 0:
        if time.time() - world.rules["SIM_LENGTH"] >= start_time:
            on_close()
    else:
        if world.tick >= world.rules["SIM_LENGTH"] * world.rules["TICK_HZ"]:
            on_close()


def call_repeatedly(interval, func, *args):
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)
    threading.Thread(target=loop, daemon=True).start()
    return stopped.set


def init_gui(world):
    global root
    root = view.tk.Tk()

    width = world.world_gen_modifiers["WIDTH"]
    height = world.world_gen_modifiers["HEIGHT"]
    root.title("CraftBots")
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.geometry(str(width + PADDING * 2) + "x" + str(height + PADDING * 2))
    return view.GUI(world, width=width, height=height, padding=PADDING, node_size=NODE_SIZE, master=root)


def on_close():
    print("Simulation time up")
    global sim_stopped, simulation_stop
    simulation_stop()
    sim_stopped = True
    if root is not None:
        try:
            root.destroy()
        except:
            on_close()
    exit()


def get_world_gen_modifiers():
    default_world_gen_file = open("craftbots/initialisation_files/default_world_gen_modifiers", "r")
    world_gen_modifiers = {}
    for line in default_world_gen_file:
        data = line.strip("\n").split(" ")
        if data[0] != '' and data[0][0] != "#":
            try:
                world_gen_modifiers[data[0]] = int(data[2])
                continue
            except ValueError:
                try:
                    world_gen_modifiers[data[0]] = float(data[2])
                    continue
                except ValueError:
                    temp = []
                    for value in data[2].split(","):
                        temp.append(int(value))
                    world_gen_modifiers[data[0]] = temp
    try:
        world_gen_file = open("craftbots/initialisation_files/world_gen_modifiers", "r")
        for line in world_gen_file:
            data = line.strip("\n").split(" ")
            if data[0] != '' and data[0][0] != "#":
                try:
                    world_gen_modifiers[data[0]] = int(data[2])
                    continue
                except ValueError:
                    try:
                        world_gen_modifiers[data[0]] = float(data[2])
                        continue
                    except ValueError:
                        temp = []
                        for value in data[2].split(","):
                            temp.append(int(value))
                        world_gen_modifiers[data[0]] = temp
    except FileNotFoundError:
        pass
    return world_gen_modifiers


def get_modifiers():
    default_file = open("craftbots/initialisation_files/default_modifiers", "r")
    modifiers = {}
    for line in default_file:
        data = line.strip("\n").split(" ")
        if data[0] != '' and data[0][0] != "#":
            try:
                modifiers[data[0]] = int(data[2])
                continue
            except ValueError:
                try:
                    modifiers[data[0]] = float(data[2])
                    continue
                except ValueError:
                    temp = []
                    for value in data[2].split(","):
                        temp.append(int(value))
                    modifiers[data[0]] = temp
    default_file.close()
    try:
        file = open("craftbots/initialisation_files/modifiers", "r")
        for line in file:
            data = line.strip("\n").split(" ")
            if data[0] != '' and data[0][0] != "#":
                try:
                    modifiers[data[0]] = int(data[2])
                    continue
                except ValueError:
                    try:
                        modifiers[data[0]] = float(data[2])
                        continue
                    except ValueError:
                        temp = []
                        for value in data[2].split(","):
                            temp.append(int(value))
                        modifiers[data[0]] = temp
        file.close()
    except FileNotFoundError:
        pass
    return modifiers


def get_rules():
    default_file = open("craftbots/initialisation_files/default_rules", "r")
    rules = {}
    for line in default_file:
        data = line.strip("\n").split(" ")
        if data[0] != '' and data[0][0] != "#":
            try:
                rules[data[0]] = int(data[2])
                continue
            except ValueError:
                try:
                    rules[data[0]] = float(data[2])
                    continue
                except ValueError:
                    temp = []
                    for value in data[2].split(","):
                        temp.append(int(value))
                    rules[data[0]] = temp
    default_file.close()
    try:
        file = open("craftbots/initialisation_files/rules", "r")
        for line in file:
            data = line.strip("\n").split(" ")
            if data[0] != '' and data[0][0] != "#":
                try:
                    rules[data[0]] = int(data[2])
                    continue
                except ValueError:
                    try:
                        rules[data[0]] = float(data[2])
                        continue
                    except ValueError:
                        temp = []
                        for value in data[2].split(","):
                            temp.append(int(value))
                        rules[data[0]] = temp
        file.close()
    except FileNotFoundError:
        pass
    return rules
