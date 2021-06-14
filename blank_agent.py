import time


class BlankAgent:
    def __init__(self):
        self.api = None
        self.thinking = False
        self.world_info = None

    def receive_results(self, _):
        self.thinking = False

    def get_next_commands(self):
        self.api.no_commands()
