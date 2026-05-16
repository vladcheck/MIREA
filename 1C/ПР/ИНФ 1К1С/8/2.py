from Stack import *

correct = "(), (())(), ()(), ((()))"
wrong = ")(, ())((), (, )))), ((())"


def is_correct(b):
    S = Stack()
    for char in b:
        S.push(char)
    count_unclosed = 0
    while not S.isEmpty():
        char = S.pop()
        if char == ")":
            count_unclosed += 1
        elif char == "(":
            count_unclosed -= 1
        if count_unclosed < 0:
            return False
    return True


print(is_correct(correct))
print(is_correct(wrong))
