# 22. Реализуйте программу для нахождения максимальной суммы
# подсеквенции с ограничением на количество элементов.
from random import randint

array = [randint(1, 100000) for _ in range(1000000)]
n = len(array)
limit = 80

sums = [0] * n
sums[0] = array[0]

for i in range(1, n):
    sums[i] = sums[i - 1] + array[i]

max_sum = float("-inf")

for i in range(n):
    start_index = max(0, i - limit + 1)
    if start_index == 0:
        current_sum = sums[i]
    else:
        current_sum = sums[i] - sums[start_index - 1]

    max_sum = max(max_sum, current_sum)

print(max_sum)
