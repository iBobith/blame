# blame

## V 0.4.7

## Core concept

Blame is a non-profit fan game created based off of the 1998 manga BLAME! by Tsutomu Nihei. Considering the vast and tretchorous world presented in the manga, I wanted to imitate the loneliness and danger as accurately as I could manage, given my capabilities. Hence I decided the least recourse-intensive way to achieve this would be via a terminal-based RPG/roguelike. My goal is to give the sense of endless traversal and perilous danger throughut the course of the game. I do not intend the player to be the MC, Kirii, but as someone else who is an inhabitant of the City. The goal is to have the player start somewhere within a lower strata, scavenging and exploring the collapsing city and its remaining megastructures. You may find people along the way, or dangerous entities. Regardless, the goal will be to escape the city, reach the netsphere and escape the dangers of whats left outside the netsphere. For this game I've taken inspiration from Roadwarden, Caves of Qud and, of course, BLAME!.

## Roadmap:

### Phase 1: Core Engine (Complete)

### Phase 2: Gameplay Systems (Complete)

### Phase 3: World & Narrative (Complete)

### Phase 4: Polish & Expansion for Alpha (Complete)

### Phase 5: Epipheny

- [x] Rework the game to run as a GUI orientated game
  - [x] Buttons for movement and selecting interactable objects.
  - [x] Style
    - [x] Main menu
      - [x] Start new game (creates save file)
      - [x] Load game (checks for save files to select from)
      - [~] Settings
        - [~] Dark/light mode (inverts the black and white textures)
        - [ ] Text speed
        - [ ] Link to github
      - [x] Exit game
    - [x] Game UI
      - [x] Has a bar at the top of the screen always displaying users HP, Hunger, Thirst, Energy, Physical state (ailments)
      - [~] Terminal imitator for text regarding actions
        - [x] Continuously displays whats within the room
        - [x] When interacting, updates text, not changing room text, just expressing what the user is doing/cant do
      - [x] To the left of the terminal indicator, space to place images to help illustrate user's location
      - [x] Button at the bottom of the screen
      - [x] Move button
        - [x] Provides a choice between cardinal directions, as well as an optino to go back
      - [x] Interact button (displays interaction options as a replaced menu)
        - [x] Get (Used to pick up items)
        - [x] Use (Used to interact with doors/keypads/terminals)
        - [~] Implant (Used to install implants that are within the user's inventory)
        - [~] Talk (Used for entering dialogue with NPCs)
      - [x] Attack button
        - [x] Display all attackable entities (enemies, damaged panels, doors, obstacles)
          - [ ] After selecting a target, promts the user what they want to use to attack
        - [ ] Escape button (Used to try and escape from combat interaction)
      - [ ]
- [ ] Apply new art style direction (Importing images, locally, that have been generated into ASCII styling)
- [ ] Enhance procedural mapping
  - [ ] Player doesnt spawn at 0,0,0. Its a random place amidst the megastructure. Exits are located at a random higher y level, x and z coords are random too, but logical within the procedural mapping of the strata.
- [ ] Rework movement/traversal
  - [ ] Add intersections with differing paths, sometimes obstacles, so player doesnt always encounter a room
  - [ ] Traveling now displays how many hours you had travelled for before encountering the next room/intersection
  - [ ]
- [ ] Add more weapons, enemies, NPCs
  - [ ] Enhance NPC dialogue
  - [ ] Enhance terminals (lore, functionality, etc.)
- [ ] Enhance cybernetic enhancements (CEs)
