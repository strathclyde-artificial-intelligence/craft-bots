import math
import view
import model
import random as r


TICK_HZ = 60

WIDTH = 600
HEIGHT = 600
PADDING = 25
NODE_SIZE = 20


def init_scenario():
    world = model.World(WIDTH, HEIGHT)
    model.Actor(world)
    # actors = []
    # for _ in range(5):
    #     actors.append(model.Actor(world))
    # model.Resource(world, world.nodes[0], 0)
    # model.Resource(world, world.nodes[0], 1)
    # model.Resource(world, world.nodes[0], 2)
    # model.Resource(world, world.nodes[0], 3)
    # model.Resource(world, world.nodes[0], 4)
    model.Mine(world, world.nodes[0], colour=0)
    # model.Mine(world, world.nodes[0], colour=1)
    # model.Mine(world, world.nodes[0], colour=2)
    # model.Mine(world, world.nodes[0], colour=3)
    # model.Mine(world, world.nodes[0], colour=4)
    # model.Site(world, world.nodes[0], colour=0)
    # model.Site(world, world.nodes[0], colour=1)
    # model.Site(world, world.nodes[0], colour=2)
    # model.Site(world, world.nodes[0], colour=3)
    # model.Site(world, world.nodes[0], colour=4)
    # model.Building(world, world.nodes[0], colour=0)
    # model.Building(world, world.nodes[0], colour=1)
    # model.Building(world, world.nodes[0], colour=2)
    # model.Building(world, world.nodes[0], colour=3)
    # model.Building(world, world.nodes[0], colour=4)

    return world
       
        
def init_gui(world):
    root = view.tk.Tk()
    root.geometry(str(WIDTH + PADDING * 2) + "x" + str(HEIGHT + PADDING * 2))
    return view.GUI(world, width=WIDTH, height=HEIGHT, padding=PADDING, node_size=NODE_SIZE, master=root)
    

def keep_moving(actors, sim_gui, world):
    actor = actors[0]
    if not world.tick % TICK_HZ:
        #print(world.edges)
        print("hello")
        if actor.node == world.nodes[0]:
            print("at node 0")
            if actor.inventory:
                print("moving to node 1")
                actor.travel_to(world.nodes[1])
            elif not actor.node.resources:
                print("mining")
                actor.mine_at(world.mines[0])
            elif not actor.inventory:
                print("collecting")
                actor.pick_up_resource(world.resources[0])

        else:
            print("at node 1")
            if not actor.node.sites:
                print("making site")
                actor.start_site(0)
            elif actor.node.sites[0].max_progress() > actor.node.sites[0].progress:
                print("building")
                actor.build_at(actor.node.sites[0])
            elif actor.inventory:
                print("depositing")
                actor.deposit(world.sites[0], world.resources[0])
            else:
                print("moving to node 0")
                actor.travel_to(world.nodes[0])
    # actors[0].mine_at(world.mines[r.randint(0, world.mines.__len__() - 1)])
    # for actor in actors:
    #     if not actor.state:
    #         if actor.inventory and world.tick > 200:
    #             actor.drop_everything()
    #         elif not actor.inventory and world.tick > 200 and actor.node.resources:
    #             actor.pick_up_resource(actor.node.resources[r.randint(0, actor.node.resources.__len__() - 1)])
    #         actor.travel_rand()


def refresh(world, sim_gui):
    keep_moving(world.actors, sim_gui, world)
    world.run_tick()
    sim_gui.update_model()

    def call_refresh():
        refresh(world, sim_gui)
    sim_gui.after(math.ceil(1000/TICK_HZ), call_refresh)


if __name__ == '__main__':
    new_world = init_scenario()
    gui = init_gui(new_world)
    refresh(new_world, gui)
    keep_moving(new_world.actors, gui, new_world)
    gui.mainloop()
