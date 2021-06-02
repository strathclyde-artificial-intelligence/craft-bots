from world import World
import view
import threading
import random as r
import math


TICK_HZ = 60
WIDTH = 600
HEIGHT = 600
PADDING = 25
NODE_SIZE = 20


def default_scenario(world):
    for _ in range(5):
        world.add_actor(world.nodes[r.randint(0, world.nodes.__len__() - 1)])
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)


def start_simulation(use_gui=True, scenario=default_scenario):
    world = World(green_decay_time=120)
    scenario(world)
    if use_gui:
        gui = init_gui(world, call_repeatedly(1 / TICK_HZ, refresh_world, world))
        refresh_gui(gui)
        gui.mainloop()
    else:
        call_repeatedly(1 / TICK_HZ, refresh_world, world)


def refresh_gui(gui):

    def refresh_gui_wrapper():
        gui.update_model()
        refresh_gui(gui)

    gui.after(math.ceil(1000 / TICK_HZ), refresh_gui_wrapper)


def refresh_world(world):
    world.run_tick()


def call_repeatedly(interval, func, *args):
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)
    threading.Thread(target=loop).start()
    return stopped.set


def init_gui(world, stop_sim):
    root = view.tk.Tk()

    def on_close():
        stop_sim()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.geometry(str(WIDTH + PADDING * 2) + "x" + str(HEIGHT + PADDING * 2))
    return view.GUI(world, width=WIDTH, height=HEIGHT, padding=PADDING, node_size=NODE_SIZE, master=root)
