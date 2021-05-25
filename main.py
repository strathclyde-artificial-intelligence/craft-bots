import math

import view
import model


TICK_HZ = 60

WIDTH = 500
HEIGHT = 500
PADDING = 100

if __name__ == '__main__':
    world = model.World(WIDTH, HEIGHT)
    actors = []
    for _ in range(5):
        actors.append(model.Actor(world))
    root = view.tk.Tk()
    root.geometry(str(WIDTH + PADDING * 2 + 10) + "x" + str(HEIGHT + PADDING * 2 + 10))
    app = view.GUI(world, WIDTH, HEIGHT, PADDING, master=root)

    def keep_moving():
        for actor in actors:
            if not actor.state:
                actor.travel_rand()
        app.after(500, keep_moving)

    def refresh():
        world.run_tick()
        app.update_actors()
        app.after(math.ceil(1000/TICK_HZ), refresh)

    refresh()
    keep_moving()
    app.mainloop()
