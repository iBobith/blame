import random
import json
from items import Item, CyberneticImplant
from interactables import Terminal, Obstacle, CyberneticTerminal
from enemies import Enemy, NPC

# Load content from JSON file
with open("content.json", "r") as f:
    CONTENT = json.load(f)

class Room:
    def __init__(self, description, zone, x, y, z):
        self.description = description
        self.zone = zone
        self.x = x
        self.y = y
        self.z = z
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

class Strata:
    def __init__(self, width, height, depth, strata_id):
        self.width = width
        self.height = height
        self.depth = depth
        self.strata_id = strata_id
        self.grid = {} # (x, y, z) -> Room object
        self.exits_to_next_strata = [] # List of (Room, direction) tuples

DIRECTIONS = ["north", "south", "east", "west", "up", "down"]

def get_opposite_direction(direction):
    opposites = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
    return opposites.get(direction)

def generate_world(num_stratas=1):
    """Creates a network of rooms with different zones and stratas."""
    all_stratas = []
    starting_room = None

    for strata_id in range(num_stratas):
        # Randomly determine strata dimensions
        strata_width = random.randint(5, 15)
        strata_height = random.randint(5, 15)
        strata_depth = random.randint(5, 15)

        current_strata = Strata(strata_width, strata_height, strata_depth, strata_id)
        all_stratas.append(current_strata)

        zones = list(CONTENT["room_descriptions"].keys())
        
        # Create rooms for the current strata
        for x in range(strata_width):
            for y in range(strata_height):
                for z in range(strata_depth):
                    zone = random.choice(zones)
                    description = random.choice(CONTENT["room_descriptions"][zone])
                    room = Room(description, zone, x, y, z)
                    current_strata.grid[(x, y, z)] = room

        # Connect adjacent rooms within the strata
        for x in range(strata_width):
            for y in range(strata_height):
                for z in range(strata_depth):
                    room = current_strata.grid[(x, y, z)]

                    # Connect North/South
                    if y > 0 and random.random() > 0.1: # 10% chance to not connect
                        north_room = current_strata.grid[(x, y - 1, z)]
                        room.add_exit("north", north_room)
                        north_room.add_exit("south", room)
                    
                    # Connect East/West
                    if x > 0 and random.random() > 0.1: # 10% chance to not connect
                        west_room = current_strata.grid[(x - 1, y, z)]
                        room.add_exit("west", west_room)
                        west_room.add_exit("east", room)

                    # Connect Up/Down
                    if z > 0 and random.random() > 0.1: # 10% chance to not connect
                        down_room = current_strata.grid[(x, y, z - 1)]
                        room.add_exit("down", down_room)
                        down_room.add_exit("up", room)
        
        # Place Strata Exits
        possible_exit_rooms = []
        for x in range(strata_width):
            for y in range(strata_height):
                # Exits to next strata (up)
                room_up = current_strata.grid[(x, y, strata_depth - 1)]
                if "up" in room_up.exits: # Only if there's an 'up' exit
                    possible_exit_rooms.append((room_up, "up"))
                # Exits to previous strata (down)
                room_down = current_strata.grid[(x, y, 0)]
                if "down" in room_down.exits: # Only if there's a 'down' exit
                    possible_exit_rooms.append((room_down, "down"))

        num_exits = random.randint(1, 3)
        random.shuffle(possible_exit_rooms)
        
        for i in range(min(num_exits, len(possible_exit_rooms))):
            exit_room, exit_direction = possible_exit_rooms[i]
            # Create a special obstacle for strata exit
            strata_exit_obstacle = Obstacle("strata exit", f"A massive portal leading {exit_direction} to another strata.", 50) # High strength required
            exit_room.add_obstacle(exit_direction, strata_exit_obstacle)
            current_strata.exits_to_next_strata.append((exit_room, exit_direction))
        
        # Set starting room for the first strata
        if strata_id == 0:
            starting_room = current_strata.grid[(0, 0, 0)]

        # Add game elements to rooms in the current strata
        all_rooms_in_strata = list(current_strata.grid.values())

        # Add the GBE (only once in the entire world, in the last strata)
        if strata_id == num_stratas - 1:
            gbe_room = random.choice(all_rooms_in_strata)
            gbe_data = CONTENT["items"]["gbe"]
            gbe = Item(gbe_data["name"], gbe_data["description"])
            gbe_room.add_item(gbe)

        # Add some random items with logs
        for _ in range(len(all_rooms_in_strata) // 10):
            item_room = random.choice(all_rooms_in_strata)
            log = random.choice(CONTENT["item_logs"])
            item = Item("data-chip", "A small, discarded data chip.", log)
            item_room.add_item(item)

        # Add some cybernetic implants
        for _ in range(len(all_rooms_in_strata) // 15):
            implant_room = random.choice(all_rooms_in_strata)
            implant_data = random.choice(CONTENT["cybernetic_implants"])
            implant = CyberneticImplant(implant_data["name"], implant_data["description"], implant_data["stat_bonus"], implant_data["implant_type"])
            implant_room.add_item(implant)

        # Add some terminals with lore and cybernetic terminals
        for _ in range(len(all_rooms_in_strata) // 8):
            terminal_room = random.choice(all_rooms_in_strata)
            if not any(isinstance(item, Terminal) for item in terminal_room.items):
                if random.random() < 0.3: # 30% chance for a CyberneticTerminal
                    lore = random.choice(CONTENT["lore_messages"])
                    terminal = CyberneticTerminal("cybernetic terminal", "A terminal with advanced interfaces for cybernetic modifications.", lore)
                else:
                    lore = random.choice(CONTENT["lore_messages"])
                    terminal = Terminal("terminal", "A dusty, forgotten terminal.", lore)
                terminal_room.add_item(terminal)

        # Add some enemies
        for _ in range(len(all_rooms_in_strata) // 6):
            enemy_room = random.choice(all_rooms_in_strata)
            if not enemy_room.enemies:
                enemy_data = random.choice(CONTENT["enemies"])
                enemy = Enemy(enemy_data["name"], enemy_data["description"], enemy_data["health"], enemy_data["damage"], enemy_data["durability"])
                enemy_room.add_enemy(enemy)

        # Add some NPCs
        for _ in range(len(all_rooms_in_strata) // 10):
            npc_room = random.choice(all_rooms_in_strata)
            if not any(isinstance(item, NPC) for item in npc_room.items): # Avoid placing multiple NPCs in one room
                npc_data = random.choice(CONTENT["npcs"])
                npc = NPC(npc_data["name"], npc_data["description"], npc_data["dialogue"])
                npc_room.items.append(npc) # NPCs are treated as items in the room for simplicity

        # Add some obstacles
        for room in all_rooms_in_strata:
            for direction in room.exits:
                if random.random() < 0.1: # 10% chance to block an exit
                    obstacle_data = random.choice(CONTENT["obstacles"])
                    obstacle = Obstacle(obstacle_data["name"], obstacle_data["description"], obstacle_data["strength_required"])
                    room.add_obstacle(direction, obstacle)

    return starting_room, all_stratas
