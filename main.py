import pygame
import os
import random

# Initialize pygame and mixer for sound
pygame.init()  # Initialize all pygame modules
pygame.mixer.init()  # Initialize mixer for sound

# Constants
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load and resize images for different spaceship types
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
RED_SPACE_SHIP = pygame.transform.scale(RED_SPACE_SHIP, (50, 50))  # Resize spaceship to 50x50

GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
GREEN_SPACE_SHIP = pygame.transform.scale(GREEN_SPACE_SHIP, (50, 50))  # Resize spaceship to 50x50

BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
BLUE_SPACE_SHIP = pygame.transform.scale(BLUE_SPACE_SHIP, (50, 50))  # Resize spaceship to 50x50

YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
YELLOW_SPACE_SHIP = pygame.transform.scale(YELLOW_SPACE_SHIP, (50, 50))  # Resize spaceship to 50x50

# Lasers with glow effect
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
RED_LASER = pygame.transform.scale(RED_LASER, (10, 30))  # Resize laser to 10x30

GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
GREEN_LASER = pygame.transform.scale(GREEN_LASER, (10, 30))  # Resize laser to 10x30

BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
BLUE_LASER = pygame.transform.scale(BLUE_LASER, (10, 30))  # Resize laser to 10x30

YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
YELLOW_LASER = pygame.transform.scale(YELLOW_LASER, (10, 30))  # Resize laser to 10x30

# Background animation (parallax effect)
BG = pygame.image.load(os.path.join("assets", "background-black.png"))
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))  # Resize background to fit the screen
BG_SCROLL = 0

# Explosion particles
EXPLOSION_PARTICLES = []

# Load sounds
laser_sound = pygame.mixer.Sound(os.path.join("assets", "laser_sound.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join("assets", "explosion_sound.wav"))

# Power-up images (resize power-ups)
SHIELD_POWERUP = pygame.image.load(os.path.join("assets", "shield_powerup.png"))
SHIELD_POWERUP = pygame.transform.scale(SHIELD_POWERUP, (30, 30))  # Resize shield power-up to 30x30

HEALTH_PACK = pygame.image.load(os.path.join("assets", "health_pack.png"))
HEALTH_PACK = pygame.transform.scale(HEALTH_PACK, (30, 30))  # Resize health pack to 30x30

# Particle class for explosions
class Particle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.alpha = 255
        self.vel = random.randint(1, 3)

    def move(self):
        self.y -= self.vel
        self.alpha -= 5  # Fade the particles
        self.radius += 1  # Expand the particles

    def draw(self, window):
        if self.alpha > 0:
            pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)
            self.alpha = max(self.alpha, 0)
            self.color = (self.color[0], self.color[1], self.color[2], self.alpha)
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            surface.set_alpha(self.alpha)
            pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius)
            window.blit(surface, (self.x - self.radius, self.y - self.radius))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.anim_frame = 0  # Frame for animation
        self.shield = False  # Start with no shield

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        if self.shield:
            pygame.draw.circle(window, (0, 0, 255), (self.x + self.get_width() // 2, self.y + self.get_height() // 2), 30, 2)  # Draw shield effect
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
                # Play explosion sound when enemy is hit
                explosion_sound.play()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            # Play laser sound when player shoots
            laser_sound.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def animate(self):
        # No animation frames for static image ships
        pass

    def activate_shield(self):
        self.shield = True
        pygame.time.set_timer(pygame.USEREVENT, 5000)  # Shield lasts for 5 seconds


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Power-up class for Shield and Health Pack
class PowerUp:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_
        self.image = SHIELD_POWERUP if type_ == "shield" else HEALTH_PACK
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def move(self, vel):
        self.y += vel

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)
    power_ups = []  # List to store power-ups

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        global BG_SCROLL
        WIN.blit(BG, (0, BG_SCROLL))  # Moving the background down
        WIN.blit(BG, (0, BG_SCROLL - HEIGHT))  # Repeat background for parallax effect
        BG_SCROLL += 1  # Move background

        if BG_SCROLL >= HEIGHT:
            BG_SCROLL = 0

        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for power_up in power_ups:
            power_up.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

            # Spawn Power-ups after each level
            if random.random() < 0.5:
                power_up_type = random.choice(["shield", "health"])
                power_up = PowerUp(random.randrange(50, WIDTH-100), -50, power_up_type)
                power_ups.append(power_up)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        # Check for collisions with power-ups
        for power_up in power_ups[:]:
            power_up.move(1)
            if collide(player, power_up):
                if power_up.type == "shield":
                    player.activate_shield()  # Activate shield power-up
                elif power_up.type == "health":
                    player.health = min(player.health + 30, player.max_health)  # Heal player
                power_ups.remove(power_up)

        player.move_lasers(-laser_vel, enemies)

# Run the game
main()
