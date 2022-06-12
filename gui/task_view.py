import dearpygui.dearpygui as dpg

from craftbots.entities.task import Task
from gui.palletes import palletes
from gui.simulation_view import SimulationView


class TaskView:

    RESOURCE_SIZE = 18
    EDGE_THICKNESS = 2

    def __init__(self, target_window):

        self.target_window = target_window
        self.task_count = 0
        self.headers = {}
        self.resources = {}
        self.node = {}
        self.score = {}
        self.difficulty = {}
        self.deadline = {}
        self.pallete = palletes['default']


    def init_tasks(self, world_info):

        self.resources.clear()
        self.node.clear()
        self.score.clear()
        self.difficulty.clear()

        width = dpg.get_item_width(self.target_window)

        dpg.delete_item("task_window", children_only=True)
        for key, task in world_info['tasks'].items():

            header = dpg.add_collapsing_header(label="Task"+str(key), default_open=True, parent=self.target_window, closable=False)
            self.headers[key] = header

            group = dpg.add_group(horizontal=True, parent=header)
            self.difficulty[key] = dpg.add_text(default_value="Difficulty: ",label="Task"+str(key)+"Difficulty", parent=header)
            
            group = dpg.add_group(horizontal=True, parent=header)
            self.node[key] = dpg.add_text(default_value="Target Node: ",label="Task"+str(key)+"Node", parent=header)
            
            group = dpg.add_group(horizontal=True, parent=header)
            dpg.add_text("Required Resources:", parent=group)
            self.resources[key] = dpg.add_drawlist(width=width, height=TaskView.RESOURCE_SIZE+3, parent=group)
            
            group = dpg.add_group(horizontal=True, parent=header)
            self.score[key] = dpg.add_text(default_value="Score: ",label="Task"+str(key)+"Score", parent=header)

            if task['deadline'] > 0: 
                group = dpg.add_group(horizontal=True, parent=header)
                self.deadline[key] = dpg.add_text(default_value="Deadline: ",label="Task"+str(key)+"Deadline", parent=header)

        self.task_count = len(world_info['tasks'])

    # =============== #
    # Utility methods #
    # =============== #

    @staticmethod
    def get_difficulty_name(state):
        for key in Task.__dict__:
            if type(Task.__dict__[key])==int and Task.__dict__[key]==state:
                return key
        return "UNKNOWN"

    def reset(self):

        self.resources.clear()
        self.node.clear()
        self.score.clear()
        self.difficulty.clear()
        self.deadline.clear()
        self.task_count = 0

    # =============== #
    # Drawing methods #
    # =============== #

    def update_draw_list(self, world_info):

        if world_info is None: return

        if len(world_info['tasks']) != self.task_count:
            self.init_tasks(world_info)

        for key, task in world_info['tasks'].items():

            # avoid GUI desync crash
            if key not in self.resources:
                self.init_tasks(world_info)
                return

            if task['completed']:
                if dpg.does_item_exist(self.headers[key]):
                    dpg.delete_item(self.headers[key])
                continue

            # difficulty
            dpg.set_value(self.difficulty[key], value="Difficulty: " + str(TaskView.get_difficulty_name(task['difficulty'])))

            # node
            dpg.set_value(self.node[key], value="Target Node: node" + str(task['node']))

            # needed resources
            x, y = 0, 3
            for resource_type, resource_amnt in enumerate(task['needed_resources']):
                for i in range(resource_amnt):
                    colour = SimulationView.SIM_COLOURS[resource_type]
                    dpg.draw_rectangle(pmin=(x, y), pmax=(x + TaskView.RESOURCE_SIZE, y + TaskView.RESOURCE_SIZE),
                                    fill=self.pallete["actor_inner"], parent=self.resources[key])
                    dpg.draw_rectangle(pmin=(x + TaskView.EDGE_THICKNESS,y + TaskView.EDGE_THICKNESS),
                                    pmax=(x + TaskView.RESOURCE_SIZE - TaskView.EDGE_THICKNESS,
                                            y + TaskView.RESOURCE_SIZE - TaskView.EDGE_THICKNESS),
                                    fill=self.pallete[colour],parent=self.resources[key])
                    x = x + TaskView.RESOURCE_SIZE*1.5

            # Score
            dpg.set_value(self.score[key], value="Score: " + str(task['score']))
            
            # Deadline
            if task['deadline'] > 0: dpg.set_value(self.deadline[key], value="Deadline: " + str(task['deadline']))
