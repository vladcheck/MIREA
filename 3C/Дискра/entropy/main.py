from math import log2
from itertools import combinations


def entropy(X: list[int]):
    res = []
    for p in X:
        if p == 0:
            res.append(0)
        else:
            res.append(p * log2(p))
    return -sum(res)


allowed_chars = "qwertyuiopasdfghjklzxcvbnm" + "1234567890"

stdin = open("in.txt", "r+", encoding="utf8").read()
stdin = stdin.lower()
stdin = "".join([s for s in stdin if s in allowed_chars])

stdout = open("out.txt", "w+", encoding="utf8")
stdout.write(stdin)
stdout.close()

stdout = open("out.txt", "r+", encoding="utf8").read()

freq1 = {}
for s in allowed_chars:
    freq1[s] = stdin.count(s) / len(stdin)
entropy1 = entropy(list(freq1.values()))

freq2 = {}
for c in combinations(allowed_chars, 2):
    c = "".join(c)
    freq2[c] = stdin.count(c) / len(stdin)
entropy2 = entropy(list(freq2.values()))

print(entropy1, entropy2)
