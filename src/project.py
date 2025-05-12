import pygame
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Campaign: The Puzzle Quest")

player_size = 30
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5
player_inventory = []
game_started = False
victory = False
switch_activated = False
switch_animation = 0
victory_fade = 0
particles = []

puzzle_block = pygame.Rect(300, 400, 50, 50)
puzzle_target = pygame.Rect(600, 300, 50, 50)
puzzle_block_vel = [0, 0]

treasure_box_walls = [
    pygame.Rect(375, 255, 50, 20),
    pygame.Rect(375, 325, 50, 20),
    pygame.Rect(355, 275, 20, 50),
    pygame.Rect(425, 275, 20, 50),
]
treasure_box_opening = False

rooms = {
    "Start": {"neighbors": {"up": "Locked Room", "right": "Key Room", "down": "Puzzle Room"}, "walls": [], "minimap_pos": (1, 1), "color": (40, 40, 60)},
    "Key Room": {"neighbors": {"left": "Start"}, "key": "Silver Key", "key_rect": pygame.Rect(400, 300, 20, 20), "walls": [pygame.Rect(200, 200, 150, 20), pygame.Rect(500, 400, 150, 20), pygame.Rect(300, 300, 20, 150)], "minimap_pos": (2, 1), "color": (60, 40, 40)},
    "Locked Room": {"neighbors": {"down": "Start", "right": "Obstacle Room"}, "locked": True, "key_required": "Silver Key", "walls": [], "minimap_pos": (1, 0), "color": (40, 60, 40)},
    "Obstacle Room": {"neighbors": {"left": "Locked Room", "right": "Treasure Room"}, "key": "Gold Key", "key_rect": pygame.Rect(700, 300, 20, 20), "walls": [pygame.Rect(100, 100, 600, 20), pygame.Rect(100, 200, 600, 20), pygame.Rect(100, 300, 600, 20), pygame.Rect(100, 400, 600, 20), pygame.Rect(300, 100, 20, 400), pygame.Rect(500, 100, 20, 400)], "minimap_pos": (2, 0), "color": (50, 30, 80)},
    "Treasure Room": {"neighbors": {"left": "Obstacle Room", "down": "Switch Room"}, "walls": [pygame.Rect(100, 500, 600, 20), pygame.Rect(200, 200, 20, 200), pygame.Rect(600, 200, 20, 200)], "minimap_pos": (3, 0), "color": (90, 90, 20)},
    "Switch Room": {"neighbors": {"up": "Treasure Room"}, "walls": [pygame.Rect(200, 150, 50, 300), pygame.Rect(550, 150, 50, 300), pygame.Rect(350, 100, 100, 20), pygame.Rect(350, 480, 100, 20)], "switch_rect": pygame.Rect(375, 275, 50, 50), "minimap_pos": (2, 2), "color": (60, 90, 60)},
    "Puzzle Room": {"neighbors": {"up": "Start"}, "walls": [pygame.Rect(200, 200, 100, 100), pygame.Rect(500, 300, 100, 100), pygame.Rect(300, 100, 200, 20)], "puzzle_solved": False, "minimap_pos": (1, 2), "color": (90, 60, 40)}
}

current_room = "Start"
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 72)

def reset_game():
    global current_room, player_pos, player_inventory, switch_activated, victory, particles, puzzle_block, puzzle_block_vel, switch_animation, treasure_box_opening, victory_fade
    current_room = "Start"
    player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
    player_inventory = []
    switch_activated = False
    victory = False
    particles = []
    rooms["Puzzle Room"]["puzzle_solved"] = False
    rooms["Puzzle Room"]["neighbors"] = {"up": "Start"}
    puzzle_block.x, puzzle_block.y = 300, 400
    puzzle_block_vel = [0, 0]
    switch_animation = 0
    treasure_box_opening = False
    victory_fade = 0

def generate_exit_walls():
    walls = []
    neighbors = rooms[current_room].get("neighbors", {})
    if "up" not in neighbors: walls.append(pygame.Rect(0, 0, SCREEN_WIDTH, 5))
    if "down" not in neighbors: walls.append(pygame.Rect(0, SCREEN_HEIGHT - 5, SCREEN_WIDTH, 5))
    if "left" not in neighbors: walls.append(pygame.Rect(0, 0, 5, SCREEN_HEIGHT))
    if "right" not in neighbors: walls.append(pygame.Rect(SCREEN_WIDTH - 5, 0, 5, SCREEN_HEIGHT))
    return walls

def draw_room():
    screen.fill(rooms[current_room]["color"])
    for wall in rooms[current_room]["walls"] + generate_exit_walls():
        pygame.draw.rect(screen, (130, 130, 130), wall)
    if current_room == "Treasure Room":
        for wall in treasure_box_walls:
            pygame.draw.rect(screen, (200, 50, 50), wall)
        pygame.draw.rect(screen, (255, 215, 0), pygame.Rect(375, 275, 50, 50))
    if current_room == "Switch Room":
        color_value = 100 + int(switch_animation * 155)
        pygame.draw.rect(screen, (0, color_value, 0), rooms["Switch Room"]["switch_rect"])
    if current_room == "Puzzle Room":
        pygame.draw.rect(screen, (150, 150, 0), puzzle_target)
        pygame.draw.rect(screen, (100, 100, 255), puzzle_block)
        if not rooms["Puzzle Room"]["puzzle_solved"]:
            hint = font.render("Push the block onto the target!", True, (255, 255, 0))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 20))
    if "key_rect" in rooms[current_room] and rooms[current_room].get("key") not in player_inventory:
        pygame.draw.rect(screen, (255, 215, 0), rooms[current_room]["key_rect"])
    pygame.draw.rect(screen, (0, 200, 0), (*player_pos, player_size, player_size))
    for p in particles:
        color = (p["color"][0], p["color"][1], p["color"][2], p["alpha"])
        surf = pygame.Surface((5, 5), pygame.SRCALPHA)
        surf.fill(color)
        screen.blit(surf, p["pos"])
    if victory:
        fade = min(int(victory_fade * 255), 255)
        win_text = big_font.render("YOU WIN!", True, (fade, fade, 0))
        screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, 100))
        play_text = font.render("Press [R] to Play Again or [Q] to Quit", True, (fade, fade, fade))
        screen.blit(play_text, (SCREEN_WIDTH//2 - play_text.get_width()//2, 200))
    draw_minimap()

def draw_minimap():
    pygame.draw.rect(screen, (50, 50, 50), (10, SCREEN_HEIGHT - 110, 100, 100))
    for name, data in rooms.items():
        pos = data["minimap_pos"]
        color = (0, 255, 0) if name == current_room else (100, 100, 100)
        pygame.draw.rect(screen, color, (10 + pos[0] * 30, SCREEN_HEIGHT - 110 + pos[1] * 30, 25, 25))

def move_player(dx, dy):
    global puzzle_block_vel
    new_rect = pygame.Rect(player_pos[0] + dx, player_pos[1] + dy, player_size, player_size)
    for wall in rooms[current_room]["walls"] + generate_exit_walls():
        if new_rect.colliderect(wall): return
    if current_room == "Treasure Room" and not switch_activated:
        for wall in treasure_box_walls:
            if new_rect.colliderect(wall): return
    if current_room == "Puzzle Room" and new_rect.colliderect(puzzle_block):
        puzzle_block_vel[0], puzzle_block_vel[1] = dx, dy
    player_pos[0] += dx
    player_pos[1] += dy

def spawn_particles(x, y):
    for _ in range(30):
        particles.append({"pos": [x, y], "vel": [random.uniform(-3, 3), random.uniform(-3, 3)], "timer": random.randint(60, 120), "color": (255, 215, 0), "alpha": 255})

def main():
    global game_started, switch_activated, victory, switch_animation, treasure_box_opening, victory_fade, puzzle_block_vel, current_room
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if not game_started:
            screen.fill((10, 10, 30))
            title = big_font.render("Campaign: The Puzzle Quest", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            prompt = font.render("Press ENTER to Start", True, (200, 200, 200))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 300))
            pygame.display.flip()
            if keys[pygame.K_RETURN]:
                game_started = True
            continue

        if victory:
            victory_fade += 0.01
            if keys[pygame.K_r]:
                reset_game()
                continue
            if keys[pygame.K_q]:
                running = False

        if keys[pygame.K_w]: move_player(0, -player_speed)
        if keys[pygame.K_s]: move_player(0, player_speed)
        if keys[pygame.K_a]: move_player(-player_speed, 0)
        if keys[pygame.K_d]: move_player(player_speed, 0)

        if player_pos[0] < 0: current_room, player_pos[0] = rooms[current_room]["neighbors"].get("left", current_room), SCREEN_WIDTH - player_size - 5
        if player_pos[0] + player_size > SCREEN_WIDTH: current_room, player_pos[0] = rooms[current_room]["neighbors"].get("right", current_room), 5
        if player_pos[1] < 0: current_room, player_pos[1] = rooms[current_room]["neighbors"].get("up", current_room), SCREEN_HEIGHT - player_size - 5
        if player_pos[1] + player_size > SCREEN_HEIGHT: current_room, player_pos[1] = rooms[current_room]["neighbors"].get("down", current_room), 5

        # Pickup keys
        if "key_rect" in rooms[current_room] and rooms[current_room].get("key") not in player_inventory:
            if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(rooms[current_room]["key_rect"]):
                player_inventory.append(rooms[current_room]["key"])
                del rooms[current_room]["key_rect"]

        if keys[pygame.K_e]:
            if current_room == "Switch Room" and not switch_activated and rooms["Puzzle Room"]["puzzle_solved"]:
                switch_activated = True
                treasure_box_opening = True

        if puzzle_block_vel != [0, 0]:
            puzzle_block.x += puzzle_block_vel[0]
            puzzle_block.y += puzzle_block_vel[1]
            puzzle_block_vel = [0, 0]

        if current_room == "Puzzle Room" and not rooms["Puzzle Room"]["puzzle_solved"]:
            if puzzle_block.colliderect(puzzle_target):
                rooms["Puzzle Room"]["puzzle_solved"] = True
                rooms["Puzzle Room"]["neighbors"]["right"] = "Switch Room"

        if switch_activated and switch_animation < 1:
            switch_animation += 0.05

        if treasure_box_opening:
            done = True
            for wall in treasure_box_walls:
                if wall.x < 300:
                    wall.x -= 2
                    done = False
                elif wall.x > 500:
                    wall.x += 2
                    done = False
                if wall.y < 200:
                    wall.y -= 2
                    done = False
                elif wall.y > 400:
                    wall.y += 2
                    done = False
            if done:
                treasure_box_opening = False
                treasure_box_walls.clear()  

        if current_room == "Treasure Room" and switch_activated:
            if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(pygame.Rect(375, 275, 50, 50)):
                if not victory:
                    victory = True
                    spawn_particles(400, 300)

        for p in particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["timer"] -= 1
            p["alpha"] = max(0, p["alpha"] - 2)
        particles[:] = [p for p in particles if p["timer"] > 0 or p["alpha"] > 0]

        draw_room()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()