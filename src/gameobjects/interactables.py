from src.gameobjects.items import Item, CyberneticImplant

class Terminal(Item):
    def __init__(self, name, description, lore_message):
        super().__init__(name, description)
        self.lore_message = lore_message

    def to_json(self):
        data = super().to_json()
        data.update({
            "lore_message": self.lore_message
        })
        return data

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["description"], data["lore_message"])

class CyberneticTerminal(Terminal):
    def __init__(self, name, description, lore_message):
        super().__init__(name, description, lore_message)

    def install_implant(self, player, implant):
        if implant.implant_type == "connection":
            player.has_connection_implant = True
        for stat, bonus in implant.stat_bonus.items():
            if hasattr(player, stat):
                setattr(player, stat, getattr(player, stat) + bonus)
        player.inventory.remove(implant)
        return f"Successfully installed {implant.name}! Your stats have been updated."

    def to_json(self):
        return super().to_json()

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["description"], data["lore_message"])

class Obstacle(Item):
    def __init__(self, name, description, strength_required):
        super().__init__(name, description)
        self.strength_required = strength_required
        self.health = strength_required

    def is_destroyed(self):
        return self.health <= 0

    def to_json(self):
        data = super().to_json()
        data.update({
            "strength_required": self.strength_required,
            "health": self.health
        })
        return data

    @classmethod
    def from_json(cls, data):
        obstacle = cls(data["name"], data["description"], data["strength_required"])
        obstacle.health = data["health"]
        return obstacle