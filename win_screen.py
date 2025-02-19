import pygame

# Initialisierung (wie in deiner Hauptdatei)
pygame.init()
WIDTH, HEIGHT = 800, 500  # Übernehmen von deiner Hauptdatei
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Farben (übernehmen)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def show_win_screen(score):  # Übergabe der Punktzahl
    win_screen = True
    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 36)

    while win_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            #if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
             #   win_screen = False  # Schließe den Bildschirm bei Klick

        screen.fill(WHITE)
        title_surface = font_title.render("Du hast gewonnen!", True, BLACK)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(title_surface, title_rect)

        text_surface = font_text.render("Herzlichen Glückwunsch! Du hast alle Level abgeschlossen.", True, BLACK)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(text_surface, text_rect)

        score_surface = font_text.render(f"Leben: {score}", True, BLACK)  # Anzeige der Punktzahl
        score_rect = score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(score_surface, score_rect)

        pygame.display.flip()
        clock.tick(60)

# Testen der Szene (optional)
if __name__ == "__main__":  # Wird nur ausgeführt, wenn die Datei direkt gestartet wird
    show_win_screen(250)  # Beispielpunktzahl