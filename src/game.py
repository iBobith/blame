
import random
import json
from datetime import datetime
from .world import generate_world, get_opposite_direction, CONTENT, Room, Strata
from .gameobjects.interactables import Terminal, Obstacle, CyberneticTerminal
from .gameobjects.enemies import Enemy, NPC
from .gameobjects.items import CyberneticImplant, Item
from .gameobjects.factory import create_from_json

class Player:
    def __init__(self, starting_room, starting_strata):
        self.current_room = starting_room
        self.current_strata = starting_strata
        self.x = starting_room.x
        self.y = starting_room.y
        self.z = starting_room.z
        self.health = 100
        self.energy = 100
        self.strength = 10
        self.hunger = 100
        self.thirst = 100
        self.ailments = []
        self.inventory = []
        self.installed_implants = []
        self.has_connection_implant = False
        self.last_direction_moved = None

    def add_item(self, item):
        self.inventory.append(item)

    def find_item_by_name(self, name):
        for item in self.inventory:
            if item.name.lower() == name.lower():
                return item
        return None

    def is_alive(self):
        return self.health > 0

    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "health": self.health,
            "energy": self.energy,
            "strength": self.strength,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "ailments": self.ailments,
            "inventory": [item.to_json() for item in self.inventory],
            "installed_implants": [implant.to_json() for implant in self.installed_implants],
            "has_connection_implant": self.has_connection_implant,
            "last_direction_moved": self.last_direction_moved,
            "strata_id": self.current_strata.strata_id
        }

    @classmethod
    def from_json(cls, data, all_stratas):
        strata = next((s for s in all_stratas if s.strata_id == data["strata_id"]), None)
        if not strata:
            return None
        room = strata.grid.get((data["x"], data["y"], data["z"]))
        if not room:
            return None
        
        player = cls(room, strata)
        player.health = data["health"]
        player.energy = data["energy"]
        player.strength = data["strength"]
        player.hunger = data["hunger"]
        player.thirst = data["thirst"]
        player.ailments = data["ailments"]
        player.inventory = [create_from_json(item_data) for item_data in data["inventory"]]
        player.installed_implants = [create_from_json(implant_data) for implant_data in data["installed_implants"]]
        player.has_connection_implant = data["has_connection_implant"]
        player.last_direction_moved = data["last_direction_moved"]
        return player

class Game:
    def __init__(self, all_stratas=None, player=None):
        self.is_running = True
        if all_stratas and player:
            self.all_stratas = all_stratas
            self.player = player
        else:
            starting_room, self.all_stratas = generate_world(num_stratas=1)
            self.player = Player(starting_room, self.all_stratas[0])
        self.message = []
        self.current_attack_target = None # New attribute

    def handle_command(self, command, colors):
        parts = command.split()
        if not parts:
            return []

        verb = parts[0]
        if self.player.current_room.enemies and verb in ['move', 'scan', 'get']:
            return [("You can't do that during combat!", colors.RED)]

        if verb == "quit":
            self.is_running = False
            return [("Exiting.", colors.YELLOW)]
        elif verb == "look":
            output = [(self.player.current_room.description, colors.BRIGHT_WHITE)]
            
            actual_items = [item for item in self.player.current_room.items if not isinstance(item, NPC)]
            npcs_in_room = [item for item in self.player.current_room.items if isinstance(item, NPC)]

            if actual_items:
                output.append(("\nYou see: ", colors.BRIGHT_WHITE))
                output.append((f", ".join([item.name for item in actual_items if item]), colors.YELLOW))
            if npcs_in_room:
                output.append(("\nFigures present: ", colors.BRIGHT_WHITE))
                output.append((f", ".join([npc.name for npc in npcs_in_room if npc]), colors.CYAN))
            if self.player.current_room.enemies:
                output.append(("\nHostiles: ", colors.BRIGHT_WHITE))
                output.append((f", ".join([f'{enemy.name} ({enemy.health} HP)' for enemy in self.player.current_room.enemies]), colors.RED))
            
            exits_output = []
            for direction, room in sorted(self.player.current_room.exits.items()):
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    exits_output.append(f"{direction} (blocked by {obstacle.name})")
                else:
                    exits_output.append(direction)
            output.append(("\nExits: ", colors.BRIGHT_WHITE))
            output.append((f", ".join(exits_output), colors.GREEN))

            if self.player.last_direction_moved:
                output.append(("\nBack: ", colors.BRIGHT_WHITE))
                output.append((get_opposite_direction(self.player.last_direction_moved), colors.GREEN))

            return output
        elif verb == "move":
            if len(parts) > 1:
                direction = parts[1]
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    if obstacle.name == "strata exit":
                        return [("You stand before a massive pillar. It leads to another strata. You must ascend the partial megastructure in order to reach the next strata.", colors.YELLOW)]
                    else:
                        return [("The way {direction} is blocked by a {obstacle.name}.", colors.RED)]
                if direction in self.player.current_room.exits:
                    new_room = self.player.current_room.exits[direction]
                    self.player.current_room = new_room
                    self.player.x = new_room.x
                    self.player.y = new_room.y
                    self.player.z = new_room.z
                    self.player.last_direction_moved = direction
                    return [("You move {direction}.", colors.GREEN)] + self.handle_command("look", colors)
                else:
                    return [("You can't go that way.", colors.RED)]
            else:
                return [("Move where?", colors.YELLOW)]
        elif verb == "get":
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                item_to_get = None
                for item in self.player.current_room.items:
                    if item.name.lower() == item_name.lower():
                        item_to_get = item
                        break
                if item_to_get:
                    self.player.add_item(item_to_get)
                    self.player.current_room.remove_item(item_to_get)
                    return [("You picked up the {item_to_get.name}.", colors.GREEN)]
                else:
                    return [("You don't see that here.", colors.RED)]
            else:
                return [("Get what?", colors.YELLOW)]
        elif verb == "inventory" or verb == "inv":
            if self.player.inventory:
                output = [("You are carrying:", colors.BRIGHT_WHITE)]
                for item in self.player.inventory:
                    log_indicator = " (log)" if item.log else ""
                    output.append((f"- {item.name}{log_indicator}: {item.description}", colors.YELLOW))
                if self.player.installed_implants:
                    output.append((f"\nInstalled Implants:", colors.BRIGHT_WHITE))
                    for implant in self.player.installed_implants:
                        output.append((f"- {implant.name}: {implant.description}", colors.CYAN))
                return output
            else:
                return [("You are not carrying anything.", colors.YELLOW)]
        elif verb == "status":
            return [
                (f"Health: {self.player.health}", colors.GREEN),
                (f"Energy: {self.player.energy}", colors.YELLOW),
                (f"Strength: {self.player.strength}", colors.CYAN),
            ]
        elif verb == "scan":
            if len(parts) > 1:
                target_name = " ".join(parts[1:])
                target_to_scan = None
                for item in self.player.current_room.items:
                    if item.name.lower() == target_name.lower() and (isinstance(item, Terminal) or isinstance(item, CyberneticTerminal)):
                        target_to_scan = item
                        break
                if target_to_scan:
                    output = [(f"You scan the {target_to_scan.name}...", colors.BRIGHT_WHITE), (target_to_scan.lore_message, colors.BRIGHT_WHITE)]
                    if isinstance(target_to_scan, CyberneticTerminal):
                        output.append(("This terminal can be used to install cybernetic implants. Use 'install [implant_name]'.", colors.BRIGHT_WHITE))
                    return output
                else:
                    return [("You can't scan that.", colors.RED)]
            else:
                return [("Scan what?", colors.YELLOW)]
        elif verb == "read":
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                item_to_read = self.player.find_item_by_name(item_name)
                if item_to_read and item_to_read.log:
                    return [(f"The log on the {item_to_read.name} reads:", colors.BRIGHT_WHITE), (f'"{item_to_read.log}"', colors.YELLOW)]
                else:
                    return [("You can't read that.", colors.RED)]
            else:
                return [("Read what?", colors.YELLOW)]
        elif verb == "install":
            if len(parts) > 1:
                implant_name = " ".join(parts[1:])
                implant_to_install = None
                for item in self.player.inventory:
                    if isinstance(item, CyberneticImplant) and item.name.lower() == implant_name.lower():
                        implant_to_install = item
                        break
                
                if not implant_to_install:
                    return [("You don't have that implant in your inventory.", colors.RED)]

                cybernetic_terminal_present = False
                for item in self.player.current_room.items:
                    if isinstance(item, CyberneticTerminal):
                        cybernetic_terminal_present = item
                        break
                
                if not cybernetic_terminal_present:
                    return [("There is no cybernetic terminal here to install implants.", colors.RED)]

                message = cybernetic_terminal_present.install_implant(self.player, implant_to_install)
                self.player.installed_implants.append(implant_to_install)
                return [(message, colors.GREEN)]
            else:
                return [("Install what?", colors.YELLOW)]
        elif verb == "scavenge":
            if len(parts) > 1:
                target_name = " ".join(parts[1:])
                if not self.player.has_connection_implant:
                    return [("You need a Neural Interface (connection implant) to scavenge corpses.", colors.RED)]

                scavenge_target = None
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == target_name.lower() and not enemy.is_alive():
                        scavenge_target = enemy
                        break
                
                if not scavenge_target:
                    return [("There is no defeated enemy by that name to scavenge.", colors.RED)]

                self.player.health -= 5
                output = [("You attempt to scavenge the {scavenge_target.name}'s corpse, taking 5 damage.", colors.YELLOW)]

                if random.random() < 0.4:
                    implant_data = random.choice(CONTENT["cybernetic_implants"])
                    found_implant = CyberneticImplant(implant_data["name"], implant_data["description"], implant_data["stat_bonus"], implant_data["implant_type"])
                    self.player.add_item(found_implant)
                    output.append((f"You found a {found_implant.name} and added it to your inventory!", colors.GREEN))
                else:
                    output.append(("You found nothing of value.", colors.YELLOW))
                
                return output
            else:
                return [("Scavenge what?", colors.YELLOW)]
        elif verb == "talk":
            if len(parts) > 1:
                target_name = " ".join(parts[1:])
                npc_to_talk = None
                for item in self.player.current_room.items:
                    if isinstance(item, NPC) and item.name.lower() == target_name.lower():
                        npc_to_talk = item
                        break
                if npc_to_talk:
                    return [(f"{npc_to_talk.name} says: {random.choice(npc_to_talk.dialogue)}", colors.CYAN)]
                else:
                    return [("There is no one here to talk to by that name.", colors.RED)]
            else:
                return [("Talk to whom?", colors.YELLOW)]
        elif verb == "attack":
            if len(parts) < 2:
                return [(f"Attack what?", colors.YELLOW)]
            
            target_name = " ".join(parts[1:])
            
            # Find target (enemy or obstacle)
            target = None
            for enemy in self.player.current_room.enemies:
                if enemy.name.lower() == target_name.lower():
                    target = enemy
                    break
            if not target:
                for direction, obstacle in self.player.current_room.obstacles.items():
                    if obstacle.name.lower() == target_name.lower():
                        target = obstacle
                        break
            
            if target:
                self.current_attack_target = target
                # This will trigger the GUI to show weapon selection
                return [(f"You target the {target.name}. Choose a weapon.", colors.BRIGHT_WHITE)]
            else:
                return [(f"There is nothing here to attack by that name.", colors.RED)]
        elif verb == "use_weapon":
            if not self.current_attack_target:
                return [(f"No target selected for attack.", colors.RED)]
            
            if len(parts) < 2:
                return [(f"Use what weapon?", colors.YELLOW)]
            
            weapon_name = " ".join(parts[1:])
            weapon = self.player.find_item_by_name(weapon_name)

            if not weapon:
                return [(f"You don't have a {weapon_name}.", colors.RED)]
            
            # Assuming 'gbe' is the only special weapon for now
            player_damage = self.player.strength
            if weapon.name.lower() == "gbe":
                player_damage = 50 # GBE specific damage

            output = []
            target = self.current_attack_target

            if isinstance(target, Enemy):
                effective_damage = max(0, player_damage - target.durability)
                target.health -= effective_damage
                output.append((f"You attack the {target.name} with {weapon.name} for {effective_damage} damage.", colors.GREEN))

                if not target.is_alive():
                    output.append((f"The {target.name} is destroyed.", colors.GREEN))
                    self.player.current_room.remove_enemy(target)
                
                # Enemy counter-attack
                for enemy in self.player.current_room.enemies: # All remaining enemies attack
                    self.player.health -= enemy.damage
                    output.append((f"The {enemy.name} attacks you for {enemy.damage} damage.", colors.RED))
            elif isinstance(target, Obstacle):
                target.health -= player_damage
                output.append((f"You attack the {target.name} with {weapon.name} for {player_damage} damage.", colors.GREEN))
                if target.is_destroyed():
                    output.append((f"The {target.name} is destroyed.", colors.GREEN))
                    # Need to find the direction of the obstacle to remove it
                    for direction, obs in self.player.current_room.obstacles.items():
                        if obs == target:
                            self.player.current_room.remove_obstacle(direction)
                            break
            
            self.current_attack_target = None # Clear target after attack
            return output

        elif verb == "escape":
            if not self.player.current_room.enemies:
                return [("You are not in combat.", colors.YELLOW)]
            
            # Simple escape logic: 50% chance to escape
            if random.random() < 0.5:
                self.player.current_room.enemies = [] # Clear enemies
                return [("You successfully escaped from combat!", colors.GREEN)]
            else:
                output = [("You failed to escape!", colors.RED)]
                # Enemies get a free attack
                for enemy in self.player.current_room.enemies:
                    self.player.health -= enemy.damage
                    output.append((f"The {enemy.name} attacks you for {enemy.damage} damage.", colors.RED))
                return output

        else:
            return [(f"Unknown command: '{command}'", colors.RED)]
