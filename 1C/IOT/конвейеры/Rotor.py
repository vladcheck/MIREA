class Rotor:
    def __init__(self, username, id):
        self.username = username
        self.id = id

    def left(self, mqttc):
        mqttc.publish(f"/{self.username}{self.id}", "left")

    def forward(self, mqttc):
        mqttc.publish(f"/{self.username}{self.id}", "none")

    def right(self, mqttc):
        mqttc.publish(f"/{self.username}{self.id}", "right")
