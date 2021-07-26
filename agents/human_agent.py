from api import agent_api


class HumanAgent:
    def __init__(self):
        self.api = None
        self.thinking = False

    def get_next_commands(self):
        self.api: agent_api.AgentAPI
        while True:
            command = input(" > ")
            args = command.split()
            if args[0] == "world_info":
                result = self.api.get_world_info()
                for i in range(1, args.__len__()):
                    try:
                        result = result[int(args[i])]
                    except ValueError:
                        result = result[args[i]]
                print(result)
            elif args[0] == "get_by_id":
                print(self.api.get_by_id(int(args[1])))
            elif args[0] == "get_field":
                print(self.api.get_field(int(args[1]), args[2]))
            elif args[0] == "move_to":
                self.api.move_to(int(args[1]), int(args[2]))
            elif args[0] == "move_rand":
                self.api.move_rand(int(args[1]))
            elif args[0] == "pick_up_resource":
                self.api.pick_up_resource(int(args[1]), int(args[2]))
            elif args[0] == "drop_resource":
                self.api.drop_resource(int(args[1]), int(args[2]))
            elif args[0] == "drop_all_resources":
                self.api.drop_all_resources(int(args[1]))
            elif args[0] == "dig_at":
                self.api.dig_at(int(args[1]), int(args[2]))
            elif args[0] == "start_site":
                self.api.start_site(int(args[1]), int(args[2]))
            elif args[0] == "construct_at":
                self.api.construct_at(int(args[1]), int(args[2]))
            elif args[0] == "deposit_resource":
                self.api.deposit_resources(int(args[1]), int(args[2]), int(args[3]))
            elif args[0] == "start_looking":
                self.api.start_looking(int(args[1]))
            elif args[0] == "cancel_action":
                self.api.cancel_action(int(args[1]))
            elif args[0] == "start_sending":
                self.api.start_sending(int(args[1]), args[2])
            elif args[0] == "start_receiving":
                self.api.start_receiving(int(args[1]))
