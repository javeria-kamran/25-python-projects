import pygame
import sys
import random
import math
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_SPEED = 8
AI_PADDLE_SPEED = 6
BALL_SPEED = 6
MAX_SCORE = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 200)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Pong")
clock = pygame.time.Clock()

# Load fonts
title_font = pygame.font.SysFont("Arial Black", 80)
font = pygame.font.SysFont("Consolas", 50)
small_font = pygame.font.SysFont("Consolas", 30)

# Sound handling
try:
    paddle_hit_sound = pygame.mixer.Sound("paddle_hit.wav")
    wall_hit_sound = pygame.mixer.Sound("wall_hit.wav")
    score_sound = pygame.mixer.Sound("score.wav")
    win_sound = pygame.mixer.Sound("win.wav")
    sound_available = True
except:
    print("Sound files not found. Continuing without sound.")
    sound_available = False

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 100)
        self.score = 0
    
    def draw(self, color):
        pygame.draw.rect(screen, color, self.rect)
    
    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        if keys[up_key] and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
        if keys[down_key] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PADDLE_SPEED
    
    def ai_move(self, ball):
        if self.rect.centery < ball.centery - 20:
            self.rect.y += AI_PADDLE_SPEED
        elif self.rect.centery > ball.centery + 20:
            self.rect.y -= AI_PADDLE_SPEED

class Ball:
    def __init__(self):
        self.reset()
        self.color = WHITE
    
    def reset(self):
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - 10, SCREEN_HEIGHT//2 - 10, 20, 20)
        self.speed_x = BALL_SPEED * random.choice((1, -1))
        self.speed_y = BALL_SPEED * random.choice((1, -1))
        self.last_hit = None
    
    def draw(self):
        pygame.draw.ellipse(screen, self.color, self.rect)
    
    def update(self, paddle1, paddle2):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Wall collision
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1
            if sound_available:
                wall_hit_sound.play()
        
        # Paddle collision
        for paddle in [paddle1, paddle2]:
            if self.rect.colliderect(paddle.rect) and paddle != self.last_hit:
                self.last_hit = paddle
                
                # Calculate bounce angle
                relative_intersect = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height/2)
                bounce_angle = relative_intersect * (5*math.pi/12)
                
                self.speed_x = -self.speed_x * 1.05
                self.speed_y = -BALL_SPEED * math.sin(bounce_angle)
                
                self.color = NEON_BLUE if paddle == paddle1 else NEON_PINK
                if sound_available:
                    paddle_hit_sound.play()
                break

def draw_center_line():
    for y in range(0, SCREEN_HEIGHT, 30):
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 2, y, 4, 15))

def show_menu():
    screen.fill(BLACK)
    
    title = title_font.render("ULTIMATE PONG", True, NEON_BLUE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    options = [
        "1. Single Player (vs AI)",
        "2. Two Players",
        "3. Exit"
    ]
    
    for i, option in enumerate(options):
        text = font.render(option, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i*70))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "single"
                if event.key == pygame.K_2:
                    return "multi"
                if event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)

def main():
    # Game setup
    game_mode = show_menu()
    player1 = Paddle(50, SCREEN_HEIGHT//2 - 50)
    player2 = Paddle(SCREEN_WIDTH - 60, SCREEN_HEIGHT//2 - 50)
    ball = Ball()
    
    # Game state
    game_active = False
    winner = None
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_active and not winner:
                    game_active = True
                if event.key == pygame.K_r and winner:
                    # Reset game
                    player1.score = 0
                    player2.score = 0
                    ball.reset()
                    winner = None
                    game_active = False
                if event.key == pygame.K_m:
                    # Return to menu
                    game_mode = show_menu()
                    player1 = Paddle(50, SCREEN_HEIGHT//2 - 50)
                    player2 = Paddle(SCREEN_WIDTH - 60, SCREEN_HEIGHT//2 - 50)
                    ball = Ball()
                    winner = None
                    game_active = False
        
        # Game logic
        if game_active and not winner:
            # Player movement
            player1.move(pygame.K_w, pygame.K_s)
            if game_mode == "multi":
                player2.move(pygame.K_UP, pygame.K_DOWN)
            else:
                player2.ai_move(ball.rect)
            
            # Ball movement
            ball.update(player1, player2)
            
            # Scoring
            if ball.rect.left <= 0:
                player2.score += 1
                if sound_available:
                    score_sound.play()
                ball.reset()
                game_active = False
                pygame.time.set_timer(pygame.USEREVENT, 1000)
            
            if ball.rect.right >= SCREEN_WIDTH:
                player1.score += 1
                if sound_available:
                    score_sound.play()
                ball.reset()
                game_active = False
                pygame.time.set_timer(pygame.USEREVENT, 1000)
            
            # Check for winner
            if player1.score >= MAX_SCORE:
                winner = "Player 1"
                if sound_available:
                    win_sound.play()
            elif player2.score >= MAX_SCORE:
                winner = "Player 2" if game_mode == "multi" else "AI"
                if sound_available:
                    win_sound.play()
        
        # Handle delayed game reactivation
        for event in pygame.event.get(pygame.USEREVENT):
            game_active = True
            pygame.time.set_timer(pygame.USEREVENT, 0)
        
        # Drawing
        screen.fill(BLACK)
        draw_center_line()
        
        player1.draw(NEON_BLUE)
        player2.draw(NEON_PINK)
        
        if game_active or winner:
            ball.draw()
        
        # Display scores
        p1_score = font.render(str(player1.score), True, NEON_BLUE)
        p2_score = font.render(str(player2.score), True, NEON_PINK)
        screen.blit(p1_score, (SCREEN_WIDTH//4, 20))
        screen.blit(p2_score, (3*SCREEN_WIDTH//4 - p2_score.get_width(), 20))
        
        # Game messages
        if not game_active and not winner:
            msg = small_font.render("Press SPACE to Serve", True, WHITE)
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT - 50))
        
        if winner:
            win_text = title_font.render(f"{winner} WINS!", True, WHITE)
            screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, 200))
            
            restart = small_font.render("Press R to Restart or M for Menu", True, WHITE)
            screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 300))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()