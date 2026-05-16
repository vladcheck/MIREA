from math import sin, pi

# 1
n = int(input())
print(n <= 1000 and n >= 100 and n % 5 == 0)

# 2
a = int(input())
b = int(input())
c = int(input())
print(
    a % 2 == 0 and b % 2 == 0 or a % 2 == 0 and c % 2 == 0 or b % 2 == 0 and c % 2 == 0
)


# 3
x = int(input())
y = int(input())
print(x >= 0 and y <= 1 and (y >= x - 1 or x**2 + y**2 <= 1))


# 4
x = int(input())
y = int(input())
print(y <= sin(x) and 0 <= y <= 0.5 and 0 <= x <= pi)


# 5
x = int(input())
y = int(input())
print(((y >= x) or (y <= x and x <= 0)) and x ** 2 + y**2 <= 1)


# 3.1
print(True if x >= 0 and y <= 1 and (y >= x - 1 or x**2 + y**2 <= 1) else False)
# 4.1
print(True if y <= sin(x) and 0 <= y <= 0.5 else False)
# 5.1
print(True if ((y >= x) or (y <= x and x <= 0)) and x ** 2 + y**2 <= 1 else False)
