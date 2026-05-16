# 1
str = input()

def is_palindrome(str):
    return str == reversed(str)

print(is_palindrome(str))

# 2
str = input()
print(str.lower())

# 3
str = input()
print(str.upper())

# 4
str = input()
print(any(n in str for n in "0123456789"))

# 5
str = "Заданастрока.Необходимомеждуеёсимволамивставитьпоодномупробелу."
print(" ".join(str.split("")))

# 6
c = "C"
print(ord(c))