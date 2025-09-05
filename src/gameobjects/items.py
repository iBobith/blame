class Item:
    def __init__(self, name, description, log=None):
        self.name = name
        self.description = description
        self.log = log

class CyberneticImplant(Item):
    def __init__(self, name, description, stat_bonus, implant_type):
        super().__init__(name, description)
        self.stat_bonus = stat_bonus
        self.implant_type = implant_type