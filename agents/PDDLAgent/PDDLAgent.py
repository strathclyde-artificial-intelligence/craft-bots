import random
import time

from agents.PDDLAgent.PDDLInterface import PDDLInterface
from api import agent_api

class PDDLAgent:

    class STATE:
        READY     = 0
        PLANNING  = 1
        EXECUTING = 2
        # this state skips the frame after
        # an action is dispatched to avoid
        # misreading the actor state.
        WAITING   = 3
        DONE      = 4

    api: agent_api.AgentAPI
    pddl_interface: PDDLInterface

    def __init__(self):

        self.verbose = 1

        # API information
        self.world_info = None
        self.thinking = False
        self.api = None
        self.command_results = []

        # planning status
        self.plan = []
        self.state = PDDLAgent.STATE.READY

    def receive_results(self, results):
        self.command_results.extend(results)

    def get_next_commands(self):

        if self.state == PDDLAgent.STATE.READY:
            self.state = PDDLAgent.STATE.PLANNING
            PDDLInterface.writeProblem(world_info=self.world_info)
            PDDLInterface.generatePlan("agents/PDDLAgent/domain-craft-bots.pddl", "agents/PDDLAgent/problem.pddl", "agents/PDDLAgent/plan.pddl", verbose=True)
            self.plan = PDDLInterface.readPDDLPlan('agents/PDDLAgent/plan.pddl')
            self.state = PDDLAgent.STATE.EXECUTING

        elif self.state == PDDLAgent.STATE.EXECUTING:
            if len(self.plan) == 0:
                self.state = PDDLAgent.STATE.DONE
            else:
                action, params = self.plan[0]
                # check if actor is ready
                if self.world_info['actors'][params[0]]['state'] == 0:
                    self.plan.pop(0)
                    self.send_action(action, params)
                    self.state = PDDLAgent.STATE.WAITING

        elif self.state == PDDLAgent.STATE.WAITING:
            self.state = PDDLAgent.STATE.EXECUTING

        self.thinking = False

    def send_action(self, action, params):
        # move (?a - actor ?from ?to - waypoint)
        if action == 'move':
            if self.verbose > 0: print("(PDDLAgent) Moving")
            self.api.move_to(params[0], params[2])

        # mine (?a - actor ?w - waypoint ?t - resource-type)
        if action == 'mine':
            if self.verbose > 0: print("(PDDLAgent) Digging")
            # get mine ID from resource type
            mines = [m for m in self.world_info['nodes'][params[1]]['mines'] if self.world_info['mines'][m]['colour'] == params[2]]
            self.api.dig_at(params[0], mines[0])

        # pick-up (?a - actor ?w - waypoint ?t - resource-type)
        if action == 'pick-up':
            if self.verbose > 0: print("(PDDLAgent) Picking up")
            # get resource ID from resource type
            resources = [r for r in self.world_info['nodes'][params[1]]['resources'] if self.world_info['resources'][r]['colour'] == params[2]]
            self.api.pick_up_resource(params[0], resources[0])

        # drop (?a - actor ?w - waypoint ?t - resource-type)
        if action == 'drop':
            if self.verbose > 0: print("(PDDLAgent) Dropping")
            # get resource ID from resource type
            resources = [r for r in self.world_info['actors'][params[0]]['resources'] if self.world_info['resources'][r]['colour'] == params[2]]
            self.api.drop_resource(params[0], resources[0])

        # start-building (?a - actor ?w - waypoint ?b - building)
        if action == 'start-building':
            if self.verbose > 0: print("(PDDLAgent) Starting Site")
            self.api.start_site(params[0], self.world_info['tasks'][params[2]]['colour'])

        # deposit (?a - actor ?w - waypoint ?b - building ?t - resource-type)
        if action == 'deposit':
            if self.verbose > 0: print("(PDDLAgent) Depositing")
            # get resource ID from resource type
            resources = [r for r in self.world_info['actors'][params[0]]['resources'] if self.world_info['resources'][r]['colour'] == params[3]]
            sites = [s for s in self.world_info['nodes'][params[1]]['sites'] if self.world_info['sites'][s]['colour'] == params[3]]
            self.api.deposit_resources(params[0], sites[0], resources[0])

        # complete-building (?a - actor ?w - waypoint ?b - building)
        if action == 'complete-building':
            if self.verbose > 0: print("(PDDLAgent) Building")
            colour = self.world_info['tasks'][params[2]]['colour']
            sites = [s for s in self.world_info['nodes'][params[1]]['sites'] if self.world_info['sites'][s]['colour'] == colour]
            self.api.construct_at(params[0], sites[0])


