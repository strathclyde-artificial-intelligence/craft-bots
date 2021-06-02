import math
import view
from world import World
import random as r
from node import Node
from edge import Edge
from actor import Actor
from resource import Resource
from site import Site
from building import Building
from mine import Mine
import craft_bots

TICK_HZ = 60

WIDTH = 600
HEIGHT = 600
PADDING = 25
NODE_SIZE = 20


def init_scenario():
    world = World(WIDTH, HEIGHT)
    Actor(world, world.nodes[0])
    # actors = []
    # for _ in range(5):
    #     actors.append(model.Actor(world))
    # Resource(world, world.nodes[0], 0)
    # Resource(world, world.nodes[0], 1)
    # Resource(world, world.nodes[0], 2)
    # Resource(world, world.nodes[0], 3)
    # Resource(world, world.nodes[0], 4)
    Mine(world, world.nodes[0], colour=0)
    Mine(world, world.nodes[0], colour=1)
    Mine(world, world.nodes[0], colour=2)
    Mine(world, world.nodes[0], colour=3)
    Mine(world, world.nodes[0], colour=4)
    # Site(world, world.nodes[0], colour=0)
    # Site(world, world.nodes[0], colour=1)
    # Site(world, world.nodes[0], colour=2)
    # Site(world, world.nodes[0], colour=3)
    # Site(world, world.nodes[0], colour=4)
    # Building(world, world.nodes[0], colour=0)
    # Building(world, world.nodes[0], colour=1)
    # Building(world, world.nodes[0], colour=2)
    # Building(world, world.nodes[0], colour=3)
    # Building(world, world.nodes[0], colour=4)

    return world
       
        
def init_gui(world):
    root = view.tk.Tk()
    root.geometry(str(WIDTH + PADDING * 2) + "x" + str(HEIGHT + PADDING * 2))
    return view.GUI(world, width=WIDTH, height=HEIGHT, padding=PADDING, node_size=NODE_SIZE, master=root)
    

def overseer(sim_gui, world):
    actors = world.get_all_actors()
    actors[0].travel_rand()
    # actors[0].mine_at(actors[0].node.mines[0])
    # actor1 = actors[0]
    # if not world.tick % TICK_HZ:
    #     #print(world.edges)
    #     print("hello")
    #     if actor1.node == world.nodes[0]:
    #         print("at node 0")
    #
    #
    #     else:
    #         print("at node 1")
    #         if not actor1.node.sites:
    #             print("making site")
    #             actor1.start_site(0)
    #         elif actor1.node.sites[0].max_progress() > actor1.node.sites[0].progress:
    #             print("building")
    #             actor1.build_at(actor1.node.sites[0])
    #         elif actor1.resources:
    #             print("depositing")
    #             actor1.deposit(world.sites[0], world.resources[0])
    #         else:
    #             print("moving to node 0")
    #             actor1.travel_to(world.nodes[0])

    # actors[0].mine_at(world.mines[r.randint(0, world.mines.__len__() - 1)])
    # for actor in actors:
    #     if not actor.state:
    #         if actor.inventory and world.tick > 200:
    #             actor.drop_everything()
    #         elif not actor.inventory and world.tick > 200 and actor.node.resources:
    #             actor.pick_up_resource(actor.node.resources[r.randint(0, actor.node.resources.__len__() - 1)])
    #         actor.travel_rand()


def refresh(world, sim_gui):
    overseer(sim_gui, world)
    world.run_tick()
    sim_gui.update_model()

    def call_refresh():
        refresh(world, sim_gui)
    sim_gui.after(math.ceil(1000/TICK_HZ), call_refresh)


if __name__ == '__main__':
    craft_bots.start_simulation()
    # new_world = init_scenario()
    # gui = init_gui(new_world)
    # refresh(new_world, gui)
    # gui.mainloop()
