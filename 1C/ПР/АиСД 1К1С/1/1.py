from math import *


def f(x):
    return 3 * x - 14 + e**x - e ** (-x)


def div(f, L, R, bound=0.000000001):
    B = 0
    while R - L > bound:
        B = (L + R) / 2
        if f(L) * f(B) < 0:
            R = B
        else:
            L = B
    return [B, f(B)]


def chord(f, L, R, bound=0.000000001):
    while abs(f(L)) > bound:
        L = L - ((R - L) * f(L)) / (f(R) - f(L))
    return [L, f(L)]


print()
print("Функция 3x-14+e^x-e^(-x)")
print(f"Метод пол-го деления: {div(f, 1, 3)}")
print(f"Метод хорд: {chord(f, 1, 3)}")
