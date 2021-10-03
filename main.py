from agents import test_agent
from craftbots import craft_bots

if __name__ == '__main__':
    craft_bots.start_simulation(agent_class=test_agent.TestAgent,
                                use_gui=True,
                                modifier_file="craftbots/initialisation_files/simple_modifiers",
                                world_modifier_file="craftbots/initialisation_files/simple_world_gen_modifiers",
                                rule_file="craftbots/initialisation_files/simple_rules"
                                )
