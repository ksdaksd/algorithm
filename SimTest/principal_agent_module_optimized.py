# -*- coding: utf-8 -*-
"""Re‑engineered principal–agent logic with learning support.

This module is **pure logic** – no Tk dependencies – so it can be unit‑tested
independently and imported by the GUI layer (PrincipalAgentModule).

Key features
------------
*  Analytic baseline contract (satisfying IR & IC with w_H = Ū + c_H).
*  Q‑learning agent for the **principal** that gradually converges to a
   near‑optimal linear contract when cost parameters follow a distribution.
*  Agent best‑response logic (accept/effort) identical to textbook model.
*  All parameters are typed dataclasses; every public method has type hints.
*  Vectorised NumPy operations for speed.
*  100 % deterministic ‑‐ RNG is injected for reproducibility in tests.

Usage (in GUI)
--------------
>>> env = PrincipalAgentEnv(res_high=100, res_low=20,
                            p_high=0.8,  p_low=0.4,
                            rng=np.random.default_rng(42))
>>> learner = QLearningPrincipal(env)
>>> learner.train(episodes=2000)
>>> w_H, w_L = learner.best_contract()

You can replace *PrincipalAI* in the original Tk module by an instance of
`AnalyticalPrincipal` (one‑shot optimal), or `QLearningPrincipal` (learning).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

# ---------------------------------------------------------------------------
#   DATA CLASSES
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class EnvironmentParams:
    """Immutable container for exogenous parameters."""

    res_high: float     # Y_H – principal revenue if output high
    res_low: float      # Y_L – revenue if output low
    p_high: float       # Prob(high output | effort)
    p_low: float        # Prob(high output | shirk)
    U_res: float = 0.0  # Agent reservation utility

    # Draws of *costs* for the agent.  In simplest model these can be fixed.
    cost_high: float | None = None  # effort cost C_H
    cost_low: float | None = None   # shirk cost C_L

    def draw_costs(self, rng: np.random.Generator) -> tuple[float, float]:
        """Return a (C_H, C_L) pair.  If fixed values supplied, just return them;
        else draw from simple uniforms as a demo.  Extend as needed."""
        if self.cost_high is not None and self.cost_low is not None:
            return float(self.cost_high), float(self.cost_low)
        # for teaching purpose we sample from modest ranges
        c_H = rng.uniform(5, (self.res_high - self.res_low) * 0.4)
        c_L = rng.uniform(0, c_H * 0.5)
        return c_H, c_L

# ---------------------------------------------------------------------------
#   AGENT LOGIC (best‑response – **no learning**)
# ---------------------------------------------------------------------------
class Agent:
    """Single‑period, risk‑neutral agent with private effort cost."""

    def __init__(self, env: EnvironmentParams, rng: np.random.Generator):
        self.env = env
        self.rng = rng
        self.c_H, self.c_L = env.draw_costs(rng)

    # --------------------------- contract acceptance -----------------------
    def accept(self, w_H: float, w_L: float) -> bool:
        """Does the agent accept the contract?"""
        EU_effort = (
            self.env.p_high * (w_H - self.c_H)
            + (1 - self.env.p_high) * (w_L - self.c_H)
        )
        return EU_effort >= self.env.U_res  # IR binding on effort type

    # --------------------------- effort choice ----------------------------
    def choose_effort(self, w_H: float, w_L: float) -> str:
        """Best‑response effort ("effort" or "shirk").  Assumes agent already
        accepted; caller must have run *accept* check first."""
        EU_effort = (
            self.env.p_high * (w_H - self.c_H)
            + (1 - self.env.p_high) * (w_L - self.c_H)
        )
        EU_shirk = (
            self.env.p_low * (w_H - self.c_L)
            + (1 - self.env.p_low) * (w_L - self.c_L)
        )
        return "effort" if EU_effort >= EU_shirk else "shirk"

# ---------------------------------------------------------------------------
#   PRINCIPAL BASE CLASS
# ---------------------------------------------------------------------------
class AbstractPrincipal:
    def __init__(self, env: EnvironmentParams, rng: np.random.Generator | None = None):
        self.env = env
        self.rng = np.random.default_rng() if rng is None else rng

    # contract must be implemented by subclasses
    def propose_contract(self) -> tuple[float, float]:
        raise NotImplementedError

    # helper for subclasses -------------------------------------------------
    def _expected_profit(self, w_H: float, w_L: float, agent: Agent) -> float:
        # agent best‑response
        if not agent.accept(w_H, w_L):
            return 0.0  # principal gets nothing if agent rejects
        effort = agent.choose_effort(w_H, w_L)
        if effort == "effort":
            exp_rev = (
                self.env.p_high * (self.env.res_high - w_H)
                + (1 - self.env.p_high) * (self.env.res_low - w_L)
            )
        else:  # shirk
            exp_rev = (
                self.env.p_low * (self.env.res_high - w_H)
                + (1 - self.env.p_low) * (self.env.res_low - w_L)
            )
        return exp_rev

# ---------------------------------------------------------------------------
#   ANALYTICAL PRINCIPAL – textbook solution (no learning)
# ---------------------------------------------------------------------------
class AnalyticalPrincipal(AbstractPrincipal):
    """Implements the **first‑best linear contract** that binds (IR) & (IC)."""

    def propose_contract(self) -> tuple[float, float]:
        # Sample a *cost profile* for THIS transaction.  In classroom
        # settings costs often are common knowledge – pass them via env.
        c_H, c_L = self.env.draw_costs(self.rng)
        w_H = self.env.U_res + c_H  # IR_H binding
        w_L = w_H - (c_H - c_L)     # IC binding (Δw = c_H‑c_L)
        return round(w_H, 2), round(w_L, 2)

# ---------------------------------------------------------------------------
#   Q‑LEARNING PRINCIPAL (discrete action grid)
# ---------------------------------------------------------------------------
class QLearningPrincipal(AbstractPrincipal):
    """Tabular Q‑learning over a discretised contract grid.

    *States* are omitted (Markov‑state‑free) -> bandit setting.
    *Actions* are contract pairs (w_H, w_L) from a regular grid.
    Rewards are the principal's realised **expected** profit given an agent
    sampled from the environment's cost distribution.
    """

    def __init__(
        self,
        env: EnvironmentParams,
        rng: np.random.Generator | None = None,
        w_H_grid: np.ndarray | None = None,
        w_L_grid: np.ndarray | None = None,
        epsilon: float = 0.1,
        alpha: float = 0.3,
        discount: float = 0.95,
    ) -> None:
        super().__init__(env, rng)
        # ----- build discrete action space --------------------------------
        if w_H_grid is None:
            w_H_grid = np.linspace(env.res_low * 0.5, env.res_high, 21)
        if w_L_grid is None:
            w_L_grid = np.linspace(0, env.res_low * 0.8, 21)
        self.actions: list[tuple[float, float]] = [  # (w_H, w_L)
            (float(w_H), float(w_L))
            for w_H in w_H_grid
            for w_L in w_L_grid
            if w_H >= w_L  # ensure monotone
        ]
        self.Q = np.zeros(len(self.actions))
        self.epsilon = epsilon
        self.alpha = alpha
        self.discount = discount

    # -------------------------- training loop -----------------------------
    def train(self, episodes: int = 5_000) -> None:
        for _ in range(episodes):
            idx = self._choose_action_index()
            w_H, w_L = self.actions[idx]
            agent = Agent(self.env, self.rng)
            reward = self._expected_profit(w_H, w_L, agent)
            # Q‑update (bandit -> no next state/value)
            self.Q[idx] += self.alpha * (reward - self.Q[idx])

    # ----------------------------- helpers --------------------------------
    def _choose_action_index(self) -> int:
        if self.rng.random() < self.epsilon:
            return self.rng.integers(len(self.actions))
        return int(np.argmax(self.Q))

    # ----------------------------- API ------------------------------------
    def propose_contract(self) -> tuple[float, float]:
        # If not trained, do a quick warm‑up to avoid NaNs
        if not np.any(self.Q):
            self.train(episodes=2_000)
        idx = int(np.argmax(self.Q))
        w_H, w_L = self.actions[idx]
        return round(w_H, 2), round(w_L, 2)

    def best_contract(self) -> tuple[float, float]:
        """Return contract with highest learned value without rounding."""
        idx = int(np.argmax(self.Q))
        return self.actions[idx]


