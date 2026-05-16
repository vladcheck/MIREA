def get_rel_matr(A, R):
    l = sorted(list(A))
    matr = []
    for i in range(len(l)):
        row = []
        for j in range(len(l)):
            row.append(R(l[i], l[j]))
        matr.append(row)
    return matr


def is_refl(matr):
    for x in range(len(matr)):
        if not matr([x][x]):
            return False
    return True


def is_antirefl(matr):
    for x in range(len(matr)):
        if matr[x][x]:
            return False
    return True


def is_symm(matr):
    for x in range(len(matr)):
        for y in range(x, len(matr)):
            if not matr[x][y] == matr[y][x]:
                return False
    return True


def is_antisymm(matr):
    for x in range(len(matr)):
        for y in range(x, len(matr)):
            if matr[x][y] and matr[y][x]:
                if x != y:
                    return False
    return True


# МОЖЕТ БЫТЬ НЕПРАВИЛЬНО
def is_transitive(matr):
    for y in range(len(matr)):
        for x in range(len(matr)):
            for z in range(len(matr)):
                if matr[x][y] == 1 and matr[y][z] == 1 and matr[x][z] != 1:
                    return False
    return True
