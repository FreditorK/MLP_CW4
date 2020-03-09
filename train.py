import os
import argparse
import numpy as np
from environments import Map_Environment
from ppo_agent import PPO_Agent, train
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='DQN_Agent')
parser.add_argument('--num_episodes', nargs="?", type=int, default=5000, help='number of episodes')
parser.add_argument('--max_steps', nargs="?", type=int, default=50, help='number of steps')
parser.add_argument('--file', nargs="?", type=str, default='maps', help='file name')
parser.add_argument('--path', nargs="?", type=str, default=os.path.abspath(os.getcwd()), help='file name')
args = parser.parse_args()

env = Map_Environment(args.file, np.array([0, 0, 0]), np.array([9, 9, 9]))
agent = PPO_Agent(env, (1, 10, 10, 10), 12, path=args.path)
rewards, losses = train(env, agent, args.num_episodes, args.max_steps)
plt.plot(rewards)
plt.plot(np.convolve(rewards, (1/50)*np.ones(50), mode='valid'))
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.show()

plt.plot(losses)
plt.plot(np.convolve(losses, (1/50)*np.ones(50), mode='valid'))
plt.xlabel("Episode")
plt.ylabel("Loss")
plt.show()