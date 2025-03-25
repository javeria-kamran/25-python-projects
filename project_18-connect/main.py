import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 650  # Extra space for header
DISC_SIZE = 100
GRID_WIDTH = 7
GRID_HEIGHT = 6

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
BLUE = (30, 30, 180)  # Grid background color
GRAY = (200, 200, 200)  # For empty slots
HEADER_COLOR = (40, 40, 40)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Connect Four Deluxe")

# Clock for controlling game speed
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont("Arial", 50)
font_medium = pygame.font.SysFont("Arial", 35)
font_small = pygame.font.SysFont("Arial", 25)

# Sound effects
try:
    drop_sound = pygame.mixer.Sound("drop.wav")
    win_sound = pygame.mixer.Sound("win.wav")
    draw_sound = pygame.mixer.Sound("draw.wav")
    sound_enabled = True
except:
    sound_enabled = False

class ConnectFourGame:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_player = "R"
        self.game_over = False
        self.winner = None
        self.last_move_time = 0
        self.animation_y = 0
        self.animating = False
        self.animation_column = 0
        self.animation_player = None
        self.red_score = 0
        self.yellow_score = 0
        self.last_win_positions = []

    def reset_game(self):
        """Reset the game state"""
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_player = "R"
        self.game_over = False
        self.winner = None
        self.last_win_positions = []

    def draw_grid(self):
        """Draw the game grid"""
        # Draw header area
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, SCREEN_WIDTH, 50))
        
        # Draw current player indicator
        player_text = font_small.render(f"Current: {'Red' if self.current_player == 'R' else 'Yellow'}", True, 
                                      RED if self.current_player == 'R' else YELLOW)
        screen.blit(player_text, (10, 10))
        
        # Draw scores
        score_text = font_small.render(f"Red: {self.red_score}  Yellow: {self.yellow_score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))
        
        # Draw grid background
        pygame.draw.rect(screen, BLUE, (0, 50, SCREEN_WIDTH, SCREEN_HEIGHT - 50))

        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = GRAY if self.grid[y][x] is None else (RED if self.grid[y][x] == "R" else YELLOW)
                
                # Highlight winning discs
                if (x, y) in self.last_win_positions:
                    pygame.draw.circle(screen, WHITE, 
                                     (x * DISC_SIZE + DISC_SIZE // 2, y * DISC_SIZE + DISC_SIZE // 2 + 50), 
                                     DISC_SIZE // 2 - 2)
                    pygame.draw.circle(screen, color, 
                                     (x * DISC_SIZE + DISC_SIZE // 2, y * DISC_SIZE + DISC_SIZE // 2 + 50), 
                                     DISC_SIZE // 2 - 5)
                else:
                    pygame.draw.circle(screen, color, 
                                     (x * DISC_SIZE + DISC_SIZE // 2, y * DISC_SIZE + DISC_SIZE // 2 + 50), 
                                     DISC_SIZE // 2 - 5)

        # Draw animation if in progress
        if self.animating:
            color = RED if self.animation_player == "R" else YELLOW
            pygame.draw.circle(screen, color, 
                             (self.animation_column * DISC_SIZE + DISC_SIZE // 2, 
                              self.animation_y + DISC_SIZE // 2), 
                             DISC_SIZE // 2 - 5)

    def start_drop_animation(self, column, player):
        """Start disc drop animation"""
        self.animating = True
        self.animation_column = column
        self.animation_player = player
        self.animation_y = 50  # Start from top
        if sound_enabled:
            drop_sound.play()

    def update_animation(self):
        """Update drop animation"""
        if not self.animating:
            return False

        self.animation_y += 15  # Animation speed
        
        # Check if animation should stop
        target_row = self.get_lowest_empty_row(self.animation_column)
        target_y = target_row * DISC_SIZE + 50
        
        if self.animation_y >= target_y:
            self.animating = False
            self.grid[target_row][self.animation_column] = self.animation_player
            return True
        
        return False

    def get_lowest_empty_row(self, column):
        """Find the lowest empty row in a column"""
        for y in range(GRID_HEIGHT - 1, -1, -1):
            if self.grid[y][column] is None:
                return y
        return -1  # Column is full

    def check_win(self, player):
        """Check if the specified player has won"""
        # Check horizontal
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH - 3):
                if (self.grid[y][x] == self.grid[y][x + 1] == 
                    self.grid[y][x + 2] == self.grid[y][x + 3] == player):
                    self.last_win_positions = [(x, y), (x+1, y), (x+2, y), (x+3, y)]
                    return True

        # Check vertical
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT - 3):
                if (self.grid[y][x] == self.grid[y + 1][x] == 
                    self.grid[y + 2][x] == self.grid[y + 3][x] == player):
                    self.last_win_positions = [(x, y), (x, y+1), (x, y+2), (x, y+3)]
                    return True

        # Check diagonal (top-left to bottom-right)
        for y in range(GRID_HEIGHT - 3):
            for x in range(GRID_WIDTH - 3):
                if (self.grid[y][x] == self.grid[y + 1][x + 1] == 
                    self.grid[y + 2][x + 2] == self.grid[y + 3][x + 3] == player):
                    self.last_win_positions = [(x, y), (x+1, y+1), (x+2, y+2), (x+3, y+3)]
                    return True

        # Check diagonal (bottom-left to top-right)
        for y in range(3, GRID_HEIGHT):
            for x in range(GRID_WIDTH - 3):
                if (self.grid[y][x] == self.grid[y - 1][x + 1] == 
                    self.grid[y - 2][x + 2] == self.grid[y - 3][x + 3] == player):
                    self.last_win_positions = [(x, y), (x+1, y-1), (x+2, y-2), (x+3, y-3)]
                    return True

        return False

    def check_draw(self):
        """Check if the game is a draw"""
        return all(cell is not None for row in self.grid for cell in row)

    def handle_input(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.animating:
                x, y = event.pos
                if y > 50:  # Only below header
                    column = x // DISC_SIZE
                    if column < GRID_WIDTH and self.get_lowest_empty_row(column) != -1:
                        self.start_drop_animation(column, self.current_player)

            if event.type == pygame.KEYDOWN and self.game_over:
                if event.key == pygame.K_r:  # Restart game
                    self.reset_game()
                if event.key == pygame.K_q:  # Quit game
                    pygame.quit()
                    sys.exit()

    def update(self):
        """Update game state"""
        if self.animating:
            if self.update_animation():  # Animation just finished
                # Check for win or draw
                if self.check_win(self.current_player):
                    self.game_over = True
                    self.winner = self.current_player
                    if self.winner == "R":
                        self.red_score += 1
                    else:
                        self.yellow_score += 1
                    if sound_enabled:
                        win_sound.play()
                elif self.check_draw():
                    self.game_over = True
                    if sound_enabled:
                        draw_sound.play()
                else:
                    # Switch player
                    self.current_player = "Y" if self.current_player == "R" else "R"

    def draw_game_over(self):
        """Draw game over message"""
        if self.winner:
            message = f"{'Red' if self.winner == 'R' else 'Yellow'} Player Wins!"
            color = RED if self.winner == 'R' else YELLOW
        else:
            message = "Game Ended in a Draw!"
            color = WHITE

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Message
        text = font_large.render(message, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                          SCREEN_HEIGHT // 2 - 50))

        # Instructions
        restart_text = font_medium.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 + 20))

    def draw(self):
        """Draw all game elements"""
        screen.fill(BLACK)
        self.draw_grid()
        
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

def main():
    game = ConnectFourGame()

    while True:
        game.handle_input()
        game.update()
        game.draw()
        clock.tick(60)

if __name__ == "__main__":
    main()