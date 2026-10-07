"""
Tabular Q-Learning Inventory Optimization Agent.
"""
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np


@dataclass
class TabularPolicy:
    q_table: Dict[Tuple[int, int, int], np.ndarray]


class QLearningInventoryAgent:
    def __init__(self, action_size: int = 5, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 0.2):
        self.action_size = action_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table: Dict[Tuple[int, int, int], np.ndarray] = {}

    def _discretize_state(self, obs: np.ndarray) -> Tuple[int, int, int]:
        # Discretize continuous state into discrete bins for tabular RL
        dc_bin = int(obs[0] // 500)
        fac_bin = int(obs[1] // 1000)
        backlog_bin = int(obs[2] // 200)
        return (dc_bin, fac_bin, backlog_bin)

    def select_action(self, obs: np.ndarray) -> int:
        state = self._discretize_state(obs)
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size)

        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_size)
        return int(np.argmax(self.q_table[state]))

    def learn(self, obs: np.ndarray, action: int, reward: float, next_obs: np.ndarray, done: bool) -> None:
        state = self._discretize_state(obs)
        next_state = self._discretize_state(next_obs)

        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size)
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(self.action_size)

        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + (0.0 if done else self.gamma * self.q_table[next_state][best_next_action])
        td_error = td_target - self.q_table[state][action]

        self.q_table[state][action] += self.alpha * td_error