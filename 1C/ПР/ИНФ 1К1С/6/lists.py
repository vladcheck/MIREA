# 1
print(list(range(0,101,17)))

# 2
words = []
for i in range(5):
    words.append(input())
lengths = [len(w) for w in words]

print(words)
print(lengths)