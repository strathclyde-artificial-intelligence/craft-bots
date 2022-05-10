from craftbots.config.config_manager import Configuration
from craftbots.world import World
import random as r

class WorldFactory:

    @classmethod
    def generate_world(cls, config):

        world = World(config)

        resource_config = Configuration.flatten(config['Resources'])
        WorldFactory.add_actors(world, Configuration.flatten(config['Actors']), resource_config)
        WorldFactory.add_mines(world, Configuration.flatten(config['Mines']))
        WorldFactory.add_resources(world, resource_config)

        return world

    # ======================== #
    # generating world objects #
    # ======================== #

    @classmethod
    def add_actors(cls, world, actor_config, resource_config):
        for _ in range(int(actor_config["num_actors"])):
            actor = world.add_actor(world.nodes[r.randint(0, len(world.nodes) - 1)])
            for _ in range(int(resource_config["actor_num_of_red_resources"])):
                world.add_resource(actor, 0)
            for _ in range(int(resource_config["actor_num_of_blue_resources"])):
                world.add_resource(actor, 1)
            for _ in range(int(resource_config["actor_num_of_orange_resources"])):
                world.add_resource(actor, 2)
            for _ in range(int(resource_config["actor_num_of_black_resources"])):
                world.add_resource(actor, 3)
            for _ in range(int(resource_config["actor_num_of_green_resources"])):
                world.add_resource(actor, 4)

    @classmethod
    def add_mines(cls, world, config):
        for _ in range(int(config["num_of_red_mines"])):
            world.add_mine(world.nodes[r.randint(0, len(world.nodes) - 1)], 0)
        for _ in range(int(config["num_of_blue_mines"])):
            world.add_mine(world.nodes[r.randint(0, len(world.nodes) - 1)], 1)
        for _ in range(int(config["num_of_orange_mines"])):
            world.add_mine(world.nodes[r.randint(0, len(world.nodes) - 1)], 2)
        for _ in range(int(config["num_of_black_mines"])):
            world.add_mine(world.nodes[r.randint(0, len(world.nodes) - 1)], 3)
        for _ in range(int(config["num_of_green_mines"])):
            world.add_mine(world.nodes[r.randint(0, len(world.nodes) - 1)], 4)

    @classmethod
    def add_resources(cls, world, config):
        for _ in range(int(config["num_of_red_resources"])):
            world.add_resource(world.nodes[r.randint(0, len(world.nodes) - 1)], 0)
        for _ in range(int(config["num_of_blue_resources"])):
            world.add_resource(world.nodes[r.randint(0, len(world.nodes) - 1)], 1)
        for _ in range(int(config["num_of_orange_resources"])):
            world.add_resource(world.nodes[r.randint(0, len(world.nodes) - 1)], 2)
        for _ in range(int(config["num_of_black_resources"])):
            world.add_resource(world.nodes[r.randint(0, len(world.nodes) - 1)], 3)
        for _ in range(int(config["num_of_green_resources"])):
            world.add_resource(world.nodes[r.randint(0, len(world.nodes) - 1)], 4)
