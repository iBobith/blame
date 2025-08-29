import os
import platform
import random
from world import generate_world, get_opposite_direction
from interactables import Terminal, Obstacle, CyberneticTerminal
from enemies import Enemy, NPC
from items import CyberneticImplant
from colors import Colors

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

class Game:
    def __init__(self):
        self.is_running = True
        starting_room, all_stratas = generate_world(num_stratas=1) # Generate 1 strata for now
        self.all_stratas = all_stratas
        self.player = Player(starting_room, self.all_stratas[0]) # Player starts in the first strata
        self.message = ""

    def clear_screen(self):
        command = 'cls' if platform.system() == "Windows" else 'clear'
        os.system(command)

    def display_ui(self):
        self.clear_screen()
        print(f"{Colors.BRIGHT_BLUE}{Colors.BOLD} blame! {Colors.RESET}".center(80, '='))
        print(f"{Colors.BRIGHT_WHITE}Health: {Colors.GREEN}{self.player.health}{Colors.RESET} | {Colors.BRIGHT_WHITE}Energy: {Colors.YELLOW}{self.player.energy}{Colors.RESET} | {Colors.BRIGHT_WHITE}Strength: {Colors.CYAN}{self.player.strength}{Colors.RESET} | {Colors.BRIGHT_WHITE}Location: {Colors.MAGENTA}{self.player.current_room.zone} ({self.player.x},{self.player.y},{self.player.z}) Strata: {self.player.current_strata.strata_id}{Colors.RESET}")
        print("=".ljust(80, '='))
        print(self.message)
        print("=".ljust(80, '='))
        
        if self.player.current_room.enemies:
            print("Commands: 'look', 'attack [target]', 'status', 'inv', 'read [item]', 'scavenge [target]', 'quit'")
        else:
            print("Commands: 'look', 'move [dir]', 'get [item]', 'scan [target]', 'attack [obstacle]', 'status', 'inv', 'read [item]', 'install [implant]', 'scavenge [target]', 'quit'")

    def run(self):
        self.message = f"{Colors.BRIGHT_WHITE}Welcome to blame!\nYou are a wanderer in a vast, dark megastructure.{Colors.RESET}"
        self.display_ui()
        self.message = self.handle_command("look")

        while self.is_running and self.player.is_alive():
            self.display_ui()
            try:
                command = input("> ").lower().strip()
            except EOFError:
                self.is_running = False
                command = "quit" # Or any other command that leads to graceful exit
            self.message = self.handle_command(command)
        
        if not self.player.is_alive():
            self.display_ui()
            print(f"{Colors.RED}You have succumbed to the dangers of The City. Game Over.{Colors.RESET}")

    def handle_command(self, command):
        parts = command.split()
        if not parts:
            return ""

        verb = parts[0]
        if self.player.current_room.enemies and verb in ["move", "scan", "get"]:
            return f"{Colors.RED}You can't do that during combat!{Colors.RESET}"

        if verb == "quit":
            self.is_running = False
            return f"{Colors.YELLOW}Exiting.{Colors.RESET}"
        elif verb == "look":
            output = f"{Colors.BRIGHT_WHITE}{self.player.current_room.description}{Colors.RESET}"
            
            actual_items = [item for item in self.player.current_room.items if not isinstance(item, NPC)]
            npcs_in_room = [item for item in self.player.current_room.items if isinstance(item, NPC)]

            if actual_items:
                output += f"\n{Colors.BRIGHT_WHITE}You see: {Colors.YELLOW}" + ", ".join([item.name for item in actual_items]) + f"{Colors.RESET}"
            if npcs_in_room:
                output += f"\n{Colors.BRIGHT_WHITE}Figures present: {Colors.CYAN}" + ", ".join([npc.name for npc in npcs_in_room]) + f"{Colors.RESET}"
            if self.player.current_room.enemies:
                output += f"\n{Colors.BRIGHT_WHITE}Hostiles: {Colors.RED}" + ", ".join([f'{enemy.name} ({enemy.health} HP)' for enemy in self.player.current_room.enemies]) + f"{Colors.RESET}"
            
            exits_output = []
            for direction, room in sorted(self.player.current_room.exits.items()):
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    exits_output.append(f"{direction} ({Colors.RED}blocked by {obstacle.name}{Colors.RESET})")
                else:
                    exits_output.append(direction)
            output += f"\n{Colors.BRIGHT_WHITE}Exits: {Colors.GREEN}" + ", ".join(exits_output) + f"{Colors.RESET}"

            if self.player.last_direction_moved:
                output += f"\n{Colors.BRIGHT_WHITE}Back: {Colors.GREEN}{get_opposite_direction(self.player.last_direction_moved)}{Colors.RESET}"

            return output
        elif verb == "move":
            if len(parts) > 1:
                direction = parts[1]
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    if obstacle.name == "strata exit":
                        # This is a strata exit, handle transition later
                        return f"{Colors.YELLOW}You stand before a massive portal. It leads to another strata. You need to clear the obstacle first.{Colors.RESET}"
                    else:
                        return f"{Colors.RED}The way {direction} is blocked by a {obstacle.name}.{Colors.RESET}"
                if direction in self.player.current_room.exits:
                    new_room = self.player.current_room.exits[direction]
                    self.player.current_room = new_room
                    self.player.x = new_room.x
                    self.player.y = new_room.y
                    self.player.z = new_room.z
                    self.player.last_direction_moved = direction
                    return f"{Colors.GREEN}You move {direction}.{Colors.RESET}\n\n" + self.handle_command("look")
                else:
                    return f"{Colors.RED}You can't go that way.{Colors.RESET}"
            else:
                return f"{Colors.YELLOW}Move where?{Colors.RESET}"
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
                    return f"{Colors.GREEN}You picked up the {item_to_get.name}.{Colors.RESET}"
                else:
                    return f"{Colors.RED}You don't see that here.{Colors.RESET}"
            else:
                return f"{Colors.YELLOW}Get what?{Colors.RESET}"
        elif verb == "inventory" or verb == "inv":
            if self.player.inventory:
                output = f"{Colors.BRIGHT_WHITE}You are carrying:{Colors.RESET}\n"
                for item in self.player.inventory:
                    log_indicator = " (log)" if item.log else ""
                    output += f"{Colors.YELLOW}- {item.name}{log_indicator}: {item.description}{Colors.RESET}\n"
                if self.player.installed_implants:
                    output += f"\n{Colors.BRIGHT_WHITE}Installed Implants:{Colors.RESET}\n"
                    for implant in self.player.installed_implants:
                        output += f"{Colors.CYAN}- {implant.name}: {implant.description}{Colors.RESET}\n"
                return output.strip()
            else:
                return f"{Colors.YELLOW}You are not carrying anything.{Colors.RESET}"
        elif verb == "status":
            return f"{Colors.BRIGHT_WHITE}Health: {Colors.GREEN}{self.player.health}{Colors.RESET}\n{Colors.BRIGHT_WHITE}Energy: {Colors.YELLOW}{self.player.energy}{Colors.RESET}\n{Colors.BRIGHT_WHITE}Strength: {Colors.CYAN}{self.player.strength}{Colors.RESET}"
        elif verb == "scan":
            if len(parts) > 1:
                target_name = parts[1]
                target_to_scan = None
                for item in self.player.current_room.items:
                    if item.name.lower() == target_name.lower() and (isinstance(item, Terminal) or isinstance(item, CyberneticTerminal)):
                        target_to_scan = item
                        break
                if target_to_scan:
                    output = f"{Colors.BRIGHT_WHITE}You scan the {target_to_scan.name}...\n{Colors.RESET}{target_to_scan.lore_message}"
                    if isinstance(target_to_scan, CyberneticTerminal):
                        output += "\nThis terminal can be used to install cybernetic implants. Use 'install [implant_name]'."
                    return output
                else:
                    return "You can't scan that."
            else:
                return "Scan what?"
        elif verb == "read":
            if len(parts) > 1:
                item_name = parts[1]
                item_to_read = self.player.find_item_by_name(item_name)
                if item_to_read and item_to_read.log:
                    return f"{Colors.BRIGHT_WHITE}The log on the {item_to_read.name} reads:\n\"{item_to_read.log}\"{Colors.RESET}"
                else:
                    return f"{Colors.RED}You can't read that.{Colors.RESET}"
            else:
                return f"{Colors.YELLOW}Read what?{Colors.RESET}"
        elif verb == "install":
            if len(parts) > 1:
                implant_name = parts[1]
                implant_to_install = None
                for item in self.player.inventory:
                    if isinstance(item, CyberneticImplant) and item.name.lower() == implant_name.lower():
                        implant_to_install = item
                        break
                
                if not implant_to_install:
                    return f"{Colors.RED}You don't have that implant in your inventory.{Colors.RESET}"

                cybernetic_terminal_present = False
                for item in self.player.current_room.items:
                    if isinstance(item, CyberneticTerminal):
                        cybernetic_terminal_present = item
                        break
                
                if not cybernetic_terminal_present:
                    return f"{Colors.RED}There is no cybernetic terminal here to install implants.{Colors.RESET}"

                message = cybernetic_terminal_present.install_implant(self.player, implant_to_install)
                self.player.installed_implants.append(implant_to_install)
                return f"{Colors.GREEN}{message}{Colors.RESET}"
            else:
                return f"{Colors.YELLOW}Install what?{Colors.RESET}"
        elif verb == "scavenge":
            if len(parts) > 1:
                target_name = parts[1]
                if not self.player.has_connection_implant:
                    return f"{Colors.RED}You need a Neural Interface (connection implant) to scavenge corpses.{Colors.RESET}"

                # Check if the target is a defeated enemy (corpse)
                # For simplicity, we'll assume defeated enemies are still in the room's enemies list
                # but their health is <= 0. In a more complex game, you'd have a separate 'corpse' list.
                scavenge_target = None
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == target_name.lower() and not enemy.is_alive():
                        scavenge_target = enemy
                        break
                
                if not scavenge_target:
                    return f"{Colors.RED}There is no defeated enemy by that name to scavenge.{Colors.RESET}"

                # Attempt to find an implant
                self.player.health -= 5 # Damage for attempting to scavenge
                output = f"{Colors.YELLOW}You attempt to scavenge the {scavenge_target.name}'s corpse, taking 5 damage.{Colors.RESET}\n"

                if random.random() < 0.4: # 40% chance to find an implant
                    implant_data = random.choice(CONTENT["cybernetic_implants"])
                    found_implant = CyberneticImplant(implant_data["name"], implant_data["description"], implant_data["stat_bonus"], implant_data["implant_type"])
                    self.player.add_item(found_implant)
                    output += f"{Colors.GREEN}You found a {found_implant.name} and added it to your inventory!{Colors.RESET}"
                else:
                    output += f"{Colors.YELLOW}You found nothing of value.{Colors.RESET}"
                
                return output
            else:
                return f"{Colors.YELLOW}Scavenge what?{Colors.RESET}"
        elif verb == "talk":
            if len(parts) > 1:
                target_name = parts[1]
                npc_to_talk = None
                for item in self.player.current_room.items:
                    if isinstance(item, NPC) and item.name.lower() == target_name.lower():
                        npc_to_talk = item
                        break
                if npc_to_talk:
                    return f"{Colors.CYAN}{npc_to_talk.name} says: {random.choice(npc_to_talk.dialogue)}{Colors.RESET}"
                else:
                    return f"{Colors.RED}There is no one here to talk to by that name.{Colors.RESET}"
            else:
                return f"{Colors.YELLOW}Talk to whom?{Colors.RESET}"
        elif verb == "attack":
            if len(parts) < 2:
                return f"{Colors.YELLOW}Attack what?{Colors.RESET}"
            
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
                    output += f"{Colors.BRIGHT_YELLOW}You fire the GBE!{Colors.RESET}\n"
                    player_damage = 50
                
                effective_damage = max(0, player_damage - enemy_to_attack.durability)
                enemy_to_attack.health -= effective_damage
                output += f"{Colors.GREEN}You attack the {enemy_to_attack.name} for {effective_damage} damage.{Colors.RESET}"

                if not enemy_to_attack.is_alive():
                    output += f"{Colors.GREEN}\nThe {enemy_to_attack.name} is destroyed.{Colors.RESET}"
                    self.player.current_room.remove_enemy(enemy_to_attack)
                
                for enemy in self.player.current_room.enemies:
                    self.player.health -= enemy.damage
                    output += f"{Colors.RED}\nThe {enemy.name} attacks you for {enemy.damage} damage.{Colors.RESET}"
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
                output = f"{Colors.GREEN}You attack the {obstacle_to_attack.name} for {player_damage} damage.{Colors.RESET}"
                if obstacle_to_attack.is_destroyed():
                    output += f"{Colors.GREEN}\nThe {obstacle_to_attack.name} is destroyed.{Colors.RESET}"
                    self.player.current_room.remove_obstacle(obstacle_direction)
                return output

            return f"{Colors.RED}There is nothing here to attack by that name.{Colors.RESET}"

        else:
            return f"{Colors.RED}Unknown command: '{command}'{Colors.RESET}"


def main():
    """Main function for the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
