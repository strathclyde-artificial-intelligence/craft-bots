# craft-bots
CraftBots is a multi-agent team simulator to evaluate/benchmark integrated planning and execution in complex tasks that could benefit from planning using a logistics problem. The simulation is lightweight and easy to setup, requiring only Python 3.9, NumPy, and Tkinter if a GUI is used. The simulation is also easily customisable via a set of easy to read/edit initalisation files to allow for specific scenarios to be easily simulated. 

The CraftBots simulation takes an agent and dynamicly creates random tasks for the agent complete using an API to control a set of actors in the simulation. It also provides a set of nested dictionaries to convey the visible portion of the world state. 

At the end of the simulation, determined by the initalisation files, the simulation returns the total score achieved by the agent, determined by how many tasks the agent completed and the determined difficulty of the tasks.

CraftBots is intended to be used for competitions, with the ability to create different easily shared scenarios for agents to compete in. An online leaderboard to submit agents to be evaluated and tested will be created. 

It is also intended to be used for evaluation/benchmarking, with the ability to create specific tracks to test specific problems, and provide a simple way to convey the overall ability of an agent.

Finally, it is intended to be used as foundation for teaching how to create planning agents, with toggleable modules allowing for a step by step introduction into the problems in Planning AI.

Competitions and teaching materials are still in development.

CraftBots is designed to be easy to learn, yet complex to master, with simple scenario rules (see [here](https://github.com/strathclyde-artificial-intelligence/craft-bots/wiki/Craft-Bots-Rules) for more information) and a simple yet effective API requiring only Python. An agent only needs a small set of fields and a single method to properly interact with CraftBots (see below for more information). However, with the possibility of temporally uncertain / non-deterministic actions, and dynamic goals with deadlines and the requirement to run the simulation in real time, the simulation can become much harder to "solve".

## Quick Start

### How to clone and run with a default agent:

CD to the directory of your choice and clone the CraftBots repo:

    git clone https://github.com/strathclyde-artificial-intelligence/craft-bots

CD into the repository and run `main.py`

    cd ./craft-bots
    python main.py

_*Note: CraftBots requires NumPy. Install by running:_

    pip install numpy

This should run CraftBots using `TestAgent`, an agent that moves all actors randomly. 


### How to run with your own agent

Once you have created your own agent (see [here](Creating-an-Agent) on how to make an agent) open `main.py` in the Python IDE of your choice or include the following lines in a separate file.

Start by importing your agent _(assuming your agent is in the agents folder)_ and craftbots:

    from agents.YourAgent import YourAgent
    from craftbots import craft_bots

Call `start_simulation` from `craftbots` with your agent:

    craft_bots.start_simulation(agent_class=YourAgent)

*_Note: You should pass in the constructor for your Agent, not an initialised object!_

To get the score from the simulation, get the return of `start_simulation`
    
    print(craft_bots.start_simulation(agent_class=YourAgent)
    
## CraftBots Wiki
See the [CraftBots Wiki here](https://github.com/strathclyde-artificial-intelligence/craft-bots/wiki) for more information, tutorials, and walkthroughs for CraftBots
