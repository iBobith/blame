class Item:
    def __init__(self, name, description, log=None):
        self.name = name
        self.description = description
        self.log = log

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "log": self.log,
            "__class__": self.__class__.__name__
        }

    @classmethod
    def from_json(cls, data):
        return Item(data["name"], data["description"], data["log"])

class CyberneticImplant(Item):
    def __init__(self, name, description, stat_bonus, implant_type):
        super().__init__(name, description)
        self.stat_bonus = stat_bonus
        self.implant_type = implant_type

    def to_json(self):
        data = super().to_json()
        data.update({
            "stat_bonus": self.stat_bonus,
            "implant_type": self.implant_type
        })
        return data

    @classmethod
    def from_json(cls, data):
        return cls(data["name"], data["description"], data["stat_bonus"], data["implant_type"])