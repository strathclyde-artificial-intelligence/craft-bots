from agents import agent_api

class HumanAgent:
    def __init__(self):
        self.api = None
        self.thinking = False

    def receive_results(self, results):
        for result in results:
            print(result[1])
        self.thinking = False

    def get_next_commands(self):
        self.api: agent_api.AgentAPI
        while True:
            command = input(" > ")
            args = command.split()
            if args.__len__() == 1:
                if args[0] == "get_all_actors":
                    self.api.get_all_actors()
                    return
                if args[0] == "get_all_resources":
                    self.api.get_all_resources()
                    return
                if args[0] == "get_all_mines":
                    self.api.get_all_mines()
                    return
                if args[0] == "get_all_sites":
                    self.api.get_all_sites()
                    return
                if args[0] == "get_all_buildings":
                    self.api.get_all_buildings()
                    return
                if args[0] == "get_tasks":
                    self.api.get_tasks()
                    return
                if args[0] == "get_all_nodes":
                    self.api.get_all_nodes()
                    return
                if args[0] == "no_commands":
                    self.api.get_all_nodes()
                    return
            elif args.__len__() == 2:
                if args[0] == "move_rand":
                    self.api.move_rand(int(args[1]))
                    return
                elif args[0] == "drop_all_resources":
                    self.api.drop_all_resources(int(args[1]))
                    return
                elif args[0] == "get_adjacent_nodes":
                    self.api.get_adjacent_nodes(int(args[1]))
                    return
                elif args[0] == "get_actors_at":
                    self.api.get_actors_at(int(args[1]))
                    return
                elif args[0] == "get_resources_at":
                    self.api.get_resources_at(int(args[1]))
                    return
                elif args[0] == "get_mines_at":
                    self.api.get_mines_at(int(args[1]))
                    return
                elif args[0] == "get_sites_at":
                    self.api.get_sites_at(int(args[1]))
                    return
                elif args[0] == "get_buildings_at":
                    self.api.get_buildings_at(int(args[1]))
                    return
                elif args[0] == "cancel_action":
                    self.api.cancel_action(int(args[1]))
                    return
            elif args.__len__() == 3:
                if args[0] == "move_to":
                    self.api.move_to(int(args[1]), int(args[2]))
                    return
                elif args[0] == "pick_up_resource":
                    self.api.pick_up_resource(int(args[1]), int(args[2]))
                    return
                elif args[0] == "drop_resource":
                    self.api.drop_resource(int(args[1]), int(args[2]))
                    return
                elif args[0] == "mine_at":
                    self.api.dig_at(int(args[1]), int(args[2]))
                    return
                elif args[0] == "start_site":
                    self.api.start_site(int(args[1]), int(args[2]))
                    return
                elif args[0] == "build_at":
                    self.api.build_at(int(args[1]), int(args[2]))
                    return
            elif args.__len__() == 4:
                if args[0] == "deposit_resources":
                    self.api.deposit_resources(int(args[1]), int(args[2]), int(args[3]))
                    return
