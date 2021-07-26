class BlankAgent:
    def __init__(self):
        self.api = None
        self.thinking = False
        self.world_info = None

    def get_next_commands(self):
        self.thinking = False
