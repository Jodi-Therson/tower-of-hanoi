import pygame
import sys

# Game settings
WIDTH, HEIGHT = 640, 480
ROD_WIDTH = 10
DISK_HEIGHT = 20
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKYBLUE = (100, 200, 255)
GRAY = (200, 200, 200)
GREEN = (0, 128, 0)

class HanoiGame:
    def __init__(self, screen, num_disks):
        self.screen = screen
        self.num_disks = num_disks
        self.rods = [list(reversed(range(1, num_disks + 1))), [], []]
        self.rod_positions = [
            (WIDTH // 4, HEIGHT - 50),
            (WIDTH // 2, HEIGHT - 50),
            (3 * WIDTH // 4, HEIGHT - 50)
        ]
        self.move_count = 0

        self.dragging = False
        self.drag_disk = None
        self.drag_from_rod = None
        self.drag_offset = (0, 0)

        self.win_shown = False
        self.win_timer = 0

    def draw(self):
        self.screen.fill(WHITE)

        # Draw rods
        for x, y in self.rod_positions:
            pygame.draw.rect(self.screen, BLACK, (x - ROD_WIDTH // 2, y - 150, ROD_WIDTH, 150))

        # Draw disks
        for rod_index, rod in enumerate(self.rods):
            x, y = self.rod_positions[rod_index]
            for i, disk in enumerate(rod):
                if self.dragging and rod_index == self.drag_from_rod and disk == self.drag_disk:
                    continue
                width = 30 + disk * 20
                rect = pygame.Rect(x - width // 2, y - (i + 1) * DISK_HEIGHT, width, DISK_HEIGHT)
                pygame.draw.rect(self.screen, SKYBLUE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)

        # Draw dragged disk
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            disk_width = 30 + self.drag_disk * 20
            rect = pygame.Rect(
                mouse_x + self.drag_offset[0] - disk_width // 2,
                mouse_y + self.drag_offset[1] - DISK_HEIGHT // 2,
                disk_width,
                DISK_HEIGHT
            )
            pygame.draw.rect(self.screen, SKYBLUE, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)

        # Draw move counter
        font = pygame.font.SysFont(None, 28)
        move_text = font.render(f"Moves: {self.move_count}", True, BLACK)
        self.screen.blit(move_text, (10, 10))

        # Draw win message and reset button
        if self.win_shown:
            if pygame.time.get_ticks() - self.win_timer > 1000:
                font = pygame.font.SysFont(None, 40)
                win_text = font.render("Congratulations! You won!", True, GREEN)
                self.screen.blit(win_text, (WIDTH // 2 - 160, HEIGHT // 2 - 50))

                # Reset button
                self.reset_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 40)
                pygame.draw.rect(self.screen, GRAY, self.reset_rect)
                button_font = pygame.font.SysFont(None, 30)
                text = button_font.render("Reset", True, BLACK)
                text_rect = text.get_rect(center=self.reset_rect.center)
                self.screen.blit(text, text_rect)

        pygame.display.flip()

    def get_rod_at_pos(self, pos):
        for i, (x, _) in enumerate(self.rod_positions):
            if abs(pos[0] - x) < 60:
                return i
        return None

    def start_drag(self, pos):
        if self.win_shown:
            return
        rod_index = self.get_rod_at_pos(pos)
        if rod_index is not None and self.rods[rod_index]:
            disk = self.rods[rod_index][-1]
            self.dragging = True
            self.drag_disk = disk
            self.drag_from_rod = rod_index
            self.drag_offset = (0, 0)
            print(f"[DEBUG] Picked disk {disk} from rod {chr(65 + rod_index)}")

    def drop_disk(self, pos):
        if not self.dragging:
            return

        rod_index = self.get_rod_at_pos(pos)
        if rod_index is not None:
            print(f"[DEBUG] Dropping disk {self.drag_disk} on rod {chr(65 + rod_index)}")

            if not self.rods[rod_index] or self.drag_disk < self.rods[rod_index][-1]:
                self.rods[self.drag_from_rod].pop()
                self.rods[rod_index].append(self.drag_disk)
                self.move_count += 1
                print(f"[DEBUG] Move valid. Disk {self.drag_disk} moved.")
            else:
                print(f"[DEBUG] Invalid move. Disk {self.drag_disk} too large for top of rod {chr(65 + rod_index)}.")
        else:
            print(f"[DEBUG] Drop failed. Not over a valid rod.")

        self.dragging = False
        self.drag_disk = None
        self.drag_from_rod = None

    def is_won(self):
        return self.rods[2] == list(reversed(range(1, self.num_disks + 1)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tower of Hanoi - Drag & Drop Version")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    num_disks = None
    game = None
    running = True
    selecting = True

    # Create disk selection buttons
    buttons = []
    for i in range(3, 9):  # 3 to 8
        rect = pygame.Rect(100 + (i - 3) * 70, HEIGHT // 2 - 25, 60, 50)
        buttons.append((i, rect))

    while running:
        clock.tick(FPS)
        screen.fill(WHITE)

        if selecting:
            title = font.render("Select Number of Disks", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

            for i, rect in buttons:
                pygame.draw.rect(screen, GRAY, rect)
                text = font.render(str(i), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

        elif game:
            game.draw()
            if game.is_won() and not game.win_shown:
                game.win_shown = True
                game.win_timer = pygame.time.get_ticks()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if selecting:
                    for i, rect in buttons:
                        if rect.collidepoint(event.pos):
                            num_disks = i
                            game = HanoiGame(screen, num_disks)
                            selecting = False
                            break
                elif game:
                    if game.win_shown and pygame.time.get_ticks() - game.win_timer > 1000:
                        if game.reset_rect.collidepoint(event.pos):
                            game = HanoiGame(screen, num_disks)
                            selecting = True
                            continue
                    game.start_drag(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and not selecting:
                game.drop_disk(event.pos)

            elif event.type == pygame.KEYDOWN and game:
                if event.key == pygame.K_SPACE and game.win_shown:
                    game = HanoiGame(screen, num_disks)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
