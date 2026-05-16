from math import *


# 1
def div(a, b):
    while a % b != 0:
        a, b = b, a % b
    return b


print("2 3 5 =>", div(2, div(3, 5)))
print("-8 0 16 =>", div(-8, div(0, 16)))


# 2


# Получает простые числа в промежутке [2;n]
def eratosfen(n):
    primes = list(range(2, n + 1))
    currentLength = len(primes)
    previousLength = None
    currIndex = 0
    while currentLength != previousLength:
        primes = [
            num
            for num in primes
            if num % primes[currIndex] != 0 or num == primes[currIndex]
        ]
        currentLength, previousLength = len(primes), currentLength
        currIndex += 1
    return primes


def factor(n):
    primes = list(reversed(eratosfen(n)))
    res = ""
    for num in primes:
        divided = 0
        while n % num == 0:
            divided += 1
            n //= num
        if divided > 0:
            res += f"{num}^{divided}"
            if num != 2:
                res += ","
    return res if (len(res) > 0) else f"{n}^1"


print("#2")
print("17 = ", factor(17))
print("18 = ", factor(18))
print()

# 3 (решето Эратосфена взято из II задания) PENDING


def q_helper(x, n, m):
    return (m + x) ** 2 - n


def factor_by_ferma(n):
    if n == 1:
        return []
    if n in eratosfen(n):
        return [n]
    if n % 2 == 0:
        return "Не могу"
    m = int(sqrt(n))
    if m**2 == n:
        return [m, m]
    x = 1
    while x < n:
        y = q_helper(x, n, m)
        if int(sqrt(y)) ** 2 == y:
            break
        else:
            x += 1
    B = int(sqrt(y))
    A = m + x
    p = int(A + B)
    q = int(A - B)
    res = []
    # проверка наличия чисел p и q в массиве простых чисел по Эратосфену
    res.append([p] if (p in eratosfen(p)) else factor_by_ferma(p))
    res.append([q] if (q in eratosfen(q)) else factor_by_ferma(q))
    res = [x for xs in res for x in xs]
    return res


def prettify_ferma(nums):
    if type(nums) == str:
        return nums
    res = ""
    primes = set(nums)
    for n in sorted(primes):
        res += f"{n}^{nums.count(n)},"
    return res


print("#3")
print(17, prettify_ferma(factor_by_ferma(17)))
print(8, prettify_ferma(factor_by_ferma(8)))
print(135, prettify_ferma(factor_by_ferma(135)))
print()


# 4 PENDING
def get_mersenn_n(num):
    n = 0
    while 2**n - 1 != num:
        n += 1
    return n


def luke_lemer(k):
    if k == 1:
        return 4
    else:
        return luke_lemer(k - 1) ** 2 - 2


def check_mersenn(num):
    n = get_mersenn_n(num)
    return luke_lemer(n - 1) % num == 0


print("#4")
print("15", check_mersenn(15))
print("31", check_mersenn(31))
print()


# 5 PENDING
def neyman(n):
    n **= 2
    n = str(n)
    mid = len(n) // 2
    n = int(n[mid - 2 : mid + 3])
    return n


print("#5")
seed = 1234567890
for i in range(10):
    seed = neyman(seed)
    print(seed, end=" ")
print()


# 6 PENDING


def sundaram(n):
    upper = floor((n - 1) / 2)
    primes = list(range(1, upper + 1))
    indexes = []
    for i in range(1, n):
        for j in range(i, n):
            k = i + j + 2 * i * j
            if k <= upper:
                indexes.append(k)
    for i in indexes:
        primes[primes.index(i)] = None
    primes = [n for n in primes if n != None]
    primes = [2 * n + 1 for n in primes]
    return [2, *primes]


print(sundaram(25))
