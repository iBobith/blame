from src.gameobjects.items import Item, CyberneticImplant
from src.gameobjects.interactables import Terminal, CyberneticTerminal, Obstacle
from src.gameobjects.enemies import NPC

def create_from_json(data):
    class_name = data.get("__class__")
    if not class_name:
        if "dialogue" in data:
            return NPC.from_json(data)
        raise ValueError(f"No __class__ found in data: {data}")

    if class_name == "CyberneticImplant":
        return CyberneticImplant.from_json(data)
    elif class_name == "Terminal":
        return Terminal.from_json(data)
    elif class_name == "CyberneticTerminal":
        return CyberneticTerminal.from_json(data)
    elif class_name == "Obstacle":
        return Obstacle.from_json(data)
    elif class_name == "NPC":
        return NPC.from_json(data)
    elif class_name == "Item":
        return Item.from_json(data)
    raise ValueError(f"Unknown class name: {class_name}")