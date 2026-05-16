from lab_gen import *

rows = 6
cols = 6

lab = Lab(rows, cols, 8, 8)
lab.print()
counts = [[0 for _ in range(cols)] for _ in range(rows)]

for i in range(1, cols):
    if lab.lab[0][i] == "P":
        counts[0][i] = counts[0][i - 1] + 1
    elif lab.lab[0][i] == "1":
        break

for i in range(1, cols):
    if lab.lab[0][i] == "P":
        counts[0][i] = counts[0][i - 1] + 1
    elif lab.lab[0][i] == "1":
        break

print()
for line in counts:
    print(line)
