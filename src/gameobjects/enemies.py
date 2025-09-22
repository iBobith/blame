class Enemy:
    def __init__(self, name, description, health, damage, durability):
        self.name = name
        self.description = description
        self.health = health
        self.damage = damage
        self.durability = durability

    def is_alive(self):
        return self.health > 0

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "health": self.health,
            "damage": self.damage,
            "durability": self.durability
        }

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["description"], data["health"], data["damage"], data["durability"])

class NPC:
    def __init__(self, name, description, dialogue):
        self.name = name
        self.description = description
        self.dialogue = dialogue

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "__class__": self.__class__.__name__
        }

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["description"], data["dialogue"])