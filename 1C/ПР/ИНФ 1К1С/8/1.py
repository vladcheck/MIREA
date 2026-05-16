from Stack import *
    
S = Stack()
a = "привет"
half = len(a)//2

for char in a[half:]:
    S.push(char)
for char in a[:half]:
    S.push(char)

while not S.isEmpty():
    print(S.pop(),end="")
