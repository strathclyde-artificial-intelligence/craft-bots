import dearpygui.dearpygui as dpg

from craftbots.entities.actor import Actor
from gui.palletes import palletes
from gui.simulation_view import SimulationView


class ActorView:

    RESOURCE_SIZE = 18
    EDGE_THICKNESS = 2

    def __init__(self, target_window):

        self.target_window = target_window
        self.actor_count = 0
        self.resources = {}
        self.state = {}
        self.progress = {}
        self.pallete = palletes['default']


    def init_actors(self, world_info):

        self.resources.clear()
        self.state.clear()
        self.progress.clear()

        width = dpg.get_item_width(self.target_window)

        dpg.delete_item("actor_window", children_only=True)
        for key, actor in world_info['actors'].items():
            header = dpg.add_collapsing_header(label="Actor"+str(key), default_open=True, parent=self.target_window)
            self.state[key] = dpg.add_text(default_value="State: ",label="Actor"+str(key)+"State", parent=header)
            group = dpg.add_group(horizontal=True, parent=header)
            dpg.add_text(default_value="Progress:", parent=group)
            self.progress[key] = dpg.add_progress_bar(default_value=0.0, parent=group)
            group = dpg.add_group(horizontal=True, parent=header)
            dpg.add_text("Inventory:", parent=group)
            self.resources[key] = dpg.add_drawlist(width=width, height=ActorView.RESOURCE_SIZE+3, parent=group)

        self.actor_count = len(world_info['actors'])

    # =============== #
    # Utility methods #
    # =============== #

    @staticmethod
    def get_state_name(state):
        for key in Actor.__dict__:
            if type(Actor.__dict__[key])==int and Actor.__dict__[key]==state:
                return key
        return "UNKNOWN"

    def reset(self):

        self.resources.clear()
        self.state.clear()
        self.progress.clear()
        self.actor_count = 0

    # =============== #
    # Drawing methods #
    # =============== #

    def update_draw_list(self, world_info):

        if world_info is None: return

        if len(world_info['actors']) != self.actor_count:
            self.init_actors(world_info)

        for key, actor in world_info['actors'].items():
   
            # avoid GUI desync when resetting simulation
            if key not in self.state: continue

            # actor's state
            dpg.set_value(self.state[key], value="State: " + self.get_state_name(actor['state']))

            # progress bar
            progress, max_progress = self.get_max_progress(world_info,actor)
            dpg.set_value(self.progress[key], value=progress / max_progress)

            # inventory
            x, y = 0, 3
            dpg.delete_item(self.resources[key], children_only=True)
            for resource in actor['resources']:
                colour = SimulationView.SIM_COLOURS[world_info['resources'][resource]['colour']]
                dpg.draw_rectangle(pmin=(x, y), pmax=(x + ActorView.RESOURCE_SIZE, y + ActorView.RESOURCE_SIZE),
                                   fill=self.pallete["actor_inner"], parent=self.resources[key])
                dpg.draw_rectangle(pmin=(x + ActorView.EDGE_THICKNESS,y + ActorView.EDGE_THICKNESS),
                                   pmax=(x + ActorView.RESOURCE_SIZE - ActorView.EDGE_THICKNESS,
                                         y + ActorView.RESOURCE_SIZE - ActorView.EDGE_THICKNESS),
                                   fill=self.pallete[colour],parent=self.resources[key])
                x = x + ActorView.RESOURCE_SIZE*1.5

    @staticmethod
    def get_max_progress(world_info, actor):
        if actor['state'] == Actor.MOVING or actor['state'] == Actor.RECOVERING:
            return actor['progress'], world_info['edges'][actor['target'][0]]['length']

        if actor['state'] == Actor.DIGGING:
            mine = world_info['mines'][actor['target']]
            return mine['progress'], mine['max_progress']

        if actor['state'] == Actor.CONSTRUCTING:
            site = world_info['sites'][actor['target']]
            return site['progress'], site['needed_effort']

        return 0, 100
