import os
import numpy as np
import gym
from gym import spaces
import pygame

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
    "W                  W",
    "W         WWWWWW   W",
    "W   WWWW       W   W",
    "W   W        WWWW  W",
    "W WWW  WWWW        W",
    "W   W     W W      W",
    "W   W     W   WWW WW",
    "W   WWW WWW   W W  W",
    "W     W   W   W W  W",
    "WWW   W   WWWWW W  W",
    "W W      WW        W",
    "W W   WWWW   WWW   W",
    "W     W    E   W   W",
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
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=255, shape=(320, 240, 3),
                                            dtype=np.uint8)

    def draw_maze(self):
        x = y = 0
        for row in level:
            for col in row:
                if col == "W":
                    Wall((x, y))
                if col == "E":
                    self.end_rect = pygame.Rect(x, y, 16, 16)
                x += 16
            y += 16
            x = 0

    def render(self):
        self.draw_maze()
        self.clock.tick(60)
        self.screen.fill((0, 0, 0))
        for wall in walls:
            pygame.draw.rect(self.screen, (255, 255, 255), wall.rect)
        pygame.draw.rect(self.screen, (255, 0, 0), self.end_rect)
        pygame.draw.rect(self.screen, (255, 200, 0), self.player.rect)
        pygame.display.flip()

    def step(self, actions):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.player.move(-2, 0)
        if key[pygame.K_RIGHT]:
            self.player.move(2, 0)
        if key[pygame.K_UP]:
            self.player.move(0, -2)
        if key[pygame.K_DOWN]:
            self.player.move(0, 2)

        if self.player.rect.colliderect(self.end_rect):
            raise SystemExit("You win!")

        return self._get_observation(), 0, 1, {}

    def _get_observation(self):
        observation = pygame.surfarray.array2d(self.screen)
        observation = observation / 255.0
        observation = np.uint8(observation * 255)

        return observation

    def observation_space(self, agent):
        return self.observation_space

    def action_space(self, agent):
        return self.action_space