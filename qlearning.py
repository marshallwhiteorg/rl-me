'''Implements Q-learning'''

import gym
import gym_minigrid
import logging
import numpy as np
from collections import defaultdict
from lib import plotting
#from utils.format import get_obss_preprocessor
import torch


#ENV_NAME = 'MiniGrid-DoorKey-5x5-v0'
ENV_NAME = 'MiniGrid-Empty-5x5-v0'
env = gym_minigrid.wrappers.FlatObsWrapper(gym.make(ENV_NAME))
logging.info(ENV_NAME)
# A function that will format the observation space for easier use
#_, preprocess_obss = get_obss_preprocessor(env.observation_space)


def make_policy(q, num_actions, epsilon):
    """Make an epsilon-greedy policy from the provided Q-function

    :param q: Q-function
    :param num_actions: Size of action space
    :param epsilon: Probability of taking a random action
    :returns: Stochastic policy as a function of the observation
    :rtype: fn: observation -> [action probability]

    """
    def policy(observation):
        print(q[observation])
        best_action_idx = np.argmax(q[observation])
        distribution = []
        for action_idx in range(num_actions):
            probability = epsilon / num_actions
            if action_idx == best_action_idx:
                probability += 1 - epsilon
            distribution.append(probability)
        return distribution
    return policy


def q_learning(env, num_episodes, alpha, gamma, epsilon):
    """Find the optimal policy using off-policy Q-learning

    :param env: OpenAI environment
    :param num_episodes: Number of episodes to run
    :param alpha: Learning rate
    :param gamma: Discount factor
    :param epsilon: Probability of taking a random action
    :returns: Optimal Q-function and statistics
    :rtype: dictionary of state -> action -> action-value, plotting.EpisodeStats

    """
    statistics = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes))
    q = defaultdict(lambda: np.zeros(env.action_space.n))
    print(q)
    for episode_idx in range(num_episodes):
        observation = torch.tensor(env.reset())
        terminal = False
        t = 0
        episode = []
        while not terminal:
            policy = make_policy(q, env.action_space.n, epsilon)
            action_distribution = policy(observation)
            action = np.random.choice(np.arange(len(action_distribution)),
                                      p=action_distribution)
            next_observation, reward, done, _ = env.step(action)
            next_observation = torch.tensor(next_observation)
            episode.append([observation, action, reward, next_observation, done])
            statistics.episode_rewards[episode_idx] += reward
            statistics.episode_lengths[episode_idx] = t
            print("\nStep {} @ Episode {}/{} ({})"
                  .format(t, episode_idx + 1, num_episodes,
                          statistics.episode_rewards[episode_idx - 1]), end="")
            best_next_action_value = max(
                [q[next_observation][next_action] - q[observation][action]
                 for next_action
                 in np.arange(len(q[next_observation]))])
            q[observation] += alpha * (reward + gamma * best_next_action_value)
            observation = next_observation
            if done:
                terminal = True
    return q, statistics



if __name__ == '__main__':
    q, stats = q_learning(env, 500, 1.0, .5, .1)
    plotting.plot_episode_stats(stats)
