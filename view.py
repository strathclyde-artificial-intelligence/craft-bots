import tkinter as tk
import model


class GUI(tk.Frame):
    def __init__(self, world, width=350, height=350, padding=7, master=None, node_size=7):
        self.node_size = node_size
        self.padding = max(self.node_size, padding)
        self.width = width
        self.height = height
        super().__init__(master)
        self.master = master
        self.world = world
        self.graph = tk.Canvas(self, bg="black", height=self.height + self.padding * 2, width=self.width + self.padding * 2)
        self.graph.create_rectangle(self.padding - self.node_size, self.padding - self.node_size, self.width + self.padding + self.node_size,
                                    self.height + self.padding + self.node_size, fill="grey", width=0)
        self.graph.create_rectangle(self.padding, self.padding, self.width + self.padding,
                                    self.height + self.padding, fill="white", width=0)
        self.update_graph()
        self.actors = []
        for actor in self.world.actors:
            self.graph.create_oval(actor.node.x + self.padding - 3, actor.node.y + self.padding - 3, 
                                   actor.node.x + self.padding + 3, actor.node.y + self.padding + 3, fill="grey")
            self.actors.append((actor, self.graph.find_all()[-1:][0]))
        self.resources = []
        for resource in self.world.resources:
            if isinstance(resource.location, model.Node):
                node_x = resource.location.x + self.padding
                node_y = resource.location.y + self.padding
                self.draw_res_on_node(resource.location, resource,
                                      self.draw_resource_sprite(node_x, node_y, resource.get_colour_string()))
            if isinstance(resource.location, model.Actor):
                actor_id = self.get_sprite_id_of(resource.location)
                actor_x = self.graph.coords(actor_id)[0] + self.padding
                actor_y = self.graph.coords(actor_id)[1] + self.padding
                self.draw_res_on_actor(resource.location, self.draw_resource_sprite(actor_x, actor_y,
                                                                                    resource.get_colour_string()))
            self.resources.append((resource, self.graph.find_all()[-1:][0]))
        self.mines = []
        for mine in self.world.mines:
            self.mines.append((mine, self.draw_mine(mine.node.x, mine.node.y, mine.get_colour_string())))
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
            self.graph.create_oval(x - self.node_size, y - self.node_size, x + self.node_size, y + self.node_size, fill="white")

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

    def update_resources(self):
        for resource in self.world.resources:
            accounted = False
            for resource_pair in self.resources:
                if resource_pair[0] == resource:
                    accounted = True
            if not accounted:
                print("uh oh")
                node_x = resource.location.x + self.padding
                node_y = resource.location.y + self.padding
                self.draw_res_on_node(resource.location, resource,
                                      self.draw_resource_sprite(node_x, node_y, resource.get_colour_string()))
                self.resources.append((resource, self.graph.find_all()[-1:][0]))
        for resource_pair in self.resources:
            if isinstance(resource_pair[0].location, model.Node):
                self.draw_res_on_node(resource_pair[0].location, resource_pair[0], resource_pair[1])
            if isinstance(resource_pair[0].location, model.Actor):
                self.draw_res_on_actor(resource_pair[0].location, resource_pair[1])


    def update_model(self):
        self.update_actors()
        self.update_resources()

    def draw_resource_sprite(self, x, y, colour):
        return self.graph.create_polygon(x, y, x, y-1, x+1, y-1, x+1, y-2, x+2, y-2, x+2, y-4, x+2, y-2, x+3, y-2, x+3,
                                         y-1, x+4, y-1, x+4, y, x, y, fill=colour, outline=colour, width=1)

    def draw_res_on_node(self, node, resource, sprite_id):
        node_x = node.x
        node_y = node.y
        if resource.colour == 0:
            node_x -= 3
            node_y -= 14
        elif resource.colour == 1:
            node_x += 0
            node_y -= 8
        elif resource.colour == 2:
            node_x += 4
            node_y -= 12
        elif resource.colour == 3:
            node_x += 6
            node_y -= 6
        elif resource.colour == 4:
            node_x += 12
            node_y -= 4
        self.move_sprite_to(sprite_id, node_x + self.padding, node_y + self.padding)

    def draw_res_on_actor(self, actor, sprite_id):
        coord = self.get_coord_of(actor)
        self.move_sprite_to(sprite_id, coord[0], coord[1])

    def move_sprite_to(self, sprite_id, x, y):
        self.graph.move(sprite_id, x - self.graph.coords(sprite_id)[0], y - self.graph.coords(sprite_id)[1])

    def get_sprite_id_of(self, item):
        if isinstance(item, model.Actor):
            for actor_pair in self.actors:
                if actor_pair[0] is item:
                    return actor_pair[1]
            return -1

    def get_coord_of(self, item):
        return self.graph.coords(self.get_sprite_id_of(item))

    def draw_mine(self, node_x, node_y, colour):
        x = node_x + self.padding
        y = node_y + self.padding
        if colour == "red":
            x += 14
            y += 2
        elif colour == "blue":
            x += 12
            y += 10
        elif colour == "orange":
            x += 8
            y += 4
        elif colour == "black":
            x += 6
            y += 10
        elif colour == "green":
            x += 2
            y += 14
        return self.graph.create_oval(x - 2, y - 2, x + 2, y + 2, fill=colour, outline=colour, width=1)
