import pygame
import os
import platform
import random
import json
from datetime import datetime
from src.world import generate_world, get_opposite_direction, CONTENT, Room, Strata
from src.gameobjects.interactables import Terminal, Obstacle, CyberneticTerminal
from src.gameobjects.enemies import Enemy, NPC
from src.gameobjects.items import CyberneticImplant, Item
from src.gameobjects.factory import create_from_json

class Colors:
    def __init__(self, theme='dark'):
        self.set_theme(theme)

    def set_theme(self, theme):
        if theme == 'dark':
            self.BRIGHT_BLUE = (0, 128, 255)
            self.BRIGHT_WHITE = (255, 255, 255)
            self.GREEN = (0, 255, 0)
            self.YELLOW = (255, 255, 0)
            self.CYAN = (0, 255, 255)
            self.MAGENTA = (255, 0, 255)
            self.RED = (255, 0, 0)
            self.BLACK = (0, 0, 0)
        else:
            self.BRIGHT_BLUE = (0, 0, 255)
            self.BRIGHT_WHITE = (0, 0, 0)
            self.GREEN = (0, 128, 0)
            self.YELLOW = (200, 200, 0)
            self.CYAN = (0, 128, 128)
            self.MAGENTA = (128, 0, 128)
            self.RED = (255, 0, 0)
            self.BLACK = (255, 255, 255)

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
                output.append((f'\nYou see: ', colors.BRIGHT_WHITE))
                output.append((f", ".join([item.name for item in actual_items if item]), colors.YELLOW))
            if npcs_in_room:
                output.append((f'\nFigures present: ', colors.BRIGHT_WHITE))
                output.append((f", ".join([npc.name for npc in npcs_in_room if npc]), colors.CYAN))
            if self.player.current_room.enemies:
                output.append((f'\nHostiles: ', colors.BRIGHT_WHITE))
                output.append((f", ".join([f'{enemy.name} ({enemy.health} HP)' for enemy in self.player.current_room.enemies]), colors.RED))
            
            exits_output = []
            for direction, room in sorted(self.player.current_room.exits.items()):
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    exits_output.append(f"{direction} (blocked by {obstacle.name})")
                else:
                    exits_output.append(direction)
            output.append((f'\nExits: ', colors.BRIGHT_WHITE))
            output.append((f", ".join(exits_output), colors.GREEN))

            if self.player.last_direction_moved:
                output.append((f'\nBack: ', colors.BRIGHT_WHITE))
                output.append((get_opposite_direction(self.player.last_direction_moved), colors.GREEN))

            return output
        elif verb == "move":
            if len(parts) > 1:
                direction = parts[1]
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    if obstacle.name == "strata exit":
                        return [(f"You stand before a massive portal. It leads to another strata. You need to clear the obstacle first.", colors.YELLOW)]
                    else:
                        return [(f"The way {direction} is blocked by a {obstacle.name}.", colors.RED)]
                if direction in self.player.current_room.exits:
                    new_room = self.player.current_room.exits[direction]
                    self.player.current_room = new_room
                    self.player.x = new_room.x
                    self.player.y = new_room.y
                    self.player.z = new_room.z
                    self.player.last_direction_moved = direction
                    return [(f"You move {direction}.", colors.GREEN)] + self.handle_command("look", colors)
                else:
                    return [(f"You can't go that way.", colors.RED)]
            else:
                return [(f"Move where?", colors.YELLOW)]
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
                    return [(f"You picked up the {item_to_get.name}.", colors.GREEN)]
                else:
                    return [(f"You don't see that here.", colors.RED)]
            else:
                return [(f"Get what?", colors.YELLOW)]
        elif verb == "inventory" or verb == "inv":
            if self.player.inventory:
                output = [(f"You are carrying:", colors.BRIGHT_WHITE)]
                for item in self.player.inventory:
                    log_indicator = " (log)" if item.log else ""
                    output.append((f"- {item.name}{log_indicator}: {item.description}", colors.YELLOW))
                if self.player.installed_implants:
                    output.append((f"\nInstalled Implants:", colors.BRIGHT_WHITE))
                    for implant in self.player.installed_implants:
                        output.append((f"- {implant.name}: {implant.description}", colors.CYAN))
                return output
            else:
                return [(f"You are not carrying anything.", colors.YELLOW)]
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
                    return [(f"You can't scan that.", colors.RED)]
            else:
                return [(f"Scan what?", colors.YELLOW)]
        elif verb == "read":
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                item_to_read = self.player.find_item_by_name(item_name)
                if item_to_read and item_to_read.log:
                    return [(f"The log on the {item_to_read.name} reads:", colors.BRIGHT_WHITE), (f'"{item_to_read.log}"', colors.YELLOW)]
                else:
                    return [(f"You can't read that.", colors.RED)]
            else:
                return [(f"Read what?", colors.YELLOW)]
        elif verb == "install":
            if len(parts) > 1:
                implant_name = " ".join(parts[1:])
                implant_to_install = None
                for item in self.player.inventory:
                    if isinstance(item, CyberneticImplant) and item.name.lower() == implant_name.lower():
                        implant_to_install = item
                        break
                
                if not implant_to_install:
                    return [(f"You don't have that implant in your inventory.", colors.RED)]

                cybernetic_terminal_present = False
                for item in self.player.current_room.items:
                    if isinstance(item, CyberneticTerminal):
                        cybernetic_terminal_present = item
                        break
                
                if not cybernetic_terminal_present:
                    return [(f"There is no cybernetic terminal here to install implants.", colors.RED)]

                message = cybernetic_terminal_present.install_implant(self.player, implant_to_install)
                self.player.installed_implants.append(implant_to_install)
                return [(message, colors.GREEN)]
            else:
                return [(f"Install what?", colors.YELLOW)]
        elif verb == "scavenge":
            if len(parts) > 1:
                target_name = " ".join(parts[1:])
                if not self.player.has_connection_implant:
                    return [(f"You need a Neural Interface (connection implant) to scavenge corpses.", colors.RED)]

                scavenge_target = None
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == target_name.lower() and not enemy.is_alive():
                        scavenge_target = enemy
                        break
                
                if not scavenge_target:
                    return [(f"There is no defeated enemy by that name to scavenge.", colors.RED)]

                self.player.health -= 5
                output = [(f"You attempt to scavenge the {scavenge_target.name}'s corpse, taking 5 damage.", colors.YELLOW)]

                if random.random() < 0.4:
                    implant_data = random.choice(CONTENT["cybernetic_implants"])
                    found_implant = CyberneticImplant(implant_data["name"], implant_data["description"], implant_data["stat_bonus"], implant_data["implant_type"])
                    self.player.add_item(found_implant)
                    output.append((f"You found a {found_implant.name} and added it to your inventory!", colors.GREEN))
                else:
                    output.append(("You found nothing of value.", colors.YELLOW))
                
                return output
            else:
                return [(f"Scavenge what?", colors.YELLOW)]
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
                    return [(f"There is no one here to talk to by that name.", colors.RED)]
            else:
                return [(f"Talk to whom?", colors.YELLOW)]
        elif verb == "attack":
            if len(parts) < 2:
                return [(f"Attack what?", colors.YELLOW)]
            
            target_name = " ".join(parts[1:])
            
            enemy_to_attack = None
            for enemy in self.player.current_room.enemies:
                if enemy.name.lower() == target_name.lower():
                    enemy_to_attack = enemy
                    break
            
            if enemy_to_attack:
                output = []
                player_damage = self.player.strength
                if self.player.find_item_by_name("gbe"):
                    output.append((f"You fire the GBE!", colors.YELLOW))
                    player_damage = 50
                
                effective_damage = max(0, player_damage - enemy_to_attack.durability)
                enemy_to_attack.health -= effective_damage
                output.append((f"You attack the {enemy_to_attack.name} for {effective_damage} damage.", colors.GREEN))

                if not enemy_to_attack.is_alive():
                    output.append((f"The {enemy_to_attack.name} is destroyed.", colors.GREEN))
                    self.player.current_room.remove_enemy(enemy_to_attack)
                
                for enemy in self.player.current_room.enemies:
                    self.player.health -= enemy.damage
                    output.append((f"The {enemy.name} attacks you for {enemy.damage} damage.", colors.RED))
                return output

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
                output = [(f"You attack the {obstacle_to_attack.name} for {player_damage} damage.", colors.GREEN)]
                if obstacle_to_attack.is_destroyed():
                    output.append((f"The {obstacle_to_attack.name} is destroyed.", colors.GREEN))
                    self.player.current_room.remove_obstacle(obstacle_direction)
                return output

            return [(f"There is nothing here to attack by that name.", colors.RED)]

        else:
            return [(f"Unknown command: '{command}'", colors.RED)]

class Button:
    def __init__(self, x, y, width, height, text, colors):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.colors = colors
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.colors.BRIGHT_BLUE if self.is_hovered else self.colors.BLACK
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.colors.BRIGHT_WHITE, self.rect, 2)

        text_surface = font.render(self.text, True, self.colors.BRIGHT_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class GameGUI:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("blame!")

        self.font = pygame.font.Font(None, 24)
        self.game_state = "main_menu"
        self.colors = Colors()

        # Main menu buttons
        self.start_button = Button(300, 200, 200, 50, "Start New Game", self.colors)
        self.load_button = Button(300, 260, 200, 50, "Load Game", self.colors)
        self.settings_button = Button(300, 320, 200, 50, "Settings", self.colors)
        self.exit_button = Button(300, 380, 200, 50, "Exit", self.colors)

        # Settings buttons
        self.dark_mode_button = Button(300, 200, 200, 50, "Dark/Light Mode", self.colors)
        self.text_speed_button = Button(300, 260, 200, 50, "Text Speed", self.colors)
        self.github_button = Button(300, 320, 200, 50, "Github", self.colors)
        self.back_button = Button(300, 380, 200, 50, "Back", self.colors)

        # In-game UI
        self.input_text = ""
        self.game = None

        self.is_running = True
        self.move_button = Button(20, self.screen_height - 120, 100, 30, "Move", self.colors)
        self.interact_button = Button(130, self.screen_height - 120, 100, 30, "Interact", self.colors)
        self.attack_button = Button(240, self.screen_height - 120, 100, 30, "Attack", self.colors)
        self.direction_buttons = []
        self.show_move_buttons = False
        self.interact_buttons = []
        self.show_interact_buttons = False
        self.attack_buttons = []
        self.show_attack_buttons = False
        self.save_files = []
        self.show_save_files = False

    

    def run_game(self):
        if not self.game.player.is_alive():
            self.game_state = "main_menu"
            self.game = None
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            
            if self.move_button.handle_event(event):
                self.show_move_buttons = not self.show_move_buttons
                if self.show_move_buttons:
                    self.direction_buttons = []
                    x_offset = 20
                    for direction in self.game.player.current_room.exits:
                        button = Button(x_offset, self.screen_height - 160, 80, 30, direction, self.colors)
                        self.direction_buttons.append(button)
                        x_offset += 90
                else:
                    self.direction_buttons = []

            if self.interact_button.handle_event(event):
                self.show_interact_buttons = not self.show_interact_buttons
                if self.show_interact_buttons:
                    self.interact_buttons = []
                    x_offset = 130
                    interactable_items = [item for item in self.game.player.current_room.items if not isinstance(item, NPC)]
                    for item in interactable_items:
                        button = Button(x_offset, self.screen_height - 160, 80, 30, f"get {item.name}", self.colors)
                        self.interact_buttons.append(button)
                        x_offset += 90
                    for item in self.game.player.current_room.items:
                        if isinstance(item, Terminal):
                            button = Button(x_offset, self.screen_height - 160, 80, 30, f"scan {item.name}", self.colors)
                            self.interact_buttons.append(button)
                            x_offset += 90
                else:
                    self.interact_buttons = []

            if self.attack_button.handle_event(event):
                self.show_attack_buttons = not self.show_attack_buttons
                if self.show_attack_buttons:
                    self.attack_buttons = []
                    x_offset = 240
                    for enemy in self.game.player.current_room.enemies:
                        button = Button(x_offset, self.screen_height - 160, 80, 30, f"attack {enemy.name}", self.colors)
                        self.attack_buttons.append(button)
                        x_offset += 90
                    for obstacle in self.game.player.current_room.obstacles.values():
                        button = Button(x_offset, self.screen_height - 160, 80, 30, f"attack {obstacle.name}", self.colors)
                        self.attack_buttons.append(button)
                        x_offset += 90
                else:
                    self.attack_buttons = []

            for button in self.direction_buttons:
                if button.handle_event(event):
                    self.game.message = self.game.handle_command(f"move {button.text}", self.colors)
                    self.show_move_buttons = False
                    self.direction_buttons = []
            
            for button in self.interact_buttons:
                if button.handle_event(event):
                    self.game.message = self.game.handle_command(button.text, self.colors)
                    self.show_interact_buttons = False
                    self.interact_buttons = []
            
            for button in self.attack_buttons:
                if button.handle_event(event):
                    self.game.message = self.game.handle_command(button.text, self.colors)
                    self.show_attack_buttons = False
                    self.attack_buttons = []

        self.screen.fill(self.colors.BLACK)

        # Draw image placeholder
        image_placeholder_rect = pygame.Rect(20, 60, 200, 200)
        pygame.draw.rect(self.screen, self.colors.BLACK, image_placeholder_rect)
        pygame.draw.rect(self.screen, self.colors.BRIGHT_WHITE, image_placeholder_rect, 2)

        # Display game message
        y_offset = 60
        x_offset = 240
        if self.game and self.game.message:
            for text, color in self.game.message:
                lines = text.split('\n')
                for line in lines:
                    text_surface = self.font.render(line, True, color)
                    self.screen.blit(text_surface, (x_offset, y_offset))
                    y_offset += 24

        # Display top bar
        top_bar_rect = pygame.Rect(0, 0, self.screen_width, 40)
        pygame.draw.rect(self.screen, self.colors.BLACK, top_bar_rect)
        pygame.draw.rect(self.screen, self.colors.BRIGHT_WHITE, top_bar_rect, 2)

        if self.game:
                        status_surface = self.font.render(status_text, True, self.colors.BRIGHT_WHITE)
            self.screen.blit(status_surface, (20, 10))

            # Display location
            location_text = f"Location: {self.game.player.current_room.zone} ({self.game.player.x},{self.game.player.y},{self.game.player.z}) Strata: {self.game.player.current_strata.strata_id}"
            location_surface = self.font.render(location_text, True, self.colors.BRIGHT_WHITE)
            self.screen.blit(location_surface, (20, self.screen_height - 80))

        

        # Draw buttons
        self.move_button.draw(self.screen, self.font)
        self.interact_button.draw(self.screen, self.font)
        self.attack_button.draw(self.screen, self.font)
        if self.show_move_buttons:
            for button in self.direction_buttons:
                button.draw(self.screen, self.font)
        if self.show_interact_buttons:
            for button in self.interact_buttons:
                button.draw(self.screen, self.font)
        if self.show_attack_buttons:
            for button in self.attack_buttons:
                button.draw(self.screen, self.font)

        pygame.display.flip()

    def get_save_files(self):
        if not os.path.exists("saves"):
            return []
        files = []
        for f in os.listdir("saves"):
            if f.endswith(".json"):
                file_path = os.path.join("saves", f)
                date_str = f.replace("save_", "").replace(".json", "")
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
                    files.append((file_path, date_obj.strftime("%Y-%m-%d %H:%M:%S")))
                except ValueError:
                    continue
        return sorted(files, key=lambda x: x[1], reverse=True)

    def save_game_state(self):
        if not os.path.exists("saves"):
            os.makedirs("saves")
        
        now = datetime.now()
        file_name = f"save_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        file_path = os.path.join("saves", file_name)

        data = {
            "player": self.game.player.to_json(),
            "stratas": [strata.to_json() for strata in self.game.all_stratas]
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_game_state(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        
        all_stratas = [Strata.from_json(s_data) for s_data in data["stratas"]]
        player = Player.from_json(data["player"], all_stratas)
        self.game = Game(all_stratas=all_stratas, player=player)
        self.game.message.extend(self.game.handle_command("look", self.colors))

if __name__ == "__main__":
    gui = GameGUI()
    gui.run()