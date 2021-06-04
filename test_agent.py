import time


class TestAgent:
    def __init__(self):
        self.api = None
        self.results = []
        self.thinking = False
        self.actors = []

    def receive_results(self, results):
        self.results.extend(results)
        self.thinking = False

    def find_result_by_id(self, result_id):
        for result in self.results:
            if result[0] == result_id:
                return result
        return None

    def get_next_commands(self):
        if not self.actors:
            self.actors = self.api.get_all_actors()
        elif isinstance(self.actors, int):
            self.actors = self.find_result_by_id(self.actors)[1]
        else:
            for actor in self.actors:
                if not actor.state:
                    self.api.move_rand(actor.id)
        time.sleep(1)
