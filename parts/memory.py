class Memory:
    def __init__(self, config=None):
        # Vehicles memory all parts can write or read this dictinory.
        self.memory = {}
        # If some parts wants to change other parts output it writes to the overwrites dict
        # When real owner sees that overwrite it changes the output accordingly
        # Real owner uses pop to get the overwiten value (pop deletes it)
        # Example:
        # memory["Overwrites"]["Record"] = {"importance": self.overwrite_importance, "value": 0}
        self.memory["Overwrites"] = {}
        self.cfg = config

    def add(self, name, value=0):
        self.memory[name] = value

    def __repr__(self) :
        return str(self.memory)