class Enemy:
    def __init__(self, name, description, health, damage, durability):
        self.name = name
        self.description = description
        self.health = health
        self.damage = damage
        self.durability = durability

    def is_alive(self):
        return self.health > 0
