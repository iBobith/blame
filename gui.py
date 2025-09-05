import pygame
import os
import platform
import random
from src.world import generate_world, get_opposite_direction, CONTENT
from src.gameobjects.interactables import Terminal, Obstacle, CyberneticTerminal
from src.gameobjects.enemies import Enemy, NPC
from src.gameobjects.items import CyberneticImplant

class Colors:
    BRIGHT_BLUE = (0, 128, 255)
    BRIGHT_WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)

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

class Game:
    def __init__(self):
        self.is_running = True
        starting_room, all_stratas = generate_world(num_stratas=1)
        self.all_stratas = all_stratas
        self.player = Player(starting_room, self.all_stratas[0])
        self.message = []

    def handle_command(self, command):
        parts = command.split()
        if not parts:
            return []

        verb = parts[0]
        if self.player.current_room.enemies and verb in ['move', 'scan', 'get']:
            return [("You can't do that during combat!", Colors.RED)]

        if verb == "quit":
            self.is_running = False
            return [("Exiting.", Colors.YELLOW)]
        elif verb == "look":
            output = [(self.player.current_room.description, Colors.BRIGHT_WHITE)]
            
            actual_items = [item for item in self.player.current_room.items if not isinstance(item, NPC)]
            npcs_in_room = [item for item in self.player.current_room.items if isinstance(item, NPC)]

            if actual_items:
                output.append((f'\nYou see: ', Colors.BRIGHT_WHITE))
                output.append((f", ".join([item.name for item in actual_items]), Colors.YELLOW))
            if npcs_in_room:
                output.append((f'\nFigures present: ', Colors.BRIGHT_WHITE))
                output.append((f", ".join([npc.name for npc in npcs_in_room]), Colors.CYAN))
            if self.player.current_room.enemies:
                output.append((f'\nHostiles: ', Colors.BRIGHT_WHITE))
                output.append((f", ".join([f'{enemy.name} ({enemy.health} HP)' for enemy in self.player.current_room.enemies]), Colors.RED))
            
            exits_output = []
            for direction, room in sorted(self.player.current_room.exits.items()):
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    exits_output.append(f"{direction} (blocked by {obstacle.name})")
                else:
                    exits_output.append(direction)
            output.append((f'\nExits: ', Colors.BRIGHT_WHITE))
            output.append((f", ".join(exits_output), Colors.GREEN))

            if self.player.last_direction_moved:
                output.append((f'\nBack: ', Colors.BRIGHT_WHITE))
                output.append((get_opposite_direction(self.player.last_direction_moved), Colors.GREEN))

            return output
        elif verb == "move":
            if len(parts) > 1:
                direction = parts[1]
                if direction in self.player.current_room.obstacles:
                    obstacle = self.player.current_room.obstacles[direction]
                    if obstacle.name == "strata exit":
                        return [(f"You stand before a massive portal. It leads to another strata. You need to clear the obstacle first.", Colors.YELLOW)]
                    else:
                        return [(f"The way {direction} is blocked by a {obstacle.name}.", Colors.RED)]
                if direction in self.player.current_room.exits:
                    new_room = self.player.current_room.exits[direction]
                    self.player.current_room = new_room
                    self.player.x = new_room.x
                    self.player.y = new_room.y
                    self.player.z = new_room.z
                    self.player.last_direction_moved = direction
                    return [(f"You move {direction}.", Colors.GREEN)] + self.handle_command("look")
                else:
                    return [(f"You can't go that way.", Colors.RED)]
            else:
                return [(f"Move where?", Colors.YELLOW)]
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
                    return [(f"You picked up the {item_to_get.name}.", Colors.GREEN)]
                else:
                    return [(f"You don't see that here.", Colors.RED)]
            else:
                return [(f"Get what?", Colors.YELLOW)]
        elif verb == "inventory" or verb == "inv":
            if self.player.inventory:
                output = [(f"You are carrying:", Colors.BRIGHT_WHITE)]
                for item in self.player.inventory:
                    log_indicator = " (log)" if item.log else ""
                    output.append((f"- {item.name}{log_indicator}: {item.description}", Colors.YELLOW))
                if self.player.installed_implants:
                    output.append((f"\nInstalled Implants:", Colors.BRIGHT_WHITE))
                    for implant in self.player.installed_implants:
                        output.append((f"- {implant.name}: {implant.description}", Colors.CYAN))
                return output
            else:
                return [(f"You are not carrying anything.", Colors.YELLOW)]
        elif verb == "status":
            return [
                (f"Health: {self.player.health}", Colors.GREEN),
                (f"Energy: {self.player.energy}", Colors.YELLOW),
                (f"Strength: {self.player.strength}", Colors.CYAN),
            ]
        elif verb == "scan":
            if len(parts) > 1:
                target_name = parts[1]
                target_to_scan = None
                for item in self.player.current_room.items:
                    if item.name.lower() == target_name.lower() and (isinstance(item, Terminal) or isinstance(item, CyberneticTerminal)):
                        target_to_scan = item
                        break
                if target_to_scan:
                    output = [(f"You scan the {target_to_scan.name}...", Colors.BRIGHT_WHITE), (target_to_scan.lore_message, Colors.BRIGHT_WHITE)]
                    if isinstance(target_to_scan, CyberneticTerminal):
                        output.append(("This terminal can be used to install cybernetic implants. Use 'install [implant_name]'.", Colors.BRIGHT_WHITE))
                    return output
                else:
                    return [(f"You can't scan that.", Colors.RED)]
            else:
                return [(f"Scan what?", Colors.YELLOW)]
        elif verb == "read":
            if len(parts) > 1:
                item_name = parts[1]
                item_to_read = self.player.find_item_by_name(item_name)
                if item_to_read and item_to_read.log:
                    return [(f"The log on the {item_to_read.name} reads:", Colors.BRIGHT_WHITE), (f'"{item_to_read.log}"', Colors.YELLOW)]
                else:
                    return [(f"You can't read that.", Colors.RED)]
            else:
                return [(f"Read what?", Colors.YELLOW)]
        elif verb == "install":
            if len(parts) > 1:
                implant_name = parts[1]
                implant_to_install = None
                for item in self.player.inventory:
                    if isinstance(item, CyberneticImplant) and item.name.lower() == implant_name.lower():
                        implant_to_install = item
                        break
                
                if not implant_to_install:
                    return [(f"You don't have that implant in your inventory.", Colors.RED)]

                cybernetic_terminal_present = False
                for item in self.player.current_room.items:
                    if isinstance(item, CyberneticTerminal):
                        cybernetic_terminal_present = item
                        break
                
                if not cybernetic_terminal_present:
                    return [(f"There is no cybernetic terminal here to install implants.", Colors.RED)]

                message = cybernetic_terminal_present.install_implant(self.player, implant_to_install)
                self.player.installed_implants.append(implant_to_install)
                return [(message, Colors.GREEN)]
            else:
                return [(f"Install what?", Colors.YELLOW)]
        elif verb == "scavenge":
            if len(parts) > 1:
                target_name = parts[1]
                if not self.player.has_connection_implant:
                    return [(f"You need a Neural Interface (connection implant) to scavenge corpses.", Colors.RED)]

                scavenge_target = None
                for enemy in self.player.current_room.enemies:
                    if enemy.name.lower() == target_name.lower() and not enemy.is_alive():
                        scavenge_target = enemy
                        break
                
                if not scavenge_target:
                    return [(f"There is no defeated enemy by that name to scavenge.", Colors.RED)]

                self.player.health -= 5
                output = [(f"You attempt to scavenge the {scavenge_target.name}'s corpse, taking 5 damage.", Colors.YELLOW)]

                if random.random() < 0.4:
                    implant_data = random.choice(CONTENT["cybernetic_implants"])
                    found_implant = CyberneticImplant(implant_data["name"], implant_data["description"], implant_data["stat_bonus"], implant_data["implant_type"])
                    self.player.add_item(found_implant)
                    output.append((f"You found a {found_implant.name} and added it to your inventory!", Colors.GREEN))
                else:
                    output.append(("You found nothing of value.", Colors.YELLOW))
                
                return output
            else:
                return [(f"Scavenge what?", Colors.YELLOW)]
        elif verb == "talk":
            if len(parts) > 1:
                target_name = parts[1]
                npc_to_talk = None
                for item in self.player.current_room.items:
                    if isinstance(item, NPC) and item.name.lower() == target_name.lower():
                        npc_to_talk = item
                        break
                if npc_to_talk:
                    return [(f"{npc_to_talk.name} says: {random.choice(npc_to_talk.dialogue)}", Colors.CYAN)]
                else:
                    return [(f"There is no one here to talk to by that name.", Colors.RED)]
            else:
                return [(f"Talk to whom?", Colors.YELLOW)]
        elif verb == "attack":
            if len(parts) < 2:
                return [(f"Attack what?", Colors.YELLOW)]
            
            target_name = parts[1]
            
            enemy_to_attack = None
            for enemy in self.player.current_room.enemies:
                if enemy.name.lower() == target_name.lower():
                    enemy_to_attack = enemy
                    break
            
            if enemy_to_attack:
                output = []
                player_damage = self.player.strength
                if self.player.find_item_by_name("gbe"):
                    output.append((f"You fire the GBE!", Colors.YELLOW))
                    player_damage = 50
                
                effective_damage = max(0, player_damage - enemy_to_attack.durability)
                enemy_to_attack.health -= effective_damage
                output.append((f"You attack the {enemy_to_attack.name} for {effective_damage} damage.", Colors.GREEN))

                if not enemy_to_attack.is_alive():
                    output.append((f"The {enemy_to_attack.name} is destroyed.", Colors.GREEN))
                    self.player.current_room.remove_enemy(enemy_to_attack)
                
                for enemy in self.player.current_room.enemies:
                    self.player.health -= enemy.damage
                    output.append((f"The {enemy.name} attacks you for {enemy.damage} damage.", Colors.RED))
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
                output = [(f"You attack the {obstacle_to_attack.name} for {player_damage} damage.", Colors.GREEN)]
                if obstacle_to_attack.is_destroyed():
                    output.append((f"The {obstacle_to_attack.name} is destroyed.", Colors.GREEN))
                    self.player.current_room.remove_obstacle(obstacle_direction)
                return output

            return [(f"There is nothing here to attack by that name.", Colors.RED)]

        else:
            return [(f"Unknown command: '{command}'", Colors.RED)]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, Colors.BRIGHT_WHITE, self.rect, 2)

        text_surface = font.render(self.text, True, Colors.BRIGHT_WHITE)
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

        # Main menu buttons
        self.start_button = Button(300, 200, 200, 50, "Start New Game", Colors.BLACK, Colors.BRIGHT_BLUE)
        self.load_button = Button(300, 260, 200, 50, "Load Game", Colors.BLACK, Colors.BRIGHT_BLUE)
        self.settings_button = Button(300, 320, 200, 50, "Settings", Colors.BLACK, Colors.BRIGHT_BLUE)
        self.exit_button = Button(300, 380, 200, 50, "Exit", Colors.BLACK, Colors.BRIGHT_BLUE)

        # In-game UI
        self.input_text = ""
        self.game = None

        self.is_running = True
        self.move_button = Button(20, self.screen_height - 120, 100, 30, "Move", Colors.BLACK, Colors.BRIGHT_BLUE)
        self.interact_button = Button(130, self.screen_height - 120, 100, 30, "Interact", Colors.BLACK, Colors.BRIGHT_BLUE)
        self.attack_button = Button(240, self.screen_height - 120, 100, 30, "Attack", Colors.BLACK, Colors.BRIGHT_BLUE)
        self.direction_buttons = []
        self.show_move_buttons = False
        self.interact_buttons = []
        self.show_interact_buttons = False
        self.attack_buttons = []
        self.show_attack_buttons = False

    def run(self):
        while self.is_running:
            if self.game_state == "main_menu":
                self.run_main_menu()
            elif self.game_state == "game":
                if self.game is None:
                    self.game = Game()
                    self.game.message = [("Welcome to blame!", Colors.BRIGHT_WHITE), ("You are a wanderer in a vast, dark megastructure.", Colors.BRIGHT_WHITE)]
                    self.game.message.extend(self.game.handle_command("look"))
                self.run_game()

        pygame.quit()

    def run_main_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            if self.start_button.handle_event(event):
                self.game_state = "game"
            if self.exit_button.handle_event(event):
                self.is_running = False

        self.screen.fill(Colors.BLACK)
        self.start_button.draw(self.screen, self.font)
        self.load_button.draw(self.screen, self.font)
        self.settings_button.draw(self.screen, self.font)
        self.exit_button.draw(self.screen, self.font)
        pygame.display.flip()

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
                        button = Button(x_offset, self.screen_height - 160, 80, 30, direction, Colors.BLACK, Colors.BRIGHT_BLUE)
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
                        button = Button(x_offset, self.screen_height - 160, 80, 30, f"get {item.name}", Colors.BLACK, Colors.BRIGHT_BLUE)
                        self.interact_buttons.append(button)
                        x_offset += 90
                    for item in self.game.player.current_room.items:
                        if isinstance(item, Terminal):
                            button = Button(x_offset, self.screen_height - 160, 80, 30, f"scan {item.name}", Colors.BLACK, Colors.BRIGHT_BLUE)
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
                        button = Button(x_offset, self.screen_height - 160, 80, 30, f"attack {enemy.name}", Colors.BLACK, Colors.BRIGHT_BLUE)
                        self.attack_buttons.append(button)
                        x_offset += 90
                    for obstacle in self.game.player.current_room.obstacles.values():
                        button = Button(x_offset, self.screen_height - 160, 80, 30, f"attack {obstacle.name}", Colors.BLACK, Colors.BRIGHT_BLUE)
                        self.attack_buttons.append(button)
                        x_offset += 90
                else:
                    self.attack_buttons = []

            for button in self.direction_buttons:
                if button.handle_event(event):
                    self.game.message = self.game.handle_command(f"move {button.text}")
                    self.show_move_buttons = False
                    self.direction_buttons = []
            
            for button in self.interact_buttons:
                if button.handle_event(event):
                    self.game.message = self.game.handle_command(button.text)
                    self.show_interact_buttons = False
                    self.interact_buttons = []
            
            for button in self.attack_buttons:
                if button.handle_event(event):
                    self.game.message = self.game.handle_command(button.text)
                    self.show_attack_buttons = False
                    self.attack_buttons = []

        self.screen.fill(Colors.BLACK)

        # Draw image placeholder
        image_placeholder_rect = pygame.Rect(20, 60, 200, 200)
        pygame.draw.rect(self.screen, Colors.BLACK, image_placeholder_rect)
        pygame.draw.rect(self.screen, Colors.BRIGHT_WHITE, image_placeholder_rect, 2)

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
        pygame.draw.rect(self.screen, Colors.BLACK, top_bar_rect)
        pygame.draw.rect(self.screen, Colors.BRIGHT_WHITE, top_bar_rect, 2)

        if self.game:
            status_text = f"HP: {self.game.player.health} | Hunger: {self.game.player.hunger} | Thirst: {self.game.player.thirst} | Energy: {self.game.player.energy} | Ailments: {', '.join(self.game.player.ailments) if self.game.player.ailments else 'None'}"
            status_surface = self.font.render(status_text, True, Colors.BRIGHT_WHITE)
            self.screen.blit(status_surface, (20, 10))

            # Display location
            location_text = f"Location: {self.game.player.current_room.zone} ({self.game.player.x},{self.game.player.y},{self.game.player.z}) Strata: {self.game.player.current_strata.strata_id}"
            location_surface = self.font.render(location_text, True, Colors.BRIGHT_WHITE)
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

if __name__ == "__main__":
    gui = GameGUI()
    gui.run()