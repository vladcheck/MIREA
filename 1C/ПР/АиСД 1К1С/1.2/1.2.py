from prettytable import PrettyTable

# 1.1


def binary_search(arr, key):
    l = 0
    r = len(arr) - 1

    while l <= r:
        mid = (l + r) // 2
        midVal = arr[mid]
        if midVal == key:
            return mid
        if midVal > key:
            r = mid - 1
        else:
            l = mid + 1
    arr.insert(l, key)
    return [l, arr]


a = [1, 3, 4, 5, 6, 7]
f = 4
print(f"{a}, {f} => {binary_search(a, f)}")
f = 2
print(f"{a}, {f} => {binary_search(a, f)}")
print()

# 1.2


def is_picky(arr):
    l = get_pick(arr, 4)
    m = get_pick(arr, 2)
    r = get_pick(arr, 1.5)
    if (l == m and l != None) or (m == r and m != None) or (l == r and l != None):
        return f"Массив горный: {m}"
    else:
        return "Массив не горный"


def get_pick(arr, coefficient):
    l = 0
    r = len(arr) - 1
    mid = int((r + l) // coefficient)

    while True:
        if (
            mid + 1 == len(arr)
            or mid - 1 == -1
            or (arr[mid - 1] > arr[mid] and arr[mid] < arr[mid + 1])
        ):
            return None
        elif arr[mid - 1] < arr[mid] and arr[mid] > arr[mid + 1]:
            return mid
        elif arr[mid - 1] < arr[mid] < arr[mid + 1]:
            l = mid + 1
        elif arr[mid - 1] > arr[mid] > arr[mid + 1]:
            r = mid - 1
        else:
            l += 1
        mid = (r + l) // 2


t = PrettyTable(["Ввод", "Вывод"])
t.align = "l"
for sample in [
    [1, 2, 3, 4, 1],
    [1, 2, 1],
    [1, 2, 3, 4],
    [4, 3, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
    [0, 0, 2, 1, 2, 0],
    [0, 0, 0],
]:
    t.add_row([sample, is_picky(sample)])
print(t)
print()

# 1.3


def comparison(neg, pos):
    if neg > pos:
        return f"Отрицательных больше: {neg}"
    if neg < pos:
        return f"Положительных больше: {pos}"
    return f"Одинаково: {neg}"


def find_neg_or_pos_more(arr):
    l = 0
    r = len(arr) - 1

    while l <= r:
        mid = (l + r) // 2
        if arr[mid] == 0:
            neg = len([a for a in arr[:mid] if a != 0])
            pos = len([a for a in arr[mid + 1 :] if a != 0])
            return comparison(neg, pos)
        if arr[mid] > 0:
            r = mid - 1
        else:
            l = mid + 1
    neg = r + 1
    pos = len(arr) - neg
    return comparison(neg, pos)


t = PrettyTable(["Ввод", "Вывод"])
t.align = "l"
for sample in [
    [0, 1, 2],
    [-3, 7, 8, 10],
    [-10, -8, -3, 0],
    [-17, -10, -8],
    [-4, 0, 0, 0, 10, 11],
    [-7, -6, -5, -4, 0, 1, 3, 5, 6, 7],
    [-3, 3],
    [-3, 0, 3],
    [-3, -2, -1, 0, 0, 1, 2, 3],
    [0, 0, 0],
]:
    t.add_row([sample, find_neg_or_pos_more(sample)])
print(t)
print()

# 1.4


def get_counts(arr):
    counts = []
    for i in range(len(arr)):
        count = 0
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                count += 1
        counts.append(count)
    return counts


a = [5, 2, 6, 1]
print(f"{a} => {get_counts(a)}")
a = [0, 1, 2, 3, 4, 5, 6]
print(f"{a} => {get_counts(a)}")
a = [6, 5, 4, 3, 2, 1]
print(f"{a} => {get_counts(a)}")
a = [6, -3, 7, -1, -5, 9, 0, 4, 3]
print(f"{a} => {get_counts(a)}")
a = [1, 2, 3, 4]
print(f"{a} => {get_counts(a)}")
a = [5, 5, 5, 5]
print(f"{a} => {get_counts(a)}")
