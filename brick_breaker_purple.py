
import pygame
import random
import math

pygame.init()

# ==========================================
# 1. GAME CONFIGURATION
# ==========================================
WIDTH, HEIGHT = 600, 500
FPS = 60

INITIAL_LIVES = 3
MAX_LIVES = 5
MAX_BALLS = 5
MAX_PARTICLES = 350
MAX_POWERUPS = 10
MAX_HEART_BLOCKS = 2

BLACK = (10, 6, 18)
STAR_COLOR = (130, 100, 180)
WHITE = (255, 255, 255)
PURPLE_PRIMARY = (186, 85, 211)
PURPLE_LIGHT = (221, 160, 221)
MAGENTA = (255, 0, 128)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
GREEN = (0, 255, 120)
HEART_RED = (255, 60, 90)
FIRE_ORANGE = (255, 140, 0)
RED = (255, 50, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Purple Arcade - Ultimate Smooth Edition")

clock = pygame.time.Clock()

font = pygame.font.SysFont("segoeui", 15, bold=True)
font_large = pygame.font.SysFont("segoeui", 34, bold=True)

# Static background
stars = [
    (random.randint(0, WIDTH),
     random.randint(0, HEIGHT - 40),
     random.randint(1, 2))
    for _ in range(60)
]


# ==========================================
# 2. PARTICLES
# ==========================================
class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color

        self.size = random.randint(2, 4)

        angle = random.uniform(0, math.tau)
        speed = random.uniform(70, 220)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = 0.5
        self.max_life = 0.5

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def display(self):
        if self.life <= 0:
            return

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            max(1, self.size)
        )


def create_particles(particles, x, y, color):
    available = MAX_PARTICLES - len(particles)
    count = min(12, available)

    for _ in range(count):
        particles.append(Particle(x, y, color))
