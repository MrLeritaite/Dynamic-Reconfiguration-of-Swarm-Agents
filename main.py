import pygame
import sys
import math


class Player:
    def __init__(self, player_width, player_height, player_x, player_y, player_speed):
        self.rotation_angle = None
        self.width = player_width
        self.height = player_height
        self.position_x = player_x
        self.position_y = player_y
        self.player_speed = player_speed

    def move(self, dx, dy):
        self.position_x += dx * self.player_speed
        self.position_y += dy * self.player_speed
        self.position_x = max(0, min(self.position_x, 1024 - self.width))
        self.position_y = max(0, min(self.position_y, 1024 - self.height))

    def rotate(self, angle):
        self.rotation_angle = angle

    def draw(self, screen):
        rotated_player = pygame.transform.rotate(pygame.Surface((self.width, self.height)),
                                                 self.rotation_angle)
        screen.blit(rotated_player, (self.position_x, self.position_y))


class Map:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path).convert()

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Cone:
    def __init__(self, cone_length, cone_angle):
        self.length = cone_length
        self.cone_angle = cone_angle
        self.color = (89, 86, 82)

    def draw(self, screen, player_x, player_y, player_width, rotation_angle):
        player_center_x = player_x + player_width // 2
        player_center_y = player_y + player_height // 2

        if player_dx != 0 or player_dy != 0:
            rotation_angle = math.degrees(math.atan2(-player_dy, player_dx))
        else:
            rotation_angle = math.degrees(math.atan2(-last_movement[1], last_movement[0]))

        cone_front_angle = math.radians(180 - cone_angle + rotation_angle)
        cone_front_x = player_center_x + cone_length * math.cos(cone_front_angle)
        cone_front_y = player_center_y - cone_length * math.sin(cone_front_angle)

        cone_front_end_angle = math.radians(180 + cone_angle + rotation_angle)
        cone_front_end_x = player_center_x + cone_length * math.cos(cone_front_end_angle)
        cone_front_end_y = player_center_y - cone_length * math.sin(cone_front_end_angle)

        cone_back_angle = math.radians(0 + cone_angle + rotation_angle)
        cone_back_x = player_center_x + cone_length * math.cos(cone_back_angle)
        cone_back_y = player_center_y - cone_length * math.sin(cone_back_angle)

        cone_back_end_angle = math.radians(0 - cone_angle + rotation_angle)
        cone_back_end_x = player_center_x + cone_length * math.cos(cone_back_end_angle)
        cone_back_end_y = player_center_y - cone_length * math.sin(cone_back_end_angle)

        pygame.draw.polygon(screen, self.color, [(player_center_x, player_center_y),
                                                 (cone_front_x, cone_front_y),
                                                 (cone_front_end_x, cone_front_end_y)])

        pygame.draw.polygon(screen, self.color, [(player_center_x, player_center_y),
                                                 (cone_back_x, cone_back_y),
                                                 (cone_back_end_x, cone_back_end_y)])


pygame.init()

screen_width = 1024
screen_height = 1024
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Wall Boundaries")

wall_image = pygame.image.load("walls.png").convert()

player_width = 30
player_height = 30
player_color = (0, 0, 0)
player_x = 960
player_y = 600
player_speed = 5

cone_length = 100
cone_angle = 60

player = Player(player_width, player_height, player_x, player_y, player_speed)
wall = Map("walls.png")
cone = Cone(cone_length, cone_angle)

score = 0

font = pygame.font.SysFont(None, 30)

player_won = False
running = True

last_movement = (0, 0)

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    prev_player_x, prev_player_y = player.position_x, player.position_y

    player_dx = (keys[pygame.K_d] - keys[pygame.K_a])
    player_dy = (keys[pygame.K_s] - keys[pygame.K_w])

    if player_dx != 0 or player_dy != 0:
        last_movement = (player_dx, player_dy)
        player.move(player_dx, player_dy)

    player.rotate(math.degrees(math.atan2(-player_dy, player_dx)))

    for x in range(player.position_x, player.position_x + player.width):
        for y in range(player.position_y, player.position_y + player.height):
            if 0 <= x < wall.image.get_width() and 0 <= y < wall.image.get_height():
                if wall.image.get_at((x, y)) == (0, 0, 0):
                    player.position_x, player.position_y = prev_player_x, prev_player_y
                elif wall.image.get_at((x, y)) == (123, 255, 0):
                    player_won = True
                    score += 10

    screen.fill((0, 0, 0))
    wall.draw(screen)
    cone.draw(screen, player.position_x, player.position_y, player.width, player.rotation_angle)
    player.draw(screen)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))

    if player_won:
        font = pygame.font.SysFont(None, 48)
        text = font.render("You won!", True, (0, 0, 0))
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(text, text_rect)
        player.position_x = 960
        player.position_y = 600
        pygame.event.clear()

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()