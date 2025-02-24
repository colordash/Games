import pygame

# Initialisierung (wie in deiner Hauptdatei)
pygame.init()
WIDTH, HEIGHT = 800, 500  # Übernehmen von deiner Hauptdatei
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Farben (übernehmen)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def show_looser_screen():  # Übergabe der Punktzahl
    win_screen = True
    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 36)

    while win_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill(WHITE)
        title_surface = font_title.render("Du hast verloren!", True, BLACK)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(title_surface, title_rect)



        pygame.display.flip()
        clock.tick(60)

