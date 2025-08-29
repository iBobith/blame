import os
import platform
import random
from world import generate_world
from interactables import Terminal, Obstacle

class Player:
    def __init__(self, starting_room):
        self.current_room = starting_room
        self.health = 100
        self.energy = 100
        self.strength = 10
        self.inventory = []

    def add_item(self, item):
        self.inventory.append(item)

    def find_item_by_name(self, name):
        for item in self.inventory:
            if item.name.lower() == name.lower():
                return item
        return None

    def is_alive(self):
        return self.health > 0

class Game:
    def __init__(self):
        self.is_running = True
        self.world = generate_world(num_rooms=30)
        self.player = Player(self.world)
        self.message = ""

    def clear_screen(self):
        command = 'cls' if platform.system() == "Windows" else 'clear'
        os.system(command)

    def display_ui(self):
        self.clear_screen()
        print(" blame! ".center(80, '='))
        print(f"Health: {self.player.health} | Energy: {self.player.energy} | Strength: {self.player.strength} | Location: {self.player.current_room.zone}")
        print("=".ljust(80, '='))
        print(self.message)
        print("=".ljust(80, '='))
        
        if self.player.current_room.enemies:
            print("Commands: 'look', 'attack [target]', 'status', 'inv', 'read [item]', 'quit'")
        else:
            print("Commands: 'look', 'move [dir]', 'get [item]', 'scan [target]', 'attack [obstacle]', 'status', 'inv', 'read [item]', 'quit'")

    def run(self):
        self.message = "Welcome to blame!\nYou are a wanderer in a vast, dark megastructure."
        self.display_ui()
        self.message = self.handle_command("look")

        while self.is_running and self.player.is_alive():
            self.display_ui()
            command = input("> ").lower().strip()
            self.message = self.handle_command(command)
        
        if not self.player.is_alive():
            self.display_ui()
            print("You have succumbed to the dangers of The City. Game Over.")

    def handle_command(self, command):
        parts = command.split()
        if not parts:
            return ""

        verb = parts[0]
        if self.player.current_room.enemies and verb in ["move", "scan", "get"]:
            return "You can\'t do that during combat!"

        if verb == "quit":
            self.is_running = False
            return "Exiting."
        elif verb == "look":
            output = self.player.current_room.description
            if self.player.current_room.items:
                output += "\nYou see: " + ", ".join([item.name for item in self.player.current_room.items])
            if self.player.current_room.enemies:
                output += "\nHostiles: " + ", ".join([f'{enemy.name} ({enemy.health} HP)' for enemy in self.player.current_room.enemies])
            
            exits_output = []
            for direction, room in sorted(self.player.current_room.exits.items()):
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    exits_output.append(f"{direction} (blocked by {obstacle.name})")
                else:
                    exits_output.append(direction)
            output += "\nExits: " + ", ".join(exits_output)

            return output
        elif verb == "move":
            if len(parts) > 1:
                direction = parts[1]
                if direction in self.player.current_room.obstacles:
                    return f"The way {direction} is blocked by a {self.player.current_room.obstacles[direction].name}."
                if direction in self.player.current_room.exits:
                    self.player.current_room = self.player.current_room.exits[direction]
                    return f"You move {direction}.\n\n" + self.handle_command("look")
                else:
                    return "You can\'t go that way."
            else:
                return "Move where?"
        elif verb == "get":
            if len(parts) > 1:
                item_name = parts[1]
                item_to_get = None
                for item in self.player.current_room.items:
                    if item.name.lower() == item_name.lower():
                        item_to_get = item
                        break
                if item_to_get:
                    self.player.add_item(item_to_get)
                    self.player.current_room.remove_item(item_to_get)
                    return f"You picked up the {item_to_get.name}."
                else:
                    return "You don\'t see that here."
            else:
                return "Get what?"
        elif verb == "inventory" or verb == "inv":
            if self.player.inventory:
                output = "You are carrying:\n"
                for item in self.player.inventory:
                    log_indicator = " (log)" if item.log else ""
                    output += f"- {item.name}{log_indicator}: {item.description}\n"
                return output.strip()
            else:
                return "You are not carrying anything."
        elif verb == "status":
            return f"Health: {self.player.health}\nEnergy: {self.player.energy}\nStrength: {self.player.strength}"
        elif verb == "scan":
            if len(parts) > 1:
                target_name = parts[1]
                target_to_scan = None
                for item in self.player.current_room.items:
                    if item.name.lower() == target_name.lower() and isinstance(item, Terminal):
                        target_to_scan = item
                        break
                if target_to_scan:
                    return f"You scan the {target_to_scan.name}...\n{target_to_scan.lore_message}"
                else:
                    return "You can\'t scan that."
            else:
                return "Scan what?"
        elif verb == "read":
            if len(parts) > 1:
                item_name = parts[1]
                item_to_read = self.player.find_item_by_name(item_name)
                if item_to_read and item_to_read.log:
                    return f"The log on the {item_to_read.name} reads:\n\"{item_to_read.log}\""
                else:
                    return "You can\'t read that."
            else:
                return "Read what?"
        elif verb == "attack":
            if len(parts) < 2:
                return "Attack what?"
            
            target_name = parts[1]
            
            # Attack enemies
            enemy_to_attack = None
            for enemy in self.player.current_room.enemies:
                if enemy.name.lower() == target_name.lower():
                    enemy_to_attack = enemy
                    break
            
            if enemy_to_attack:
                output = ""
                player_damage = self.player.strength
                if self.player.find_item_by_name("gbe"):
                    output += "You fire the GBE!\n"
                    player_damage = 50
                
                enemy_to_attack.health -= player_damage
                output += f"You attack the {enemy_to_attack.name} for {player_damage} damage."

                if not enemy_to_attack.is_alive():
                    output += f"\nThe {enemy_to_attack.name} is destroyed."
                    self.player.current_room.remove_enemy(enemy_to_attack)
                
                for enemy in self.player.current_room.enemies:
                    self.player.health -= enemy.damage
                    output += f"\nThe {enemy.name} attacks you for {enemy.damage} damage."
                return output

            # Attack obstacles
            obstacle_to_attack = None
            obstacle_direction = None
            for direction, obstacle in self.player.current_room.obstacles.items():
                if obstacle.name.lower() == target_name.lower():
                    obstacle_to_attack = obstacle
                    obstacle_direction = direction
                    break
            
            if obstacle_to_attack:
                player_damage = self.player.strength
                obstacle_to_attack.health -= player_damage
                output = f"You attack the {obstacle_to_attack.name} for {player_damage} damage."
                if obstacle_to_attack.is_destroyed():
                    output += f"\nThe {obstacle_to_attack.name} is destroyed."
                    self.player.current_room.remove_obstacle(obstacle_direction)
                return output

            return "There is nothing here to attack by that name."

        else:
            return f"Unknown command: '{command}'"


def main():
    """Main function for the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
