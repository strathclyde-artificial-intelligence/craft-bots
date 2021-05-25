import view
import model


if __name__ == '__main__':
    world = model.World()
    actor = model.Actor(world)
    root = view.tk.Tk()
    root.geometry("350x350")
    app = view.GUI(world, master=root)

    def keep_moving():
        actor.move_rand()
        app.after(500, keep_moving)

    def refresh():
        app.update_actors()
        app.after(30, refresh)

    refresh()
    keep_moving()
    app.mainloop()
