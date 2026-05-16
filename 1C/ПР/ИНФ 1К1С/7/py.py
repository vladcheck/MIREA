# 1
def div(a, b):
    return (a // b, a % b)


# 2
def sign(x):
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1


# 3
def is_palindrome(str):
    return str == str[::-1]


# 4
def pretty_time(sec):
    days = sec // 86400
    hours = sec % 86400 // 3600
    minutes = sec % 3600 // 60
    seconds = sec % 60
    return f"{days}:{hours}:{minutes}:{seconds}"


# 5
def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


print(pretty_time(312599))
