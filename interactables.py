from items import Item, CyberneticImplant

class Terminal(Item):
    def __init__(self, name, description, lore_message):
        super().__init__(name, description)
        self.lore_message = lore_message

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

class Obstacle(Item):
    def __init__(self, name, description, strength_required):
        super().__init__(name, description)
        self.strength_required = strength_required