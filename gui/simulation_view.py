import math
import dearpygui.dearpygui as dpg

from craftbots.entities.actor import Actor
from gui.palletes import palletes

class SimulationView:

    NODE_RADIUS = 20
    MINE_RADIUS = 3
    ACTOR_RADIUS = 4
    ACTOR_INNER_RADIUS = 3
    EDGE_THICKNESS = 2

    SIM_COLOURS = {0:"red", 1:"blue", 2:"orange", 3:"black", 4:"green"}


    def __init__(self, target_window):

        self.target_window = target_window
        self.view_width, self.view_height = 0, 0

        # window contents
        self.canvas = dpg.add_draw_layer(tag="simulation_drawing", parent=self.target_window)
        self.pallete = palletes['default']

        # handlers (drag, zoom, etc.)
        with dpg.handler_registry():
            dpg.add_mouse_drag_handler(callback=self.drag_sim, user_data=self)
            dpg.add_mouse_wheel_handler(callback=self.zoom_sim, user_data=self)
            dpg.add_mouse_release_handler(callback=self.mouse_up_sim, user_data=self)

        # sim distance per pixel
        self.scale = 0.5

        # offset of view
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.drag_x = 0.0
        self.drag_y = 0.0

        # world info
        self.world_started = False
        self.bounds = None

        # additional info
        self.labels = {
            "all": False,
            "nodes": False,
            "actors": True,
            "mines": False,
            "sites": False,
            "buildings": False
        }

    # =========== #
    # IO handlers #
    # =========== #

    @staticmethod
    def drag_sim(sender, data, sim_view):
        if dpg.is_item_hovered("simulation_window"):
            sim_view.drag_x = data[1]
            sim_view.drag_y = data[2]

    @staticmethod
    def mouse_up_sim(sender, data, sim_view):
        # reset view panning
        sim_view.offset_x = sim_view.offset_x + sim_view.drag_x
        sim_view.offset_y = sim_view.offset_y + sim_view.drag_y
        sim_view.drag_x = 0
        sim_view.drag_y = 0

    @staticmethod
    def zoom_sim(sender, data, sim_view):
        if dpg.is_item_hovered("simulation_window"):
            sim_view.scale = sim_view.scale + data*0.05

    # =============== #
    # Control methods #
    # =============== #

    def pallete_switch(self, sender, data):
        self.pallete = palletes[data]

    def box_checked(self, sender, data):
        # label checkbox
        if sender in self.labels:
            self.labels[sender] = data

    def fit_sim_to_view(self):
        scale_x = self.view_width / (self.bounds[1][0] - self.bounds[0][0] + 6*SimulationView.NODE_RADIUS)
        scale_y = self.view_height / (self.bounds[1][1] - self.bounds[0][1] + 6*SimulationView.NODE_RADIUS)
        self.scale = min(scale_x,scale_y)
        self.offset_x = (3*SimulationView.NODE_RADIUS - self.bounds[0][0]) * self.scale
        self.offset_y = (3*SimulationView.NODE_RADIUS - self.bounds[0][1]) * self.scale

    # =============== #
    # Utility methods #
    # =============== #

    def sim_to_view(self, pos):
        return (self.offset_x+self.drag_x) + pos[0] * self.scale, (self.offset_y+self.drag_y) + pos[1] * self.scale

    def view_to_sim(self, pos):
        return (pos[0] - (self.offset_x+self.drag_x)) / self.scale, (pos[1] - (self.offset_y+self.drag_y)) / self.scale

    # =============== #
    # Drawing methods #
    # =============== #

    def init_world(self, world_info):

        self.world_started = True

        # initialise bounds
        node_x = [node['x'] for node in world_info['nodes'].values()]
        node_y = [node['y'] for node in world_info['nodes'].values()]
        self.bounds = [ [min(node_x),min(node_y)], [max(node_x),max(node_y)]]

        self.fit_sim_to_view()

    def update_draw_list(self, world_info):

        # background
        self.view_width =  dpg.get_item_width(self.target_window)
        self.view_height = dpg.get_item_height(self.target_window)
        dpg.delete_item(self.canvas, children_only=True)
        dpg.draw_rectangle([-10, -10], [self.view_width+20, self.view_height+20], fill=self.pallete['background'], parent=self.canvas)

        if world_info is None: return
        if not self.world_started: self.init_world(world_info)

        # initialise bounds
        node_x = [node['x'] for node in world_info['nodes'].values()]
        node_y = [node['y'] for node in world_info['nodes'].values()]
        self.bounds = [ [min(node_x),min(node_y)], [max(node_x),max(node_y)]]

        # elements
        self.draw_nodes(world_info)
        self.draw_mines(world_info)
        self.draw_sites(world_info)
        self.draw_resources(world_info)
        self.draw_actors(world_info)

    def draw_nodes(self, world_info):

        # edges behind
        for key, edge in world_info['edges'].items():
            if edge['node_a'] not in world_info['nodes'] or edge['node_b'] not in world_info['nodes']:
                continue
            node_a = world_info['nodes'][edge['node_a']]
            node_b = world_info['nodes'][edge['node_b']]
            dpg.draw_line(
                self.sim_to_view([node_a['x'], node_a['y']]),
                self.sim_to_view([node_b['x'], node_b['y']]),
                color=self.pallete['background'], thickness=2*SimulationView.EDGE_THICKNESS*self.scale, parent=self.canvas)
            dpg.draw_line(
                self.sim_to_view([node_a['x'], node_a['y']]),
                self.sim_to_view([node_b['x'], node_b['y']]),
                color=self.pallete['node'], thickness=SimulationView.EDGE_THICKNESS*self.scale, parent=self.canvas)

        # nodes on top
        for key, node in world_info['nodes'].items():
            dpg.draw_circle(center=self.sim_to_view((node['x'],node['y'])),
                            radius=SimulationView.NODE_RADIUS*self.scale,
                            fill=self.pallete['node'], parent=self.canvas)
            if self.labels['nodes'] or self.labels['all']:
                anchor = self.sim_to_view((node['x'] + self.NODE_RADIUS, node['y'] - self.NODE_RADIUS))
                self.draw_label("node" + str(key), anchor)

    def draw_mines(self, world_info):
        for key, node in world_info['nodes'].items():
            angle_offset = key
            for i in range(len(node['mines'])):
                x = node['x'] + math.cos(2*math.pi*i/len(node['mines']) + angle_offset)*(SimulationView.NODE_RADIUS-SimulationView.MINE_RADIUS)
                y = node['y'] + math.sin(2*math.pi*i/len(node['mines']) + angle_offset)*(SimulationView.NODE_RADIUS-SimulationView.MINE_RADIUS)
                color = SimulationView.SIM_COLOURS[world_info['mines'][node['mines'][i]]['colour']]
                dpg.draw_circle(center=self.sim_to_view((x,y)),
                                radius=SimulationView.MINE_RADIUS * self.scale,
                                fill=self.pallete[color],
                                parent=self.canvas)
                if self.labels['mines'] or self.labels['all']:
                    anchor = self.sim_to_view((x + self.MINE_RADIUS, y - self.MINE_RADIUS))
                    self.draw_label("mine" + str(world_info['mines'][node['mines'][i]]['id']), anchor)


    def draw_sites(self, world_info):
        for key, node in world_info['nodes'].items():
            angle_offset = key
            for i in range(len(node['sites'])):
                x = node['x'] + math.cos(2 * math.pi * i / len(node['sites']) + angle_offset) * (SimulationView.NODE_RADIUS + SimulationView.MINE_RADIUS*3)
                y = node['y'] + math.sin(2 * math.pi * i / len(node['sites']) + angle_offset) * (SimulationView.NODE_RADIUS + SimulationView.MINE_RADIUS*3)
                dpg.draw_rectangle(
                    pmin = self.sim_to_view((x - SimulationView.MINE_RADIUS, y - SimulationView.MINE_RADIUS)),
                    pmax = self.sim_to_view((x + SimulationView.MINE_RADIUS, y + SimulationView.MINE_RADIUS)),
                    fill=self.pallete["node"],
                    parent=self.canvas
                )
                if node['sites'][i] in world_info['sites']:
                    progress = world_info['sites'][node['sites'][i]]["progress"] / world_info['sites'][node['sites'][i]]["needed_effort"]
                else: 
                    # catch site completion during draw
                    progress = 1

                dpg.draw_rectangle(
                    pmin=self.sim_to_view((x + 1 - SimulationView.MINE_RADIUS, y - (2*progress - 1)*(SimulationView.MINE_RADIUS-2))),
                    pmax=self.sim_to_view((x - 1 + SimulationView.MINE_RADIUS, y + SimulationView.MINE_RADIUS - 1)),
                    fill=self.pallete["background"],
                    parent=self.canvas
                )
                if self.labels['sites'] or self.labels['all']:
                    anchor = self.sim_to_view((x + self.MINE_RADIUS, y - self.MINE_RADIUS))
                    self.draw_label("site" + str(world_info['sites'][node['sites'][i]]['id']), anchor)

    def draw_resources(self, world_info):
        for key, node in world_info['nodes'].items():
            angle_offset = key
            for i in range(len(node['resources'])):
                x = node['x'] + math.cos(2*math.pi*i/max(10,len(node['resources'])) + angle_offset)*(SimulationView.NODE_RADIUS-3*SimulationView.MINE_RADIUS)
                y = node['y'] + math.sin(2*math.pi*i/max(10,len(node['resources'])) + angle_offset)*(SimulationView.NODE_RADIUS-3*SimulationView.MINE_RADIUS)
                color = SimulationView.SIM_COLOURS[world_info['resources'][node['resources'][i]]['colour']]
                dpg.draw_rectangle(
                    pmin=self.sim_to_view((x-SimulationView.MINE_RADIUS/2,y-SimulationView.MINE_RADIUS/2)),
                    pmax=self.sim_to_view((x+SimulationView.MINE_RADIUS/2,y+SimulationView.MINE_RADIUS/2)),
                    fill=self.pallete[color],
                    parent=self.canvas)

    def draw_actors(self, world_info):
        for key, actor in world_info['actors'].items():
                x = world_info['nodes'][actor['node']]['x']
                y = world_info['nodes'][actor['node']]['y']

                if actor['state']==Actor.MOVING or actor['state']==Actor.RECOVERING:
                    target_edge = actor['target'][0]
                    target_node = actor['target'][1]
                    p = actor['progress'] / world_info['edges'][target_edge]['length']
                    target_x = world_info['nodes'][target_node]['x']
                    target_y = world_info['nodes'][target_node]['y']
                    x = x * (1 - p) + target_x * p
                    y = y * (1 - p) + target_y * p
                dpg.draw_circle(center=self.sim_to_view((x,y)),
                                radius=SimulationView.ACTOR_RADIUS * self.scale,
                                fill=self.pallete['actor_border'],
                                parent=self.canvas)
                dpg.draw_circle(center=self.sim_to_view((x,y)),
                                radius=SimulationView.ACTOR_INNER_RADIUS * self.scale,
                                fill=self.pallete['actor_inner'],
                                parent=self.canvas)
                if self.labels['actors'] or self.labels['all']:
                    anchor = self.sim_to_view((x + self.ACTOR_RADIUS, y - self.ACTOR_RADIUS))
                    self.draw_label("actor" + str(key),anchor)


    def draw_label(self, label, anchor):
        dpg.draw_rectangle(
            pmin=anchor,
            pmax=(anchor[0] + 70, anchor[1] + 16),
            fill=self.pallete['text_background'],
            parent=self.canvas)
        dpg.draw_text((anchor[0] + 10, anchor[1]),
            text=label,
            color=self.pallete['text'],
            size=16,
            parent=self.canvas)
