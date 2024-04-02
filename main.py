from gym.envs.registration import register
import gym
import matplotlib.pyplot as plt
from agent import DDQNAgent
import gc
import os
import torch
import numpy as np
import csv

save_interval = 10

plt.figure(figsize=(10, 5))
NUM_STEPS = 150
NUM_EPISODES = 30
NUM_AGENTS = 1
SEED = 42


def save_rewards_to_csv(rewards, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Episode', 'Total Reward'])
        for episode, reward in enumerate(rewards, start=1):
            writer.writerow([episode, reward])


if __name__ == "__main__":
    register(
        id='Test',
        entry_point='env.env:Environment',
    )
    env = gym.make('Test')
    pretrained_model_path = f"cel_castigator.pth"
    if os.path.exists(pretrained_model_path):
        agent = DDQNAgent(state_size=(240 // 16 * 320 // 16), action_size=4, seed=SEED, eps=0)
        agent.qnetwork_local.load_state_dict(torch.load(pretrained_model_path))
    else:
        agent = DDQNAgent(state_size=(240 // 16 * 320 // 16), action_size=4, seed=SEED)

    done = False
    best_agent_score = -np.inf
    for episode in range(1, NUM_EPISODES):
        total_rewards = [0] * NUM_EPISODES
        state = env.reset()
        env.render()
        for steps in range(1, NUM_STEPS + 1):
            env.render()
            action = agent.act(state)  # Get actions for each agent
            print(action)
            # Execute actions for each agent and store results
            next_state, reward, done, _ = env.step(action)
            total_rewards[episode] += reward

            agent.step(state, action, reward, next_state, done)

            if done:
                print("Agent won")
                torch.save(agent.qnetwork_local.state_dict(), f"cel_castigator.pth")
                break

        for i, total_reward in enumerate(total_rewards):
            print(f"Agent {i + 1}: Total Reward = {total_reward}")

        if agent is not None:
            if best_agent_score < total_rewards[episode]:
                best_agent_score = total_rewards[episode]
                torch.save(agent.qnetwork_local.state_dict(), f"best_agent_model.pth")
            else:
                print("The agents are not surpassing the latest one")

        save_rewards_to_csv(total_rewards, 'data.csv')
        del state, action, next_state, reward, done, total_rewards
        gc.collect()
        print("Done episode: ", episode)

    env.close()