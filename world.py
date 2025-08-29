import random
import json
from items import Item
from interactables import Terminal, Obstacle
from enemies import Enemy

# Load content from JSON file
with open("blame/content.json", "r") as f:
    CONTENT = json.load(f)

class Room:
    def __init__(self, description, zone):
        self.description = description
        self.zone = zone
        self.exits = {}
        self.items = []
        self.enemies = []
        self.obstacles = {}

    def add_exit(self, direction, room):
        self.exits[direction] = room

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)

    def add_obstacle(self, direction, obstacle):
        self.obstacles[direction] = obstacle

    def remove_obstacle(self, direction):
        if direction in self.obstacles:
            del self.obstacles[direction]

    def get_random_exit(self):
        if not self.exits:
            return None
        return random.choice(list(self.exits.keys()))

DIRECTIONS = ["north", "south", "east", "west"]

def get_opposite_direction(direction):
    opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}
    return opposites.get(direction)

def generate_world(num_rooms=30, rooms_per_zone=10):
    """Creates a network of rooms with different zones."""
    zones = list(CONTENT["room_descriptions"].keys())
    rooms = []
    
    # Create rooms for each zone
    for i in range(num_rooms):
        zone_index = min(i // rooms_per_zone, len(zones) - 1)
        zone = zones[zone_index]
        description = random.choice(CONTENT["room_descriptions"][zone])
        rooms.append(Room(description, zone))

    starting_room = rooms[0]

    for i, room in enumerate(rooms):
        # Ensure the world is connected
        if i < num_rooms - 1:
            next_room = rooms[i+1]
            direction = random.choice(DIRECTIONS)
            while direction in room.exits:
                direction = random.choice(DIRECTIONS)
            
            room.add_exit(direction, next_room)
            next_room.add_exit(get_opposite_direction(direction), room)

    # Add some extra random connections to create loops
    for room in rooms:
        if random.random() < 0.3: # 30% chance to add an extra connection
            other_room = random.choice(rooms)
            if room is not other_room and room.zone == other_room.zone: # Try to keep loops within zones
                direction = random.choice(DIRECTIONS)
                if direction not in room.exits:
                    room.add_exit(direction, other_room)
                    other_room.add_exit(get_opposite_direction(direction), room)
    
    # Add the GBE
    last_zone_rooms = [r for r in rooms if r.zone == zones[-1]]
    item_room = random.choice(last_zone_rooms)
    gbe_data = CONTENT["items"]["gbe"]
    gbe = Item(gbe_data["name"], gbe_data["description"])
    item_room.add_item(gbe)

    # Add some random items with logs
    for i in range(num_rooms // 5):
        item_room = random.choice(rooms)
        log = random.choice(CONTENT["item_logs"])
        item = Item("data-chip", "A small, discarded data chip.", log)
        item_room.add_item(item)

    # Add some terminals with lore
    for i in range(num_rooms // 4):
        terminal_room = random.choice(rooms)
        if not any(isinstance(item, Terminal) for item in terminal_room.items):
            lore = random.choice(CONTENT["lore_messages"])
            terminal = Terminal("terminal", "A dusty, forgotten terminal.", lore)
            terminal_room.add_item(terminal)

    # Add some enemies
    for i in range(num_rooms // 3):
        enemy_room = random.choice(rooms[1:])
        if not enemy_room.enemies:
            enemy_data = random.choice(CONTENT["enemies"])
            enemy = Enemy(enemy_data["name"], enemy_data["description"], enemy_data["health"], enemy_data["damage"], enemy_data["durability"])
            enemy_room.add_enemy(enemy)

    # Add some obstacles
    for room in rooms:
        for direction in room.exits:
            if random.random() < 0.1: # 10% chance to block an exit
                obstacle_data = random.choice(CONTENT["obstacles"])
                obstacle = Obstacle(obstacle_data["name"], obstacle_data["description"], obstacle_data["strength_required"])
                room.add_obstacle(direction, obstacle)

    return starting_room
