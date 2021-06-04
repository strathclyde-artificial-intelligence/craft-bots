import time


class BlankAgent:
    def __init__(self):
        self.api = None
        self.thinking = False

    def receive_results(self, _):
        self.thinking = False

    def get_next_commands(self):
        time.sleep(1)
