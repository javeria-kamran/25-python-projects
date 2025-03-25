import pygame
import random
import os
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
COLORS = [
    (0, 255, 255),  # Cyan (I)
    (255, 255, 0),   # Yellow (O)
    (255, 165, 0),   # Orange (L)
    (0, 0, 255),     # Blue (J)
    (0, 255, 0),     # Green (S)
    (255, 0, 0),     # Red (Z)
    (128, 0, 128)    # Purple (T)
]

# Game area dimensions
GAME_WIDTH = 10
GAME_HEIGHT = 20
GRID_OFFSET_X = 30
GRID_OFFSET_Y = 30

# Initialize screen and clock
screen = None
clock = None

def initialize_game():
    global screen, clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

# Fonts
font_medium = pygame.font.SysFont("Arial", 24)
font_large = pygame.font.SysFont("Arial", 32)

class TetrisGame:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
        self.bag = self.create_bag()
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = 0.5
        self.last_move_time = 0
        self.move_delay = 100
        self.high_score = self.load_high_score()

    def create_bag(self):
        """Create a bag of all 7 pieces"""
        pieces = ['I', 'O', 'L', 'J', 'S', 'Z', 'T']
        random.shuffle(pieces)
        return pieces

    def new_piece(self):
        """Get a new random piece from the bag"""
        if not self.bag:
            self.bag = self.create_bag()
        piece_type = self.bag.pop()
        
        if piece_type == 'I':
            shape = [[1, 1, 1, 1]]
        elif piece_type == 'O':
            shape = [[1, 1], [1, 1]]
        elif piece_type == 'L':
            shape = [[1, 0, 0], [1, 1, 1]]
        elif piece_type == 'J':
            shape = [[0, 0, 1], [1, 1, 1]]
        elif piece_type == 'S':
            shape = [[0, 1, 1], [1, 1, 0]]
        elif piece_type == 'Z':
            shape = [[1, 1, 0], [0, 1, 1]]
        elif piece_type == 'T':
            shape = [[0, 1, 0], [1, 1, 1]]
        
        color = COLORS[['I', 'O', 'L', 'J', 'S', 'Z', 'T'].index(piece_type)]
        
        return {
            'shape': shape,
            'color': color,
            'x': GAME_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0,
            'type': piece_type
        }

    def load_high_score(self):
        """Load high score from file"""
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r") as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
        except:
            return 0

    def save_high_score(self):
        """Save high score to file"""
        try:
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass

    def draw_grid(self):
        """Draw the game grid"""
        pygame.draw.rect(screen, GRAY, 
                        (GRID_OFFSET_X, GRID_OFFSET_Y, 
                         GAME_WIDTH * BLOCK_SIZE, GAME_HEIGHT * BLOCK_SIZE))
        
        for y in range(GAME_HEIGHT):
            for x in range(GAME_WIDTH):
                if self.grid[y][x] != BLACK:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                   (GRID_OFFSET_X + x * BLOCK_SIZE, 
                                    GRID_OFFSET_Y + y * BLOCK_SIZE, 
                                    BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(screen, WHITE, 
                                   (GRID_OFFSET_X + x * BLOCK_SIZE, 
                                    GRID_OFFSET_Y + y * BLOCK_SIZE, 
                                    BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, piece):
        """Draw a tetromino piece"""
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'], 
                                   (GRID_OFFSET_X + (piece['x'] + x) * BLOCK_SIZE, 
                                    GRID_OFFSET_Y + (piece['y'] + y) * BLOCK_SIZE, 
                                    BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(screen, WHITE, 
                                   (GRID_OFFSET_X + (piece['x'] + x) * BLOCK_SIZE, 
                                    GRID_OFFSET_Y + (piece['y'] + y) * BLOCK_SIZE, 
                                    BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_sidebar(self):
        """Draw the sidebar with game info"""
        # Next piece
        next_text = font_medium.render("NEXT:", True, WHITE)
        screen.blit(next_text, (GRID_OFFSET_X + GAME_WIDTH * BLOCK_SIZE + 20, 30))
        
        if self.next_piece:
            temp_piece = self.next_piece.copy()
            temp_piece['x'] = GAME_WIDTH + 2
            temp_piece['y'] = 2
            self.draw_piece(temp_piece)
        
        # Score
        score_text = font_medium.render(f"SCORE: {self.score}", True, WHITE)
        screen.blit(score_text, (GRID_OFFSET_X + GAME_WIDTH * BLOCK_SIZE + 20, 150))
        
        # Level
        level_text = font_medium.render(f"LEVEL: {self.level}", True, WHITE)
        screen.blit(level_text, (GRID_OFFSET_X + GAME_WIDTH * BLOCK_SIZE + 20, 180))
        
        # High score
        high_score_text = font_medium.render(f"HIGH: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (GRID_OFFSET_X + GAME_WIDTH * BLOCK_SIZE + 20, 210))

    def draw_pause_screen(self):
        """Draw pause screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = font_large.render("PAUSED", True, WHITE)
        screen.blit(pause_text, 
                   (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                    SCREEN_HEIGHT // 2 - 30))
        
        continue_text = font_medium.render("Press P to continue", True, WHITE)
        screen.blit(continue_text, 
                   (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                    SCREEN_HEIGHT // 2 + 20))

    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font_large.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, 
                   (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                    SCREEN_HEIGHT // 2 - 50))
        
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, 
                   (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                    SCREEN_HEIGHT // 2))
        
        restart_text = font_medium.render("Press R to restart", True, WHITE)
        screen.blit(restart_text, 
                   (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                    SCREEN_HEIGHT // 2 + 50))

    def is_valid_position(self, x, y, shape):
        """Check if piece is in valid position"""
        for shape_y, row in enumerate(shape):
            for shape_x, cell in enumerate(row):
                if cell:
                    new_x = x + shape_x
                    new_y = y + shape_y
                    if (new_x < 0 or new_x >= GAME_WIDTH or 
                        new_y >= GAME_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x] != BLACK)):
                        return False
        return True

    def rotate_piece(self):
        """Rotate current piece"""
        if not self.current_piece:
            return
        
        rotated = list(zip(*reversed(self.current_piece['shape'])))
        rotated = [list(row) for row in rotated]
        
        if self.is_valid_position(self.current_piece['x'], self.current_piece['y'], rotated):
            self.current_piece['shape'] = rotated

    def hold_piece(self):
        """Hold current piece"""
        if not self.can_hold:
            return
        
        if self.held_piece is None:
            self.held_piece = self.current_piece
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        else:
            self.held_piece, self.current_piece = self.current_piece, self.held_piece
            self.current_piece['x'] = GAME_WIDTH // 2 - len(self.current_piece['shape'][0]) // 2
            self.current_piece['y'] = 0
        
        self.can_hold = False
        
        if not self.is_valid_position(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape']):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def clear_lines(self):
        """Clear completed lines and return number cleared"""
        lines_to_clear = []
        for y in range(GAME_HEIGHT):
            if all(cell != BLACK for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        if not lines_to_clear:
            return 0
        
        for line in sorted(lines_to_clear, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [BLACK for _ in range(GAME_WIDTH)])
        
        # Update score
        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_scores.get(len(lines_to_clear), 0) * self.level
        self.lines_cleared += len(lines_to_clear)
        
        # Update level every 10 lines
        new_level = self.lines_cleared // 10 + 1
        if new_level > self.level:
            self.level = new_level
            self.fall_speed = max(0.05, 0.5 - (self.level * 0.05))
        
        return len(lines_to_clear)

    def hard_drop(self):
        """Drop piece immediately"""
        if not self.current_piece:
            return
        
        while self.is_valid_position(self.current_piece['x'], self.current_piece['y'] + 1, self.current_piece['shape']):
            self.current_piece['y'] += 1
        
        self.lock_piece()

    def lock_piece(self):
        """Lock current piece into grid"""
        if not self.current_piece:
            return
        
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']
        
        lines_cleared = self.clear_lines()
        
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True
        
        if not self.is_valid_position(self.current_piece['x'], self.current_piece['y'], self.current_piece['shape']):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def update(self, dt):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.is_valid_position(self.current_piece['x'], self.current_piece['y'] + 1, self.current_piece['shape']):
                self.current_piece['y'] += 1
            else:
                self.lock_piece()

    def draw(self):
        """Draw all game elements"""
        if screen is None:
            return
            
        try:
            screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_sidebar()
            
            if self.paused:
                self.draw_pause_screen()
            elif self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
        except pygame.error:
            pass

    def handle_input(self):
        """Handle user input"""
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                
                if self.game_over and event.key == pygame.K_r:
                    self.__init__()
                
                if self.paused or self.game_over:
                    continue
                
                if event.key == pygame.K_LEFT:
                    if self.is_valid_position(self.current_piece['x'] - 1, self.current_piece['y'], self.current_piece['shape']):
                        self.current_piece['x'] -= 1
                
                if event.key == pygame.K_RIGHT:
                    if self.is_valid_position(self.current_piece['x'] + 1, self.current_piece['y'], self.current_piece['shape']):
                        self.current_piece['x'] += 1
                
                if event.key == pygame.K_DOWN:
                    if self.is_valid_position(self.current_piece['x'], self.current_piece['y'] + 1, self.current_piece['shape']):
                        self.current_piece['y'] += 1
                        self.score += 1
                
                if event.key == pygame.K_UP:
                    self.rotate_piece()
                
                if event.key == pygame.K_SPACE:
                    self.hard_drop()
                
                if event.key == pygame.K_c:
                    self.hold_piece()
        
        # Continuous movement
        keys = pygame.key.get_pressed()
        if current_time - self.last_move_time > self.move_delay:
            if keys[pygame.K_LEFT]:
                if self.is_valid_position(self.current_piece['x'] - 1, self.current_piece['y'], self.current_piece['shape']):
                    self.current_piece['x'] -= 1
            if keys[pygame.K_RIGHT]:
                if self.is_valid_position(self.current_piece['x'] + 1, self.current_piece['y'], self.current_piece['shape']):
                    self.current_piece['x'] += 1
            if keys[pygame.K_DOWN]:
                if self.is_valid_position(self.current_piece['x'], self.current_piece['y'] + 1, self.current_piece['shape']):
                    self.current_piece['y'] += 1
                    self.score += 1
            
            self.last_move_time = current_time
        
        return True

def main():
    initialize_game()
    game = TetrisGame()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        running = game.handle_input()
        game.update(dt)
        game.draw()
    
    pygame.quit()

if __name__ == "__main__":
    main()