from gym.envs.registration import register
import gym
import matplotlib.pyplot as plt
import pygame

save_interval = 10

plt.figure(figsize=(10, 5))
NUM_EPISODES = 10000
SEED = 1234

max_steps_per_episode = 1000
steps = 0

if __name__ == "__main__":
    register(
        id='Test',
        entry_point='env.env:Environment',
    )
    env = gym.make('Test')

    running = True
    while running:
        env.reset()
        env.render()
        env.step(0)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False