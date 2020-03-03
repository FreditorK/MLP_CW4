import torch
from networks import Conv_Net
from memory import Memory
import torch.nn.functional as F
from environments import Action
from tqdm import tqdm

import numpy as np


class PPO_Agent:
    def __init__(self, env, map_dim, action_dim, path="/home/frederik/MLP_CW4", learning_rate=1e-3,
                 gamma=0.99, tau=0.05, buffer_size=50000):
        self.env = env
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon_decay = 0.95
        self.epsilon = 0.9
        self.tau = tau
        self.memory = Memory(max_size=buffer_size)
        self.path = path

        try:
            self.model = torch.load(self.path + "/model.pth")
            print("--------------------------------\n"
                  "Models were loaded successfully! \n"
                  "--------------------------------")
        except:
            print("-----------------------\n"
                  "No models were loaded! \n"
                  "-----------------------")
            self.model = Conv_Net(map_dim, action_dim)
        self.old_model = Conv_Net(map_dim, action_dim)
        self.old_model.load_state_dict(self.model.state_dict())

        self.model_optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate, eps=1e-3, weight_decay=0.999)

    def save(self):
        torch.save(self.actor, self.path + "/model.pth")
        torch.save(self.old_policy, self.path + "/target.pth")

    def get_action(self, map, explore=True):
        state = torch.from_numpy(map).float()
        action_probs = (state)
        dist = Categorical(action_probs)
        action = dist.sample()

        memory.states.append(state)
        memory.actions.append(action)
        memory.logprobs.append(dist.log_prob(action))

        return action.item()

        if np.random.rand() < self.epsilon and explore:
            return self.env.sample()

        self.epsilon *= self.epsilon_decay

        map = torch.FloatTensor(map).unsqueeze(0).unsqueeze(0)
        qvals = self.policy.forward(map).detach()
        action = np.argmax(qvals.numpy())

        return action

    def loss(self, batch):
        maps, actions, rewards, next_maps, dones = batch
        maps = torch.FloatTensor(maps).unsqueeze(1)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_maps = torch.FloatTensor(next_maps).unsqueeze(1)
        dones = torch.BoolTensor(dones)

        # resize tensors
        actions = actions.view(actions.size(0), 1)
        rewards = rewards.view(rewards.size(0), 1)
        dones = dones.view(dones.size(0), 1)

        state_action_values = self.actor.forward(maps).gather(1, actions)
        next_state_action_values = torch.max(self.old_policy.forward(next_maps), 1)[0].unsqueeze(1).detach()
        expected_state_action_values = rewards + (~dones) * self.gamma * next_state_action_values
        q_loss = F.mse_loss(state_action_values, expected_state_action_values)

        self.model_optimizer.zero_grad()
        q_loss.backward()
        self.model_optimizer.step()

        return q_loss

    def train(self, batch_size):
        batch = self.memory.sample(batch_size)
        model_loss = self.loss(batch)

        for target_param, param in zip(self.old_policy.parameters(), self.actor.parameters()):
            target_param.data = (param.data * self.tau + target_param.data * (1.0 - self.tau)).clone()

        return model_loss


def train(env, agent, num_episodes, max_steps, batch_size=32):
    episode_rewards = []
    episode_losses = []
    tqdm_e = tqdm(range(num_episodes), desc='Training', leave=True, unit="episode")
    for e in tqdm_e:
        map = env.reset()
        episode_reward = 0
        episode_loss = 0
        for step in range(max_steps):
            action = agent.get_action(map)
            next_map, reward, done, _ = env.step(action)
            agent.memory.push(map, action, reward, next_map, done)
            episode_reward += reward

            if len(agent.memory) > batch_size:
                loss = agent.train(batch_size)
                episode_loss += loss

            if done:
                print("Target reached: ", episode_reward)
                break

            map = next_map

        tqdm_e.set_description("Episode {} reward: {}".format(e, episode_reward))
        tqdm_e.refresh()
        episode_rewards.append(episode_reward)
        episode_losses.append(episode_loss/max_steps)

    agent.save()
    return episode_rewards, episode_losses