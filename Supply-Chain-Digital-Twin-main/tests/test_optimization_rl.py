"""
Unit tests for Phase 6 MEIO & Reinforcement Learning Engine.
"""

import pytest
import numpy as np

from src.optimization import MultiEchelonOptimizer, EchelonStageConfig
from src.rl import SupplyChainInventoryEnv, QLearningInventoryAgent


def test_multi_echelon_optimizer():
    stages = {
        "FAC_01": EchelonStageConfig("FAC_01", echelon_level=1, nominal_lead_time=5.0, inbound_stage_ids=[]),
        "WH_01": EchelonStageConfig("WH_01", echelon_level=2, nominal_lead_time=3.0, inbound_stage_ids=["FAC_01"]),
        "DC_01": EchelonStageConfig("DC_01", echelon_level=3, nominal_lead_time=2.0, inbound_stage_ids=["WH_01"]),
    }

    meio = MultiEchelonOptimizer(stages)
    res = meio.optimize_multi_echelon_safety_stock()

    assert "FAC_01" in res
    assert "DC_01" in res
    assert res["DC_01"]["net_lead_time"] == 10.0  # 5 + 3 + 2
    assert res["DC_01"]["multi_echelon_safety_stock"] > res["DC_01"]["single_echelon_safety_stock"]


def test_rl_environment_reset_step():
    env = SupplyChainInventoryEnv(horizon_days=10)
    obs = env.reset()

    assert len(obs) == 3
    assert env.current_day == 1

    next_obs, reward, done, info = env.step(action_idx=2)
    assert len(next_obs) == 3
    assert isinstance(reward, float)
    assert not done
    assert info["day"] == 2


def test_q_learning_agent_step():
    env = SupplyChainInventoryEnv(horizon_days=5)
    agent = QLearningInventoryAgent(action_size=5)

    obs = env.reset()
    action = agent.select_action(obs)
    next_obs, reward, done, info = env.step(action)

    agent.learn(obs, action, reward, next_obs, done)
    assert len(agent.q_table) > 0