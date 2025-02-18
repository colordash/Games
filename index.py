import pygame
import math
from collections import deque
import random
import json
import os


# Initialisierung
pygame.init()
WIDTH, HEIGHT = 800, 500
GRID_SIZE = 10
CELL_SIZE = HEIGHT // GRID_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#----------------kONSTANTEN--------------------------------------------
VALUE_PER_ENEMY = 1
SAVE_FILE = "game_data.json"

# Initialisierung der Timer
cycle_time = 0
spawn_timer = 0
time_since_last_update = 0
spawn_interval = 1000  # Initialer Spawn-Intervall in ms

# Spielobjekte
enemies = []
towers = []
spawn_timer = 0
time_since_last_update = 0 
lives = 10
gold = 200
spawn_interval = 100
enemy_count = 0 
selected_tower_type = None
running = True

# Button Parameter
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 80
BUTTON_SPACING = 20
START_Y = 200

# Farben
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BLACK = (0,0,0)
PATH_COLOR = (150, 150, 150)

# Pfaddefinition
PATH = {"easy":
    [(0, 6), (1, 6), (2, 6), (3, 6), (4, 6),
    (5, 6), (5, 7), (5, 8), (4, 8), (3, 8),
    (2, 8), (2, 7), (2, 6), (2, 5), (2, 4), 
    (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
    (7, 3), (8, 3), (8, 4), (8, 5), (8, 6),
    (8, 7), (8, 8), (8, 9)], 
    "medium": 
    [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
    (4, 5), (4, 6), (5, 6), (6, 6), (7, 6),
    (7, 5), (7, 4), (8, 4), (9, 4)]
}

# Tower-Typen mit Preisen und Eigenschaften
TOWER_TYPES = [
    {"color": GREEN, "price": 100, "range": 3, "damage": 10, "cooldown": 10},
    {"color": BLUE, "price": 150, "range": 4, "damage": 15, "cooldown": 8},
    {"color": PURPLE, "price": 200, "range": 5, "damage": 20, "cooldown": 6},
]

# ----------------Klassen----------------------------------------------------
class Enemy:
    def __init__(self):
        self.path = deque(PATH["easy"])
        self.pos = pygame.Vector2(self.path[0][0] * CELL_SIZE + CELL_SIZE // 2, 
                                  self.path[0][1] * CELL_SIZE + CELL_SIZE // 2)
        self.target_index = 1
        self.speed = 1
        self.health = 10
        self.radius = 10

    def update(self):
        if self.target_index < len(self.path):
            target = self.path[self.target_index]
            target_pos = pygame.Vector2(target[0] * CELL_SIZE + CELL_SIZE//2,
                                        target[1] * CELL_SIZE + CELL_SIZE//2)
            direction = target_pos - self.pos
            if direction.length() > self.speed:
                direction.scale_to_length(self.speed)
            self.pos += direction

            if self.pos.distance_to(target_pos) < 1:
                self.target_index += 1

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.pos.x), int(self.pos.y)), self.radius)

class Tower:
    def __init__(self, x, y, color, range, damage, cooldown):
        self.x = x
        self.y = y
        self.color = color
        self.range = range * CELL_SIZE
        self.damage = damage
        self.cooldown = cooldown
        self.last_shot = 0
        self.bullets = []

    def in_range(self, enemy):
        distance = math.hypot(self.x - enemy.pos.x, self.y - enemy.pos.y)
        return distance <= self.range

    def shoot(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.cooldown:
            targets = [enemy for enemy in enemies if self.in_range(enemy)]
            if targets:
                target = random.choice(targets)
                self.bullets.append(Bullet(self.x, self.y, target, self.damage))
                self.last_shot = now

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x - CELL_SIZE//2, self.y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE))

class Bullet:
    def __init__(self, x, y, target, damage):
        self.pos = pygame.Vector2(x, y)
        self.target = target
        self.speed = 5
        self.damage = damage

    def update(self):
        if self.target.health > 0:
            direction = self.target.pos - self.pos
            if direction.length() > self.speed:
                direction.scale_to_length(self.speed)
            self.pos += direction
            return self.pos.distance_to(self.target.pos) < 5
        return True

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.pos.x), int(self.pos.y)), 3)


#----------------------def Funktionen-------------------------------------
# Checkt ob das Intro angezeigt werden soll
def check_first_run():
    if os.path.exists(SAVE_FILE):
        return False  # Datei existiert, also nicht erster Start
    else:
        with open(SAVE_FILE, "w") as f:
            json.dump({"first_run": False}, f)
        return True  # Erstmaliger Start

# Intro-Bildschirm
def show_intro():
    intro = True
    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 36)
    # Position und Größe des Start-Buttons oben rechts (mit 20px Rand)
    start_button_rect = pygame.Rect(WIDTH - 220, 20, 200, 60)

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    intro = False

        screen.fill(WHITE)
        # Titel anzeigen (mittig oben)
        title_surface = font_title.render("Tower Defense", True, BLACK)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 80))
        screen.blit(title_surface, title_rect)

        # Anleitungstext
        instructions = [
            "Willkommen bei Tower Defense!",
            "Platziere Türme, um die angreifenden Gegner abzuwehren.",
            "Wähle einen Turm aus der rechten Seitenleiste aus",
            "und klicke dann auf das Spielfeld, um ihn zu platzieren.",
            "Hinweis: Du kannst keine Türme auf dem Pfad platzieren.",
            "Jeder Turm hat unterschiedliche Eigenschaften:",
            "Reichweite, Schaden und Abklingzeit.",
            "Verhindere, dass die Gegner dein Ziel erreichen.",
            "Du hast 10 Leben. Viel Erfolg!"
        ]
        for i, line in enumerate(instructions):
            text_surface = font_text.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, 150 + i * 40))
            screen.blit(text_surface, text_rect)

        # Start-Button oben rechts zeichnen
        pygame.draw.rect(screen, GREEN, start_button_rect)
        button_text = font_text.render("Spiel Starten", True, WHITE)
        button_rect = button_text.get_rect(center=start_button_rect.center)
        screen.blit(button_text, button_rect)

        pygame.display.flip()
        clock.tick(60)


# Zeige das Intro, bevor das Spiel beginnt
if check_first_run():
    show_intro()
# -----------------------main loop---------------------------------
while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            # Klick auf Tower-Buttons
            if x >= 500:
                for i, tower_type in enumerate(TOWER_TYPES):
                    button_x = 500 + (300 - BUTTON_WIDTH) // 2
                    button_y = START_Y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
                    rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if rect.collidepoint(x, y):
                        selected_tower_type = i
                        break
            # Klick auf Grid
            else:
                grid_x = x // CELL_SIZE
                grid_y = y // CELL_SIZE
                if selected_tower_type is not None:
                    if (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and
                        (grid_x, grid_y) not in PATH["easy"] and
                        not any(t.x == grid_x * CELL_SIZE + CELL_SIZE//2 and
                                t.y == grid_y * CELL_SIZE + CELL_SIZE//2 for t in towers)):
                        cost = TOWER_TYPES[selected_tower_type]['price']
                        if gold >= cost:
                            tower_type = TOWER_TYPES[selected_tower_type]
                            towers.append(Tower(
                                grid_x * CELL_SIZE + CELL_SIZE//2,
                                grid_y * CELL_SIZE + CELL_SIZE//2,
                                tower_type['color'],
                                tower_type['range'],
                                tower_type['damage'],
                                tower_type['cooldown']
                            ))
                            gold -= cost
                            selected_tower_type = None


    
    # Zyklus-Time tracking
    dt = clock.get_rawtime()
    cycle_time += dt
    cycle_time %= 23000  # 23 Sekunden Zyklus (20000 + 3000)
    print(cycle_time)
    
    # Spawn-Logik
    if cycle_time < 20000:  # Spawning-Phase (20 Sekunden)
        # Timer aktualisieren
        spawn_timer += dt
        time_since_last_update += dt
        
        # Gegner spawnen
        if spawn_timer > spawn_interval:
            enemies.append(Enemy())
            spawn_timer = 0
            enemy_count += 1
        
        # Spawn-Intervall beschleunigen
        if time_since_last_update > 20000:
            spawn_interval = max(50, spawn_interval - 15)  # Mindestintervall 50 ms
            print(f"Mehr Balloons! Neuer Intervall: {spawn_interval}ms")
            time_since_last_update = 0
    else:  # Pausen-Phase (3 Sekunden)
        spawn_timer = 0  # Reset für nahtlosen Übergang zur nächsten Spawning-Phase
        print("Pause")

    # Update
    for enemy in enemies[:]:
        enemy.update()
        if enemy.target_index >= len(PATH["easy"]):
            enemies.remove(enemy)
            lives -= 1
            if lives == 0:
                print("GAME OVER")
                running = False

    for tower in towers:
        tower.shoot(enemies)
        for bullet in tower.bullets[:]:
            if bullet.update():
                if bullet.target in enemies:
                    bullet.target.health -= bullet.damage
                    if bullet.target.health <= 0:
                        enemies.remove(bullet.target)
                        gold += VALUE_PER_ENEMY
                tower.bullets.remove(bullet)

    # Zeichnen
    screen.fill(WHITE)

    # Zeichne Grid
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (x, y) in PATH["easy"]:
                pygame.draw.rect(screen, PATH_COLOR, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    # Zeichne Tower-Buttons
    for i, tower_type in enumerate(TOWER_TYPES):
        button_x = 500 + (300 - BUTTON_WIDTH) // 2
        button_y = START_Y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
        rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        color = tower_type['color']
        if selected_tower_type == i:
            pygame.draw.rect(screen, (255, 255, 0), rect, 3)  # Auswahlrahmen
        pygame.draw.rect(screen, color, rect)
        font = pygame.font.Font(None, 36)
        text = font.render(f"${tower_type['price']}", True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Zeichne Objekte
    for enemy in enemies:
        enemy.draw()
    for tower in towers:
        tower.draw()
        for bullet in tower.bullets:
            bullet.draw()

    # Labels Anzeige
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(text, (10, 10))
    text = font.render(f"Gold: ${gold}", True, BLACK)
    screen.blit(text, (500 + 150, 10))
    text = font.render(f"Towers:", True, BLACK)
    screen.blit(text, (500 + 50, 100))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()