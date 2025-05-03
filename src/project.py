import pygame
import pickle
import os

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventure Game")

player_size = 30
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5
player_inventory = []

game_started = False
menu_selection = 0
menu_options = ["New Game", "Load Game", "Quit"]
pickup_message = ""
pickup_timer = 0

last_direction = None

rooms = {
    "Start": {
        "neighbors": {"up": "Locked Room", "right": "Key Room", "down": "Puzzle Room"},
        "locked": False,
        "walls": [pygame.Rect(100, 100, 600, 20), pygame.Rect(100, 480, 600, 20)],
        "minimap_pos": (1, 1),
        "color": (40, 40, 60)
    },
    "Key Room": {
        "neighbors": {"left": "Start"},
        "locked": False,
        "key": "Silver Key",
        "key_rect": pygame.Rect(400, 300, 20, 20),
        "walls": [pygame.Rect(200, 200, 400, 20), pygame.Rect(200, 380, 400, 20)],
        "minimap_pos": (2, 1),
        "color": (60, 40, 40)
    },
    "Locked Room": {
        "neighbors": {"down": "Start", "right": "Obstacle Room"},
        "locked": True,
        "key_required": "Silver Key",
        "walls": [pygame.Rect(150, 150, 500, 20), pygame.Rect(150, 430, 500, 20)],
        "minimap_pos": (1, 0),
        "color": (40, 60, 40)
    },
    "Obstacle Room": {
        "neighbors": {"left": "Locked Room", "right": "Treasure Room"},
        "locked": False,
        "key": "Gold Key",
        "key_rect": pygame.Rect(700, 300, 20, 20),
        "walls": [
            pygame.Rect(200, 100, 20, 400),
            pygame.Rect(400, 0, 20, 300),
            pygame.Rect(600, 200, 20, 400),
        ],
        "minimap_pos": (2, 0),
        "color": (50, 30, 80)
    },
    "Treasure Room": {
        "neighbors": {"left": "Obstacle Room"},
        "locked": False,
        "walls": [],
        "minimap_pos": (3, 0),
        "color": (90, 90, 20)
    },
    "Switch Room": {
        "neighbors": {"up": "Treasure Room", "left": "Puzzle Room"},
        "locked": False,
        "walls": [],
        "switch_puzzle": True,
        "door_locked": True,
        "minimap_pos": (2, 2),
        "color": (60, 90, 60),
        "switch_area": pygame.Rect(350, 250, 100, 100)
    },
    "Puzzle Room": {
        "neighbors": {"up": "Start", "right": "Switch Room"},
        "locked": False,
        "walls": [],
        "minimap_pos": (1, 2),
        "color": (90, 60, 40)
    }
}

current_room = "Start"
SAVE_FILE = "savegame.pkl"

font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 72)

def save_game():
    with open(SAVE_FILE, "wb") as f:
        pickle.dump((current_room, player_inventory), f)

def load_game():
    global current_room, player_inventory
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as f:
            current_room, player_inventory = pickle.load(f)

def draw_menu():
    screen.fill((10, 10, 30))
    title = big_font.render("Adventure Game", True, (200, 200, 250))
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

    for i, option in enumerate(menu_options):
        color = (180, 180, 180) if i != menu_selection else (255, 255, 100)
        txt = font.render(option, True, color)
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 250 + i * 40))

    pygame.display.flip()

def draw_room():
    screen.fill(rooms[current_room]["color"])

    for wall in rooms[current_room]["walls"]:
        pygame.draw.rect(screen, (130, 130, 130), wall)

    if rooms[current_room].get("switch_puzzle") and rooms[current_room]["door_locked"]:
        pygame.draw.rect(screen, (200, 50, 50), pygame.Rect(0, 0, 800, 20))

    if "key_rect" in rooms[current_room] and rooms[current_room].get("key") not in player_inventory:
        pygame.draw.rect(screen, (255, 215, 0), rooms[current_room]["key_rect"])

    pygame.draw.rect(screen, (0, 200, 0), (*player_pos, player_size, player_size))

    screen.blit(font.render(f"Room: {current_room}", True, (220, 220, 220)), (20, 10))
    neighbors = rooms[current_room].get("neighbors", {})
    screen.blit(font.render(f"Neighbors: {list(neighbors.keys())}", True, (180, 180, 180)), (20, 40))
    screen.blit(font.render(f"Inventory: {player_inventory}", True, (140, 220, 140)), (20, 70))

    if pickup_message:
        msg = font.render(pickup_message, True, (255, 255, 0))
        screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2))

    draw_minimap()

def draw_minimap():
    pygame.draw.rect(screen, (50, 50, 50), (10, SCREEN_HEIGHT - 110, 100, 100))

    for name, data in rooms.items():
        pos = data["minimap_pos"]
        color = (0, 255, 0) if name == current_room else (100, 100, 100)
        pygame.draw.rect(screen, color, (10 + pos[0] * 30, SCREEN_HEIGHT - 110 + pos[1] * 30, 25, 25))

def try_move_room(direction):
    global current_room, player_pos
    neighbors = rooms[current_room].get("neighbors", {})
    if direction in neighbors:
        next_room = neighbors[direction]
        if rooms[next_room].get("locked"):
            if rooms[next_room]["key_required"] in player_inventory:
                rooms[next_room]["locked"] = False
            else:
                return
        if current_room == "Switch Room" and direction == "up" and rooms[current_room]["door_locked"]:
            return
        current_room = next_room
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
    player_pos[0] += dx
    player_pos[1] += dy

def main():
    global game_started, menu_selection, pickup_message, pickup_timer, last_direction
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)

        if pickup_timer > 0:
            pickup_timer -= 1
        else:
            pickup_message = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_started and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: menu_selection = (menu_selection - 1) % len(menu_options)
                if event.key == pygame.K_DOWN: menu_selection = (menu_selection + 1) % len(menu_options)
                if event.key == pygame.K_RETURN:
                    if menu_selection == 0: game_started = True
                    elif menu_selection == 1: load_game(); game_started = True
                    elif menu_selection == 2: running = False

        if not game_started:
            draw_menu()
            continue

        keys = pygame.key.get_pressed()
        direction = None
        if keys[pygame.K_w]: move_player(0, -player_speed); direction = "up"
        if keys[pygame.K_s]: move_player(0, player_speed); direction = "down"
        if keys[pygame.K_a]: move_player(-player_speed, 0); direction = "left"
        if keys[pygame.K_d]: move_player(player_speed, 0); direction = "right"

        if player_pos[0] < 0: last_direction = "left"; try_move_room("left")
        if player_pos[0] + player_size > SCREEN_WIDTH: last_direction = "right"; try_move_room("right")
        if player_pos[1] < 0: last_direction = "up"; try_move_room("up")
        if player_pos[1] + player_size > SCREEN_HEIGHT: last_direction = "down"; try_move_room("down")

        if "key_rect" in rooms[current_room] and rooms[current_room].get("key") not in player_inventory:
            if pygame.Rect(player_pos[0], player_pos[1], player_size, player_size).colliderect(rooms[current_room]["key_rect"]):
                player_inventory.append(rooms[current_room]["key"])
                pickup_message = f"Picked up {rooms[current_room]['key']}!"
                pickup_timer = 120

        if rooms[current_room].get("switch_puzzle") and rooms[current_room]["door_locked"]:
            if rooms[current_room]["switch_area"].colliderect(pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
                rooms[current_room]["door_locked"] = False

        draw_room()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()