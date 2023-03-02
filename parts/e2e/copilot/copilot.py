import logging

logger = logging.getLogger(__name__)

class Copilot:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {"Stop": 0, "Taxi": 0, "Direction": None, "Lane": "Right"}
        logger.info("Successfully Added")

        self.current_mode = 0
        self.direction = None
        self.cancel_turn_signal = memory.cfg["CANCEL_TURN_SIGNAL"]
        self.left_threshold = memory.cfg["LEFT_THRESHOLD"]
        self.right_threshold = memory.cfg["RIGHT_THRESHOLD"]
        self.prev_steering = 0

    def update(self):
        mode = self.memory.memory["Mode2"]
        if mode != self.current_mode:
            if mode == 1:
                self.direction = "Left"
            if mode == 2:
                self.direction = "Forward"
            if mode == 3:
                self.direction = "Right"
            self.current_mode = mode

        # Automatickly turns off the signal after we made the turn(like real car)
        if self.cancel_turn_signal:
            steering = self.memory.memory["Steering"]
            if self.direction == "Left" and self.prev_steering > self.left_threshold > steering:
                self.direction = None
            if self.direction == "Right" and self.prev_steering < self.right_threshold < steering:
                self.direction = None
            self.prev_steering = steering

        self.memory.memory["Direction"] = self.direction

    def shut_down(self):
        self.run = False
        logger.info("Stopped")