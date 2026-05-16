def sub(username, client, topics):
    for topic in topics:
        client.subscribe(f"/{username}/{topic}")


def rotateConveyors(data, mqttc, left, mid, right):
    print(data)
    if "tomato" in data:
        mid.right(mqttc)
        right.forward(mqttc)
    elif "product" in data:
        mid.left(mqttc)
        left.left(mqttc)
    elif "apple" in data:
        mid.right(mqttc)
        right.forward(mqttc)
    elif "cupcake" in data:
        mid.forward(mqttc)
    elif "coffee" in data or "cup" in data:
        mid.right(mqttc)
        right.right(mqttc)


def enteringFirstDetector(topic):
    return "detection-1/enter" in topic


def isPutToStorage(topic):
    return "warehouse/exit" in topic


def isInCorrectBox(payload):
    print(payload)
    return ("incorrect" not in payload) and "correct" in payload


def changeStatistics(data, type, good):
    if good:
        data["good"][type] += 1
    else:
        data["bad"][type] += 1
    return data


def write_to_file(dataset, filename):
    f = open(f"{filename}.txt", "w")
    for key, value in dataset.items():
        f.write(str(key + ":" + str(value) + "\n"))
    f.close()


def write_statistics(data, data_pending, payload):
    product = data_pending.pop(0)
    data = changeStatistics(data, product, isInCorrectBox(payload))

    write_to_file(data["good"], "good")
    write_to_file(data["bad"], "bad")

    return [data, data_pending]
