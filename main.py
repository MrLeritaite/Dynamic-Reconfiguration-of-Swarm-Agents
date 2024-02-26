from gym.envs.registration import register
import gym
import matplotlib.pyplot as plt
import pygame
from agent import DDQNAgent
import pickle
import torch

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

    state_size = env.observation_space.shape[0]
    action_size = 5

    agent = DDQNAgent(state_size, action_size, SEED)

    # Initialize lists to store rewards and observations
    rewards_per_episode = []
    observations_per_episode = []

    # Run multiple episodes
    for episode in range(NUM_EPISODES):
        observation = env.reset()
        done = False
        total_reward = 0
        episode_observations = []

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # Perform a step in the environment
            action = [agent.act(observation) for _ in range(3)]
            observation, reward, done, _ = env.step(action)

            # Accumulate rewards
            total_reward += reward
            episode_observations.append(observation)

            # Render the environment
            steps += 1

            # Check if maximum steps reached without solving the environment
            if steps >= max_steps_per_episode:
                print("Maximum steps reached without solving the environment. Resetting...")
                done = True
                break


            env.render()

        steps = 0

        # Store rewards and observations for the episode
        rewards_per_episode.append(total_reward)
        observations_per_episode.append(episode_observations)

        if (episode + 1) % save_interval == 0:
            # Save Q-network weights
            torch.save(agent.qnetwork_local.state_dict(), f'qnetwork_local_{episode + 1}.pth')
            torch.save(agent.qnetwork_target.state_dict(), f'qnetwork_target_{episode + 1}.pth')

            # Save replay buffer
            with open(f'replay_buffer_{episode + 1}.pkl', 'wb') as f:
                pickle.dump(agent.replay_buffer, f)

            print(f"Learning progress saved at episode {episode + 1}")

            plt.plot(rewards_per_episode, label='Reward')
            plt.xlabel('Episode')
            plt.ylabel('Total Reward')
            plt.title('Training Progress')
            plt.legend()
            plt.grid(True)
            plt.pause(0.05)
            plt.show()
            plt.savefig(f"replay_buffer_{episode + 1}.png")

        print(f"Episode {episode + 1}, Total Reward: {total_reward}")

    # Close the environment
    env.close()