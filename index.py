import pygame
import math
from collections import deque

# Initialisierung
pygame.init()
WIDTH, HEIGHT = 500, 500
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Farben
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PATH_COLOR = (150, 150, 150)

# Pfaddefinition (vordefinierter Pfad)
PATH = [
    (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
    (4, 5), (4, 6), (5, 6), (6, 6), (7, 6),
    (7, 5), (7, 4), (8, 4), (9, 4)
]

class Enemy:
    def __init__(self):
        self.path = deque(PATH)
        self.pos = pygame.Vector2(self.path[0][0] * CELL_SIZE + CELL_SIZE//2, 
                                 self.path[0][1] * CELL_SIZE + CELL_SIZE//2)
        self.target_index = 1
        self.speed = 1
        self.health = 100
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 3 * CELL_SIZE
        self.damage = 20
        self.cooldown = 1000
        self.last_shot = 0
        self.bullets = []

    def in_range(self, enemy):
        distance = math.hypot(self.x - enemy.pos.x, self.y - enemy.pos.y)
        return distance <= self.range

    def shoot(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.cooldown:
            # Finde das am weitesten fortgeschrittene Ziel
            max_progress = -1
            target = None
            for enemy in enemies:
                if self.in_range(enemy):
                    progress = enemy.target_index
                    if progress > max_progress:
                        max_progress = progress
                        target = enemy
            
            if target:
                self.bullets.append(Bullet(self.x, self.y, target))
                self.last_shot = now

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x - CELL_SIZE//2, self.y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE))

class Bullet:
    def __init__(self, x, y, target):
        self.pos = pygame.Vector2(x, y)
        self.target = target
        self.speed = 5
        self.damage = 20

    def update(self):
        if self.target.health > 0:
            direction = self.target.pos - self.pos
            if direction.length() > self.speed:
                direction.scale_to_length(self.speed)
            self.pos += direction
        return self.pos.distance_to(self.target.pos) < 5  # Kollision

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.pos.x), int(self.pos.y)), 3)

# Spielobjekte
enemies = []
towers = []
spawn_timer = 0

running = True
while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_x = x // CELL_SIZE
            grid_y = y // CELL_SIZE
            # Überprüfe ob Platz frei und nicht auf dem Pfad
            if (grid_x, grid_y) not in PATH and all(
                (grid_x != t.x // CELL_SIZE or grid_y != t.y // CELL_SIZE) for t in towers):
                towers.append(Tower(grid_x * CELL_SIZE + CELL_SIZE//2,
                                  grid_y * CELL_SIZE + CELL_SIZE//2))

    # Spawn Gegner
    spawn_timer += clock.get_rawtime()
    if spawn_timer > 2000:
        enemies.append(Enemy())
        spawn_timer = 0

    # Update
    for enemy in enemies[:]:
        enemy.update()
        if enemy.target_index >= len(PATH):
            enemies.remove(enemy)

    for tower in towers:
        tower.shoot(enemies)
        for bullet in tower.bullets[:]:
            if bullet.update():
                bullet.target.health -= bullet.damage
                if bullet.target.health <= 0:
                    enemies.remove(bullet.target)
                tower.bullets.remove(bullet)

    # Zeichnen
    screen.fill(WHITE)

    # Zeichne Grid
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (x, y) in PATH:
                pygame.draw.rect(screen, PATH_COLOR, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    # Zeichne Objekte
    for enemy in enemies:
        enemy.draw()
    for tower in towers:
        tower.draw()
        for bullet in tower.bullets:
            bullet.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()