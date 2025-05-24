from __future__ import annotations
"""Optimised RiskPreferenceModule

• 向量化期望效用/确定性等价计算
• 统一风险类型映射
• 数值稳定性修复
• 预留 Monte‑Carlo 敏感性分析接口
• 非阻塞绘图 (draw_idle)

与现有 sim_soft.py 其它类解耦，只需确保 BaseModule 已在运行环境中。
"""

import numpy as np
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# matplotlib 全局中文 & 负号
plt.rcParams["font.family"] = "FangSong"
plt.rcParams["axes.unicode_minus"] = False

# ---------------------------------------------------------------------------
#  Utility layer (pure logic, 可进行单元测试)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class UtilitySpec:
    """Utility function U(w) 及其反函数 U^{-1}(·)。"""

    u: Callable[[np.ndarray], np.ndarray]
    u_inv: Callable[[np.ndarray], np.ndarray]
    default_gamma: float


class RiskPreferenceCore:
    """Vectorised certainty‑equivalent / expected‑utility calculator."""

    #: Risk‑type → utility‑spec 映射（preferring 于运行时根据 γ 动态生成）
    BASE_UTILS: Dict[str, UtilitySpec] = {
        "averse": UtilitySpec(
            u=lambda w: np.log(np.clip(w, 1e-8, None)),  # log(w) with clip for w<=0
            u_inv=lambda u: np.exp(u),
            default_gamma=0.5,
        ),
        "neutral": UtilitySpec(
            u=lambda w: w,
            u_inv=lambda u: u,
            default_gamma=1.0,
        ),
    }

    # ------------------------------ helpers --------------------------------
    @staticmethod
    def power_spec(gamma: float) -> UtilitySpec:
        """Return CRRA (power) utility spec for γ>1."""
        gamma_eff = max(1.01, gamma)  # 避免 γ<=1 数值问题
        return UtilitySpec(
            u=lambda w, g=gamma_eff: np.power(w, g, dtype=np.float64),
            u_inv=lambda u, g=gamma_eff: np.power(u, 1.0 / g, dtype=np.float64),
            default_gamma=gamma_eff,
        )

    # ------------------------------ core -----------------------------------
    def get_spec(self, pref: str, gamma: float | None = None) -> tuple[UtilitySpec, str]:
        """Return (spec, name) given risk‑type & γ."""
        if pref == "preferring":
            g = 2.0 if gamma is None or gamma <= 1 else gamma
            spec = self.power_spec(g)
            name = fr"w^{g:.2f}"
        else:
            spec = self.BASE_UTILS[pref]
            name = "ln w" if pref == "averse" else "w"
        return spec, name

    # ----------------------------------------------------------------------
    def certainty_equivalent(
        self,
        p: np.ndarray,
        w1: np.ndarray,
        w2: np.ndarray,
        pref: str,
        gamma: float | None = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Vectorised CE computation.

        All arguments broadcast against each other (np.asarray). Returns
        (E[w], EU, CE).
        """

        p = np.asarray(p, dtype=np.float64)
        w1 = np.asarray(w1, dtype=np.float64)
        w2 = np.asarray(w2, dtype=np.float64)

        spec, _ = self.get_spec(pref, gamma)
        U1, U2 = spec.u(w1), spec.u(w2)
        Ew = p * w1 + (1 - p) * w2
        EU = p * U1 + (1 - p) * U2
        CE = spec.u_inv(EU)
        return Ew, EU, CE

    # ----------------------------------------------------------------------
    def monte_carlo_ce(self, n: int, pref: str, gamma: float) -> np.ndarray:
        """Monte Carlo distribution of CE with random (p, w1, w2)."""
        # NOTE: 参数分布可根据业务需求调整
        rng = np.random.default_rng()
        p = rng.random(n)
        w1 = rng.uniform(10, 200, n)
        w2 = rng.uniform(0, w1)
        _, _, ce = self.certainty_equivalent(p, w1, w2, pref, gamma)
        return ce


# ---------------------------------------------------------------------------
#  Tkinter UI layer – extends existing BaseModule
# ---------------------------------------------------------------------------
class RiskPreferenceModule(BaseModule):
    """Optimised GUI module with vectorised core & Monte Carlo sampling."""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.core = RiskPreferenceCore()
        # counters & tk‑variables -------------------------------------------------
        self.eu_count = 0
        self.prob_var = tk.DoubleVar(value=0.5)
        self.outcome1_var = tk.DoubleVar(value=100.0)
        self.outcome2_var = tk.DoubleVar(value=50.0)
        self.pref_var = tk.StringVar(value="neutral")
        self.gamma_var = tk.DoubleVar(value=1.0)
        self.sample_var = tk.IntVar(value=0)  # Monte Carlo sample size (0 = off)

        # ---------- UI build ----------------------------------------------------
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # 1) 风险类型 + γ ---------------------------------------------------
        pref_frame = ttk.LabelFrame(self, text="风险偏好类型")
        pref_frame.pack(fill="x", padx=15, pady=5)
        for val, text in [("averse", "风险厌恶"), ("neutral", "风险中性"), ("preferring", "风险爱好")]:
            ttk.Radiobutton(
                pref_frame,
                text=text,
                variable=self.pref_var,
                value=val,
                command=self._on_pref_change,
            ).pack(side="left", padx=5)

        gamma_row = ttk.Frame(self)
        gamma_row.pack(fill="x", padx=15, pady=5)
        ttk.Label(gamma_row, text="效用参数 γ:").pack(side="left")
        ttk.Entry(gamma_row, textvariable=self.gamma_var, width=8).pack(side="left", padx=5)

        # 2) 参数输入 --------------------------------------------------------
        params = ttk.Frame(self)
        params.pack(side="left", fill="y", padx=15, pady=15)
        ttk.Label(params, text="输入参数").pack(pady=5)
        for lbl, var in [
            ("概率 p:", self.prob_var),
            ("收益 1:", self.outcome1_var),
            ("收益 2:", self.outcome2_var),
            ("Monte Carlo 样本:", self.sample_var),
        ]:
            ttk.Label(params, text=lbl).pack(anchor="w")
            ttk.Entry(params, textvariable=var).pack(fill="x")

        # 3) 操作按钮 -------------------------------------------------------
        btn_frame = ttk.Frame(params)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="计算 CE", command=self.compute_utility).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="绘制图像", command=self.plot_utility).pack(side="left", padx=4)

        # 4) 日志 + 图区 ----------------------------------------------------
        self.log = scrolledtext.ScrolledText(params, width=35, height=12)
        self.log.pack(pady=5)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    # ------------------------ callbacks ------------------------------------
    def _on_pref_change(self):
        pref = self.pref_var.get()
        if pref in RiskPreferenceCore.BASE_UTILS:
            self.gamma_var.set(RiskPreferenceCore.BASE_UTILS[pref].default_gamma)
        else:  # preferring
            self.gamma_var.set(2.0)

    # --------------------------------------------------------------------
    def compute_utility(self):
        """Compute CE; if sample_var>0, additionally run Monte Carlo."""
        p = self.prob_var.get()
        w1 = self.outcome1_var.get()
        w2 = self.outcome2_var.get()
        pref = self.pref_var.get()
        gamma = self.gamma_var.get()

        # deterministic CE -------------------------------------------------
        Ew, EU, CE = self.core.certainty_equivalent(p, w1, w2, pref, gamma)
        self.eu_count += 1
        self.log.insert(
            "end",
            f"[第{self.eu_count}次] 类型: {pref} | U: {EU:.4f} | E(w): {Ew:.4f} | CE: {CE:.4f}\n",
        )

        # Monte Carlo (optional) ------------------------------------------
        n_mc = self.sample_var.get()
        if n_mc > 0:
            ce_samples = self.core.monte_carlo_ce(n_mc, pref, gamma)
            mean, low, high = ce_samples.mean(), np.percentile(ce_samples, 2.5), np.percentile(
                ce_samples, 97.5
            )
            self.log.insert(
                "end",
                f"  Monte‑Carlo({n_mc}) CĒ={mean:.2f}  95%CI=({low:.2f},{high:.2f})\n",
            )
        self.log.see("end")

    # --------------------------------------------------------------------
    def plot_utility(self):
        # read UI state ----------------------------------------------------
        p = self.prob_var.get()
        w1 = self.outcome1_var.get()
        w2 = self.outcome2_var.get()
        pref = self.pref_var.get()
        gamma = self.gamma_var.get()

        spec, _ = self.core.get_spec(pref, gamma)
        U1, U2 = spec.u(np.array([w1, w2]))
        Ew = p * w1 + (1 - p) * w2
        EU = p * U1 + (1 - p) * U2
        CE = spec.u_inv(EU)
        U_Ew = spec.u(Ew)

        xs = np.linspace(min(w1, w2) * 0.8, max(w1, w2) * 1.2, 400)
        self.ax.clear()
        self.ax.plot(xs, spec.u(xs), label="U(w)")
        self.ax.plot([w1, w2], [U1, U2], color="gray", lw=1.0, label="线段")

        # scatter points ---------------------------------------------------
        pts = [
            ("A", w1, U1),
            ("D", w2, U2),
            ("B", Ew, EU),
            ("C", Ew, U_Ew),
            ("E", CE, EU),
        ]
        cmap = {"A": "black", "B": "royalblue", "C": "firebrick", "D": "black", "E": "seagreen"}
        for lbl, x, y in pts:
            self.ax.scatter(x, y, color=cmap.get(lbl, "black"), zorder=3)
            self.ax.text(x, y, f" {lbl}")

        # aesthetics -------------------------------------------------------
        self.ax.set_xlabel("财富 w")
        self.ax.set_ylabel("效用 U(w)")
        self.ax.set_title({"averse": "风险厌恶", "neutral": "风险中性", "preferring": "风险爱好"}[pref])
        self.ax.legend()
        self.fig.tight_layout()
        # 非阻塞刷新
        self.canvas.draw_idle()
