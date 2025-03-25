import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 100)
PURPLE = (150, 50, 255)

# Fonts
font_small = pygame.font.Font(None, 28)
font_medium = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 72)

class Player:
    def __init__(self):
        self.width = 60
        self.height = 15
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 70
        self.speed = 6
        self.color = BLUE
        self.cooldown = 0
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw gun turret
        pygame.draw.rect(screen, YELLOW, (self.x + self.width//2 - 3, self.y - 10, 6, 10))
    
    def move(self, direction):
        if direction == "left" and self.x > 10:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.width - 10:
            self.x += self.speed
    
    def shoot(self):
        if self.cooldown <= 0:
            bullets.append(Bullet(self.x + self.width//2, self.y))
            self.cooldown = 15
        return None

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 9
        self.width = 4
        self.height = 15
        self.color = GREEN
    
    def update(self):
        self.y -= self.speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def is_off_screen(self):
        return self.y < 0

class Enemy:
    def __init__(self):
        self.radius = 22
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(30, 150)
        self.speed_x = random.choice([-3, -2, 2, 3])
        self.speed_y = 1.5
        self.color = RED
        self.health = 1
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.speed_x *= -1
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Health indicator
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius-2, 1)
    
    def reached_bottom(self):
        return self.y >= HEIGHT - 50
    
    def hit(self):
        self.health -= 1
        return self.health <= 0

# Game objects
player = Player()
enemies = [Enemy() for _ in range(3)]
bullets = []
particles = []

# Game variables
score = 0
lives = 3
level = 1
game_state = "playing"  # playing, game_over, victory
clock = pygame.time.Clock()

def reset_game():
    global player, enemies, bullets, score, lives, level, game_state
    player = Player()
    enemies = [Enemy() for _ in range(2 + level)]
    bullets = []
    game_state = "playing"

def show_message(text, color=YELLOW, size="medium"):
    if size == "large":
        font = font_large
    elif size == "small":
        font = font_small
    else:
        font = font_medium
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text_surface, text_rect)
    return text_rect

# Main game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.shoot()
            if event.key == pygame.K_r and game_state in ("game_over", "victory"):
                reset_game()
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw stars background
    for _ in range(2):
        pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
    
    if game_state == "playing":
        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")
        
        # Update player cooldown
        if player.cooldown > 0:
            player.cooldown -= 1
        
        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                bullets.remove(bullet)
        
        # Update enemies
        for enemy in enemies[:]:
            enemy.update()
            
            # Check if enemy reached bottom
            if enemy.reached_bottom():
                lives -= 1
                enemies.remove(enemy)
                enemies.append(Enemy())
                if lives <= 0:
                    game_state = "game_over"
            
            # Check bullet collisions
            for bullet in bullets[:]:
                distance = ((enemy.x - bullet.x)**2 + (enemy.y - bullet.y)**2)**0.5
                if distance < enemy.radius + 5:
                    if enemy.hit():
                        enemies.remove(enemy)
                        enemies.append(Enemy())
                        score += 10
                    bullets.remove(bullet)
                    break
        
        # Level progression
        if score >= level * 50:
            level += 1
            for _ in range(2):
                enemies.append(Enemy())
            
            # Victory condition
            if level > 3:
                game_state = "victory"
    
    # Draw game objects
    for bullet in bullets:
        bullet.draw()
    
    for enemy in enemies:
        enemy.draw()
    
    player.draw()
    
    # Draw UI
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    lives_text = font_small.render(f"Lives: {lives}", True, WHITE)
    level_text = font_small.render(f"Level: {level}", True, WHITE)
    
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 50))
    screen.blit(level_text, (20, 80))
    
    # Game over/victory screens
    if game_state == "game_over":
        show_message("GAME OVER", RED, "large")
        show_message("Press R to Restart or Q to Quit", WHITE, "small")
    
    if game_state == "victory":
        show_message("MISSION COMPLETE!", GREEN, "large")
        show_message(f"Final Score: {score}", WHITE, "medium")
        show_message("Press R to Play Again or Q to Quit", WHITE, "small")
    
    # Update display
    pygame.display.flip()
    clock.tick(60)