class BlankAgent:
    def __init__(self):
        self.api = None
        self.thinking = False
        self.world_info = None

    def receive_results(self, _):
        pass

    def get_next_commands(self):
        self.thinking = False
