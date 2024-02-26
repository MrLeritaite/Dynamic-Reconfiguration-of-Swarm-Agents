import gym
from gym import spaces
import pygame
import numpy as np
import math


class Environment(gym.Env):
    def __init__(self):
        super(Environment, self).__init__()
        pygame.init()

        self.screen_width = 1024
        self.screen_height = 1024
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.wall_image = pygame.image.load("env/Maze1.jpg").convert()

        self.cone_length = 50
        self.cone_angle = 60
        self.cone = Cone(self.cone_length, self.cone_angle, 3)

        self.player_width = 30
        self.player_height = 30
        self.player_speed = 15

        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.screen_width, self.screen_height, 3),
                                            dtype=np.uint8)

        self.players = [Player(self.player_width, self.player_height, 360, 800 + 40 * _, self.player_speed)
                        for _ in range(3)]
        self.wall = Map("env/Maze1.jpg")
        self.score = 0
        self.font = pygame.font.SysFont(None, 30)
        self.player_won = False
        self.last_movement = [(0, 0), (0, 0), (0, 0)]
        self.reward = 0

    def reset(self):
        self.reward = 0
        self.players = [Player(self.player_width, self.player_height, 360, 800 + 70 * _, self.player_speed)
                        for _ in range(3)]
        self.score = 0
        self.player_won = False
        self.last_movement = [(0, 0), (0, 0), (0, 0)]
        return self._get_observation()

    def step(self, actions):
        player_won = False

        lines_position = []
        dx = dy = 0

        for i, action in enumerate(actions):
            self.reward -= 1
            if action == 0:  # Move up
                dx, dy = 0, -1
            elif action == 1:  # Move down
                dx, dy = 0, 1
            elif action == 2:  # Move left
                dx, dy = -1, 0
            elif action == 3:  # Move right
                dx, dy = 1, 0
            elif action == 4:  # Don't move
                dx = dy = 0

            x, y = self.players[i].move(dx, dy, self.wall, self.players[i].position_x,
                                        self.players[i].position_y)
            self.last_movement[i] = (dx, dy)

            if self.wall.image.get_at((x, y)) == (123, 255, 0):
                player_won = True
                self.reward += 100

            lines_position.append(
                self.cone.get_cord_line(self.players[i].position_x // 2, self.players[i].position_y // 2,
                                        self.players[i].rotation_angle))
            if player_won:
                self.reward += 100
            if self.lines_connected(lines_position):
                self.reward += 5
            else:
                self.reward -= 10

        return self._get_observation(), self.reward, player_won, {}

    def lines_connected(self, lines_position, threshold=100):
        num_lines = len(lines_position)
        if num_lines < 2:
            return False

        lines_array = np.array(lines_position)

        distances = np.zeros((num_lines, num_lines))
        for i in range(num_lines):
            for j in range(i + 1, num_lines):
                dist = np.linalg.norm(lines_array[i] - lines_array[j])
                distances[i, j] = distances[j, i] = dist

        return np.all(distances < threshold)

    def render(self):
        self.screen.fill((0, 0, 0))
        self.wall.draw(self.screen)
        for i in range(3):
            self.cone.draw(self.screen, self.players[i].position_x, self.players[i].position_y, self.players[i].width,
                           self.last_movement[i])
            self.players[i].draw(self.screen)
        score_text = self.font.render(f"Score: {self.reward}", True, (0, 0, 0))
        self.screen.blit(score_text, (20, 20))
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    def _get_observation(self):
        observation = pygame.surfarray.array2d(self.screen)
        observation = observation / 255.0
        observation = np.uint8(observation * 255)

        return observation

    def observation_space(self, agent):
        return self.observation_space

    def action_space(self, agent):
        return self.action_space


class Map:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path).convert()

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Player:
    def __init__(self, player_width, player_height, player_x, player_y, player_speed):
        self.rotation_angle = 0
        self.width = player_width
        self.height = player_height
        self.position_x = player_x
        self.position_y = player_y
        self.player_speed = player_speed

    def move(self, dx, dy, wall, prev_player_x, prev_player_y):
        self.position_x += dx * self.player_speed
        self.position_y += dy * self.player_speed
        self.position_x = max(0, min(self.position_x, 1024 - self.width))
        self.position_y = max(0, min(self.position_y, 1024 - self.height))

        for x in range(self.position_x, self.position_x + self.width):
            for y in range(self.position_y, self.position_y + self.height):
                if 0 <= x < wall.image.get_width() and 0 <= y < wall.image.get_height():
                    if wall.image.get_at((x, y)) == (0, 0, 0):
                        self.position_x, self.position_y = prev_player_x, prev_player_y

        return self.position_x, self.position_y

    def rotate(self, angle):
        self.rotation_angle = angle

    def draw(self, screen):
        rotated_player = pygame.transform.rotate(pygame.Surface((self.width, self.height)),
                                                 self.rotation_angle)
        screen.blit(rotated_player, (self.position_x, self.position_y))


class Cone:
    def __init__(self, cone_length, cone_angle, line_thickness):
        self.length = cone_length
        self.cone_angle = cone_angle
        self.color = (0, 0, 255)
        self.line_thickness = line_thickness
        self.first_frame = True
        self.rotation_angle = 90

        self.cone_front_x = 0
        self.cone_front_y = 0
        self.cone_back_x = 0
        self.cone_back_y = 0

    def draw(self, screen, player_x, player_y, player_width, last_movement):
        if last_movement != (0, 0):
            rotation_angle = math.degrees(math.atan2(-last_movement[1], last_movement[0]))
        else:
            rotation_angle = self.rotation_angle

        player_center_x = player_x + player_width // 2
        player_center_y = player_y + player_width // 2

        cone_front_x, cone_front_y, cone_back_x, cone_back_y = \
            self.get_cord_line(player_center_x, player_center_y, rotation_angle)

        pygame.draw.line(screen, self.color, (player_center_x, player_center_y), (cone_front_x, cone_front_y),
                         self.line_thickness)
        pygame.draw.line(screen, self.color, (player_center_x, player_center_y), (cone_back_x, cone_back_y),
                         self.line_thickness)

    def get_cord_line(self, player_center_x, player_center_y, rotation_angle):
        self.cone_front_x = player_center_x + self.length * math.cos(math.radians(rotation_angle))
        self.cone_front_y = player_center_y - self.length * math.sin(math.radians(rotation_angle))

        self.cone_back_x = player_center_x + self.length * math.cos(math.radians(180 + rotation_angle))
        self.cone_back_y = player_center_y - self.length * math.sin(math.radians(180 + rotation_angle))

        return self.cone_front_x, self.cone_front_y, self.cone_back_x, self.cone_back_y