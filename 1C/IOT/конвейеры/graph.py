import matplotlib.pyplot as plt
import numpy as np


def parse(f):
    dt = {}
    for line in f:
        [food, amount] = line.split(":")
        amount = int(amount)
        dt[food] = amount
    return dt


def draw_graph(good, bad):
    categories = ["Correct", "Incorrect"]
    values_correct = list(good.values())
    values_incorrect = list(bad.values())

    index = np.arange(len(values_correct))

    bar_width = 0.35

    plt.bar(index, values_correct, width=bar_width, label="Correct", color="green")
    plt.bar(
        index + bar_width,
        values_incorrect,
        width=bar_width,
        label="Incorrect",
        color="red",
    )

    plt.xlabel("Subcategories")
    plt.ylabel("Counts")
    plt.title("Correct vs Incorrect")
    plt.xticks(index + bar_width / 2, list(good.keys()))  # Подписи подкатегорий

    plt.legend()

    for i in range(len(values_correct)):
        plt.text(
            i,
            values_correct[i] + 0.5,
            str(values_correct[i]),
            ha="center",
            fontweight="bold",
        )
        plt.text(
            i + bar_width,
            values_incorrect[i] + 0.5,
            str(values_incorrect[i]),
            ha="center",
            fontweight="bold",
        )

    plt.tight_layout()
    plt.show()


good = parse(open("./good.txt", "r"))
bad = parse(open("./bad.txt", "r"))
draw_graph(good, bad)
