Title - Campaign

Repository
[(https://github.com/XavierpenaUTD/campaign.git)]

Description
Campaign is a 2D pixel-style exploration game built in Python using Pygame. Players explore rooms, collect items, solve puzzles, and unlock areas — combining interactive design with storytelling elements, making it relevant to media and digital arts through its focus on user engagement and visual narrative.

Features
Item Collection System
Players will be able to pick up items (like keys) that get stored in an inventory, tracked through the game state.
Locked Doors & Exploration
Some doors require keys to open, creating game flow that encourages discovery and interaction with the environment.
Puzzle Mechanic
Switch-based puzzles that unlock areas or trigger changes when solved, adding interactive challenge.
Save/Load Functionality
Players can save their progress and continue later, using Python’s pickle module to serialize game state.
Background Music
The game includes looping background music to enhance the atmosphere using pygame.mixer.

Challenges
Learning how to implement save/load systems using file serialization.
Creating and managing game states between rooms and objects.
Designing interactive puzzle mechanics that are fun and intuitive.

Outcomes
Ideal Outcome:
A fully playable short game with 3–4 rooms, collectible items, puzzles, music, save/load, and a clear progression path.

Minimal Viable Outcome:
A working player that can move between rooms, collect a key, and use it to unlock a door, with music and a save system.

Milestones
Week 1
Build base game loop with player movement and room transitions
Add item pickup and inventory logic

Week 2
Implement door/key mechanics
Add background music and simple UI

Week 3
Add puzzles and game logic for solving them
Design layout and flow of rooms

Week 4 (Final)
Add save/load system and polish interactions
Playtest and refine visuals, sounds, and UX
