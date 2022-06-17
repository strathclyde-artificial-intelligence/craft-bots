import dearpygui.dearpygui as dpg

from craftbots.config.config_manager import Configuration
from craftbots.log_manager import Logger
from craftbots.simulation import Simulation
from gui.palletes import palletes
from gui.simulation_view import SimulationView
from gui.actor_view import ActorView
from gui.task_view import TaskView

class CraftBotsGUI:

    WINDOW_WIDTH  = 1600
    WINDOW_HEIGHT = 950
    SIDEBAR_WIDTH = 350
    CONFIG_WIDTH = 250

    def __init__(self, simulation: Simulation):

        # panels/windows
        self.primary_window = None
        self.config_window = None
        self.simulation_window = None
        self.actor_window = None
        self.task_window = None
        self.load_dialog = None
        self.save_dialog = None
        
        # simulation viewport and drawing
        self.sim_view = None
        self.actor_view = None
        self.task_view = None
        self.info_text = None
        self.command_count = 0
        self.time_bar = None
        self.time_text = None
        self.rate_slider = None
        self.score_text = None

        # model
        self.simulation = simulation
        self.world_info = None

        # callbacks
        self.reset_callback = self.reset_simulation
        self.pause_callback = simulation.pause_simulation
        self.start_callback = simulation.start_simulation

        # additional info
        self.log = {
            "log_node": True,
            "log_actor": True,
            "log_mine": True,
            "log_site": True,
            "log_building": True
        }

    def start_window(self):

        # prepare window
        dpg.create_context()
        dpg.create_viewport(title="CraftBots", resizable=True)
        dpg.set_viewport_small_icon("craftbots_icon.ico")
        dpg.set_viewport_large_icon("craftbots_icon.ico")

        # load font
        with dpg.font_registry():
            dpg.bind_font(dpg.add_font("resources/fonts/Roboto_Mono/static/RobotoMono-Regular.ttf", 20))
            dpg.set_global_font_scale(1.0)

        dpg.set_viewport_width(self.WINDOW_WIDTH)
        dpg.set_viewport_height(self.WINDOW_HEIGHT)

        # create internal panels
        with dpg.window(label="CraftBots", horizontal_scrollbar=True, no_scrollbar=False) as primary_window:
            self.primary_window = primary_window
            dpg.set_primary_window(self.primary_window, True)

            # simulation viewport
            sim_height = self.WINDOW_HEIGHT - 60
            sim_width = self.WINDOW_WIDTH - 2*self.SIDEBAR_WIDTH - 50
            with dpg.window(label="Simulation", tag="simulation_window",
                            no_scrollbar=True, no_resize=False, no_move=False, no_collapse=False, no_close=True,
                            pos=[self.SIDEBAR_WIDTH+20, 10], width=sim_width, height=sim_height) as simulation_window:
                self.simulation_window = simulation_window
                self.sim_view = SimulationView(self.simulation_window)

            with dpg.window(label="Actors", tag="actor_window",
                            no_scrollbar=False, no_resize=False, no_move=False, no_collapse=False, no_close=True,
                            pos=[self.SIDEBAR_WIDTH + sim_width + 30, 10], width=self.SIDEBAR_WIDTH, height=(sim_height-10)/2) as actor_window:
                self.actor_window = actor_window
                self.actor_view = ActorView(self.actor_window)

            with dpg.window(label="Tasks", tag="task_window",
                            no_scrollbar=False, no_resize=False, no_move=False, no_collapse=False, no_close=True,
                            pos=[self.SIDEBAR_WIDTH + sim_width + 30, 20 + (sim_height-10)/2], width=self.SIDEBAR_WIDTH, height=(sim_height-10)/2) as task_window:
                self.task_window = task_window
                self.task_view = TaskView(self.task_window)

            # sidebar
            with dpg.child_window(label="sidebar_window", width=self.SIDEBAR_WIDTH, autosize_y=True, pos=[10, 10]):

                # configuration options
                dpg.add_button(label="Configuration", tag="config", width=self.SIDEBAR_WIDTH, callback=self.config_callback)

                # sim controls
                dpg.add_button(label="Reset", width=self.SIDEBAR_WIDTH, callback=self.reset_callback)
                dpg.add_button(label="Start", width=self.SIDEBAR_WIDTH, callback=self.start_callback)
                dpg.add_button(label="Pause", width=self.SIDEBAR_WIDTH, callback=self.pause_callback)
                self.score_text = dpg.add_text("Score: 0")
                with dpg.group(horizontal=True):
                    self.time_text = dpg.add_text("Simulation Time: 0")
                self.time_bar = dpg.add_progress_bar(default_value=0)
                dpg.add_text("Simulation Rate")
                self.rate_slider = dpg.add_slider_float(tag="simulation_speed", default_value=30, clamped=True, min_value=0.1, max_value=200, callback=self.slider_callback)

                # view options
                with dpg.collapsing_header(label="View", default_open=False):
                    dpg.add_button(label="Reset Zoom",  width=self.SIDEBAR_WIDTH, callback=self.sim_view.fit_sim_to_view)
                    with dpg.group(horizontal=True):
                        dpg.add_text("Colors")
                        dpg.add_combo(items=list(palletes.keys()), default_value="default", callback=self.sim_view.pallete_switch)
                    with dpg.collapsing_header(label="Labels", default_open=True, leaf=True):
                        for label_name, checked in self.sim_view.labels.items():
                            dpg.add_checkbox(label=label_name, tag=label_name, default_value=checked, callback=self.sim_view.box_checked)

                # text console
                with dpg.collapsing_header(label="Info", default_open=True):
                    for name, checked in self.log.items():
                        dpg.add_checkbox(label=name, tag=name, default_value=checked, callback=self.box_checked)
                    with dpg.child_window(height=int(self.WINDOW_HEIGHT/4), border=True):
                        self.info_text = dpg.add_text("Interface started", wrap=-1, tracked=False, track_offset=1.0)

            # configuration window
            with dpg.window(label="Configuration", tag="config_window", show=False,
                                no_scrollbar=False, no_resize=False, no_move=False, no_collapse=True, no_close=False,
                                pos=[int(0.1 * self.WINDOW_WIDTH), int(0.1 * self.WINDOW_HEIGHT)],
                                width=int(0.7*self.WINDOW_WIDTH), height=int(0.7*self.WINDOW_HEIGHT)) as config_window:
                self.config_window = config_window
                with dpg.menu_bar():
                    with dpg.menu(label="File"):
                        dpg.add_menu_item(label="Save Config", tag="save_world", callback=self.save_configuration)
                        dpg.add_menu_item(label="Load Config", tag="load_world", callback=self.load_configuration)

                dpg.add_text("Most changes will take effect when the simulation is reset.")
                with dpg.tab_bar(label="config_tabs"):
                    for category, params in self.simulation.config.items():
                        with dpg.tab(label=category):
                            with dpg.child_window(border=True, horizontal_scrollbar=True):
                                for key, value in params.items():
                                    if key=="_description":
                                        # header description
                                        dpg.add_text(value, wrap=3*self.CONFIG_WIDTH)
                                        dpg.add_separator()
                                    elif "value" in value:
                                        # normal element
                                        self.add_config_element(key, value['value'], value['_description'])
                                    else:
                                        # nested element
                                        dpg.add_separator()
                                        with dpg.group(horizontal=True):
                                            dpg.add_text(key, indent=self.CONFIG_WIDTH+5)
                                            t = dpg.add_text("(?)")
                                            with dpg.tooltip(t): dpg.add_text(value['_description'], wrap=2 * self.CONFIG_WIDTH)
                                        for sub_key, sub_value in value.items():
                                            if sub_key != "_description": self.add_config_element(sub_key, sub_value, None)
                                        dpg.add_separator()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        # dpg.maximize_viewport()

        # main GUI loop
        log_length = 0
        while dpg.is_dearpygui_running():

            if self.simulation.world:
                world_info = self.simulation.world.get_world_info()

                # update simulation view
                self.sim_view.update_draw_list(world_info)
                self.actor_view.update_draw_list(world_info)
                self.task_view.update_draw_list(world_info)

                # update sim controls panel
                dpg.set_value(self.time_text, "Simulation Time: " + str(world_info['tick']))
                dpg.set_value(self.time_bar, world_info['tick'] / Configuration.get_value(self.simulation.config, 'sim_length'))
                dpg.set_value(self.score_text, "Score: " + str(world_info['score']))

            # update sidebar controls to match configuration
            dpg.set_value(self.rate_slider, float(Configuration.get_value(self.simulation.config,"simulation_rate")))

            # update info panel with logger text
            info = ""
            if log_length != len(Logger.log):
                log_length = len(Logger.log)
                for message in Logger.log:
                    info = info + "[" + str(message[0]) + "] " + "(" + message[1] + ") " + message[2] + "\n"
                dpg.set_value(self.info_text, info)
                
            # render
            dpg.render_dearpygui_frame()

    # ============================= #
    # Updating Configuration window #
    # ============================= #

    def update_config_element(self,key,value):
        if type(value) in [bool, int, float, str]:
            dpg.configure_item(key, default_value=value)
        elif type(value) == list or type(value) == tuple:
            for i in range(len(value)):
                dpg.configure_item(key+"@"+str(i), default_value=value[i])

    def add_config_element(self,key,value,description):
        with dpg.group(horizontal=True):
            if type(value) == bool:
                dpg.add_checkbox(label=key, tag=key, default_value=value, indent=self.CONFIG_WIDTH - dpg.mvCheckbox, callback=self.configure)
            elif type(value) == int or type(value) == float:
                 dpg.add_input_text(label=key, tag=key, default_value=value, decimal=True, width=self.CONFIG_WIDTH, callback=self.configure)
            elif type(value) == str:
                 dpg.add_input_text(label=key, tag=key, default_value=value, decimal=False, width=self.CONFIG_WIDTH, callback=self.configure)
            elif type(value) == list or type(value) == tuple:
                for i in range(len(value)):
                    dpg.add_input_text(label=None if i<len(value)-1 else key,
                                       tag=key+"@"+str(i),
                                       default_value=value[i], decimal=True,
                                       width=int((self.CONFIG_WIDTH - dpg.mvStyleVar_PopupRounding)/len(value)),
                                       callback=self.configure)
            if description:
                t = dpg.add_text("(?)")
                with dpg.tooltip(t): dpg.add_text(description, wrap=2*self.CONFIG_WIDTH)

    # ========= #
    # Callbacks #
    # ========= #

    def box_checked(self, sender, data):
        if sender in self.log:
            self.log[sender] = data

    def slider_callback(self, sender, data):
        # Alter the simulation rate using the slider instead of the config window.
        if sender=="simulation_speed":
            Configuration.set_value(self.simulation.config, "simulation_rate", data)
            self.update_config_element("simulation_rate", data)

    def config_callback(self, sender, data):
        # Configure button is pressed - display the window.
        if sender=="config": dpg.configure_item(self.config_window, show=True)

    def configure(self, sender, data):
        # Item set in configuration window.
        if "decimal" in dpg.get_item_configuration(sender):
            if data=='': data=0
            try:
                data = float(data)
            except ValueError:
                # user may have typed "-"
                data=0
        Configuration.set_value(self.simulation.config, sender, data)

    def reset_simulation(self, sender, data):
        # TODO fix agent threads that currently just die.
        # reset button pressed, reset sim and then fit map to window.
        self.simulation.reset_simulation()
        self.actor_view.reset()
        world_info = self.simulation.world.get_world_info()
        self.sim_view.init_world(world_info)
        self.sim_view.update_draw_list(world_info)
        self.sim_view.fit_sim_to_view()

    def save_configuration(self, sender, data):
        if self.save_dialog == None:
            with dpg.file_dialog(label='save_dialog',
                    callback=self.save_config_callback,
                    directory_selector=False,
                    width=CraftBotsGUI.WINDOW_WIDTH*0.7,
                    height=CraftBotsGUI.WINDOW_HEIGHT*0.7,
                    show=True,
                    default_path='./craftbots/config/',
                    default_filename='simulation_configuration.yaml',
                    modal=True,
                    id="save_dialog") as dialog:
                dpg.add_file_extension(".*")
                dpg.add_file_extension(".yaml", color=(150, 255, 150, 255), custom_text="[config]")
                self.save_dialog = dialog
        dpg.show_item("save_dialog")

    def save_config_callback(self, sender, data):
        file_path = data['file_path_name']
        if file_path[-2:]==".*":
            file_path = file_path[:-2] + '.yaml'
        print(file_path)
        Configuration.save_ini_file(self.simulation.config, file_path)
        
    def load_configuration(self, sender, data):
        if self.load_dialog == None:
            with dpg.file_dialog(label='load_dialog',
                    callback=self.load_config_callback,
                    directory_selector=False,
                    width=CraftBotsGUI.WINDOW_WIDTH*0.7,
                    height=CraftBotsGUI.WINDOW_HEIGHT*0.7,
                    show=True,
                    default_path='./craftbots/config/',
                    default_filename='simulation_configuration.yaml',
                    modal=True,
                    id="load_dialog") as dialog:
                dpg.add_file_extension(".*")
                dpg.add_file_extension(".yaml", color=(150, 255, 150, 255), custom_text="[config]")
                self.load_dialog = dialog
        dpg.show_item("load_dialog")

    def load_config_callback(self, sender, data):
        file_paths = list(data['selections'].values())
        if len(file_paths) > 0:
            self.simulation.config = Configuration.read_ini_file(file_paths[0])
            for category, params in self.simulation.config.items():
                for key, value in params.items():
                    if key=="_description":
                        continue
                    if "value" in value:
                        # normal element
                        self.update_config_element(key, value['value'])
                    else:
                        # nested element
                        for sub_key, sub_value in value.items():
                            if sub_key != "_description": self.update_config_element(sub_key, sub_value)
