import os
import numpy as np
import gym
from gym import spaces
import pygame
import math

walls = []


# Class for the orange dude
class Player(object):

    def __init__(self):
        self.rect = pygame.Rect(32, 32, 16, 16)

    def move(self, dx, dy):

        # Move each axis separately. Note that this checks for collisions both times.
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):

        # Move the rect
        self.rect.x += dx
        self.rect.y += dy

        # If you collide with a wall, move out based on velocity
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:  # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0:  # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                if dy > 0:  # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                if dy < 0:  # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.rect.bottom


# Nice class to hold a wall rect
class Wall(object):

    def __init__(self, pos):
        walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)


level = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W         W        W",
    "W         WWWWWW   W",
    "WWWWWWWW    WWWW   W",
    "W   W  W     WWWW  W",
    "W WWW  WW    W     W",
    "W   W    W   W     W",
    "W   W    W   WWW WW",
    "W   WWW WWW  WW W  W",
    "W     W   W  WW W  W",
    "WWW   W   W  WW W  W",
    "W W      W   W     W",
    "W W   WWWW   WWW   W",
    "W           E      W",
    "WWWWWWWWWWWWWWWWWWWW",
]


class Environment(gym.Env):
    def __init__(self):
        super(Environment, self).__init__()
        self.end_rect = None
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.display.set_caption("Get to the red square!")
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240))
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Dict({
            'maze': spaces.Box(low=0, high=1, shape=(320, 240), dtype=np.uint8),
        })
        self.finish_pos = (0, 0)

    def draw_maze(self):
        x = y = 0
        for row in level:
            for col in row:
                if col == "W":
                    Wall((x, y))
                if col == "E":
                    self.end_rect = pygame.Rect(x, y, 16, 16)
                    self.finish_pos = (x, y)
                x += 16
            y += 16
            x = 0

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_maze()
        self.clock.tick(60)
        for wall in walls:
            pygame.draw.rect(self.screen, (255, 255, 255), wall.rect)
        pygame.draw.rect(self.screen, (255, 0, 0), self.end_rect)
        pygame.draw.rect(self.screen, (255, 200, 0), self.player.rect)
        pygame.display.flip()

    def step(self, action):
        dx, dy = 0, 0
        if action == 0:
            dx = -16
        elif action == 1:
            dx = 16
        elif action == 2:
            dy = -16
        elif action == 3:
            dy = 16

        self.player.move(dx, dy)

        reward = 0
        done = False

        if self.player.rect.colliderect(self.end_rect):
            reward = 100
            done = True

        state = self._get_observation()

        distance = math.sqrt((self.end_rect.x // 16 - self.player.rect.x // 16) ** 2 +
                             (self.end_rect.y // 16 - self.player.rect.y // 16) ** 2)

        max_distance = math.sqrt((self.screen.get_width() // 16) ** 2 + (self.screen.get_height() // 16) ** 2)
        normalized_distance = distance / max_distance

        reward += 2 * (1 - normalized_distance) - 1

        return state, reward, done, {}

    def _map_rewards(self):
        # Initialize reward map
        reward_map = np.zeros((self.screen.get_height() // 16, self.screen.get_width() // 16))

        # Assign base rewards
        for wall in walls:
            reward_map[wall.rect.y // 16, wall.rect.x // 16] = -1

        reward_map[self.end_rect.y // 16, self.end_rect.x // 16] = 100

        # Calculate relative rewards based on distance from player and end line
        player_pos = (self.player.rect.y // 16, self.player.rect.x // 16)
        end_line_pos = (self.end_rect.y // 16, self.end_rect.x // 16)

        for y in range(self.screen.get_height() // 16):
            for x in range(self.screen.get_width() // 16):
                distance_to_player = max(abs(player_pos[0] - y), abs(player_pos[1] - x))
                distance_to_end_line = max(abs(end_line_pos[0] - y), abs(end_line_pos[1] - x))

                reward_map[y, x] += (10 - distance_to_player) + (10 - distance_to_end_line)

        return reward_map

    def _get_observation(self):
        self.render()
        maze_array = np.zeros((self.screen.get_height() // 16, self.screen.get_width() //16), dtype=np.uint8)

        # Fill the maze array based on the wall positions
        for wall in walls:
            wall_x = wall.rect.x // 16
            wall_y = wall.rect.y // 16
            maze_array[wall_y, wall_x] = 1

        finish_x = self.finish_pos[0] // 16
        finish_y = self.finish_pos[1] // 16
        maze_array[finish_y, finish_x] = -1

        maze_array[self.player.rect.y // 16, self.player.rect.x // 16] = 2

        map_reward = self._map_rewards()

        observation = maze_array + map_reward

        return {"maze": observation}

    def reset(self):
        # Reset player position
        self.player.rect.x = 32
        self.player.rect.y = 32
        return self._get_observation()