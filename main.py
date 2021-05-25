import math

import view
import model


TICK_HZ = 30

if __name__ == '__main__':
    world = model.World()
    actor = model.Actor(world)
    root = view.tk.Tk()
    root.geometry("350x350")
    app = view.GUI(world, master=root)

    def keep_moving():
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
