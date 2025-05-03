import pygame
import pickle
import os

pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventure Game")

# Player settings
player_size = 30
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5
player_inventory = []

# Room settings (with walls)
rooms = {
    "Start": {
        "neighbors": {"up": "Locked Room", "right": "Key Room"},
        "locked": False,
        "walls": [pygame.Rect(100, 100, 600, 20), pygame.Rect(100, 480, 600, 20)],
        "minimap_pos": (1, 1)
    },
    "Key Room": {
        "neighbors": {"left": "Start"},
        "locked": False,
        "key": "Silver Key",
        "walls": [pygame.Rect(200, 200, 400, 20), pygame.Rect(200, 380, 400, 20)],
        "minimap_pos": (2, 1)
    },
    "Locked Room": {
        "neighbors": {"down": "Start"},
        "locked": True,
        "key_required": "Silver Key",
        "walls": [pygame.Rect(150, 150, 500, 20), pygame.Rect(150, 430, 500, 20)],
        "minimap_pos": (1, 0)
    },
}

current_room = "Start"

SAVE_FILE = "savegame.pkl"
font = pygame.font.SysFont(None, 36)

def save_game():
    with open(SAVE_FILE, "wb") as f:
        pickle.dump((current_room, player_inventory), f)
    print("Game Saved.")

def load_game():
    global current_room, player_inventory
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as f:
            current_room, player_inventory = pickle.load(f)
        print("Game Loaded.")
    else:
        print("No save file found.")

def draw_room():
    screen.fill((30, 30, 30))

    # Draw walls
    for wall in rooms[current_room]["walls"]:
        pygame.draw.rect(screen, (100, 100, 100), wall)

    # Draw player
    pygame.draw.rect(screen, (0, 200, 0), (*player_pos, player_size, player_size))

    # Room name
    text = font.render(f"Room: {current_room}", True, (200, 200, 200))
    screen.blit(text, (20, 20))

    # Neighbors
    neighbors = rooms[current_room].get("neighbors", {})
    neighbor_text = font.render(f"Neighbors: {list(neighbors.keys())}", True, (150, 150, 150))
    screen.blit(neighbor_text, (20, 60))

    # Inventory
    inv_text = font.render(f"Inventory: {player_inventory}", True, (100, 200, 100))
    screen.blit(inv_text, (20, 100))

    # Key in room
    key = rooms[current_room].get("key")
    if key and key not in player_inventory:
        key_text = font.render(f"Press [E] to collect {key}", True, (200, 200, 0))
        screen.blit(key_text, (20, 140))

    # Locked room message
    if rooms[current_room].get("locked"):
        lock_text = font.render(f"This room is locked!", True, (200, 50, 50))
        screen.blit(lock_text, (20, 180))

    draw_minimap()

def draw_minimap():
    minimap_size = 100
    room_size = 30
    pygame.draw.rect(screen, (50, 50, 50), (10, SCREEN_HEIGHT - minimap_size - 10, minimap_size, minimap_size))

    for room_name, room_data in rooms.items():
        pos = room_data["minimap_pos"]
        color = (100, 100, 100)
        if room_name == current_room:
            color = (0, 255, 0)

        pygame.draw.rect(screen, color, (10 + pos[0] * room_size, SCREEN_HEIGHT - minimap_size - 10 + pos[1] * room_size, room_size - 5, room_size - 5))

def try_move_room(direction):
    global current_room, player_pos
    neighbors = rooms[current_room].get("neighbors", {})
    if direction in neighbors:
        next_room = neighbors[direction]
        if rooms[next_room].get("locked"):
            required_key = rooms[next_room].get("key_required")
            if required_key in player_inventory:
                rooms[next_room]["locked"] = False
                current_room = next_room
                reset_player_pos()
            else:
                print(f"{next_room} is locked. Requires {required_key}.")
        else:
            current_room = next_room
            reset_player_pos()

def reset_player_pos():
    player_pos[0] = SCREEN_WIDTH // 2
    player_pos[1] = SCREEN_HEIGHT // 2

def move_player(dx, dy):
    new_rect = pygame.Rect(player_pos[0] + dx, player_pos[1] + dy, player_size, player_size)

    for wall in rooms[current_room]["walls"]:
        if new_rect.colliderect(wall):
            return  # Collision, don't move

    player_pos[0] += dx
    player_pos[1] += dy

def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game()
                if event.key == pygame.K_l:
                    load_game()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            move_player(0, -player_speed)
        if keys[pygame.K_s]:
            move_player(0, player_speed)
        if keys[pygame.K_a]:
            move_player(-player_speed, 0)
        if keys[pygame.K_d]:
            move_player(player_speed, 0)

        # Move between rooms when player hits screen edge
        if player_pos[0] < 0:
            try_move_room("left")
        if player_pos[0] + player_size > SCREEN_WIDTH:
            try_move_room("right")
        if player_pos[1] < 0:
            try_move_room("up")
        if player_pos[1] + player_size > SCREEN_HEIGHT:
            try_move_room("down")

        # Collect key
        if keys[pygame.K_e]:
            key = rooms[current_room].get("key")
            if key and key not in player_inventory:
                player_inventory.append(key)
                print(f"Collected {key}!")

        draw_room()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()