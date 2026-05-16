import paho.mqtt.client as mqtt
from Rotor import Rotor
import utils

USERNAME = "v"

data_pending = []
data = {
    "good": {
        "burger": 0,
        "apple": 0,
        "coffecup": 0,
        "cupcake": 0,
        "soda": 0,
        "tomato": 0,
    },
    "bad": {
        "burger": 0,
        "apple": 0,
        "coffecup": 0,
        "cupcake": 0,
        "soda": 0,
        "tomato": 0,
    },
}

left = Rotor(USERNAME, "/truck/Rotation-3")
mid = Rotor(USERNAME, "/truck/Rotation-1")
right = Rotor(USERNAME, "/truck/Rotation-2")

correct = 0
wrong = 0


def on_connect(client, userdata, flags, reason_code, properties):
    SUB_TO = [
        "#",
        "Warehouse-Apple",
        "Warehouse-Product",
        "Warehouse-Tomato",
        "Warehouse-Cup",
        "Warehouse-Soda",
    ]
    print(f"Connected with result code {reason_code}")
    utils.sub(USERNAME, client, SUB_TO)


def on_message(client, userdata, msg):
    global mqttc
    global data
    global data_pending

    payload = msg.payload.decode().lower()
    topic = msg.topic.lower()
    if "correct" in payload:
        while len(data_pending) > 0:
            [data, data_pending] = utils.write_statistics(data, data_pending, payload)
    elif utils.enteringFirstDetector(topic):
        utils.rotateConveyors(payload, mqttc, left, mid, right)
    elif len(payload.split()) > 1 and utils.isPutToStorage(topic):
        product = payload.split()[1].split("(")[0]
        data_pending.append(product)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("levandrovskiy.ru", 1883, 60)

mqttc.loop_forever()
