import pprint

from os import system
import time
import numpy as np
from agents.agent import Agent
from api import agent_api
from craftbots.entities.actor import Actor
from craftbots.log_manager import Logger
import sys

class RBAgent(Agent):

    def __init__(self):

        super().__init__()

        # task to actor assignment and list of unassigned actors
        self.task_actors : dict = {}
        self.free_actors = []

        # map information for pathfiding
        self.nodes = []
        self.edges = {}
        self.paths = {}

    def get_next_commands(self):
        """
        Sends commands to the agent API until the simulation is completed. Does not work with lockstep.
        """

        self.api: agent_api.AgentAPI
        self.world_info : dict

        # prepare free actors
        self.task_actors.clear()
        self.free_actors.clear()
        for actor_id in self.world_info["actors"]:
            self.free_actors.append(actor_id)

        # find all shortest paths
        self.prepare_graph()

        Logger.info("Agent", "Starting control.")
        while not self.simulation_complete:

            # assign actors to tasks
            for task_id, task in self.world_info['tasks'].items(): 
                
                # task complete, free actor
                if task["completed"]:
                    if task_id in self.task_actors:
                        Logger.info("Agent", "Task "+str(task_id)+" completed.")
                        self.free_actors.append(self.task_actors[task_id])
                        del self.task_actors[task_id]
                    continue

                # task already assigned
                if task_id in self.task_actors: continue

                # assign task
                if len(self.free_actors) > 0:
                    actor_id = self.free_actors.pop()
                    self.task_actors[task_id] = actor_id
                    Logger.info("Agent", "Assigning agent "+str(actor_id)+" to task "+str(task_id))

            # check for idle assigned actors and take actions
            for task_id, actor_id in self.task_actors.items():
                if self.api.get_field(actor_id, "state") == Actor.IDLE:
                    self.take_action(task_id, actor_id)

            time.sleep(0.02)                    

        Logger.info("Agent", "Finished.")

    def take_action(self, task_id, actor_id):
        
        site_id = self.api.get_field(task_id, "site")
        target_node = self.api.get_field(task_id, "node")
        actor_node = self.api.get_field(actor_id, "node")

        # if the site is not started and the agent is at the node, start the site.
        if site_id == None and actor_node == target_node:
            Logger.info("Agent", "Start site: actor{id} node{node} task{task}.".format(id=actor_id, node=target_node, task=task_id))
            self.api.start_site(actor_id, task_id)
            return

        # if the site is not started, move to the target node.
        if site_id == None and actor_node != target_node:
            next_node = self.paths[actor_node][target_node]
            Logger.info("Agent", "Move: actor{id} node{node}.".format(id=actor_id, node=next_node))
            self.api.move_to(actor_id, next_node)
            return

        # if the site has all resources deposited, construct.
        site_resources = self.api.get_field(site_id, 'deposited_resources')
        task_resources = self.api.get_field(site_id, 'needed_resources')

        # check if site is completed (race condition)
        if site_resources==None or task_resources==None:
            return

        remaining_resources = [a - b for a,b in zip(task_resources,site_resources)]
        if sum(remaining_resources)<=0 and actor_node == target_node:
            Logger.info("Agent", "Construct: actor{id} site{site}.".format(id=actor_id, site=site_id))
            self.api.construct_at(actor_id, site_id)
            return

        # if the agent is carrying a required resource at the site, deposit.
        actor_resources = self.api.get_field(actor_id, 'resources')
        matching_resources = [ resource_id for resource_id in actor_resources if self.api.get_field(resource_id,'colour') is not None and remaining_resources [self.api.get_field(resource_id,'colour')]>0 ]
        if actor_node == target_node and len(matching_resources)>0:
            Logger.info("Agent", "Deposit: actor{id} site{site} resource{resource}.".format(id=actor_id, site=site_id, resource=matching_resources[0]))
            self.api.deposit_resources(actor_id,site_id,matching_resources[0])
            return

        # if the agent is carrying a required resource, move to the site.
        if actor_node != target_node and len(matching_resources)>0:
            next_node = self.paths[actor_node][target_node]
            Logger.info("Agent", "Move: actor{id} node{node}.".format(id=actor_id, node=next_node))
            self.api.move_to(actor_id, next_node)
            return

        # if the agent is at a required resource, pick it up.
        node_resources = self.api.get_field(actor_node,'resources')
        matching_node_resources = [ resource_id for resource_id in node_resources if remaining_resources [self.api.get_field(resource_id,'colour')]>0 ]
        if len(matching_node_resources) > 0:
            Logger.info("Agent", "Pickup: actor{id} resource{resource}.".format(id=actor_id, resource=matching_node_resources[0]))
            self.api.pick_up_resource(actor_id, matching_node_resources[0])
            return

        # if the agent is at the mine of a required resource, dig.
        node_mines = self.api.get_field(actor_node,'mines')
        matching_mines = [ mine_id for mine_id in node_mines if remaining_resources [self.api.get_field(mine_id,'colour')]>0 ]
        if len(matching_mines) > 0:
            Logger.info("Agent", "Mine: actor{id} mine{mine}.".format(id=actor_id, mine=matching_mines[0]))
            self.api.dig_at(actor_id, matching_mines[0])
            return

        # move to the mine of a required resource.
        min_distance = -1
        best_node = None
        for node in self.nodes:
            node_mines = self.api.get_field(node, "mines")
            matching_mines = [ mine_id for mine_id in node_mines if remaining_resources [self.api.get_field(mine_id,'colour')]>0 ]
            if len(matching_mines) > 0 and (min_distance<0 or self.edges[actor_node][node] < min_distance):
                min_distance = self.edges[actor_node][node]
                best_node = node
        if best_node != None:
            next_node = self.paths[actor_node][best_node]
            Logger.info("Agent", "Move: actor{id} node{node}.".format(id=actor_id, node=next_node))
            self.api.move_to(actor_id, next_node)
            return
        
        Logger.info("Agent", "Actor couldn't find an action.")


    def prepare_graph(self):
        
        self.nodes = []
        self.edges = {}
        self.paths = {}

        # add nodes and self distances
        self.nodes.extend(self.world_info['nodes'].keys())
        for node in self.nodes:
            self.edges[node] = {node: 0}
            self.paths[node] = {}

        for edge in self.world_info['edges'].values():
            # remember distances
            self.edges[edge['node_a']][edge['node_b']] = edge['length']
            self.edges[edge['node_b']][edge['node_a']] = edge['length']
            # remember shortest paths
            self.paths[edge['node_b']][edge['node_a']] = edge['node_a']
            self.paths[edge['node_a']][edge['node_b']] = edge['node_b']

        # floyd-warshall, recalling paths
        for i in self.nodes:
            for j in self.nodes:
                for k in self.nodes:
                    if k not in self.edges[i]: continue
                    if j not in self.edges[k]: continue
                    if j not in self.edges[i] or self.edges[i][j] > self.edges[i][k] + self.edges[k][j]:
                        self.edges[i][j] = self.edges[i][k] + self.edges[k][j]
                        self.paths[i][j] = self.paths[i][k]
