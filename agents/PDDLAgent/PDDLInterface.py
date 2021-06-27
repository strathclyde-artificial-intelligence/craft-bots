from collections.abc import Set
from typing import List, Tuple, Union

import requests

class PDDLInterface:

    COLOURS = ['red', 'blue', 'orange', 'black', 'green']
    ACTIONS = ['move', 'mine', 'pick-up', 'drop', 'start-building', 'deposit', 'complete-building']

    @staticmethod
    def writeProblem(world_info, file="agents/PDDLAgent/problem.pddl"):

        with open(file, "w") as f:
            f.write("(define(problem craft-bots-problem)\n")
            f.write("(:domain craft-bots)\n")

            f.write("(:objects\n ")

            for actor in world_info['actors']:
                f.write("a"+str(actor)+" ")
                break
            f.write("- actor\n ")

            for node in world_info['nodes']:
                f.write("w"+str(node)+" ")
            f.write("- waypoint\n ")

            for task in world_info['tasks']:
                f.write("b"+str(task)+" ")
                break
            f.write("- building\n ")

            f.write(")\n")
            # end of objects

            f.write("(:init\n")

            f.write("\n  ;; actors\n")
            for actor in world_info['actors']:
                f.write("  (at a"+str(actor)+" w"+str(world_info['actors'][actor]['node'])+")\n")
                for colour in PDDLInterface.COLOURS:
                    f.write("  (= (inventory a" + str(actor) + " " + colour + ") 0)\n")
                break

            f.write("\n  ;; mines\n")
            for mine in world_info['mines']:
                f.write("  (mine-at w" + str(world_info['mines'][mine]['node']) + " " + PDDLInterface.COLOURS[world_info['mines'][mine]['colour']] + ")\n")

            f.write("\n  ;; waypoint\n")
            for node in world_info['nodes']:
                for colour in PDDLInterface.COLOURS:
                    f.write("  (= (waypoint-resources w" + str(node) + " " + colour + ") 0)\n")

            f.write("\n  ;; connections\n")
            for edge in world_info['edges']:
                f.write("  (connected w" + str(world_info['edges'][edge]['node_a']) + " w" + str(world_info['edges'][edge]['node_b']) + ")")
                f.write(" (connected w" + str(world_info['edges'][edge]['node_b']) + " w" + str(world_info['edges'][edge]['node_a']) + ")\n")

            f.write("\n  ;; buildings\n")
            for task in world_info['tasks']:
                f.write("  (at b"+str(task)+" w"+str(world_info['tasks'][task]['node'])+")\n")
                f.write("  (= (building-requirements b" + str(task) + " "
                        + PDDLInterface.COLOURS[world_info['tasks'][task]['colour']] + ") "
                        + str(world_info['tasks'][task]['amount']) + ")\n")
                f.write("  (= (building-total-requirements b" + str(task) + ") "
                        + str(world_info['tasks'][task]['amount']) + ")\n")
                f.write("  (not-started b"+str(task)+")\n")
                break

            f.write(")\n")
            # end of initial state

            f.write("(:goal (and\n")

            for task in world_info['tasks']:
                if world_info['tasks'][task]['complete']: continue
                f.write("  (completed b" + str(task) + ")\n")
                # only plan for one task
                break


            f.write(")))\n")
            f.close()

    @staticmethod
    def readPDDLPlan(file: str):
        plan = []
        with open(file, "r") as f:
            line = f.readline().strip()
            while line:
                tokens = line.split()
                action = tokens[1][1:]
                params = tokens [2:-1]
                # remove trailing bracket
                params[-1] = params[-1][:-1]
                # remove character prefix and convert colours to ID
                params = [int(p[1:]) if p not in PDDLInterface.COLOURS else PDDLInterface.COLOURS.index(p) for p in params]
                plan.append((action, params))
                line = f.readline().strip()
            f.close()
        return plan

    @staticmethod
    def generatePlan(domain: str, problem: str, plan: str, verbose=False):
        data = {'domain': open(domain, 'r').read(), 'problem': open(problem, 'r').read()}
        resp = requests.post('https://popf-cloud-solver.herokuapp.com/solve', verify=True, json=data).json()
        if not 'plan' in resp['result']:
            if verbose:
                print("WARN: Plan was not found!")
                print(resp)
            return False
        with open(plan, 'w') as f:
            f.write(''.join([act for act in resp['result']['plan']]))
        f.close()
        return True

if __name__ == '__main__':
    PDDLInterface.generatePlan("domain-craft-bots.pddl", "problem.pddl", "plan.pddl", verbose=True)
    plan = PDDLInterface.readPDDLPlan('plan.pddl')
    print(plan)