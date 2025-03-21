import pygame, asyncio
import math
from collections import deque
import random
import json
import os
import win_screen
import defeated
import time


# Initialisierung
pygame.init()
WIDTH, HEIGHT = 800, 500
GRID_SIZE = 10
CELL_SIZE = HEIGHT // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Titel setzen
pygame.display.set_caption("Towerdefense by Jamil Sostizzo")

# Initialisierung der Musik
pygame.mixer.init()
pygame.mixer.music.load("sounds/music.mp3")
pygame.mixer.music.play(-1)  # -1 sorgt für Endlosschleife

plop_sound = pygame.mixer.Sound("sounds/plop.mp3")
plop_sound.set_volume(0.4)

tadaa_sound = pygame.mixer.Sound("sounds/tadaa.mp3")

hit_sound = pygame.mixer.Sound("sounds/hit.mp3")

game_over_sound = pygame.mixer.Sound("sounds/game_over.mp3")

#----------------KONSTANTEN--------------------------------------------
VALUE_PER_ENEMY = 10
SAVE_FILE = "game_data.json"

# Initialisierung der Timer
cycle_time = 0
spawn_timer = 0
time_since_last_update = 0
last_time = 0 

# Spielobjekte
enemies = []
towers = []
spawn_timer = 0
time_since_last_update = 0 
lives = 10
gold = 150
spawn_interval = 1000
enemy_count = 0 
selected_tower_type = None
running = True


# Button Parameter für die Towers Auswahl
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

PATH_TYPES = ["easy", "medium"]
current_level = PATH_TYPES[0]

# Tower-Typen mit Preisen und Eigenschaften
TOWER_TYPES = [
    {"color": GREEN, "price": 100, "range": 3, "damage": 10, "cooldown": 2500},
    {"color": BLUE, "price": 200, "range": 4, "damage": 15, "cooldown": 1900},
    {"color": PURPLE, "price": 600, "range": 5, "damage": 20, "cooldown": 1000},
]

# ----------------Klassen----------------------------------------------------
class Enemy:
    speed = 2  # Standard-Klassenattribut

    def __init__(self):
        self.path = deque(PATH[current_level])
        self.pos = pygame.Vector2(self.path[0][0] * CELL_SIZE + CELL_SIZE // 2, 
                                  self.path[0][1] * CELL_SIZE + CELL_SIZE // 2)
        self.target_index = 1
        self.speed = Enemy.speed  # Falls kein eigenes Instanzattribut gesetzt wird
        self.health = 10
        self.radius = 10

    def update(self):
        # Prüfen, ob noch Ziele auf dem Pfad vorhanden sind
        if self.target_index < len(self.path):
            # Das aktuelle Ziel auf dem Pfad abrufen
            target = self.path[self.target_index]
            # Die Zielposition im Spielfeld berechnen (Mittelpunkt der Zelle)
            target_pos = pygame.Vector2(target[0] * CELL_SIZE + CELL_SIZE//2,
                                        target[1] * CELL_SIZE + CELL_SIZE//2)
            direction = target_pos - self.pos
            # Falls die Entfernung grösser als die Bewegungsgeschwindigkeit ist, skalieren
            if direction.length() > self.speed:
                direction.scale_to_length(self.speed)
            # Die Position des Objekts aktualisieren
            self.pos += direction
            # Falls das Ziel erreicht wurde, zum nächsten Ziel übergehen
            if self.pos.distance_to(target_pos) < 1:
                self.target_index += 1

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.pos.x), int(self.pos.y)), self.radius)

class Tower:
    def __init__(self, x, y, color, range, damage, cooldown, price):
        self.x = x
        self.y = y
        self.color = color
        self.range = range * CELL_SIZE
        self.damage = damage
        self.cooldown = cooldown
        self.last_shot = 0
        self.bullets = []
        self.price = price

    def in_range(self, enemy):
        # berechnet ob ein einemy in seiner Schussreichweite ist
        distance = math.hypot(self.x - enemy.pos.x, self.y - enemy.pos.y)
        return distance <= self.range

    def shoot(self, enemies):
        now = pygame.time.get_ticks()
        # Überprüfen, ob die Abklingzeit (Cooldown) abgelaufen ist
        if now - self.last_shot > self.cooldown:
            targets = [enemy for enemy in enemies if self.in_range(enemy)]
            # Falls es Feinde in Reichweite gibt
            if targets:
                # ein Schuss auf das Erste erreichbare Ziel abgeben
                target = targets[0]
                self.bullets.append(Bullet(self.x, self.y, target, self.damage))
                self.last_shot = now

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x - CELL_SIZE//2, self.y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE))


class Bullet:
    def __init__(self, x, y, target, damage):
        self.pos = pygame.Vector2(x, y)
        self.target = target
        self.speed = 8
        self.damage = damage

    def update(self):
        # Überprüfen, ob das Ziel noch Lebenspunkte hat
        if self.target.health > 0:
            # Richtung vom aktuellen Standpunkt zum Ziel berechnen
            direction = self.target.pos - self.pos
            # Gleiches Verfahren zur Animation über das Spielfeld wie bei den Enemys
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

# das nächste Level wird geladen und dir das Gold zurückgegeben
def next_level(towers, gold, lives):
    global current_level  # Wichtig: current_level als global deklarieren
    try:
        current_level = PATH_TYPES[PATH_TYPES.index(current_level) + 1]
    except IndexError:
        print("Keine weiteren Level!")
        tadaa_sound.play()
        win_screen.show_win_screen(lives)

    for tower in towers[:]:
        gold += round(tower.price/2)
        towers.remove(tower)
    return gold

# Berechnung des neuen spawnintervalles mitels Polinom der in Geogebra konstruiert wurde. 
def get_new_interval_timer(rounds, current_level):
    if current_level == "easy":
        return round((0.01*rounds**3-0.02*rounds**2-1.33*rounds+10)*100)
    elif current_level == "medium":
        print("Level 2 hat begonnen")
        return round((-0.01*rounds**3+0.2*rounds**2-1.5*rounds+5)*100)

# Intro-Bildschirm
def show_intro():
    intro = True
    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 36)
    # Position und Grösse des Start-Buttons oben rechts (mit 20px Rand)
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
spawner_flag = True
button_rect = None
rounds = 0

async def main():
    global running, current_level, lives, gold, spawn_interval, selected_tower_type, button_rect, rounds, last_time, cycle_time, spawn_timer, time_since_last_update, spawner_flag, button_rect,enemy_count


    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if event.button == 1:  # Linksklick
                    # Zuerst: Prüfe, ob auf den aktiven Sell-Button geklickt wurde
                    if button_rect and button_rect.collidepoint(x, y):
                        if selected_tower in towers:
                            gold += round(selected_tower.price/2)
                            towers.remove(selected_tower)
                        button_rect = None
                        selected_tower = None
                    # Dann: Prüfe, ob in der Tower-Auswahl (rechter Bereich) geklickt wurde
                    elif x >= 500:
                        for i, tower_type in enumerate(TOWER_TYPES):
                            button_x = 500 + (300 - BUTTON_WIDTH) // 2
                            button_y = START_Y + i * (BUTTON_HEIGHT + BUTTON_SPACING)
                            rect = pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                            if rect.collidepoint(x, y):
                                selected_tower_type = i
                                break
                        # Optional: Sell-Button ausblenden, wenn in der Seitenleiste geklickt wurde
                        button_rect = None
                    # Andernfalls: Klick auf das Grid zum Platzieren eines Towers
                    else:
                        grid_x = x // CELL_SIZE
                        grid_y = y // CELL_SIZE
                        if selected_tower_type is not None:
                            if (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and
                                (grid_x, grid_y) not in PATH[current_level] and
                                not any(t.x == grid_x * CELL_SIZE + CELL_SIZE//2 and
                                        t.y == grid_y * CELL_SIZE + CELL_SIZE//2 for t in towers)):
                                cost = TOWER_TYPES[selected_tower_type]['price']
                                # neue Instanz der Klasse Tower wird erstellt
                                if gold >= cost:
                                    tower_type = TOWER_TYPES[selected_tower_type]
                                    towers.append(Tower(
                                        grid_x * CELL_SIZE + CELL_SIZE//2,
                                        grid_y * CELL_SIZE + CELL_SIZE//2,
                                        tower_type['color'],
                                        tower_type['range'],
                                        tower_type['damage'],
                                        tower_type['cooldown'],
                                        tower_type["price"]
                                    ))
                                    gold -= cost
                                    selected_tower_type = None
                        # Klick außerhalb: Sell-Button ausblenden
                        button_rect = None

                elif event.button == 3:  # Rechtsklick
                    for tower in towers:
                        tower_rect = pygame.Rect(
                            tower.x - CELL_SIZE // 2,
                            tower.y - CELL_SIZE // 2,
                            CELL_SIZE,
                            CELL_SIZE
                        )
                        if tower_rect.collidepoint(x, y):
                            button_rect = pygame.Rect(x, y, 80, 30)
                            selected_tower = tower
                            break
                    else:
                        button_rect = None

            # --- Update-Logik ----------------------------------------------------
        current_time = time.perf_counter() * 1000  # Umrechnung in Millisekunden
        dt = current_time - last_time  # Zeitdifferenz in ms
        last_time = current_time  # Aktualisiere die letzte Zeit

        cycle_time += dt
        cycle_time %= 13000  # Beispiel: 13 Sekunden Zyklus

        if cycle_time < 10000:  # Spawning-Phase (z. B. 10 Sekunden)
            spawn_timer += dt
            time_since_last_update += dt

            if spawn_timer > spawn_interval and spawner_flag:
                enemies.append(Enemy())  # Neuen Gegner hinzufügen
                spawn_timer = 0
                enemy_count += 1
                print(cycle_time)

            if time_since_last_update > 10000:
                spawn_interval = get_new_interval_timer(rounds, current_level)
                Enemy.speed += 0.02
                print(f"Mehr Balloons! Neuer Intervall: {spawn_interval}ms")
                time_since_last_update = 0
                print(rounds)
                rounds += 1
        else:
            spawn_timer = 0  # Reset in der Pause

        # Check für Levelwechsel (erst nach Zehn Runden)
        if rounds >= 10:
            spawner_flag = False  # Stoppe das Spawnen neuer Gegner

            if not enemies:  # Warten, bis alle Gegner verschwunden sind, dann alles zurücksetzen für das nächste level
                print("Alle Gegner besiegt! Levelaufstieg...")
                gold = next_level(towers, gold, lives)
                rounds = 0
                spawner_flag = True  # Spawner wieder aktivieren für das neue Level
                spawn_interval = get_new_interval_timer(rounds, current_level)
                time_since_last_update = 0
                spawn_timer = 0



        # Gegner aktualisieren
        for enemy in enemies[:]: # Iteration über eine Kopie der Liste, um sicheres Entfernen zu ermöglichen
            enemy.update()
            # Überprüfen, ob der Gegner das Ende des Pfads erreicht hat
            if enemy.target_index >= len(PATH[current_level]):
                enemies.remove(enemy)
                lives -= 1
                hit_sound.play()
                # Game over logik
                if lives <= 0:
                    print("GAME OVER")
                    game_over_sound.play()
                    defeated.show_looser_screen()
                    running = False

        # Türme und ihre Bullets aktualisieren
        for tower in towers:
            tower.shoot(enemies)
            for bullet in tower.bullets[:]:
                if bullet.update():
                    if bullet.target in enemies:
                        bullet.target.health -= bullet.damage
                        if bullet.target.health <= 0:
                            enemies.remove(bullet.target)
                            plop_sound.play()
                            gold += VALUE_PER_ENEMY
                    tower.bullets.remove(bullet)

        # --- Zeichnen --------------------------------------------------------------
        screen.fill(WHITE)

        # Zeichne Grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) in PATH[current_level]:
                    pygame.draw.rect(screen, PATH_COLOR, rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

        # Zeichne der Tower-Auswahl-Buttons
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

        # Zeichne Gegner
        for enemy in enemies:
            enemy.draw()

        # Zeichne Türme und Bullets
        for tower in towers:
            tower.draw()
            for bullet in tower.bullets:
                bullet.draw()

        # Zeichne Labels (Lives, Gold, etc.)
        font = pygame.font.Font(None, 36)
        screen.blit(font.render(f"Lives: {lives}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Gold: ${gold}", True, BLACK), (500 + 150, 10))
        screen.blit(font.render("Towers:", True, BLACK), (500 + 50, 100))
        screen.blit(font.render(f"Raids: {rounds}/10", True, BLACK), (200,10))
        screen.blit(font.render(f"Level: {PATH_TYPES.index(current_level) + 1}", True, BLACK), (360, 10))

        # Zeichne den Sell-Button (wenn aktiv) zuletzt, damit er nicht überschrieben wird
        if button_rect:
            pygame.draw.rect(screen, PURPLE, button_rect)
            font_small = pygame.font.Font(None, 24)
            text = font_small.render(f"sell ${round(selected_tower.price/2)}", True, WHITE)
            screen.blit(text, (button_rect.x + 5, button_rect.y + 5))
        # Bildschirm aktualisieren, um die Änderungen anzuzeigen
        pygame.display.flip()
        clock.tick(60)
    await asyncio.sleep(0)
asyncio.run(main())


