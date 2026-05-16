def arrow_down(x, y):
    return not (x or y)


def vertical(x, y):
    return not (x and y)


def xor(x, y):
    return (x and (not y)) or ((not x) and y)


print("[x, y, z]|[1, 2, 3, 4, 5, 6, 7, 8]")
print()
for x in [0, 1]:
    for y in [0, 1]:
        for z in [0, 1]:
            f1 = arrow_down(x, y)
            f2 = xor(not x, z)
            f3 = f1 or f2
            f4 = x == z
            f5 = vertical(y, not z)
            f6 = f4 <= f5
            f7 = not f6
            f8 = f3 and f7
            arr = [int(v) for v in [f1, f2, f3, f4, f5, f6, f7, f8]]
            print([x, y, z], arr, sep="|")
