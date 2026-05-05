

class GUIEvent:

    def __init__(self):
        self.subs = []

    def subscribe(self, callback):
        self.subs.append(callback)

    def invoke(self):
        for sub in self.subs:
            sub()
