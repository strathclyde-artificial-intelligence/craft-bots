![Screenshot of Craftbots simulation](/screenshot.png)

## Quickstart

Install the dependencies, clone the repository, and run `main.py`
```
git clone https://github.com/strathclyde-artificial-intelligence/craft-bots
cd ./craft-bots
pip install -r requirements.txt
python main.py
```

Press "reset" to generate a new simulation, and "start" to begin the simulation.

### Connect your own agent

Once you have created your own agent open `main.py` and modify the lines which append the default agent to the simulation.
```
    # agent
    agent = TestAgent()
    sim.agents.append(agent)
```

Further information is available on the [CraftBots Wiki here](https://github.com/strathclyde-artificial-intelligence/craft-bots/wiki).
