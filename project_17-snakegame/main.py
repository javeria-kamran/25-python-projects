import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # For special food

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Snake Game")

# Clock for controlling game speed
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont("Arial", 20)
font_medium = pygame.font.SysFont("Arial", 25)
font_large = pygame.font.SysFont("Arial", 40)

# Sound effects
try:
    eat_sound = pygame.mixer.Sound("eat.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
    sound_enabled = True
except:
    sound_enabled = False

class SnakeGame:
    def __init__(self):
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = "RIGHT"
        self.food = self.generate_food()
        self.special_food = None
        self.special_food_timer = 0
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.difficulty = 10  # Medium speed by default
        self.last_move_time = 0
        self.move_delay = 100  # milliseconds

    def generate_food(self):
        """Generate regular food at random position"""
        while True:
            food_x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food_y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food_pos = (food_x, food_y)
            if food_pos not in self.snake:
                return food_pos

    def generate_special_food(self):
        """Generate special food that gives bonus points"""
        if random.random() < 0.1:  # 10% chance to spawn
            while True:
                food_x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                food_y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                food_pos = (food_x, food_y)
                if food_pos not in self.snake and food_pos != self.food:
                    self.special_food_timer = pygame.time.get_ticks() + 5000  # 5 seconds
                    return food_pos
        return None

    def load_high_score(self):
        """Load high score from file if exists"""
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read())
        except:
            pass
        return 0

    def save_high_score(self):
        """Save high score to file"""
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def reset_game(self):
        """Reset game state"""
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = "RIGHT"
        self.food = self.generate_food()
        self.special_food = None
        self.score = 0
        self.game_over = False

    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_UP and self.direction != "DOWN":
                        self.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP":
                        self.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                        self.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                        self.direction = "RIGHT"
                else:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                # Change difficulty
                if event.key == pygame.K_1:
                    self.difficulty = 5
                elif event.key == pygame.K_2:
                    self.difficulty = 10
                elif event.key == pygame.K_3:
                    self.difficulty = 15

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay:
            return
        self.last_move_time = current_time

        # Move snake
        head_x, head_y = self.snake[0]
        if self.direction == "UP":
            new_head = (head_x, head_y - BLOCK_SIZE)
        elif self.direction == "DOWN":
            new_head = (head_x, head_y + BLOCK_SIZE)
        elif self.direction == "LEFT":
            new_head = (head_x - BLOCK_SIZE, head_y)
        else:  # RIGHT
            new_head = (head_x + BLOCK_SIZE, head_y)

        # Check collisions
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            new_head in self.snake):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            if sound_enabled:
                game_over_sound.play()
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check food collision
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            # Chance to spawn special food
            if random.random() < 0.3:  # 30% chance
                self.special_food = self.generate_special_food()
            if sound_enabled:
                eat_sound.play()
        elif self.special_food and new_head == self.special_food:
            self.score += 3  # Bonus points
            self.special_food = None
            if sound_enabled:
                eat_sound.play()
        else:
            self.snake.pop()

        # Check special food timer
        if (self.special_food and 
            pygame.time.get_ticks() > self.special_food_timer):
            self.special_food = None

    def draw(self):
        """Draw all game elements"""
        screen.fill(BLACK)

        # Draw snake
        for i, block in enumerate(self.snake):
            color = GREEN if i == 0 else (0, 200, 0)  # Darker green for body
            pygame.draw.rect(screen, color, (block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw food
        pygame.draw.rect(screen, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw special food if exists
        if self.special_food:
            pygame.draw.rect(screen, YELLOW, (self.special_food[0], self.special_food[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw score and high score
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        high_score_text = font_medium.render(f"High Score: {self.high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 10, 10))

        # Draw difficulty level
        diff_text = font_small.render(
            f"Speed: {self.difficulty} (Press 1-3 to change)", True, BLUE)
        screen.blit(diff_text, (10, SCREEN_HEIGHT - 30))

        # Draw game over message if needed
        if self.game_over:
            game_over_text = font_large.render("GAME OVER", True, WHITE)
            score_text = font_medium.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = font_small.render("Press R to Restart or Q to Quit", True, WHITE)

            screen.blit(game_over_text, 
                       (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                        SCREEN_HEIGHT//2 - 60))
            screen.blit(score_text, 
                       (SCREEN_WIDTH//2 - score_text.get_width()//2, 
                        SCREEN_HEIGHT//2))
            screen.blit(restart_text, 
                       (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                        SCREEN_HEIGHT//2 + 50))

        pygame.display.flip()

def main():
    game = SnakeGame()

    while True:
        game.handle_input()
        game.update()
        game.draw()
        clock.tick(game.difficulty)

if __name__ == "__main__":
    main()