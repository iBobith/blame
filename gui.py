import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import platform
import webbrowser
import json
from datetime import datetime
from src.game import Game, Player
from src.world import generate_world, get_opposite_direction, CONTENT, Room, Strata
from src.colors import Colors
from src.gameobjects.items import CyberneticImplant
from src.gameobjects.enemies import NPC

class GameGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("blame!")
        self.geometry("800x600")

        self.colors = Colors()
        self.game_state = "main_menu"
        self.game = None
        self.text_speed = 1
        self.text_speed_options = [1, 2, 3]

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.apply_theme()
        self.create_main_menu()

    def apply_theme(self):
        self.main_frame.config(bg=self.colors.BLACK)
        self.configure(bg=self.colors.BLACK)

        if hasattr(self, 'message_area'):
            self.message_area.config(bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE)
            self.message_area.tag_config("BRIGHT_BLUE", foreground=self.colors.BRIGHT_BLUE)
            self.message_area.tag_config("BRIGHT_WHITE", foreground=self.colors.BRIGHT_WHITE)
            self.message_area.tag_config("GREEN", foreground=self.colors.GREEN)
            self.message_area.tag_config("YELLOW", foreground=self.colors.YELLOW)
            self.message_area.tag_config("CYAN", foreground=self.colors.CYAN)
            self.message_area.tag_config("MAGENTA", foreground=self.colors.MAGENTA)
            self.message_area.tag_config("RED", foreground=self.colors.RED)
            self.message_area.tag_config("BLACK", foreground=self.colors.BLACK)


    def create_main_menu(self):
        self.clear_frame()

        self.game_state = "main_menu"

        menu_frame = tk.Frame(self.main_frame, bg=self.colors.BLACK)
        menu_frame.pack(pady=20)

        start_button = tk.Button(menu_frame, text="Start New Game", command=self.start_new_game, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        start_button.pack(pady=10)

        load_button = tk.Button(menu_frame, text="Load Game", command=self.show_load_game, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        load_button.pack(pady=10)

        settings_button = tk.Button(menu_frame, text="Settings", command=self.show_settings, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        settings_button.pack(pady=10)

        exit_button = tk.Button(menu_frame, text="Exit", command=self.quit, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        exit_button.pack(pady=10)

    def start_new_game(self):
        self.game = Game()
        self.game.message.extend(self.game.handle_command("look", self.colors))
        self.create_game_view()

    def show_load_game(self):
        self.clear_frame()
        self.game_state = "load_game"

        load_frame = tk.Frame(self.main_frame, bg=self.colors.BLACK)
        load_frame.pack(pady=20)

        save_files = self.get_save_files()

        if not save_files:
            no_saves_label = tk.Label(load_frame, text="No saved games found.", bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE)
            no_saves_label.pack(pady=10)
        else:
            for file_path, date_str in save_files:
                load_button = tk.Button(load_frame, text=date_str, command=lambda f=file_path: self.load_game_state(f), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
                load_button.pack(pady=5)

        back_button = tk.Button(load_frame, text="Back", command=self.create_main_menu, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        back_button.pack(pady=10)

    def show_settings(self):
        self.clear_frame()
        self.game_state = "settings"

        settings_frame = tk.Frame(self.main_frame, bg=self.colors.BLACK)
        settings_frame.pack(pady=20)

        dark_mode_button = tk.Button(settings_frame, text="Dark/Light Mode", command=self.toggle_dark_mode, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        dark_mode_button.pack(pady=10)

        self.text_speed_button = tk.Button(settings_frame, text=f"Text Speed: {self.text_speed}", command=self.toggle_text_speed, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        self.text_speed_button.pack(pady=10)

        github_button = tk.Button(settings_frame, text="Github", command=self.open_github, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        github_button.pack(pady=10)

        back_button = tk.Button(settings_frame, text="Back", command=self.create_main_menu, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        back_button.pack(pady=10)

    def create_game_view(self):
        self.clear_frame()
        self.game_state = "in_game"

        # Top bar
        top_bar = tk.Frame(self.main_frame, height=40, bg=self.colors.BLACK)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        self.status_label = tk.Label(top_bar, text="", bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE)
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Main content
        main_content = tk.Frame(self.main_frame, bg=self.colors.BLACK)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Image placeholder
        image_placeholder = tk.Frame(main_content, width=200, height=200, bg="black")
        image_placeholder.pack(side=tk.LEFT, padx=10)

        # Game message area
        self.message_area = scrolledtext.ScrolledText(main_content, wrap=tk.WORD, state="disabled", bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE)
        self.message_area.pack(fill=tk.BOTH, expand=True)

        # Location bar
        location_bar = tk.Frame(self.main_frame, height=40, bg=self.colors.BLACK)
        location_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.location_label = tk.Label(location_bar, text="", bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE)
        self.location_label.pack(side=tk.LEFT, padx=10)

        # Button bar
        button_bar = tk.Frame(self.main_frame, bg=self.colors.BLACK)
        button_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        self.move_button = tk.Button(button_bar, text="Move", command=self.show_move_buttons, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        self.move_button.pack(side=tk.LEFT, padx=5)

        self.interact_button = tk.Button(button_bar, text="Interact", command=self.show_interact_buttons, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        self.interact_button.pack(side=tk.LEFT, padx=5)

        self.attack_button = tk.Button(button_bar, text="Attack", command=self.show_attack_buttons, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        self.attack_button.pack(side=tk.LEFT, padx=5)

        self.escape_button = tk.Button(button_bar, text="Escape", command=self.escape_combat, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        self.escape_button.pack(side=tk.LEFT, padx=5)

        self.menu_button = tk.Button(button_bar, text="Menu", command=self.show_pause_menu, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        self.menu_button.pack(side=tk.RIGHT, padx=5)

        self.apply_theme()
        self.update_game_view()

    def update_game_view(self):
        if not self.game.player.is_alive():
            messagebox.showinfo("Game Over", "You have died.")
            self.create_main_menu()
            return

        # Update status
        status_text = f"HP: {self.game.player.health} | Hunger: {self.game.player.hunger} | Thirst: {self.game.player.thirst} | Energy: {self.game.player.energy}"
        if self.game.player.ailments:
            status_text += f" | Ailments: {', '.join(self.game.player.ailments)}"
        self.status_label.config(text=status_text)

        # Update location
        location_text = f"Location: {self.game.player.current_room.zone} ({self.game.player.x},{self.game.player.y},{self.game.player.z}) Strata: {self.game.player.current_strata.strata_id}"
        self.location_label.config(text=location_text)

        # Update message area
        self.message_area.config(state="normal")
        self.message_area.delete("1.0", tk.END)
        self.display_text_animated(self.game.message)
        self.game.message = []

        # Update escape button visibility
        if self.game.player.current_room.enemies:
            self.escape_button.pack(side=tk.LEFT, padx=5)
        else:
            self.escape_button.pack_forget()

    def display_text_animated(self, messages, index=0):
        if index < len(messages):
            text, color_name = messages[index]
            self.message_area.insert(tk.END, text + "\n", color_name)
            self.message_area.config(state="disabled")
            self.after(50 // self.text_speed, self.display_text_animated, messages, index + 1)

    def show_move_buttons(self):
        self.clear_action_buttons()
        for direction in self.game.player.current_room.exits:
            button = tk.Button(self.action_bar, text=direction, command=lambda d=direction: self.handle_command(f"move {d}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
            button.pack(side=tk.LEFT, padx=5)

    def show_interact_buttons(self):
        self.clear_action_buttons()
        interactable_items = [item for item in self.game.player.current_room.items if not isinstance(item, NPC)]
        for item in interactable_items:
            button = tk.Button(self.action_bar, text=f"get {item.name}", command=lambda i=item.name: self.handle_command(f"get {i}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
            button.pack(side=tk.LEFT, padx=5)
        for item in self.game.player.current_room.items:
            if isinstance(item, Terminal):
                button = tk.Button(self.action_bar, text=f"scan {item.name}", command=lambda i=item.name: self.handle_command(f"scan {i}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
                button.pack(side=tk.LEFT, padx=5)
        for item in self.game.player.inventory:
            if isinstance(item, CyberneticImplant):
                button = tk.Button(self.action_bar, text=f"install {item.name}", command=lambda i=item.name: self.handle_command(f"install {i}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
                button.pack(side=tk.LEFT, padx=5)
        for item in self.game.player.current_room.items:
            if isinstance(item, NPC):
                button = tk.Button(self.action_bar, text=f"talk {item.name}", command=lambda i=item.name: self.handle_command(f"talk {i}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
                button.pack(side=tk.LEFT, padx=5)

    def show_attack_buttons(self):
        self.clear_action_buttons()
        for enemy in self.game.player.current_room.enemies:
            button = tk.Button(self.action_bar, text=f"attack {enemy.name}", command=lambda e=enemy.name: self.handle_command(f"attack {e}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
            button.pack(side=tk.LEFT, padx=5)
        for obstacle in self.game.player.current_room.obstacles.values():
            button = tk.Button(self.action_bar, text=f"attack {obstacle.name}", command=lambda o=obstacle.name: self.handle_command(f"attack {o}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
            button.pack(side=tk.LEFT, padx=5)

    def escape_combat(self):
        self.handle_command("escape")

    def show_pause_menu(self):
        self.clear_frame()
        self.game_state = "pause_menu"

        pause_frame = tk.Frame(self.main_frame, bg=self.colors.BLACK)
        pause_frame.pack(pady=20)

        resume_button = tk.Button(pause_frame, text="Resume Game", command=self.create_game_view, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        resume_button.pack(pady=10)

        save_button = tk.Button(pause_frame, text="Save Game", command=self.save_game_state, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        save_button.pack(pady=10)

        load_button = tk.Button(pause_frame, text="Load Game", command=self.show_load_game, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        load_button.pack(pady=10)

        settings_button = tk.Button(pause_frame, text="Settings", command=self.show_settings, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        settings_button.pack(pady=10)

        exit_to_main_button = tk.Button(pause_frame, text="Exit to Main Menu", command=self.create_main_menu, bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
        exit_to_main_button.pack(pady=10)

    def handle_command(self, command):
        self.game.message.extend(self.game.handle_command(command, self.colors))
        if self.game.current_attack_target:
            self.show_weapon_selection()
        else:
            self.update_game_view()

    def show_weapon_selection(self):
        self.clear_action_buttons()
        for item in self.game.player.inventory:
            if isinstance(item, Item) and item.name.lower() == "gbe":
                button = tk.Button(self.action_bar, text=item.name, command=lambda w=item.name: self.handle_command(f"use_weapon {w}"), bg=self.colors.BLACK, fg=self.colors.BRIGHT_WHITE, highlightbackground=self.colors.BRIGHT_WHITE)
                button.pack(side=tk.LEFT, padx=5)

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
        messagebox.showinfo("Game Saved", "Game saved successfully!")

    def load_game_state(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        
        all_stratas = [Strata.from_json(s_data) for s_data in data["stratas"]]
        player = Player.from_json(data["player"], all_stratas)
        self.game = Game(all_stratas=all_stratas, player=player)
        self.game.message.extend(self.game.handle_command("look", self.colors))
        self.create_game_view()

    def toggle_dark_mode(self):
        current_theme = 'dark' if self.colors.theme == 'dark' else 'light'
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        self.colors.set_theme(new_theme)
        self.apply_theme()
        self.create_main_menu()

    def toggle_text_speed(self):
        current_index = self.text_speed_options.index(self.text_speed)
        next_index = (current_index + 1) % len(self.text_speed_options)
        self.text_speed = self.text_speed_options[next_index]
        self.text_speed_button.config(text=f"Text Speed: {self.text_speed}")

    def open_github(self):
        webbrowser.open("https://github.com/iBobith/blame")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def clear_action_buttons(self):
        if hasattr(self, 'action_bar'):
            for widget in self.action_bar.winfo_children():
                widget.destroy()
        else:
            self.action_bar = tk.Frame(self.main_frame, bg=self.colors.BLACK)
            self.action_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

if __name__ == "__main__":
    app = GameGUI()
    app.mainloop()