from random import randint

DAMAGE = 20

class Fighter:
    def __init__(self,name,health=100):
        self.name = name
        self.health = health
        
    def attack(self,fighter):
        fighter.get_attacked(DAMAGE)
        print(f"{self.name} attacked {fighter.name}. {fighter.health}hp left.")
        
    def get_attacked(self,damage):
        self.health -= damage

u1 = Fighter("Dan")
u2 = Fighter("Kyle")
print(u1.name + " and " + u2.name)

while u1.health > 0 and u2.health > 0:
    attacker = randint(0,1)
    if attacker == 0:
        u1.attack(u2)
    else:
        u2.attack(u1)

if u1.health > 0:
    print(f"{u1.name} won!")
else:
    print(f"{u2.name} won!")