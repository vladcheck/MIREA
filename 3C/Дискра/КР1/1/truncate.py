import math


def truncate(number: float, digits: int = 3) -> float:
    if "." not in str(number):
        return number

    nbDecimals: int = len(str(number).split(".")[1])

    if nbDecimals <= digits:
        return number

    stepper: float = 10.0**digits
    res: float = math.trunc(stepper * number) / stepper
    return res
