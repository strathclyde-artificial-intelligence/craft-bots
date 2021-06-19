from api.agent_api import AgentAPI
from entities.actor import Actor
from entities.node import Node
from entities.resource import Resource
from entities.task import Task

class RBA:

    STATE_START_SITE = 0
    STATE_COLLECT_RESOURCE = 1
    STATE_DELIVER_RESOURCE = 2
    STATE_BUILD = 3

    COLOUR = { 0: "red", 1: "blue", 2: "orange", 3: "black", 4: "green" }

    api: AgentAPI
    selected_actor: Actor
    selected_task: Task

    def __init__(self):

        self.api = None
        self.thinking = False
        self.state = RBA.STATE_START_SITE

        # model IDs
        self.actor_id = [] # list of objects
        self.task_id  = [] # list of objects
        self.node_id  = {} # dictionary of node ID to node object
        self.resources = []  # list of resources at latest node

        # fetching information
        self.get_actor_id = -1
        self.get_nodes_id = -1
        self.get_tasks_id = -1
        self.get_resources_id = -1

        # task information
        self.selected_actor = None
        self.selected_task = None

    def receive_results(self, results):
        for result in results:

            # set observed information
            if result[0] == self.get_actor_id:
                self.actor_id = result[1]
                self.selected_actor = result[1][0]
            if result[0] == self.get_tasks_id:
                self.task_id = result[1]
                self.selected_task = result[1][0]
            if result[0] == self.get_nodes_id:
                for node in result[1]: self.node_id[node.id] = node
            if result[0] == self.get_resources_id:
                self.resources = result[1]

        self.thinking = False

    def get_next_commands(self):

        # fetch information
        if not self.actor_id: self.get_actor_id = self.api.get_all_actors()
        if not self.node_id: self.get_nodes_id = self.api.get_all_nodes()
        if not self.task_id: self.get_tasks_id = self.api.get_tasks()

        if not self.selected_task: return
        if not self.selected_actor: return

        if self.selected_actor.state != 0: return

        aid = self.selected_actor.id
        # TODO no way to get node from actor ID
        node: Node
        node = self.selected_actor.node
        nid = node.id

        if self.state == RBA.STATE_START_SITE:

            # TODO no way to get the actor state from the actor ID (don't want to wait a tick)
            if nid == self.selected_task.node.id:
                # start site
                print("RBA: Starting the building site.")
                self.api.start_site(aid,self.selected_task.colour)
                self.state = RBA.STATE_COLLECT_RESOURCE
            else:
                # move to site node
                print("RBA: Moving to the task site.")
                path = self.get_path(node, destination_check=lambda n: n.id==self.selected_task.node.id)
                self.api.move_to(aid, path[0])
            return

        if self.state == RBA.STATE_COLLECT_RESOURCE:

            # TODO no way to get the required materials from the task (can only be done from the site).
            # TODO This means I can't plan to gather materials before starting the site!
            # TODO don't want to wait for a tick.
            if len(self.selected_task.node.sites)==0: return
            site = self.selected_task.node.sites[0]

            # TODO No clean way to convert site requirement index to into to colour.
            required_resources: list
            colour = next((i for i, x in enumerate(site.needed_resources) if x!=0), None)

            if colour in [m.colour for m in node.mines]:
                print("RBA: Mining for",RBA.COLOUR[colour],"resource.")
                mine = next((m for m in node.mines if m.colour == colour), None)
                self.api.mine_at(aid,mine.id)
                self.state = RBA.STATE_DELIVER_RESOURCE
            else:
                print("RBA: Moving to the closest",RBA.COLOUR[colour],"mine.")
                # TODO No way to get mine details from only mine ID
                path = self.get_path(node, destination_check=lambda n: colour in [m.colour for m in n.mines])
                self.api.move_to(aid, path[0])
            return

        if self.state == RBA.STATE_DELIVER_RESOURCE:

            # TODO this way of fetching information from the model is too convoluted
            # TODO the following 10 lines, including a yield, should be one line.
            if self.get_resources_id == -1:
                self.get_resources_id = self.api.get_resources_at(nid)
                return

            if len(self.resources) > 0:
                print("RBA: Picking up resource.")
                resource: Resource
                resource = self.resources[0]
                self.api.pick_up_resource(aid,resource.id)
                self.get_resources_id = -1
                self.resources.clear()

                print("RBA: Moving to the task site and dropping resource.")
                path = self.get_path(node, destination_check=lambda n: n.id == self.selected_task.node.id)
                if len(path)>0: self.api.move_to(aid, path[0])
                self.api.drop_all_resources(aid)
            return



    def get_path(self, src: Node, destination_check = lambda a: True):

        if destination_check(src): return []

        unvisited = {node: None for node in self.node_id.keys()}
        visited = {}
        parent = {}
        distance = 0
        unvisited[src.id] = distance

        current: Node
        current = src
        cid = current.id
        while True:

            # update distances to neighbouring vertices
            # TODO fetching neighbours not as command (don't want to wait a tick)
            for neighbour in current.get_adjacent_nodes():

                nid = neighbour.id
                if nid not in unvisited: continue

                # TODO using "1" in place of edge distance
                d = distance + 1
                if unvisited[nid] is None or unvisited[nid] > d:
                    unvisited[nid] = d
                    parent[nid] = cid

            # set this node to visited
            visited[cid] = distance
            del unvisited[cid]

            # if all nodes visited, finish
            if len(unvisited)==0: break

            # destination found, return path
            if destination_check(current):
                path = []
                while cid != src.id:
                    path.insert(0, cid)
                    cid = parent[cid]
                return path

            # select next node
            candidates = [node for node in unvisited.items() if node[1]]
            cid, distance = sorted(candidates, key=lambda x: x[1])[0]
            current = self.node_id[cid]

        print("ERROR: destination not connected in get path!")
        return None


