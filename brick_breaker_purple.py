
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


# ==========================================
# 3. POWER UP
# ==========================================
class PowerUp:
    def __init__(self, x, y, p_type):
        self.x = float(x)
        self.y = float(y)

        self.width = 30
        self.height = 20

        self.type = p_type
        self.speed = 150

        self.rect = pygame.Rect(
            int(x), int(y), self.width, self.height
        )

    def update(self, dt):
        self.y += self.speed * dt
        self.rect.topleft = (int(self.x), int(self.y))

    def display(self):
        settings = {
            "expand": (CYAN, "E"),
            "multiball": (GREEN, "M"),
            "life": (HEART_RED, "♥"),
            "fire": (FIRE_ORANGE, "F")
        }

        color, symbol = settings[self.type]

        pygame.draw.rect(
            screen, color, self.rect,
            border_radius=5
        )

        label = font.render(symbol, True, WHITE)

        screen.blit(label, (self.x + 9, self.y + 1))


# ==========================================
# 4. STRIKER
# ==========================================
class Striker:
    def __init__(self):
        self.width = 110
        self.height = 16

        self.posx = WIDTH / 2 - self.width / 2
        self.posy = HEIGHT - 50

        self.speed = 520

        self.rect = pygame.Rect(
            int(self.posx),
            int(self.posy),
            self.width,
            self.height
        )

    def update(self, direction, dt):
        self.posx += direction * self.speed * dt

        self.posx = max(
            0,
            min(WIDTH - self.width, self.posx)
        )

        self.rect.topleft = (
            int(self.posx),
            int(self.posy)
        )

    def resize(self, width):
        center = self.posx + self.width / 2

        self.width = width

        self.posx = max(
            0,
            min(WIDTH - width, center - width / 2)
        )

        self.rect = pygame.Rect(
            int(self.posx),
            int(self.posy),
            self.width,
            self.height
        )

    def display(self):
        glow = pygame.Rect(
            int(self.posx - 2),
            int(self.posy - 2),
            self.width + 4,
            self.height + 4
        )

        pygame.draw.rect(
            screen, PURPLE_LIGHT,
            glow, border_radius=8, width=1
        )

        pygame.draw.rect(
            screen, PURPLE_PRIMARY,
            self.rect, border_radius=6
        )

        pygame.draw.rect(
            screen, WHITE,
            (
                int(self.posx + 12),
                int(self.posy + 4),
                max(1, self.width - 24),
                3
            ),
            border_radius=2
        )


# ==========================================
# 5. BLOCK
# ==========================================
class Block:
    def __init__(self, x, y, color, is_life=False):
        self.posx = x
        self.posy = y

        self.width = 48
        self.height = 18

        self.is_life_block = is_life

        self.color = HEART_RED if is_life else color

        self.health = (
            200 if color == GOLD and not is_life else 100
        )

        self.rect = pygame.Rect(
            x, y, self.width, self.height
        )

    def hit(self):
        self.health -= 100

    def display(self):
        if self.health <= 0:
            return

        border = (
            WHITE
            if self.health > 100 or self.is_life_block
            else BLACK
        )

        pygame.draw.rect(
            screen, self.color,
            self.rect, border_radius=4
        )

        pygame.draw.rect(
            screen, border,
            self.rect, 2, border_radius=4
        )

        if self.is_life_block:
            label = font.render("♥", True, WHITE)
            screen.blit(label, (self.posx + 17, self.posy - 1))

        elif self.health > 100:
            label = font.render("2X", True, WHITE)
            screen.blit(label, (self.posx + 15, self.posy))


# ==========================================
# 6. BALL
# ==========================================
class Ball:
    def __init__(self, x, y, speed):
        self.posx = float(x)
        self.posy = float(y)

        self.radius = 8
        self.speed = speed

        self.xFac = random.choice([-0.65, 0.65])
        self.yFac = -math.sqrt(1 - self.xFac ** 2)

        self.is_fire = False

        self.rect = pygame.Rect(
            0, 0,
            self.radius * 2,
            self.radius * 2
        )

        self.update_rect()

    def update_rect(self):
        self.rect.center = (
            round(self.posx),
            round(self.posy)
        )

    def display(self):
        color = FIRE_ORANGE if self.is_fire else WHITE
        core = (255, 255, 0) if self.is_fire else CYAN

        pygame.draw.circle(
            screen, color,
            (round(self.posx), round(self.posy)),
            self.radius
        )

        pygame.draw.circle(
            screen, core,
            (round(self.posx), round(self.posy)),
            self.radius // 2
        )


# ==========================================
# 7. BLOCK GENERATOR
# ==========================================
def populateBlocks():
    blocks = []

    positions = [
        (x, y)
        for x in range(30, WIDTH - 48, 60)
        for y in range(45, 190, 30)
    ]

    heart_positions = set(
        random.sample(positions, MAX_HEART_BLOCKS)
    )

    for x, y in positions:

        if (x, y) in heart_positions:
            blocks.append(Block(x, y, HEART_RED, True))

        else:
            color = random.choice([
                PURPLE_PRIMARY,
                PURPLE_LIGHT,
                MAGENTA,
                GOLD
            ])

            blocks.append(Block(x, y, color))

    return blocks


# ==========================================
# 8. SPAWN POWER UP
# ==========================================
def spawn_powerup(powerups, x, y, p_type):
    if len(powerups) >= MAX_POWERUPS:
        return

    powerups.append(PowerUp(x, y, p_type))


# ==========================================
# 9. GAME OVER
# ==========================================
def gameOverScreen(score, level):
    while True:
        screen.fill(BLACK)

        title = font_large.render(
            "GAME OVER", True, RED
        )

        score_text = font.render(
            f"Final Score: {score}", True, WHITE
        )

        level_text = font.render(
            f"Level Reached: {level}", True, GOLD
        )

        restart = font.render(
            "SPACE: PLAY AGAIN", True, CYAN
        )

        exit_text = font.render(
            "ESC: EXIT", True, WHITE
        )

        screen.blit(
            title,
            (WIDTH // 2 - title.get_width() // 2, 145)
        )

        screen.blit(
            score_text,
            (WIDTH // 2 - score_text.get_width() // 2, 215)
        )

        screen.blit(
            level_text,
            (WIDTH // 2 - level_text.get_width() // 2, 245)
        )

        screen.blit(
            restart,
            (WIDTH // 2 - restart.get_width() // 2, 310)
        )

        screen.blit(
            exit_text,
            (WIDTH // 2 - exit_text.get_width() // 2, 340)
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    return True

                if event.key == pygame.K_ESCAPE:
                    return False

        clock.tick(FPS)


# ==========================================
# 10. MAIN GAME
# ==========================================
def main():

    lives = INITIAL_LIVES
    score = 0
    level = 1

    striker = Striker()

    balls = [
        Ball(WIDTH // 2, HEIGHT // 2, 300)
    ]

    blocks = populateBlocks()

    particles = []
    powerups = []

    expand_timer = 0.0
    fire_timer = 0.0

    direction = 0
    paused = False

    running = True

    while running:

        dt = min(clock.tick(FPS) / 1000.0, 0.05)


        # ==================================
        # EVENTS
        # ==================================
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_LEFT:
                    direction = -1

                elif event.key == pygame.K_RIGHT:
                    direction = 1

                elif event.key == pygame.K_p:
                    paused = not paused

            if event.type == pygame.KEYUP:

                if event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT
                ):
                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_LEFT]:
                        direction = -1
                    elif keys[pygame.K_RIGHT]:
                        direction = 1
                    else:
                        direction = 0

        if not running:
            break

        if paused:
            pause_text = font_large.render(
                "PAUSED", True, CYAN
            )

            screen.fill(BLACK)

            screen.blit(
                pause_text,
                (
                    WIDTH // 2 - pause_text.get_width() // 2,
                    HEIGHT // 2 - 20
                )
            )

            pygame.display.flip()
            continue

        # ==================================
        # TIMERS
        # ==================================
        if expand_timer > 0:

            expand_timer = max(0, expand_timer - dt)

            if expand_timer == 0:
                striker.resize(110)

        if fire_timer > 0:

            fire_timer = max(0, fire_timer - dt)

            if fire_timer == 0:

                for ball in balls:
                    ball.is_fire = False

        # ==================================
        # LEVEL UP
        # ==================================
        if not blocks:

            level += 1

            blocks = populateBlocks()

            balls = [
                Ball(
                    WIDTH // 2,
                    HEIGHT // 2,
                    min(300 + (level - 1) * 25, 520)
                )
            ]

            powerups.clear()

            fire_timer = 0
            expand_timer = 0
            striker.resize(110)

        # ==================================
        # STRIKER
        # ==================================
        striker.update(direction, dt)

        # ==================================
        # POWER UPS
        # ==================================
        for p in powerups[:]:

            p.update(dt)

            if striker.rect.colliderect(p.rect):

                if p.type == "expand":
                    striker.resize(160)
                    expand_timer = 10.0

                elif p.type == "multiball":

                    original_balls = balls[:]

                    for b in original_balls:

                        if len(balls) >= MAX_BALLS:
                            break

                        new_ball = Ball(
                            b.posx,
                            b.posy,
                            b.speed
                        )

                        new_ball.xFac = -b.xFac
                        new_ball.yFac = b.yFac
                        new_ball.is_fire = b.is_fire

                        balls.append(new_ball)

                elif p.type == "life":

                    if lives < MAX_LIVES:
                        lives += 1

                elif p.type == "fire":

                    for b in balls:
                        b.is_fire = True

                    fire_timer = 7.0

                powerups.remove(p)

            elif p.y > HEIGHT:
                powerups.remove(p)

        # ==================================
        # BALL MOVEMENT AND COLLISION
        # ==================================
        for ball in balls[:]:

            max_distance = ball.speed * dt

            steps = max(
                1,
                math.ceil(max_distance / 4)
            )

            step_dt = dt / steps

            lost = False

            for _ in range(steps):

                previous = ball.rect.copy()

                dx = ball.xFac * ball.speed * step_dt
                dy = ball.yFac * ball.speed * step_dt

                # Horizontal movement
                ball.posx += dx

                if ball.posx <= ball.radius:
                    ball.posx = ball.radius
                    ball.xFac = abs(ball.xFac)

                elif ball.posx >= WIDTH - ball.radius:
                    ball.posx = WIDTH - ball.radius
                    ball.xFac = -abs(ball.xFac)

                # Vertical movement
                ball.posy += dy

                if ball.posy <= ball.radius:
                    ball.posy = ball.radius
                    ball.yFac = abs(ball.yFac)

                ball.update_rect()

                # Ball lost
                if ball.posy - ball.radius > HEIGHT:
                    lost = True
                    break

                # Paddle collision
                if (
                    ball.yFac > 0
                    and ball.rect.colliderect(striker.rect)
                    and previous.bottom <= striker.rect.top + 5
                ):

                    ball.posy = striker.posy - ball.radius

                    offset = (
                        ball.posx -
                        (striker.posx + striker.width / 2)
                    ) / (striker.width / 2)

                    ball.xFac = max(
                        -0.9,
                        min(0.9, offset)
                    )

                    if abs(ball.xFac) < 0.12:
                        ball.xFac = random.choice([-0.12, 0.12])

                    ball.yFac = -math.sqrt(
                        1 - ball.xFac ** 2
                    )

                    ball.update_rect()

                # Block collision
                for block in blocks[:]:

                    if not ball.rect.colliderect(block.rect):
                        continue

                    if not ball.is_fire:

                        if (
                            previous.bottom <= block.rect.top
                            and ball.yFac > 0
                        ):

                            ball.posy = block.rect.top - ball.radius
                            ball.yFac = -abs(ball.yFac)

                        elif (
                            previous.top >= block.rect.bottom
                            and ball.yFac < 0
                        ):

                            ball.posy = block.rect.bottom + ball.radius
                            ball.yFac = abs(ball.yFac)

                        elif (
                            previous.right <= block.rect.left
                            and ball.xFac > 0
                        ):

                            ball.posx = block.rect.left - ball.radius
                            ball.xFac = -abs(ball.xFac)

                        elif (
                            previous.left >= block.rect.right
                            and ball.xFac < 0
                        ):

                            ball.posx = block.rect.right + ball.radius
                            ball.xFac = abs(ball.xFac)

                        else:
                            ball.yFac *= -1

                        block.hit()

                    else:
                        block.health = 0

                    ball.update_rect()

                    if block.health <= 0:

                        create_particles(
                            particles,
                            block.posx + block.width // 2,
                            block.posy + block.height // 2,
                            block.color
                        )

                        if block.is_life_block:

                            spawn_powerup(
                                powerups,
                                block.posx + 9,
                                block.posy,
                                "life"
                            )

                        elif random.random() < 0.25:

                            p_type = random.choice([
                                "expand",
                                "multiball",
                                "fire"
                            ])

                            spawn_powerup(
                                powerups,
                                block.posx + 9,
                                block.posy,
                                p_type
                            )

                        blocks.remove(block)

                        score += 40 * level

                    break

            if lost:
                balls.remove(ball)
