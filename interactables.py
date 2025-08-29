from items import Item

class Terminal(Item):
    def __init__(self, name, description, lore_message):
        super().__init__(name, description)
        self.lore_message = lore_message

class Obstacle(Item):
    def __init__(self, name, description, strength_required):
        super().__init__(name, description)
        self.strength_required = strength_required
