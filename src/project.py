import pygame
import os
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventure Game")

player_size = 30
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5
player_inventory = []

game_started = False
victory = False
switch_activated = False
particles = []

treasure_box_walls = [
    pygame.Rect(375, 255, 50, 20),
    pygame.Rect(375, 325, 50, 20),
    pygame.Rect(355, 275, 20, 50),
    pygame.Rect(425, 275, 20, 50),
]

rooms = {
    "Start": {
        "neighbors": {"up": "Locked Room", "right": "Key Room", "down": "Puzzle Room"},
        "walls": [],
        "minimap_pos": (1, 1),
        "color": (40, 40, 60)
    },
    "Key Room": {
        "neighbors": {"left": "Start"},
        "key": "Silver Key",
        "key_rect": pygame.Rect(400, 300, 20, 20),
        "walls": [pygame.Rect(300, 200, 200, 20), pygame.Rect(250, 400, 300, 20)],
        "minimap_pos": (2, 1),
        "color": (60, 40, 40)
    },
    "Locked Room": {
        "neighbors": {"down": "Start", "right": "Obstacle Room"},
        "locked": True,
        "key_required": "Silver Key",
        "walls": [],
        "minimap_pos": (1, 0),
        "color": (40, 60, 40)
    },
    "Obstacle Room": {
        "neighbors": {"left": "Locked Room", "right": "Treasure Room"},
        "key": "Gold Key",
        "key_rect": pygame.Rect(700, 300, 20, 20),
        "walls": [
            pygame.Rect(100, 100, 600, 20),
            pygame.Rect(100, 200, 600, 20),
            pygame.Rect(100, 300, 600, 20),
            pygame.Rect(100, 400, 600, 20),
        ],
        "minimap_pos": (2, 0),
        "color": (50, 30, 80)
    },
    "Treasure Room": {
        "neighbors": {"left": "Obstacle Room", "down": "Switch Room"},
        "walls": [pygame.Rect(100, 500, 600, 20)],
        "minimap_pos": (3, 0),
        "color": (90, 90, 20)
    },
    "Switch Room": {
        "neighbors": {"up": "Treasure Room"},
        "walls": [pygame.Rect(200, 150, 50, 300), pygame.Rect(550, 150, 50, 300)],
        "switch_rect": pygame.Rect(350, 250, 50, 50),
        "minimap_pos": (2, 2),
        "color": (60, 90, 60)
    },
    "Puzzle Room": {
        "neighbors": {"up": "Start"},
        "walls": [pygame.Rect(200, 200, 100, 100), pygame.Rect(500, 300, 100, 100)],
        "puzzle_unsolved": True,
        "minimap_pos": (1, 2),
        "color": (90, 60, 40)
    }
}

current_room = "Start"
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 72)

def reset_game():
    global current_room, player_pos, player_inventory, switch_activated, victory, particles
    current_room = "Start"
    player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
    player_inventory = []
    switch_activated = False
    victory = False
    particles = []
    rooms["Puzzle Room"]["puzzle_unsolved"] = True
    rooms["Puzzle Room"]["neighbors"] = {"up": "Start"}

def draw_room():
    screen.fill(rooms[current_room]["color"])

    neighbors = rooms[current_room].get("neighbors", {})
    if "up" not in neighbors:
        pygame.draw.rect(screen, (100, 100, 100), (0, 0, SCREEN_WIDTH, 5))
    if "down" not in neighbors:
        pygame.draw.rect(screen, (100, 100, 100), (0, SCREEN_HEIGHT - 5, SCREEN_WIDTH, 5))
    if "left" not in neighbors:
        pygame.draw.rect(screen, (100, 100, 100), (0, 0, 5, SCREEN_HEIGHT))
    if "right" not in neighbors:
        pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH - 5, 0, 5, SCREEN_HEIGHT))

    for wall in rooms[current_room]["walls"]:
        pygame.draw.rect(screen, (130, 130, 130), wall)

    if current_room == "Treasure Room":
        if not switch_activated:
            for wall in treasure_box_walls:
                pygame.draw.rect(screen, (200, 50, 50), wall)
        pygame.draw.rect(screen, (255, 215, 0), pygame.Rect(375, 275, 50, 50))

    if current_room == "Switch Room":
        color = (0, 200, 0) if switch_activated else (200, 0, 0)
        pygame.draw.rect(screen, color, rooms["Switch Room"]["switch_rect"])

    if current_room == "Puzzle Room" and rooms["Puzzle Room"]["puzzle_unsolved"]:
        hint = font.render("Press E to solve the puzzle and open Switch Room.", True, (255, 255, 0))
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 20))

    if "key_rect" in rooms[current_room] and rooms[current_room].get("key") not in player_inventory:
        pygame.draw.rect(screen, (255, 215, 0), rooms[current_room]["key_rect"])

    pygame.draw.rect(screen, (0, 200, 0), (*player_pos, player_size, player_size))

    for p in particles:
        pygame.draw.rect(screen, p["color"], pygame.Rect(p["pos"][0], p["pos"][1], 5, 5))

    if victory:
        win_text = big_font.render("YOU WIN!", True, (255, 255, 0))
        screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, 100))

        play_text = font.render("Press [R] to Play Again or [Q] to Quit", True, (255, 255, 255))
        screen.blit(play_text, (SCREEN_WIDTH//2 - play_text.get_width()//2, 200))

    draw_minimap()

def draw_minimap():
    pygame.draw.rect(screen, (50, 50, 50), (10, SCREEN_HEIGHT - 110, 100, 100))
    for name, data in rooms.items():
        pos = data["minimap_pos"]
        color = (0, 255, 0) if name == current_room else (100, 100, 100)
        pygame.draw.rect(screen, color, (10 + pos[0] * 30, SCREEN_HEIGHT - 110 + pos[1] * 30, 25, 25))

def try_move_room(direction):
    global current_room
    neighbors = rooms[current_room].get("neighbors", {})
    if direction in neighbors:
        current_room = neighbors[direction]
        reset_player_pos(direction)

def reset_player_pos(direction):
    if direction == "left": player_pos[0] = SCREEN_WIDTH - player_size - 5
    elif direction == "right": player_pos[0] = 5
    elif direction == "up": player_pos[1] = SCREEN_HEIGHT - player_size - 5
    elif direction == "down": player_pos[1] = 5

def move_player(dx, dy):
    new_rect = pygame.Rect(player_pos[0] + dx, player_pos[1] + dy, player_size, player_size)

    for wall in rooms[current_room]["walls"]:
        if new_rect.colliderect(wall):
            return

    if current_room == "Treasure Room" and not switch_activated:
        for wall in treasure_box_walls:
            if new_rect.colliderect(wall):
                return

    player_pos[0] += dx
    player_pos[1] += dy

def spawn_particles(x, y):
    for _ in range(30):
        particles.append({
            "pos": [x, y],
            "vel": [random.uniform(-3, 3), random.uniform(-3, 3)],
            "timer": random.randint(20, 40),
            "color": (255, 215, 0)
        })

def main():
    global game_started, switch_activated, victory
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
            title = big_font.render("Adventure Game", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            prompt = font.render("Press ENTER to Start", True, (200, 200, 200))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 300))
            pygame.display.flip()

            if keys[pygame.K_RETURN]:
                game_started = True
            continue

        if victory:
            if keys[pygame.K_r]:
                reset_game()
                continue
            if keys[pygame.K_q]:
                running = False

        if keys[pygame.K_w]: move_player(0, -player_speed)
        if keys[pygame.K_s]: move_player(0, player_speed)
        if keys[pygame.K_a]: move_player(-player_speed, 0)
        if keys[pygame.K_d]: move_player(player_speed, 0)

        if player_pos[0] < 0: try_move_room("left")
        if player_pos[0] + player_size > SCREEN_WIDTH: try_move_room("right")
        if player_pos[1] < 0: try_move_room("up")
        if player_pos[1] + player_size > SCREEN_HEIGHT: try_move_room("down")

        if keys[pygame.K_e]:
            if current_room == "Puzzle Room" and rooms["Puzzle Room"]["puzzle_unsolved"]:
                rooms["Puzzle Room"]["puzzle_unsolved"] = False
                rooms["Puzzle Room"]["neighbors"]["right"] = "Switch Room"
            if current_room == "Switch Room" and not switch_activated:
                switch_activated = True

        if "key_rect" in rooms[current_room] and rooms[current_room].get("key") not in player_inventory:
            if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(rooms[current_room]["key_rect"]):
                player_inventory.append(rooms[current_room]["key"])

        if current_room == "Treasure Room" and switch_activated:
            if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(pygame.Rect(375, 275, 50, 50)):
                if not victory:
                    victory = True
                    spawn_particles(400, 300)

        for p in particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["timer"] -= 1
        particles[:] = [p for p in particles if p["timer"] > 0]

        draw_room()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()