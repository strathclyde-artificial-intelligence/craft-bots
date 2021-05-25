import tkinter as tk


class GUI(tk.Frame):
    def __init__(self, world, width=350, height=350, padding=0, master=None):
        self.padding = max(0, padding)
        self.width = width
        self.height = height
        super().__init__(master)
        self.master = master
        self.world = world
        self.graph = tk.Canvas(self, bg="black", height=self.height + self.padding * 2, width=self.width + self.padding * 2)
        self.graph.create_rectangle(self.padding, self.padding, self.width + self.padding,
                                    self.height + self.padding, fill="white")
        self.update_graph()
        self.actors = []
        for actor in self.world.actors:
            self.graph.create_oval(actor.node.x + self.padding - 3, actor.node.y + self.padding - 3, 
                                   actor.node.x + self.padding + 3, actor.node.y + self.padding + 3, fill="red")
            self.actors.append((actor, self.graph.find_all()[-1:][0]))
        self.update_actors()
        self.graph.pack()
        self.pack()

    def update_graph(self):
        for edge in self.world.edges:
            x1 = edge.node_a.x + self.padding
            y1 = edge.node_a.y + self.padding
            x2 = edge.node_b.x + self.padding
            y2 = edge.node_b.y + self.padding
            self.graph.create_line(x1, y1, x2, y2, fill="blue")
        for node in self.world.nodes:
            x = node.x + self.padding
            y = node.y + self.padding
            self.graph.create_oval(x - 7, y - 7, x + 7, y + 7, fill="black")

    def update_actors(self):
        for actor_pair in self.actors:
            if actor_pair[0].state == 0:
                dx = actor_pair[0].node.x + self.padding - 3 - self.graph.coords(actor_pair[1])[0]
                dy = actor_pair[0].node.y + self.padding - 3 - self.graph.coords(actor_pair[1])[1]
                self.graph.move(actor_pair[1], dx, dy)
            if actor_pair[0].state == 1:
                new_x = (actor_pair[0].target[1].x - actor_pair[0].node.x) \
                        * (actor_pair[0].progress / actor_pair[0].target[0].length()) + actor_pair[0].node.x
                new_y = (actor_pair[0].target[1].y - actor_pair[0].node.y) \
                    * (actor_pair[0].progress / actor_pair[0].target[0].length()) + actor_pair[0].node.y
                dx = new_x + self.padding - 3 - self.graph.coords(actor_pair[1])[0]
                dy = new_y + self.padding - 3 - self.graph.coords(actor_pair[1])[1]
                self.graph.move(actor_pair[1], dx, dy)
