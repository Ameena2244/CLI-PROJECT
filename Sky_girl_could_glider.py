import pygame
import random
import math
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)  # Sky blue
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class Particle:
    def __init__(self, x, y, color, size, velocity_x, velocity_y, life):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = life
        self.max_life = life
        self.alpha = 255
    
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.life -= 1
        self.alpha = int(255 * (self.life / self.max_life))
        self.size = max(1, int(self.size * (self.life / self.max_life)))
        return self.life > 0
    
    def draw(self, screen):
        if self.alpha > 0:
            # Create a surface with per-pixel alpha
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(particle_surface, (self.x - self.size, self.y - self.size))

class SkyGirl:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 48
        self.velocity_y = 0
        self.gravity = 0.5
        self.flap_power = -8
        self.max_fall_speed = 10
        
        # Animation
        self.flap_animation = 0
        self.wing_angle = 0
        self.is_flapping = False
        self.flap_timer = 0
        
        # Create a simple sprite representation
        self.create_sprite()
    
    def create_sprite(self):
        """Create a simple sprite surface for the sky girl"""
        self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Body (pink dress)
        pygame.draw.ellipse(self.sprite, PINK, (16, 20, 16, 20))
        
        # Head
        pygame.draw.circle(self.sprite, (255, 220, 177), (24, 16), 8)
        
        # Hair
        pygame.draw.circle(self.sprite, (139, 69, 19), (24, 12), 10)
        
        # Eyes
        pygame.draw.circle(self.sprite, BLACK, (21, 14), 2)
        pygame.draw.circle(self.sprite, BLACK, (27, 14), 2)
        
        # Wings (will be drawn separately for animation)
        self.wing_color = (255, 255, 255, 180)
    
    def flap(self):
        """Make the girl flap upward"""
        self.velocity_y = self.flap_power
        self.is_flapping = True
        self.flap_timer = 10
    
    def update(self):
        """Update girl's position and animation"""
        # Apply gravity
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed
        
        # Update position
        self.y += self.velocity_y
        
        # Keep on screen
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
        
        # Update animation
        if self.flap_timer > 0:
            self.flap_timer -= 1
            self.wing_angle = math.sin(self.flap_timer * 0.5) * 30
        else:
            self.is_flapping = False
            self.wing_angle = math.sin(pygame.time.get_ticks() * 0.01) * 15
    
    def draw(self, screen):
        """Draw the sky girl with animated wings"""
        # Draw wings behind the body
        wing_surface = pygame.Surface((60, 30), pygame.SRCALPHA)
        
        # Left wing
        wing_points_left = [
            (15, 15),
            (5, 5 + self.wing_angle),
            (0, 15),
            (5, 25 - self.wing_angle),
            (15, 15)
        ]
        pygame.draw.polygon(wing_surface, self.wing_color, wing_points_left)
        
        # Right wing
        wing_points_right = [
            (45, 15),
            (55, 5 + self.wing_angle),
            (60, 15),
            (55, 25 - self.wing_angle),
            (45, 15)
        ]
        pygame.draw.polygon(wing_surface, self.wing_color, wing_points_right)
        
        # Add wing glow effect
        if self.is_flapping:
            glow_surface = pygame.Surface((60, 30), pygame.SRCALPHA)
            pygame.draw.polygon(glow_surface, (255, 255, 255, 100), wing_points_left)
            pygame.draw.polygon(glow_surface, (255, 255, 255, 100), wing_points_right)
            screen.blit(glow_surface, (self.x - 6, self.y + 5))
        
        screen.blit(wing_surface, (self.x - 6, self.y + 5))
        
        # Draw the main sprite
        screen.blit(self.sprite, (self.x, self.y))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x + 8, self.y + 8, self.width - 16, self.height - 16)

class Cloud:
    def __init__(self, x, y, cloud_type="normal"):
        self.x = x
        self.y = y
        self.type = cloud_type
        self.speed = random.uniform(2, 4)
        
        if cloud_type == "storm":
            self.width = random.randint(80, 120)
            self.height = random.randint(50, 70)
            self.color = DARK_GRAY
        else:
            self.width = random.randint(60, 100)
            self.height = random.randint(40, 60)
            self.color = WHITE
        
        # Lightning animation for storm clouds
        self.lightning_timer = 0
        self.show_lightning = False
    
    def update(self, game_speed):
        """Update cloud position"""
        self.x -= self.speed * game_speed
        
        # Lightning animation for storm clouds
        if self.type == "storm":
            self.lightning_timer += 1
            if self.lightning_timer > 60:
                self.show_lightning = random.random() < 0.1
                if self.show_lightning:
                    self.lightning_timer = 0
    
    def draw(self, screen):
        """Draw the cloud"""
        # Draw cloud body
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, self.color, (self.x + 20, self.y - 10, self.width - 20, self.height - 10))
        pygame.draw.ellipse(screen, self.color, (self.x + 10, self.y + 10, self.width - 30, self.height - 20))
        
        # Draw lightning for storm clouds
        if self.type == "storm" and self.show_lightning:
            lightning_x = self.x + self.width // 2
            lightning_y = self.y + self.height
            pygame.draw.lines(screen, YELLOW, False, [
                (lightning_x, lightning_y),
                (lightning_x - 10, lightning_y + 20),
                (lightning_x + 5, lightning_y + 20),
                (lightning_x - 5, lightning_y + 40)
            ], 3)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(8, 12)
        self.speed = random.uniform(1, 3)
        self.glow_timer = 0
        self.collected = False
    
    def update(self, game_speed):
        """Update star position"""
        self.x -= self.speed * game_speed
        self.glow_timer += 0.2
    
    def draw(self, screen):
        """Draw the glowing star"""
        if self.collected:
            return
            
        # Glow effect
        glow_size = self.size + int(math.sin(self.glow_timer) * 3)
        glow_surface = pygame.Surface((glow_size * 4, glow_size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 0, 50), (glow_size * 2, glow_size * 2), glow_size * 2)
        screen.blit(glow_surface, (self.x - glow_size * 2, self.y - glow_size * 2))
        
        # Star shape
        star_points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                radius = self.size
            else:
                radius = self.size // 2
            
            x = self.x + math.cos(angle) * radius
            y = self.y + math.sin(angle) * radius
            star_points.append((x, y))
        
        pygame.draw.polygon(screen, GOLD, star_points)
        pygame.draw.polygon(screen, YELLOW, star_points, 2)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.speed = random.uniform(3, 5)
        self.wing_flap = 0
        self.vertical_movement = random.uniform(0.5, 1.5)
        self.vertical_offset = 0
    
    def update(self, game_speed):
        """Update bird position"""
        self.x -= self.speed * game_speed
        self.wing_flap += 0.3
        self.vertical_offset = math.sin(self.wing_flap) * self.vertical_movement
    
    def draw(self, screen):
        """Draw the bird"""
        # Bird body
        bird_y = self.y + self.vertical_offset
        pygame.draw.ellipse(screen, BLACK, (self.x, bird_y, self.width, self.height))
        
        # Wings
        wing_offset = int(math.sin(self.wing_flap * 2) * 5)
        pygame.draw.ellipse(screen, DARK_GRAY, (self.x - 5, bird_y - wing_offset, 15, 10))
        pygame.draw.ellipse(screen, DARK_GRAY, (self.x + 20, bird_y - wing_offset, 15, 10))
        
        # Beak
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + self.width, bird_y + self.height // 2),
            (self.x + self.width + 8, bird_y + self.height // 2 - 3),
            (self.x + self.width + 8, bird_y + self.height // 2 + 3)
        ])
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y + self.vertical_offset, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sky Girl - Cloud Glider")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        
        # Game objects
        self.sky_girl = SkyGirl(100, SCREEN_HEIGHT // 2)
        self.clouds = []
        self.stars = []
        self.birds = []
        self.particles = []
        
        # Game variables
        self.score = 0
        self.game_speed = 1.0
        self.spawn_timer = 0
        self.background_offset = 0
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Background clouds for decoration
        self.bg_clouds = []
        for _ in range(8):
            self.bg_clouds.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(50, SCREEN_HEIGHT - 100),
                'size': random.randint(40, 80),
                'speed': random.uniform(0.2, 0.8)
            })
    
    def reset_game(self):
        """Reset game to initial state"""
        self.sky_girl = SkyGirl(100, SCREEN_HEIGHT // 2)
        self.clouds.clear()
        self.stars.clear()
        self.birds.clear()
        self.particles.clear()
        self.score = 0
        self.game_speed = 1.0
        self.spawn_timer = 0
    
    def spawn_objects(self):
        """Spawn clouds, stars, and birds"""
        self.spawn_timer += 1
        
        # Spawn clouds
        if self.spawn_timer % max(60, 120 - int(self.score / 10)) == 0:
            cloud_type = "storm" if random.random() < 0.3 else "normal"
            y_pos = random.randint(50, SCREEN_HEIGHT - 150)
            self.clouds.append(Cloud(SCREEN_WIDTH, y_pos, cloud_type))
        
        # Spawn stars
        if self.spawn_timer % max(30, 80 - int(self.score / 5)) == 0:
            y_pos = random.randint(50, SCREEN_HEIGHT - 50)
            self.stars.append(Star(SCREEN_WIDTH, y_pos))
        
        # Spawn birds
        if self.spawn_timer % max(120, 200 - int(self.score / 8)) == 0:
            y_pos = random.randint(100, SCREEN_HEIGHT - 200)
            self.birds.append(Bird(SCREEN_WIDTH, y_pos))
    
    def create_star_particles(self, x, y):
        """Create particle effect when collecting a star"""
        for _ in range(15):
            particle = Particle(
                x + random.randint(-10, 10),
                y + random.randint(-10, 10),
                random.choice([GOLD, YELLOW, WHITE]),
                random.randint(2, 6),
                random.uniform(-3, 3),
                random.uniform(-3, 3),
                random.randint(20, 40)
            )
            self.particles.append(particle)
    
    def update_game(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Update sky girl
        self.sky_girl.update()
        
        # Update game speed based on score
        self.game_speed = 1.0 + (self.score / 100)
        
        # Spawn objects
        self.spawn_objects()
        
        # Update clouds
        for cloud in self.clouds[:]:
            cloud.update(self.game_speed)
            if cloud.x < -cloud.width:
                self.clouds.remove(cloud)
            
            # Check collision with sky girl
            if self.sky_girl.get_rect().colliderect(cloud.get_rect()):
                self.state = GameState.GAME_OVER
        
        # Update stars
        for star in self.stars[:]:
            star.update(self.game_speed)
            if star.x < -star.size:
                self.stars.remove(star)
            
            # Check collection
            if not star.collected and self.sky_girl.get_rect().colliderect(star.get_rect()):
                star.collected = True
                self.score += 10
                self.create_star_particles(star.x, star.y)
                self.stars.remove(star)
        
        # Update birds
        for bird in self.birds[:]:
            bird.update(self.game_speed)
            if bird.x < -bird.width:
                self.birds.remove(bird)
            
            # Check collision with sky girl
            if self.sky_girl.get_rect().colliderect(bird.get_rect()):
                self.state = GameState.GAME_OVER
        
        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
        
        # Update background
        self.background_offset -= self.game_speed
        if self.background_offset <= -100:
            self.background_offset = 0
    
    def draw_background(self):
        """Draw scrolling sky background"""
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(135 + (70 * color_ratio))
            g = int(206 + (50 * color_ratio))
            b = int(235 + (20 * color_ratio))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Background clouds
        for cloud in self.bg_clouds:
            cloud['x'] -= cloud['speed'] * self.game_speed
            if cloud['x'] < -cloud['size']:
                cloud['x'] = SCREEN_WIDTH + random.randint(0, 200)
                cloud['y'] = random.randint(50, SCREEN_HEIGHT - 100)
            
            # Draw background cloud
            alpha_surface = pygame.Surface((cloud['size'], cloud['size'] // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(alpha_surface, (255, 255, 255, 100), 
                              (0, 0, cloud['size'], cloud['size'] // 2))
            self.screen.blit(alpha_surface, (cloud['x'], cloud['y']))
    
    def draw_menu(self):
        """Draw main menu"""
        self.draw_background()
        
        # Title
        title = self.font_large.render("Sky Girl - Cloud Glider", True, WHITE)
        title_shadow = self.font_large.render("Sky Girl - Cloud Glider", True, BLACK)
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 152))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Instructions
        instructions = [
            "Press SPACE to flap and stay airborne",
            "Avoid storm clouds and birds",
            "Collect glowing stars for points",
            "Game gets faster as your score increases!",
            "",
            "Press SPACE to start flying!"
        ]
        
        y_offset = 300
        for instruction in instructions:
            if instruction:
                text = self.font_small.render(instruction, True, WHITE)
                text_shadow = self.font_small.render(instruction, True, BLACK)
                self.screen.blit(text_shadow, (SCREEN_WIDTH//2 - text.get_width()//2 + 1, y_offset + 1))
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 35
        
        # Draw a demo sky girl
        demo_girl = SkyGirl(SCREEN_WIDTH//2 - 24, 250)
        demo_girl.wing_angle = math.sin(pygame.time.get_ticks() * 0.01) * 20
        demo_girl.draw(self.screen)
    
    def draw_game(self):
        """Draw game screen"""
        self.draw_background()
        
        # Draw game objects
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        for star in self.stars:
            star.draw(self.screen)
        
        for bird in self.birds:
            bird.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw sky girl
        self.sky_girl.draw(self.screen)
        
        # Draw UI
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_shadow = self.font_medium.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_shadow, (21, 21))
        self.screen.blit(score_text, (20, 20))
        
        speed_text = self.font_small.render(f"Speed: {self.game_speed:.1f}x", True, WHITE)
        self.screen.blit(speed_text, (20, 60))
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_background()
        
        # Game over text
        game_over = self.font_large.render("Game Over!", True, RED)
        game_over_shadow = self.font_large.render("Game Over!", True, BLACK)
        self.screen.blit(game_over_shadow, (SCREEN_WIDTH//2 - game_over.get_width()//2 + 2, 252))
        self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 250))
        
        # Final score
        final_score = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        final_score_shadow = self.font_medium.render(f"Final Score: {self.score}", True, BLACK)
        self.screen.blit(final_score_shadow, (SCREEN_WIDTH//2 - final_score.get_width()//2 + 1, 321))
        self.screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, 320))
        
        # Restart instructions
        restart_text = self.font_small.render("Press SPACE to play again or ESC to return to menu", True, WHITE)
        restart_shadow = self.font_small.render("Press SPACE to play again or ESC to return to menu", True, BLACK)
        self.screen.blit(restart_shadow, (SCREEN_WIDTH//2 - restart_text.get_width()//2 + 1, 401))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 400))
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                        self.reset_game()
                    elif self.state == GameState.PLAYING:
                        self.sky_girl.flap()
                    elif self.state == GameState.GAME_OVER:
                        self.state = GameState.PLAYING
                        self.reset_game()
                
                elif event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING or self.state == GameState.GAME_OVER:
                        self.state = GameState.MENU
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update_game()
            
            # Draw current state
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
