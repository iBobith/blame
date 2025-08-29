# blame

## Core concept

Blame is a non-profit fan game created based off of the 1998 manga BLAME! by Tsutomu Nihei. Considering the vast and tretchorous world presented in the manga, I wanted to imitate the loneliness and danger as accurately as I could manage, given my capabilities. Hence I decided the least recourse-intensive way to achieve this would be via a terminal-based RPG/roguelike. My goal is to give the sense of endless traversal and perilous danger throughut the course of the game. I do not intend the player to be the MC, Kirii, but as someone else who is an inhabitant of the City. The goal is to have the player start somewhere within a lower strata, scavenging and exploring the collapsing city and its remaining megastructures. You may find people along the way, or dangerous entities. Regardless, the goal will be to escape the city, reach the netsphere and escape the dangers of whats left outside the netsphere. For this game I've taken inspiration from Roadwarden, Caves of Qud and, of course, BLAME!.

## Roadmap:

### Phase 1: Core Engine (Complete)

- [x] Basic project structure (game loop, player input parsing).
- [x] Foundational procedural generation for simple rooms and corridors.
- [x] Player character module with movement capabilities.
- [x] A command system for player actions (e.g., `move`, `look`).

### Architecture Improvements (Complete)

- [x] Externalized text content into a `content.json` file for easier management.
- [x] Implemented a persistent UI that clears the screen and displays stats/commands.

### Phase 2: Gameplay Systems (Complete)

- [x] Character stats system (e.g., Health, Energy).
- [x] Item and inventory management.
- [x] Basic interaction system (e.g., scanning terminals, opening doors).
- [x] Simple enemy encounters and a rudimentary turn-based combat model.

### Phase 3: World & Narrative (Complete)

- [x] Enhanced procedural generation: large-scale structures, unique landmarks, and varied "biomes" within The City.
- [x] Fragmented narrative system: discoverable logs, item descriptions, and environmental storytelling.
- [x] Introduction of simple NPCs or environmental hazards.
- [x] Atmospheric text descriptions to build the world.

### Phase 4: Polish & Expansion (Complete)

- [x] Advanced enemy AI and more complex combat mechanics.
- [x] Cybernetic Implants and Installation System.
- [x] Sound and visual cues using ASCII/terminal colors.
- [x] Dead ends and Strata generation with varying dimensions.
- [x] Refinement of the generation algorithm for a more cohesive and endless world.
