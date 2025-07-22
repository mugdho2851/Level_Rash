import pygame
import random
import math
import os
from pygame import gfxdraw

# Initialize
pygame.init()
pygame.mixer.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Neon Racer Extreme v2.0")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 0, 128)
ROAD_COLOR = (30, 30, 40)

# Load Assets
def load_image(name, scale=1):
    try:
        img = pygame.image.load(f"assets/{name}").convert_alpha()
        return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    except:
        print(f"Missing asset: {name}")
        return None

# Load all game assets
car_img = load_image("car.png", 0.15)  # Your downloaded car image
enemy_imgs = [load_image(f"enemy_{i}.png", 0.15) for i in range(1,4)]  # Multiple enemy cars
road_img = load_image("road.png")  # Optional road texture

# Sound Effects
try:
    engine_sound = pygame.mixer.Sound("assets/engine.wav")
    crash_sound = pygame.mixer.Sound("assets/crash.wav")
    engine_sound.play(-1, fade_ms=2000)  # Loop engine sound
except:
    print("Sound files missing - running in silent mode")

# Particle System
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2,5)
        self.life = 100
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, math.pi*2)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.size *= 0.95
        return self.life > 0
        
    def draw(self, surface):
        alpha = min(255, self.life * 2.55)
        color = (*self.color[:3], int(alpha))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

# Enhanced Player Class
class Player:
    def __init__(self):
        self.x = screen_width // 2
        self.y = screen_height - 120
        self.speed = 5
        self.img = car_img
        self.width = car_img.get_width() if car_img else 50
        self.height = car_img.get_height() if car_img else 80
        self.particles = []
        self.nitro = False
        
    def draw(self, surface):
        if self.img:
            surface.blit(self.img, (self.x - self.width//2, self.y - self.height//2))
        else:
            pygame.draw.rect(surface, NEON_BLUE, (self.x, self.y, self.width, self.height))
        
        # Draw particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            else:
                particle.draw(surface)
                
        # Add exhaust particles
        if random.random() < 0.3:
            particle_color = (255, 100, 0) if self.nitro else (200, 200, 200)
            self.particles.append(Particle(
                self.x + random.randint(-10,10),
                self.y + self.height//2,
                particle_color
            ))

# Game Manager
class Game:
    def __init__(self):
        self.player = Player()
        self.score = 0
        self.road_offset = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_small = pygame.font.Font(None, 36)
        
    def draw_road(self):
        # Parallax scrolling road
        self.road_offset = (self.road_offset + 2) % screen_height
        if road_img:
            screen.blit(road_img, (0, self.road_offset - screen_height))
            screen.blit(road_img, (0, self.road_offset))
        else:
            pygame.draw.rect(screen, ROAD_COLOR, (0, 0, screen_width, screen_height))
            for i in range(-1, 2):
                pygame.draw.rect(screen, (50,50,60), (100, self.road_offset + i*screen_height, screen_width-200, screen_height))

    def draw_neon_text(self, text, font, color, pos, glow=True):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=pos)
        
        if glow:
            for i in range(1, 4):
                glow_surf = font.render(text, True, (*color[:3], 50//i))
                glow_rect = glow_surf.get_rect(center=(pos[0], pos[1]+i))
                screen.blit(glow_surf, glow_rect)
        
        screen.blit(text_surf, text_rect)

# Main Game Loop
def main():
    game = Game()
    running = True
    
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Game Logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: game.player.x = max(150, game.player.x - game.player.speed)
        if keys[pygame.K_RIGHT]: game.player.x = min(screen_width-150, game.player.x + game.player.speed)
        if keys[pygame.K_SPACE]: game.player.nitro = True
        
        # Drawing
        screen.fill(BLACK)
        game.draw_road()
        game.player.draw(screen)
        
        # UI Elements
        game.draw_neon_text(f"SCORE: {game.score}", game.font_small, NEON_BLUE, (screen_width//2, 30))
        game.draw_neon_text("NITRO READY!" if game.player.nitro else "", game.font_small, NEON_PINK, (screen_width//2, 70))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()