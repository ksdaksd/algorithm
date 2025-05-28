# from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv
import random
import datetime
import math
import os

plt.rcParams["font.family"] = "FangSong"  # 仿宋
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

# 可选引入现代主题库（如 ttkbootstrap）
from ttkbootstrap import Style
from ttkbootstrap.scrolled import ScrolledFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # 应用现代主题和全局样式
        self.style = Style(theme="flatly")  # 选择 flatly 主题（可选 cosmo、morph 等）
        self.style.configure('.', font=("Microsoft YaHei", 11))  # 设置全局统一字体
        self.title("信息经济学仿真软件")

        # 1) 计算 90 % 的屏幕可视区域
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        width = int(sw * 0.5)
        height = int(sh * 0.8)

        # 2) 设置初始几何并允许用户自由缩放
        self.geometry(f"{width}x{height}+{(sw - width) // 2}+{(sh - height) // 2}")
        self.minsize(800, 600)  # 给个下限，防止拖得太小
        self.resizable(True, True)  # 允许水平、垂直拉伸

        # 顶部标题栏
        header_frame = ttk.Frame(self, style="primary.TFrame")
        header_frame.pack(side="top", fill="x")
        ttk.Label(header_frame, text="信息经济学仿真平台", anchor="center",
                  font=("Microsoft YaHei", 16, "bold"),
                  foreground="white", background=self.style.colors.primary
                  ).pack(pady=10, fill="x")
        # ↑ 注：将顶栏背景设为主题主色(primary)，字体白色，加粗显示应用标题

        # 中央内容区容器（卡片容器布局）
        content_area = ttk.Frame(self, style="light.TFrame")
        content_area.pack(fill="both", expand=True, padx=20, pady=10)
        # ↑ content_area 使用浅色底，周围留白，作为承载各模块页面的容器

        # 底部工具栏
        footer_frame = ttk.Frame(self, style="secondary.TFrame")
        footer_frame.pack(side="bottom", fill="x")
        # 可在底部工具栏放置全局按钮（例如关于或状态信息等），此处简化省略

        # 初始化各模块页面 Frame，并使用网格堆叠它们
        self.frames = {}
        for F in (MainMenu, RiskPreferenceModule, PrincipalAgentModule,
                  AdverseSelectionModule, MoralHazardModule, SignalingModule, ReportView):
            frame = F(content_area, self)
            # 为每个模块Frame应用卡片样式：浅背景色，细边框
            frame.configure(style="TFrame")  # ttkbootstrap 默认 TFrame 背景为主题 bg 色

            frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.frames[F] = frame

        # 让内容区网格可扩展
        content_area.rowconfigure(0, weight=1)
        content_area.columnconfigure(0, weight=1)

        self.show_frame(MainMenu)

    def show_frame(self, page):
        """切换显示指定的模块页面"""
        self.frames[page].tkraise()

    def generate_report_filename(self) -> str:
        """返回形如 20250515_143258_847.txt 的文件名"""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        rand = random.randint(100, 999)
        return f"{ts}_{rand}.txt"

class BaseModule(ttk.Frame):
    """各功能模块页面的基类，提供统一的布局结构"""
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")  # 基础Frame使用主题样式
        self.controller = controller
        # 主内容区 Frame（滚动支持），子类在其中添加控件
        self.content = ScrolledFrame(self, autohide=True)
        self.content.pack(fill="both", expand=True, padx=15, pady=10)
        # 底部导航工具栏（返回主菜单、查看报告等按钮）
        toolbar = ttk.Frame(self)
        toolbar.pack(side="bottom", fill="x", pady=5)
        ttk.Button(toolbar, text="返回主菜单", bootstyle="secondary-outline",
                   command=lambda: controller.show_frame(MainMenu)
                   ).pack(side="left", padx=5)
        ttk.Button(toolbar, text="查看报告", bootstyle="secondary-outline",
                   command=lambda: controller.show_frame(ReportView)
                   ).pack(side="right", padx=5)
        # ↑ 使用 bootstyle="secondary-outline" 创建浅色圆角边框按钮，悬停时会高亮，风格统一

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        # 主菜单界面内容布局
        ttk.Label(self, text="请选择一个模块：", font=("Microsoft YaHei", 12)).pack(pady=20)
        menu_buttons = [
            ("风险偏好", RiskPreferenceModule),
            ("委托代理与激励机制", PrincipalAgentModule),
            ("逆向选择：柠檬市场", AdverseSelectionModule),
            ("道德风险：汽车保险", MoralHazardModule),
            ("信号发送：教育信号", SignalingModule),
            ("仿真报告", ReportView)
        ]
        for txt, FrameClass in menu_buttons:
            ttk.Button(self, text=txt, bootstyle="primary", width=30,
                       command=lambda f=FrameClass: controller.show_frame(f)
                       ).pack(pady=8)
        # ↑ 主菜单按钮使用主题 primary 色填充样式，统一宽度

class RiskPreferenceModule(BaseModule):
    """风险偏好教学演示模块（自动按 γ 判断风险态度）

    主要特性
    -------------
    1. **γ 滑杆决定风险态度**：γ < 1 → 风险厌恶，≈1 → 风险中性，>1 → 风险爱好。
    2. **滑杆实时重绘曲线**：拖动 γ 即时刷新效用曲线与标注，学生可直观观察变化。
    3. **预设三套赌局场景**：一键切换“小波动 / 大波动 / 高概率”。
    4. **日志输出口语化解读**：自动说明 "需要/愿意让出 X 元" 的额外补偿，并用简洁文字解释态度。
    """
    # ------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.calc_count = 0

        # ---------- Tk 变量 -----------------------------------------
        self.gamma_var = tk.DoubleVar(value=0.5)  # 默认风险厌恶
        self.prob_var = tk.DoubleVar(value=0.5)
        self.outcome1_var = tk.DoubleVar(value=150)
        self.outcome2_var = tk.DoubleVar(value=50)

        # ---------- 顶部：γ 滑杆 + 理论按钮 -------------------------
        top = ttk.LabelFrame(self.content, text="风险参数 γ")
        top.pack(fill="x", padx=16, pady=8)

        slider = ttk.Scale(top, from_=0.1, to=3.5, orient="horizontal",
                           variable=self.gamma_var, command=self._on_gamma_change)
        slider.pack(side="left", fill="x", expand=True, padx=(6, 4))
        self.gamma_lbl = ttk.Label(top, text="γ = 0.50 (凹形：厌恶)")
        self.gamma_lbl.pack(side="left", padx=6)
        ttk.Button(top, text="❓理论说明", width=12, command=self._show_theory).pack(side="right", padx=6)

        # ---------- 左侧：参数输入 + 场景按钮 -----------------------
        left = ttk.LabelFrame(self.content, text="赌局参数")
        left.pack(side="left", fill="y", padx=16, pady=8)

        for txt, var in [("概率 p", self.prob_var), ("收益1 w₁", self.outcome1_var), ("收益2 w₂", self.outcome2_var)]:
            ttk.Label(left, text=f"{txt}：").pack(anchor="w")
            ttk.Entry(left, textvariable=var, width=8).pack(fill="x", pady=1)

        scene = ttk.Frame(left)
        scene.pack(pady=6)
        ttk.Button(scene, text="小波动示例", width=9, command=lambda: self._set_scene(0.5, 120, 80)).pack(side="left", padx=2)
        ttk.Button(scene, text="大波动示例", width=9, command=lambda: self._set_scene(0.5, 300, 10)).pack(side="left", padx=2)
        ttk.Button(scene, text="高概率示例", width=9, command=lambda: self._set_scene(0.9, 150, 50)).pack(side="left", padx=2)

        btns = ttk.Frame(left)
        btns.pack(pady=6)
        ttk.Button(btns, text="计算", command=self._compute).pack(side="left", padx=4)
        ttk.Button(btns, text="绘图", command=self._plot).pack(side="left", padx=4)

        self.log = scrolledtext.ScrolledText(left, width=36, height=13)
        self.log.pack(pady=4)

        # ---------- 右侧：Matplotlib 图 ----------------------------
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.content)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10, pady=8)

        # 初始绘制
        self._plot()

    # ===============================================================
    #  工具方法
    # ===============================================================
    def _classify_gamma(self, g: float) -> str:
        if abs(g - 1.0) < 1e-3:
            return "neutral"
        return "averse" if g < 1.0 else "preferring"

    def _util_funcs(self, g: float):
        """返回 (u, u_inv, 表示文本)"""
        if abs(g - 1.0) < 1e-3:
            u = lambda x: x
            u_inv = lambda y: y
            label = "w"
        else:
            u = lambda x, a=g: x ** a
            u_inv = lambda y, a=g: y ** (1 / a)
            label = f"w^{g:.2f}"
        return u, u_inv, label

    # ===============================================================
    #  事件响应
    # ===============================================================
    def _on_gamma_change(self, _evt=None):
        g = self.gamma_var.get()
        pref_txt = {"averse": "凹形：厌恶", "neutral": "线性：中性", "preferring": "凸形：爱好"}[self._classify_gamma(g)]
        self.gamma_lbl.config(text=f"γ = {g:.2f} ({pref_txt})")
        # 实时更新曲线
        self._plot()

    def _set_scene(self, p, w1, w2):
        self.prob_var.set(p)
        self.outcome1_var.set(w1)
        self.outcome2_var.set(w2)
        self._plot()

    # ===============================================================
    #  计算 & 日志
    # ===============================================================
    def _compute(self):
        self.calc_count += 1
        g = self.gamma_var.get()
        p = self.prob_var.get()
        w1, w2 = self.outcome1_var.get(), self.outcome2_var.get()
        u, u_inv, u_name = self._util_funcs(g)
        pref = self._classify_gamma(g)

        U1, U2 = u(w1), u(w2)
        Ew = p * w1 + (1 - p) * w2
        EU = p * U1 + (1 - p) * U2
        CE = u_inv(EU)
        diff = Ew - CE

        # 日志输出
        self.log.insert("end",
                        f"[第{self.calc_count}次] γ={g:.2f} → {pref}\n"
                        f"  U(w): {u_name}\n  E(w) = {Ew:.2f}\n  CE   = {CE:.2f}\n  绝对差 = {diff:.2f}\n")
        self._append_note(Ew, CE)

    def _append_note(self, Ew, CE):
        if abs(CE - Ew) < 1e-6:
            note = "CE 几乎等于 E(w) ⇒ 不需要额外补偿 (风险中性)。"
        elif CE < Ew:
            note = "CE 比 E(w) 小 ⇒ 你得多给我一点补偿，我才愿意冒这个风险。"
        else:
            note = "CE 比 E(w) 大 ⇒ 我愿意自己多花点钱，只为尝试这份冒险。"
        self.log.insert("end", f"  理论说明：{note}\n\n")
        self.log.see("end")

    # ===============================================================
    #  绘图
    # ===============================================================
    def _plot(self):
        g = self.gamma_var.get()
        p = self.prob_var.get()
        w1, w2 = self.outcome1_var.get(), self.outcome2_var.get()
        u, u_inv, _ = self._util_funcs(g)

        # 关键点
        U1, U2 = u(w1), u(w2)
        Ew = p * w1 + (1 - p) * w2
        EU = p * U1 + (1 - p) * U2
        CE = u_inv(EU)
        U_Ew = u(Ew)

        # 曲线范围
        xs = np.linspace(min(w1, w2) * 0.8, max(w1, w2) * 1.2, 400)

        self.ax.clear()
        self.ax.plot(xs, u(xs), label="U(w)")
        self.ax.plot([w1, w2], [U1, U2], color="gray", lw=1, ls="--", label="连线")

        pts = [("A", w1, U1), ("D", w2, U2), ("B", Ew, EU), ("C", Ew, U_Ew), ("E", CE, EU)]
        for lbl, x, y in pts:
            self.ax.scatter(x, y)
            self.ax.text(x, y, f" {lbl}")
            self.ax.vlines(x, min(U1, U2, EU, U_Ew)*0.95, y, color="gray", ls="dotted", lw=0.5)

        self.ax.set_xlabel("财富 w")
        self.ax.set_ylabel("效用 U(w)")
        title = {"averse": "风险厌恶", "neutral": "风险中性", "preferring": "风险爱好"}[self._classify_gamma(g)]
        self.ax.set_title(title)
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()

    # ===============================================================
    #  理论弹窗
    # ===============================================================
    def _show_theory(self):
        g = self.gamma_var.get()
        pref = self._classify_gamma(g)
        notes = {
            "averse": ("风险厌恶 (Risk‑Averse)",
                        "γ < 1，效用函数呈凹形 (如 ln w)。\n确定性等价 CE 会低于期望收益 E(w)。"),
            "neutral": ("风险中性 (Risk‑Neutral)",
                         "γ ≈ 1，效用函数线性 U(w)=w。\nCE 与 E(w) 基本相等。"),
            "preferring": ("风险爱好 (Risk‑Seeking)",
                            "γ > 1，效用函数凸形 (如 w^γ)。\nCE 会高于 E(w)。")
        }
        title, msg = notes[pref]
        messagebox.showinfo(title, msg)

class PrincipalAI:
    """智能委托人：给定代理成本后输出满足 IR+IC 的最优工资"""

    def __init__(self):
        self.U_res = 0.0  # 代理人保留效用
        self.res_high = 0.0  # 高产出收益 Y_H
        self.res_low = 0.0  # 低产出收益 Y_L
        self.p_high = 0.0
        self.p_low = 0.0

    # -------------------------------------------------------------
    def set(self, res_high, res_low, p_high, p_low, U_res=0):
        self.res_high, self.res_low = res_high, res_low
        self.p_high, self.p_low = p_high, p_low
        self.U_res = U_res

    # -------------------------------------------------------------
    def propose_contract(self, c_high, c_low):
        """返回 (w_high, w_low) —— 满足约束且令委托人期望工资最小"""
        self.cost_high_var, self.cost_low_var = c_high, c_low
        Δc = c_high - c_low
        Δp = self.p_high - self.p_low
        Y_H, Y_L = self.res_high, self.res_low
        U0 = self.U_res

        # ---------- 1) 若 Δp≤0 → 兜底 0.5 分成 -------------------
        if Δp <= 1e-8 or Y_H <= Y_L:
            share = 0.5
            return round(share * Y_H, 2), round(share * Y_L, 2)

        # ---------- 2) 先确定“最小分成”满足 IC -------------------
        ΔY = Y_H - Y_L
        b_star = Δc / (Δp * ΔY)  # IC:  b ≥ Δc /(Δp·ΔY)

        if b_star > 1:  # 要求分成>100% → 不可行
            share = 0.5  # 退回 50% 分成
            return round(share * Y_H, 2), round(share * Y_L, 2)

        # ---------- 3) 再求“底薪”满足 IR (取等号最省钱) ----------
        #  努力期望工资  E_w = a + b·E[Y]
        E_Y = self.p_high * Y_H + (1 - self.p_high) * Y_L
        a_star = U0 + c_high - b_star * E_Y  # 使 EU = U0

        # ---------- 4) 调整 a_star 使工资非负且不超产出 ----------
        #  若低产出工资 < 0 → 抬高 a_star 到 w_L = 0
        w_L = a_star + b_star * Y_L
        if w_L < 0:
            a_star += -w_L
            w_L = 0

        #  若高产出工资 > Y_H → 降低 a_star (保持分成不变)
        w_H = a_star + b_star * Y_H
        if w_H > Y_H:
            drop = w_H - Y_H
            a_star -= drop
            w_H = Y_H
            w_L = max(0, a_star + b_star * Y_L)  # 重新算 w_L

        #  最后安全检查：若仍违约束，则退回 50% 分成
        if w_L < 0 or w_H < 0 or w_H > Y_H:
            share = 0.5
            self.w_high, self.w_low = round(share * Y_H, 2), round(share * Y_L, 2)
            return round(share * Y_H, 2), round(share * Y_L, 2)
        self.w_high, self.w_low =round(w_H, 2), round(w_L, 2)
        # ---------- 5) 返回两档工资 ------------------------------
        return round(w_H, 2), round(w_L, 2)


    def agent_income(self, effort):
        if effort == '努力':
            return round(self.p_high * (self.w_high-self.cost_high_var) + (1 - self.p_high) * (self.w_low - self.cost_high_var),2)
        else:
            return round(self.p_low * (self.w_high-self.cost_low_var) + (1 - self.p_low) * (self.w_low - self.cost_low_var),2)

class AgentAI:
    """智能代理人：可评估合同并给出最小 counter-offer"""

    def __init__(self):
        self.cost_high_var = 0.0
        self.cost_low_var = 0.0
        self.U_res = 0.0
        self.p_high = 0.0
        self.p_low = 0.0

    # -------------------------------------------------------------
    def cost_set(self, res_high, res_low):
        """
        为教学演示生成“可行且适中”的努力/偷懒成本。

        规则：
        1. 努力成本 c_H 介于 [5%, 15%]·res_high 之间；
        2. 偷懒成本 c_L 介于 0 ~ 50%·c_H 之间；
        3. 差额 Δc = c_H − c_L 不超过 (res_high − res_low)/4，
           以保证委托人有空间设计满足 IC 的工资差。
        """
        # -- 1) 基于产出规模给出区间 -------------------------------
        hi_min = int(0.05 * res_high)
        hi_max = int(0.15 * res_high)
        c_H = random.randint(hi_min, hi_max)

        # -- 2) c_L 不能太接近 c_H，否则 Δc 太小 --------------------
        lo_max = max(1, int(c_H * 0.5))
        c_L = random.randint(0, lo_max)

        # -- 3) 若 Δc 过大，微调 c_H ↓ 直到可行 ----------------------
        max_gap = (res_high - res_low) / 4
        while (c_H - c_L) > max_gap and c_H > hi_min:
            c_H -= 1

        # -- 4) 保证最终仍满足 c_H > c_L ----------------------------
        if c_H <= c_L:
            c_L = max(0, c_H - 1)

        self.cost_high_var = c_H
        self.cost_low_var = c_L

    def set(self, res_high, res_low, p_high, p_low, U_res=0.0):
        self.p_high, self.p_low = p_high, p_low
        self.res_high, self.res_low = res_high, res_low
        self.U_res = U_res

    # -------------------------------------------------------------
    def _expected_utility(self, w_high, w_low, effort):
        if effort == '努力':
            return self.p_high * (w_high-self.cost_high_var) + (1 - self.p_high) * (w_low - self.cost_high_var)
        else:
            return self.p_low * (w_high- self.cost_low_var) + (1 - self.p_low) * (w_low - self.cost_low_var)

    # -------------------------------------------------------------
    def evaluate_contract(self, w_high, w_low):
        UE = self._expected_utility(w_high, w_low, '努力')
        UL = self._expected_utility(w_high, w_low, '偷懒')
        accept = (UE >= self.U_res) and (UE >= UL)
        self._cache = (UE, UL)
        return accept

    # -------------------------------------------------------------
    def counter_offer(self, w_high, w_low, min_principal_profit: float = 0.0):
        """
        基于纳什分割：在满足 IR、IC 且 π ≥ min_principal_profit 的前提下，
        令双方各获得总剩余 TS 的一半。
        返回新的 (w_high, w_low)，若 TS ≤ 0 则返回 None。
        """
        # 1. 参数
        c_H = self.cost_high_var
        p_H, p_L = self.p_high, self.p_low
        R_H, R_L = self.res_high, self.res_low
        U0 = self.U_res
        π_min = min_principal_profit

        Δc = c_H - self.cost_low_var
        Δp = p_H - p_L
        if Δp <= 0:
            return None   # 参数异常

        # 2. 总剩余 TS
        TE = p_H * R_H + (1-p_H) * R_L - c_H
        TS = TE - π_min - U0
        if TS <= 0:
            return None   # 无可行合同

        # 3. 工资差 s 保证 IC
        s = Δc / Δp

        # 4. 期望工资目标 E_w = c_H + U0 + TS/2
        E_w = c_H + U0 + TS / 2

        # 5. 解出 w_low, w_high
        w_L_new = E_w - p_H * s
        w_H_new = w_L_new + s

        # 6. 若 w_L < 0，可退回最小 IR+IC 合同（或按比例调整；此处取保守抹零）
        if w_L_new < 0:
            # 最小 IC+IR：w_H - w_L = s，且满足 EU=U0
            # p_H w_H + (1-p_H)w_L = c_H + U0
            w_L_alt = (c_H + U0 - p_H * s)
            w_H_alt = w_L_alt + s
            if w_L_alt < 0:
                return None
            return round(w_H_alt, 2), round(w_L_alt, 2)

        return round(w_H_new, 2), round(w_L_new, 2)

        # -------------------------------------------------------------

    def choose_effort(self, w_high, w_low):
        UE, UL = self._cache if hasattr(self, "_cache") else \
            (self._expected_utility(w_high, w_low, '努力'),
             self._expected_utility(w_high, w_low, '偷懒'))
        return '努力' if UE >= UL else '偷懒'

    # -------------------------------------------------------------
    def principal_income(self, effort, w_high, w_low):
        """委托人期望利润（用于日志反馈）"""
        if effort == '努力':
            return self.p_high * (self.res_high - w_high) + \
                   (1 - self.p_high) * (self.res_low - w_low)
        else:
            return self.p_low * (self.res_high - w_high) + \
                   (1 - self.p_low) * (self.res_low - w_low)

class PrincipalAgentModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.user_role = None
        self.principalAI = PrincipalAI()
        self.agentAI = AgentAI()
        self.vars = {}
        self.count = 0
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.content)
        # self.title_label = ttk.Label(self.main_frame,text='', font=(None, 16)).pack(pady=10)
        self.main_frame.pack(padx=10, pady=10, fill="x")
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(padx=10, pady=10, fill="x")

        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(padx=10, pady=10, fill="x")

        log_frame = ttk.Frame(self.main_frame)
        log_frame.pack(side='bottom', fill='x')
        self.log = scrolledtext.ScrolledText(log_frame, width=80, height=12)
        self.log.pack(fill='x', padx=5, pady=5)
        self.render_role_selection()

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def clear_button(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()

    def render_role_selection(self):
        self.count += 1
        self.clear_content()
        self.clear_button()
        ttk.Label(self.content_frame,
                  text="情景背景：股东（委托人）雇佣经理（代理人）管理企业。由于信息不对称，股东无法直接观察经理的努力程度，需要设计激励合同约束经理行为。",
                  wraplength=600).pack(pady=5)
        ttk.Label(self.content_frame, text="请设置自然变量：", font=(None, 12, 'bold')).pack(pady=10)
        self.rev_high_var = tk.DoubleVar(value=100)
        self.rev_low_var = tk.DoubleVar(value=20)
        self.p_high_var = tk.DoubleVar(value=0.8)
        self.p_low_var = tk.DoubleVar(value=0.4)
        for text, var in [('高产出收益', self.rev_high_var),
                          ('低产出收益', self.rev_low_var),
                          ('努力时高产出概率', self.p_high_var),
                          ('偷懒时高产出概率', self.p_low_var)]:
            row = ttk.Frame(self.content_frame)
            row.pack(pady=5)
            ttk.Label(row, text=text + '：').pack(side='left', padx=2)
            ttk.Entry(row, textvariable=var, width=8).pack(side='left')
        self.agentAI.cost_set(self.rev_high_var.get(), self.rev_low_var.get())
        ttk.Label(self.content_frame, text="\n请选择您的角色：", font=(None, 12, 'bold')).pack(pady=10)
        self.role_var = tk.StringVar(value='principal')
        ttk.Radiobutton(self.content_frame, text="股东(委托人)", variable=self.role_var, value='principal').pack()
        ttk.Radiobutton(self.content_frame, text="经理(代理人)", variable=self.role_var, value='agent').pack()
        ttk.Button(self.btn_frame, text="确认", command=self.on_role_confirm).pack(pady=10)

    def on_role_confirm(self):
        self.user_role = self.role_var.get()
        if self.user_role == 'principal':
            self.role_CN = '股东'
        else:
            self.role_CN = '经理'
        # 默认模型参数
        self.vars = {'高产出收益': self.rev_high_var.get(),
                     '低产出收益': self.rev_low_var.get(),
                     '努力时高产出概率': self.p_high_var.get(),
                     '偷懒时高产出概率': self.p_low_var.get()}
        self.log.insert('end', f"第{self.count}次实验，您选择了角色：{self.role_CN}\n")
        self.log.insert('end', f"高产出收益: {self.rev_high_var.get()}\n低产出收益: {self.rev_low_var.get()}\n努力时高产出概率: {self.p_high_var.get()}\n偷懒时高产出概率: {self.p_low_var.get()}\n\n")
        self.log.see('end')
        # ### >>> 教学增强 2：角色提示
        if self.user_role == 'principal':
            self._popup(
                "角色提示：委托人",
                "您将设计激励合同。\n请同时满足：\n"
                "  • 参与约束 (IR)：经理愿意接受合同\n"
                "  • 激励约束 (IC)：经理更愿意努力而非偷懒")
        else:
            self._popup(
                "角色提示：代理人",
                "您将报出自身成本、保留效用。\n"
                "这些信息决定委托人怎样为您设计合同。")
        self.after(500, self.render_contract_design)

    def render_contract_design(self):
        self.clear_button()
        self.clear_content()
        if self.user_role == 'principal':
            ttk.Label(self.content_frame, text="股东界面\n", font=(None, 16, 'bold')).grid(row=0, column=2, sticky="n", pady=10)
            # self.title_label.config(text = "委托人界面")
            params = ["高产出收益", "低产出收益", "努力时高产出概率", "偷懒时高产出概率"]
            ttk.Label(self.content_frame, text="--- 自然信息 ---", font=(None, 10, 'bold')).grid(row=1, column=0, padx=10)
            for i, name in enumerate(params):
                ttk.Label(self.content_frame, text=f"{name}: ").grid(row=i + 2, column=0, sticky="e", pady=5)
                var = self.vars[name]
                ttk.Label(self.content_frame, text=f"{var}").grid(row=i + 2, column=1, sticky="w", pady=5)

            ttk.Label(self.content_frame, text="--- 合同条款 ---", font=(None, 10, 'bold')).grid(row=1, column=2, padx=20)
            self.w_high_var = tk.DoubleVar(value=60)
            self.w_low_var = tk.DoubleVar(value=10)

            ttk.Label(self.content_frame, text="高产出工资: ").grid(row=2, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.w_high_var).grid(row=2, column=3, sticky="w")
            ttk.Label(self.content_frame, text="低产出工资: ").grid(row=3, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.w_low_var).grid(row=3, column=3, sticky="w")

            self.set_AI_var(self.rev_high_var.get(), self.rev_low_var.get(), self.p_high_var.get(), self.p_low_var.get())
            self.agent_information()

            ttk.Button(self.btn_frame, text="提交合同", command=self.on_submit_contract).pack(padx=10)
            # ### >>> 教学增强 3：IC/IR 提示行
            tip_frame = ttk.Frame(self.content_frame)
            tip_frame.grid(row=4, column=2, columnspan=2, pady=(6, 2), sticky="w")
            ttk.Label(tip_frame, text="📘 提示：为激励经理努力，需要 w高−w低 ≥ Δc  (IC)  且  经理期望效用 ≥ 保留效用 (IR)",
                      foreground="steelblue").pack(side="left")
            # 详细说明按钮
            self._add_info_button(
                tip_frame, "IC / IR 公式",
                "IC: p_H·(w_H−c_H)+(1−p_H)(w_L−c_L) ≥ p_L·(w_H−c_L)+(1−p_L)(w_L−c_L)\n"
                "IR: 上式左端 ≥ 保留效用 U_res").pack(side="left", padx=2)
        else:
            ttk.Label(self.content_frame, text="经理界面\n", font=(None, 16, 'bold')).grid(row=0, column=2, sticky="n", pady=10)
            params = ["高产出收益", "低产出收益", "努力时高产出概率", "偷懒时高产出概率"]
            ttk.Label(self.content_frame, text="--- 自然信息 ---", font=(None, 10, 'bold')).grid(row=1, column=0, padx=10)
            for i, name in enumerate(params):
                ttk.Label(self.content_frame, text=f"{name}: ").grid(row=i + 2, column=0, sticky="e", pady=5)
                var = self.vars[name]
                ttk.Label(self.content_frame, text=f"{var}").grid(row=i + 2, column=1, sticky="w", pady=5)

            ttk.Label(self.content_frame, text="--- 经理信息 ---", font=(None, 10, 'bold')).grid(row=1, column=2, padx=10)
            self.cost_high_var = tk.DoubleVar(value=10)
            self.cost_low_var = tk.DoubleVar(value=5)
            self.reserve_var = tk.DoubleVar(value=0)

            ttk.Label(self.content_frame, text="努力成本: ").grid(row=2, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.cost_high_var).grid(row=2, column=3, sticky="w")
            ttk.Label(self.content_frame, text="偷懒成本: ").grid(row=3, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.cost_low_var).grid(row=3, column=3, sticky="w")
            ttk.Label(self.content_frame, text="保留效用: ").grid(row=4, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.reserve_var).grid(row=4, column=3, sticky="w")

            self.set_AI_var(self.rev_high_var.get(), self.rev_low_var.get(), self.p_high_var.get(), self.p_low_var.get())

            ttk.Button(self.btn_frame, text="提交信息", command=self.system_propose_contract).pack(padx=10)
            # ### >>> 教学增强 6：按钮提示
            tip = ttk.Label(self.btn_frame, text="📘 提示：接受 = 期望效用 ≥ 保留效用；\n         拒绝 = 放弃交易 (效用 = 保留效用)",
                            foreground="steelblue")
            tip.pack()
            self._add_info_button(
                self.btn_frame, "努力动力？",
                "思考：合同给予的 w高−w低 是否足以让你努力？").pack()

    # 将自然信息的值传给自定义的系统AI
    def set_AI_var(self, rev_high_var, rev_low_var, p_high_var, p_low_var):
        self.agentAI.set(rev_high_var, rev_low_var, p_high_var, p_low_var)
        self.principalAI.set(rev_high_var, rev_low_var, p_high_var, p_low_var)

    # 委托人提交合同
    def on_submit_contract(self):
        # ### >>> 教学增强 4：思考提问
        self._popup("思考",
                    "你认为经理会接受这份合同吗？为什么？\n"
                    "请回想 IC 与 IR 条件。")
        w1, w2 = self.w_high_var.get(), self.w_low_var.get()
        if w1 < w2:
            messagebox.showinfo("错误", "高产出工资不应小于低产出工资！")
            self.render_contract_design()
        else:
            self.w1_sys, self.w2_sys = w1, w2
            self.log.insert('end', f"您提交合同: w_high={w1}, w_low={w2}\n经理（系统）正在评估...\n")
            self.log.see('end')
            self.after(1000, lambda: self.system_evaluate_contract(w1, w2))

    # 代理人信息
    def agent_information(self):
        cost_high_var = self.agentAI.cost_high_var
        cost_low_var = self.agentAI.cost_low_var
        reserve_var = self.agentAI.U_res
        self.log.insert('end', f"经理的信息如下:\n努力成本：{cost_high_var}\n偷懒成本：{cost_low_var}\n保留效用: {reserve_var}\n")
        self.log.see('end')

    def system_propose_contract(self):
        self.clear_button()
        if self.cost_high_var.get() < self.cost_low_var.get():
            messagebox.showinfo("错误", "努力成本不应小于偷懒成本！")
            self.render_contract_design()
        else:
            self.log.insert('end', "您的信息如下\n")
            self.log.insert('end', f"努力成本：{self.cost_high_var.get()}\n")
            self.log.insert('end', f"偷懒成本：{self.cost_low_var.get()}\n")
            self.log.insert('end', f"保留效用：{self.reserve_var.get()}\n")
            self.log.insert('end', "股东（系统）正在计算最优合同...\n")
            self.log.see('end')
            # —— 基于代理人输入的成本，直接计算最优合同 ——
            w1, w2 = self.principalAI.propose_contract(
                self.cost_high_var.get(), self.cost_low_var.get())
            self.w1_sys, self.w2_sys = w1, w2
            self.log.insert('end', f"股东（系统）提出合同: 高产出工资 = {w1}, 低产出工资 = {w2}\n")
            self.log.see('end')
            ttk.Button(self.btn_frame, text="接受合同", command=self.on_accept_contract).pack(pady=5)
            ttk.Button(self.btn_frame, text="拒绝合同", command=self.on_reject_contract).pack(pady=5)

    # 委托人重新填写合同
    def system_evaluate_contract(self, w1, w2):
        accept = self.agentAI.evaluate_contract(w1, w2)
        if accept:
            self.log.insert('end', "经理（系统）接受合同\n")
            self.log.see('end')
            self.after(500, self.render_effort_stage)
            # ### >>> 教学增强 5：结果解释
            self._explain_contract_result(accept)
        else:
            # —— 生成最小 counter-offer ——
            offer = self.agentAI.counter_offer(w1, w2)  # ← 可能返回 None
            if offer is None:
                self.log.insert('end',
                                "系统(代理人)评估后认为：在不损害委托人利益的前提下，不存在满足自身约束的改进合同，故拒绝。\n")
                self.log.see('end')
                return
            w1_new, w2_new = offer
            self.log.insert('end', "经理（系统）拒绝该合同\n"
                            f"建议的无损委托合同：\n"
                            f"  高产出工资 = {w1_new}, 低产出工资 = {w2_new}\n")
            self.log.see('end')
            # 让用户直接看到调整后的数值
            self.w_high_var.set(w1_new)
            self.w_low_var.set(w2_new)
            # ### >>> 教学增强 5：结果解释
            self._explain_contract_result(accept)

    # 代理人接受合同情况
    def on_accept_contract(self):
        self.log.insert('end', "您接受了合同，请选择努力/偷懒...\n")
        self.log.see('end')
        self.after(1000, self.render_effort_stage)

    # 代理人拒绝合同情况
    def on_reject_contract(self):
        self.log.insert('end', "您拒绝了合同，返回合同设计\n")
        self.log.see('end')
        self.after(500, self.render_contract_design)

    def render_effort_stage(self):
        self.clear_content()
        self.clear_button()
        if self.user_role == 'principal':
            self.log.insert('end', "经理（系统）正在选择努力/偷懒...\n")
            self.log.see('end')
            self.after(1000, self.system_choose_effort)
        else:
            ttk.Label(self.content_frame, text="请选择您的努力水平：").pack(pady=10)
            self.effort_var = tk.StringVar(value='努力')
            ttk.Radiobutton(self.content_frame, text="努力", variable=self.effort_var, value='努力').pack()
            ttk.Radiobutton(self.content_frame, text="偷懒", variable=self.effort_var, value='偷懒').pack()
            ttk.Button(self.btn_frame, text="提交选择", command=self.on_submit_effort).pack(pady=10)

    def system_choose_effort(self):
        effort = self.agentAI.choose_effort(self.w_high_var.get(), self.w_low_var.get())
        self.log.insert('end', f"经理（系统）选择: {effort}\n")
        self.log.see('end')
        self.income = self.agentAI.principal_income(effort, self.w_high_var.get(), self.w_low_var.get())
        self.after(500, self.render_result)

    def on_submit_effort(self):
        effort = self.effort_var.get()
        self.log.insert('end', f"您选择: {effort}\n股东（系统）正在计算结果...\n")
        self.log.see('end')
        self.income = self.principalAI.agent_income(effort)
        self.after(1000, self.render_result)

    def render_result(self):
        self.clear_content()
        self.clear_button()
        self.log.insert('end', f"您最后的收益为{self.income}\n\n\n\n\n")
        ttk.Label(self.content_frame, text="仿真结束，详情见日志").pack(pady=20)
        # 绘制收益-效用图表
        # 准备数据：以高产出工资为横轴
        rev_high = self.rev_high_var.get()
        rev_low  = self.rev_low_var.get()
        p_high   = self.p_high_var.get()
        p_low    = self.p_low_var.get()
        cost_high = self.agentAI.cost_high_var
        cost_low  = self.agentAI.cost_low_var
        w_l = max(self.w2_sys, 0)
        w_values = np.linspace(w_l, rev_high*1.2, 100)
        profits = []
        utils = []
        # 计算每个工资水平下的股东收益和经理效用
        # 假设低产出工资 w_L = 0（示意可视化效果）

        for w in w_values:
            U_high = p_high * (w - cost_high) + (1 - p_high) * (w_l - cost_high)
            U_low  = p_low  * (w - cost_low) + (1 - p_low)  * (w_l - cost_low)
            if U_high >= U_low:
                # 经理选择努力
                profit = p_high * (rev_high - w) + (1 - p_high) * (rev_low - w_l)
                util   = U_high
            else:
                # 经理选择偷懒
                profit = p_low  * (rev_high - w) + (1 - p_low)  * (rev_low - w_l)
                util   = U_low
            profits.append(profit)
            utils.append(util)

        # 绘制图表
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(w_values, profits, label="股东收益")
        ax.plot(w_values, utils,   label="经理效用")
        ax.set_xlabel("高产出工资")
        ax.set_ylabel("收益 / 效用")
        ax.legend()
        ax.set_title("股东收益与经理效用随合同的变化")
        # 将图表嵌入Tkinter界面
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        ttk.Button(self.btn_frame, text="重新开始", command=self.render_role_selection).pack(pady=5)
        # ttk.Button(self.btn_frame, text="退出", command=self.destroy).pack(pady=5)

        # ### >>> 教学增强 1：工具方法

    def _popup(self, title: str, msg: str):
        """通用弹窗。"""
        messagebox.showinfo(title, msg)

    def _add_info_button(self, parent, hint: str, detail: str):
        """在某控件旁放一个“❓”按钮，点击弹详细说明。"""
        btn = ttk.Button(parent, text="❓", width=2,
                         command=lambda: self._popup(hint, detail))
        return btn

    def _explain_contract_result(self, accepted: bool):
        """系统评估合同后，日志附教学解释。"""
        if accepted:
            self.log.insert('end',
                            "*(教学) 合同满足 IR(参与约束) 和 IC(激励约束)，经理接受并更可能努力。*\n")
        else:
            self.log.insert('end',
                            "*(教学) 合同未满足 IR 或 IC —— 经理拒绝；请提高绩效差或总体报酬。*\n")
        self.log.see('end')

class PrincipalPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

class AgentPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

class LemonMarketSimulator:
    """Discrete‑time simulator for Akerlof's lemon market with adaptive trust."""
    def __init__(
            self,
            total_cars: int = 100,
            q0: float = 0.5,
            V_high: float = 2400,
            V_low: float = 1200,
            beta: float = 0.3,
            gamma: float = 0.2,
            steps: int = 30,
            seed: int | None = None,
    ) -> None:
        if seed is not None:
            np.random.seed(seed)
        self.total_cars = total_cars
        self.high = int(round(total_cars * q0))
        self.low = total_cars - self.high
        self.tau = q0
        self.Vh, self.Vl = V_high, V_low
        self.beta, self.gamma = beta, gamma
        self.steps = steps
        # history containers --------------------------------------------------
        self.history: dict[str, list[float]] = {
            "high": [], "low": [], "q": [], "tau": [], "price": []}

    # ---------------------------------------------------------------------
    def _step(self) -> None:
        q_t = self.high / max(self.high + self.low, 1)
        p_t = self.tau * self.Vh + (1 - self.tau) * self.Vl
        # High‑quality sellers exit proportionally if p_t below reservation.
        if p_t < self.Vh and self.high > 0:
            exit_ratio = self.gamma * (1 - p_t / self.Vh)
            exit_num = max(1, int(round(self.high * exit_ratio)))
            self.high -= min(exit_num, self.high)
        # Buyers update trust towards *observed* share of good cars.
        self.tau += self.beta * (q_t - self.tau)
        # clamp tau to [0,1].
        self.tau = max(0.0, min(1.0, self.tau))
        # log ----------------------------------------------------------------
        self.history["high"].append(self.high)
        self.history["low"].append(self.low)
        self.history["q"].append(q_t)
        self.history["tau"].append(self.tau)
        self.history["price"].append(p_t)

class AdverseSelectionModule(BaseModule):
    """UI & controller for the lemon market simulation."""
    # ---------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_left_panel()
        self._build_right_panel()
        self.sim_data: dict[str, list[float]] | None = None

        # ### >>> 逆向选择教学 1：弹窗 + 小按钮

    def _popup(self, title: str, msg: str):
        messagebox.showinfo(title, msg)

    def _info_btn(self, parent, title: str, detail: str):
        """在 parent 中生成一个❓按钮，点击弹出 detail。"""
        return ttk.Button(parent, text="❓", width=2,
                          command=lambda: self._popup(title, detail))

    # ------------------------------------------------------------------ UI
    def _build_left_panel(self) -> None:
        left = ttk.Frame(self.content)
        left.pack(side="left", fill="y", padx=12, pady=10)

        # ------ title
        ttk.Label(left, text="柠檬市场参数设置", font=(None, 12, "bold")).pack(pady=4)

        self.total_var = tk.IntVar(value=100)
        self.q0_var = tk.DoubleVar(value=0.5)
        # self.tau0_var = tk.DoubleVar(value=0.5)
        self.Vh_var = tk.DoubleVar(value=2400)
        self.Vl_var = tk.DoubleVar(value=1200)
        self.beta_var = tk.DoubleVar(value=0.3)
        self.gamma_var = tk.DoubleVar(value=0.2)
        self.T_var = tk.IntVar(value=30)

        _rows = [
            ("总车辆数", self.total_var, 10, 500, 1),
            ("初始高质量比例", self.q0_var, 0.0, 1.0, 0.01),
            ("高质量价值", self.Vh_var, 500, 5000, 50),
            ("低质量价值", self.Vl_var, 0, 4000, 50),
            ("信任调整速度", self.beta_var, 0.05, 1.0, 0.05),
            ("卖家退出敏感", self.gamma_var, 0.05, 1.0, 0.05),
            ("仿真周期数", self.T_var, 5, 200, 1),
        ]
        for label, var, frm, to, inc in _rows:
            ttk.Label(left, text=label).pack(anchor="w", pady=1)
            if isinstance(var, tk.IntVar):
                ttk.Spinbox(left, from_=frm, to=to, textvariable=var,
                            increment=inc, width=10).pack(fill="x")
            else:
                ttk.Scale(left, from_=frm, to=to, orient="horizontal",
                          variable=var).pack(fill="x")
                ttk.Entry(left, textvariable=var, width=8).pack(anchor="e")

        # ### >>> 逆向选择教学 2：参数说明行
        explain = ttk.LabelFrame(left, text="参数含义")
        explain.pack(fill="x", pady=4)

        # 初始高质量比例 q0
        row = ttk.Frame(explain); row.pack(anchor="w")
        ttk.Label(row, text="初始高质量比例").pack(side="left")
        self._info_btn(row, "说明",
                       "初始市场中高质量(好车)所占比例。\n"
                       "q₀ 越高，买家初始信任越强，价格越接近好车价值。"
                       ).pack(side="left")

        # 信任调整速度 β
        row = ttk.Frame(explain); row.pack(anchor="w")
        ttk.Label(row, text="信任调整速度").pack(side="left")
        self._info_btn(row, "说明",
                       "买家根据观察到的质量比例更新信任的快慢。\n"
                       "β 越大，价格对市场质量变化反应越迅速。"
                       ).pack(side="left")

        # 卖家退出敏感 γ
        row = ttk.Frame(explain); row.pack(anchor="w")
        ttk.Label(row, text="卖家退出敏感").pack(side="left")
        self._info_btn(row, "说明",
                       "好车卖家因价格低于价值而退出的敏感程度。\n"
                       "γ 越大，价格偏低时好车退出越快。"
                       ).pack(side="left")

        # ---------- action buttons
        btns = ttk.Frame(left)
        btns.pack(pady=8)
        ttk.Button(btns, text="开始模拟", command=self._on_run).pack(side="left", padx=4)
        ttk.Button(btns, text="导出 CSV", command=self._export_csv).pack(side="left", padx=4)

        # ----------- log box
        ttk.Label(left, text="日志").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(left, height=12, width=34)
        self.log.pack(fill="both", expand=False)

    # ------------------------------------------------------------------ UI
    def _build_right_panel(self) -> None:
        right = ttk.Frame(self.content)
        right.pack(side="right", fill="both", expand=True, padx=5)
        self.fig, self.ax1 = plt.subplots(figsize=(6, 4))
        self.ax2 = self.ax1.twinx()
        self.ax1.set_xlabel("周期 t")
        self.ax1.set_ylabel("车辆数量")
        self.ax2.set_ylabel("价格(p)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------------------------------------------------------- run
    # ### >>> 逆向选择教学 3：改写 _on_run()
    def _on_run(self) -> None:
        self.log.insert("end",
                        f"参数：q₀={self.q0_var.get():.2%}  β={self.beta_var.get()}  γ={self.gamma_var.get()}  T={self.T_var.get()}期\n")
        # 1. 读取参数并新建模拟器
        sim = LemonMarketSimulator(
            total_cars=self.total_var.get(),
            q0=self.q0_var.get(),
            V_high=self.Vh_var.get(),
            V_low=self.Vl_var.get(),
            beta=self.beta_var.get(),
            gamma=self.gamma_var.get(),
            steps=self.T_var.get(),
        )
        self.log.delete("1.0", "end")
        self.log.insert("end", "[INFO] 开始仿真…\n")
        init_high = sim.high
        init_price = sim.tau * sim.Vh + (1 - sim.tau) * sim.Vl

        # 2. 逐期手动执行 _step()，便于插入日志
        for t in range(1, sim.steps + 1):
            sim._step()
            hi = sim.history["high"][-1]
            q = sim.history["q"][-1]
            p = sim.history["price"][-1]
            # —— 每 5 期或关键事件输出一次 —— #
            if t % 5 == 0 or hi == 0:
                self.log.insert("end",
                                f"第 {t:02d} 期：价格 p={p:.1f}，好车占比 q={q:.2%}\n")
            if hi == 0:
                self.log.insert("end",
                                "⚠ 高质量汽车全部退出，市场崩溃！\n")
                break

        self.sim_data = sim.history
        self._draw()  # 更新图表

        # 3. 结束总结
        final_high = sim.history['high'][-1]
        final_q = sim.history['q'][-1]
        final_p = sim.history['price'][-1]
        self.log.insert("end", "\n—— 仿真总结 ——\n")
        self.log.insert("end",
                        f"高质量车数量：{init_high} → {final_high}\n"
                        f"价格：{init_price:.1f} → {final_p:.1f}\n")
        if final_high == 0:
            self.log.insert("end",
                            "**发生逆向选择**：好车全部退出，只剩劣质产品。\n")
        else:
            self.log.insert("end",
                            f"**部分逆向选择**：好车比例下降至 {final_q:.2%}，但未完全退出。\n")

        # 4. 引导思考问题
        self._popup(
            "思考",
            "观察价格与好车占比的曲线：\n"
            "• 价格下跌速度是否随 信任调整速度和卖家退出敏感 增大而加快？\n"
            "• 如果把 初始高质量比例 调高，会缓解好车退出吗？\n"
            "尝试修改参数重新模拟以验证你的猜想。")
        self.log.see("end")

    # ---------------------------------------------------------------- draw
    def _draw(self) -> None:
        if not self.sim_data:
            return
        t = np.arange(1, len(self.sim_data["q"]) + 1)
        self.ax1.clear(); self.ax2.clear()
        self.ax1.plot(t, self.sim_data["high"], label="高质量", linestyle="-", marker="o")
        self.ax1.plot(t, self.sim_data["low"], label="低质量", linestyle="--", marker="x")
        self.ax1.legend(loc="upper left")
        self.ax1.set_xlabel("周期 t"); self.ax1.set_ylabel("车辆数量")
        # self.ax2.plot(t, self.sim_data["tau"], label="买家信任 τ", linestyle=":")
        self.ax2.plot(t, self.sim_data["price"], label="价格 p", linestyle="-")
        self.ax2.legend(loc="upper right")
        self.ax2.set_ylabel("信任(τ) / 价格(p)")
        self.fig.tight_layout()
        self.canvas.draw()

    # --------------------------------------------------------------- export
    def _export_csv(self) -> None:
        if not self.sim_data:
            messagebox.showinfo("提示", "请先运行一次模拟！")
            return
        fname = filedialog.asksaveasfilename(
            title="保存仿真结果",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")],
            initialfile=datetime.datetime.now().strftime("lemon_%Y%m%d_%H%M%S.csv"),
        )
        if not fname:
            return
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = ["t", "high", "low", "q", "tau", "price"]
            writer.writerow(headers)
            for i in range(len(self.sim_data["q"])):
                row = [i + 1] + [self.sim_data[k][i] for k in headers[1:]]
                writer.writerow(row)
        messagebox.showinfo("成功", f"结果已保存至 {fname}")

class MoralHazardModule(BaseModule):
    """Hidden‑action moral hazard simulator with variable risk preference."""
    # ------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_ui()

        # ### >>> 道德风险教学 1：通用弹窗+按钮

    def _popup(self, title: str, msg: str):
        messagebox.showinfo(title, msg)

    def _info_btn(self, parent, title: str, detail: str):
        btn = ttk.Button(parent, text="❓", width=2,
                         command=lambda: self._popup(title, detail))
        btn.pack(side="left", padx=2)

    # ---------------------------- UI ----------------------------------
    def _build_ui(self):
        left = ttk.Frame(self.content)
        left.pack(side="left", fill="y", padx=14, pady=10)

        ttk.Label(left, text="参数设置", font=(None, 12, "bold")).pack(pady=4)

        # model parameters vars
        self.w_var = tk.DoubleVar(value=100_000)
        self.d_var = tk.DoubleVar(value=20_000)
        self.p_var = tk.DoubleVar(value=0.25)
        self.pd_var = tk.DoubleVar(value=0.15)
        self.c_var = tk.DoubleVar(value=1_950)
        self.q_var = tk.DoubleVar(value=0.00)
        self.gamma_var = tk.DoubleVar(value=1.00)  # CRRA coefficient γ

        params = [
            ("初始财富 w", self.w_var,
             "张三最开始拥有的财富，用于衡量损失对他的影响。"),
            ("汽车价值 d", self.d_var,
             "车辆被盗后造成的经济损失金额。"),
            ("盗窃概率 p", self.p_var,
             "未安装防盗装置时被盗概率。"),
            ("装置后概率 p_d", self.pd_var,
             "安装防盗装置后被盗概率（应低于 p）。"),
            ("装置成本 c_d", self.c_var,
             "购买并安装防盗装置需要支付的成本。"),
        ]
        for label, var, tip in params:
            row = ttk.Frame(left); row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{label}：", width=13, anchor="e").pack(side="left")
            ttk.Entry(row, textvariable=var, width=10).pack(side="left")
            self._info_btn(row, label, tip)

        # ----------- ② 风险偏好 & 道德风险 Δp -------------------------
        extra = [
            ("风险偏好 γ", self.gamma_var,
             "CRRA 风险厌恶系数：γ>0 越大越厌恶风险，γ≈0 近似风险中性。"),
            ("道德风险 Δp", self.q_var,
             "投保后因懈怠增加的额外盗窃概率。\n"
             "Δp>0 表示张三不再安装装置导致风险回升。"),
        ]
        for label, var, tip in extra:
            ttk.Label(left, text=label).pack(anchor="w", pady=1)
            # 滑杆 + 输入框放一行
            row = ttk.Frame(left); row.pack(fill="x")
            ttk.Scale(row, from_=-1 if 'γ' in label else 0,
                      to=3 if 'γ' in label else 1.0,
                      orient="horizontal", variable=var).pack(fill="x", expand=True, side="left")
            ttk.Entry(row, textvariable=var, width=6).pack(side="left", padx=3)
            self._info_btn(row, label, tip)

        ttk.Button(left, text="模拟决策", command=self._simulate).pack(pady=8, fill="x")
        ttk.Button(left, text="随机演示一次", command=self._random_demo).pack(pady=2, fill="x")

        # right pane: output
        self.log = scrolledtext.ScrolledText(self.content, width=62, height=32)
        self.log.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self._write_intro()

    # --------------------------- intro --------------------------------
    def _write_intro(self):
        intro = (
            "模块说明\n"
            "  本工具演示完全保险导致的隐藏行动道德风险：投保后张三不再主动安装防盗装置，使盗窃概率回升 (加上 Δp)。\n"
            "  您可通过风险厌恶系数 γ 观察不同风险偏好对“是否投保 / 是否安装装置”决策的影响。\n"
            "  γ=1 为对数效用，γ>0 风险厌恶，γ=0 风险中性，γ<0 风险爱好。\n\n"
        )
        self.log.insert("end", intro)
        self.log.see("end")

    # --------------------------- utility ------------------------------
    @staticmethod
    def _utility(w, gamma):
        if w <= 0:
            return -float('inf')  # disallow non‑positive wealth
        if abs(gamma - 1.0) < 1e-8:
            return math.log(w)
        else:
            return (w ** (1 - gamma) - 1) / (1 - gamma)

    # --------------------------- simulation ---------------------------
    def _simulate(self):
        # read parameters
        w, d, p, p_d, c_d, q, gamma = (self.w_var.get(), self.d_var.get(), self.p_var.get(),
                                       self.pd_var.get(), self.c_var.get(), self.q_var.get(),
                                       self.gamma_var.get())
        # fair premium (insurer assumes no device, prob=p)
        premium = d * p

        util = lambda wealth: self._utility(wealth, gamma)

        # ------ decisions if No insurance --------------------------------
        EU_no_dev = (1 - p) * util(w) + p * util(w - d)
        EU_dev = (1 - p_d) * util(w - c_d) + p_d * util(w - d - c_d)
        install_no_ins = EU_dev > EU_no_dev
        EU_no_ins_opt = max(EU_no_dev, EU_dev)

        # ------ Full insurance decisions ---------------------------------
        U_no_dev = util(w - premium)
        U_dev = util(w - premium - c_d)
        install_ins = U_dev > U_no_dev  # still unlikely

        would_insure = U_no_dev >= EU_no_ins_opt  # compare with optimal uninsured

        # ------ moral hazard extra loss ----------------------------------
        base_prob = p_d if install_ins else p
        prob_actual = min(max(base_prob + q, 0.0), 1.0)
        extra_loss = d * (prob_actual - p) if prob_actual > p else 0.0

        # ------------------- print report --------------------------------
        # ---------- 教学解读 ---------------------------------------
        def explain_install(flag):
            return "(安装装置降低风险成本高于收益)" if not flag else \
                "(在无保险情况下，自费降低风险是最优)"

        self.log.insert("end", "\n—— 结果解读 ——\n")

        # 无保险说明
        note_unins = ("（安装装置降低风险成本高于收益，张三更愿意承担风险）"
                      if not install_no_ins else
                      "（说明在无保险情况下，通过自付成本降低风险最优）")
        self.log.insert("end", f"· 无保险：{note_unins}\n")

        # 保险说明
        if not would_insure:
            self.log.insert("end",
                            "· 全额保险：张三拒绝保险（确定损失高于承担风险的期望损失）。\n")
        else:
            if not install_ins:
                self.log.insert("end",
                                "· 投保后张三不安装装置 → 道德风险：有了保险缺乏动机防盗。\n")
            else:
                self.log.insert("end",
                                "· 投保后仍安装装置（风险厌恶且装置成本低）。\n")
            self.log.insert("end",
                            f"· 额外预期赔付 Δ = {extra_loss:.2f} —— 保险公司承担的道德风险成本。\n")

        # ---------- 小结 ------------------------------------------
        self.log.insert("end", "\n—— 参数 & 决策小结 ——\n")
        self.log.insert("end",f"w={w:.0f}  d={d:.0f}  p={p:.2f}  p_d={p_d:.2f}  c_d={c_d:.0f}  γ={gamma:.2f}\n")
        self.log.insert("end",f"无保险：{'安装' if install_no_ins else '不装'}  EU={EU_no_ins_opt:.4f}\n")
        self.log.insert("end",f"有保险：{'投保' if would_insure else '不投保'}, {'安装' if install_ins else '不装'}  U={U_dev if install_ins else U_no_dev:.4f}\n\n")

        # ---------- 讨论问题弹窗 ----------------------------------
        self._popup("思考","• 当 γ 从风险偏好到风险厌恶变化时，张三的投保决策有何变化？\n• 为什么完全保险会让张三不安装防盗装置？若设置免赔额会怎样？\n尝试调整参数再模拟，验证你的想法。")

        self.log.see("end")

        # store for demo
        self._cached_decision = {
            "insured": would_insure,
            "install": install_no_ins if not would_insure else install_ins,
            "premium": premium,
            "prob_unins": p_d if install_no_ins else p,
            "prob_ins": p_d if install_ins else p,
            "gamma": gamma,
            "util": util,
            "params": (w, d, c_d, q)
        }

    # ------------------------ random demo -----------------------------
    def _random_demo(self):
        if not hasattr(self, "_cached_decision"):
            self.log.insert("end", "请先点击“模拟决策”再进行演示\n")
            self.log.see("end")
            return
        cd = self._cached_decision
        w, d, c_d, q = cd["params"]
        insured = cd["insured"]
        install = cd["install"]
        premium = cd["premium"] if insured else 0.0
        base_p = cd["prob_ins"] if insured else cd["prob_unins"]
        p_theft = min(max(base_p + (q if insured else 0.0), 0.0), 1.0)
        theft = random.random() < p_theft
        wealth_end = (w - premium - (c_d if install else 0)) + (d if (theft and insured) else 0) - (
            d if (theft and not insured) else 0)
        scenario = "投保" if insured else "未投保"
        self.log.insert("end", f"[随机演示] {scenario} | 盗窃概率 {p_theft:.1%} → {'被盗' if theft else '未被盗'}\n")
        self.log.insert("end", f"张三最终财富: {wealth_end:.2f}\n\n")
        self.log.see("end")

class SignalingModule(BaseModule):
    """教育信号发送（Spence 信号模型）可视化模块。

    左侧：参数输入 + 日志；右侧：成本‑收益与信号阈值图。
    支持判定分离 / 混同均衡并绘制关键阈值 e_L, e_H 及推荐 e*。
    """
    # ------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # Matplotlib 中文 & 负号正常
        plt.rcParams.setdefault("font.family", "FangSong")
        plt.rcParams.setdefault("axes.unicode_minus", False)

        self._build_left_panel()
        self._build_right_panel()

        # ### >>> 信号教学 1：弹窗 + ❓按钮

    def _popup(self, title: str, msg: str):
        messagebox.showinfo(title, msg)

    def _info_btn(self, parent, title: str, detail: str):
        btn = ttk.Button(parent, text="❓", width=2,
                         command=lambda: self._popup(title, detail))
        btn.pack(side="left", padx=2)

    # ------------------------------------------------------------------ UI
    def _build_left_panel(self):
        left = ttk.Frame(self.content)
        left.pack(side="left", fill="y", padx=12, pady=10)

        ttk.Label(left, text="教育信号模型参数", font=(None, 12, "bold")).pack(pady=4)

        # ------------------------- 参数变量
        self.a1_var = tk.DoubleVar(value=1.0)
        self.a2_var = tk.DoubleVar(value=2.0)
        self.c1_var = tk.DoubleVar(value=1.5)
        self.c2_var = tk.DoubleVar(value=1.0)
        self.e_max_var = tk.DoubleVar(value=3.0)

        explain = {
            "低类型工资 a1": "低学历员工工资水平",
            "高类型工资 a2": "高学历员工工资水平（应 > a1）",
            "低类型单位成本 c1": "低能力者每提高 1 单位教育水平所需成本，c1 > c2",
            "高类型单位成本 c2": "高能力者的单位教育成本（学习效率更高）",
            "教育水平上限 e_max": "可供选择的最高教育水平（信号强度上限）"
        }

        _rows = [
            ("低类型工资 a1", self.a1_var, 0.0, 20.0, 0.1),
            ("高类型工资 a2", self.a2_var, 0.1, 20.0, 0.1),
            ("低类型单位成本 c1", self.c1_var, 0.1, 10.0, 0.1),
            ("高类型单位成本 c2", self.c2_var, 0.05, 10.0, 0.1),
            ("教育水平上限 e_max", self.e_max_var, 1.0, 50.0, 1.0),
        ]

        for label, var, frm, to, inc in _rows:
            row = ttk.Frame(left)
            row.pack(anchor="w", pady=2)
            ttk.Label(row, text=label).pack(side="left")

            # 输入框（Spinbox）
            ttk.Spinbox(row, from_=frm, to=to, textvariable=var,
                        increment=inc, width=10).pack(side="left", padx=3)
            # 解释按钮
            self._info_btn(row, f"{label} 说明", explain[label])

        # ---------- action buttons
        btns = ttk.Frame(left)
        btns.pack(pady=6)
        ttk.Button(btns, text="计算 / 绘制", command=self._on_calculate).pack(side="left", padx=2)
        ttk.Button(btns, text="清空日志", command=lambda: self.log.delete("1.0", "end")).pack(side="left", padx=2)

        # ----------- log box
        ttk.Label(left, text="日志").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(left, height=14, width=34)
        self.log.pack(fill="both", expand=False)

    # ------------------------------------------------------------------ UI
    def _build_right_panel(self):
        right = ttk.Frame(self.content)
        right.pack(side="right", fill="both", expand=True, padx=5)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.fig.tight_layout()

    # ---------------------------------------------------------------- calc
    def _on_calculate(self):
        a1, a2 = self.a1_var.get(), self.a2_var.get()
        c1, c2 = self.c1_var.get(), self.c2_var.get()
        e_max = max(1e-3, self.e_max_var.get())

        # --- 参数合法性检查
        if a2 <= a1:
            messagebox.showerror("参数错误", "必须满足 a2 > a1 (学历溢价)！")
            return
        if c1 <= c2:
            messagebox.showerror("参数错误", "必须满足 c1 > c2 (单交叉条件)！")
            return

        delta_a = a2 - a1
        e_L = delta_a / c1  # 低类型伪装阈值 (cost > benefit)
        e_H = delta_a / c2  # 高类型激励阈值 (benefit > cost)

        # ---------- 日志输出
        self.log.insert("end", f"\n[计算] a₂-a₁ = {delta_a:.3f},  e_L = {e_L:.3f},  e_H = {e_H:.3f}\n")

        separating = e_L < e_H
        # if separating:
        #     e_star = (e_L + e_H) / 2
        #     self.log.insert("end",
        #                     f"存在分离均衡区间 ({e_L:.3f}, {e_H:.3f})，推荐 e* = {e_star:.3f}\n"
        #                     "解释：高类型可选择 e* 作为信号；\n"
        #                     f"  高类型净收益 = a₂ - c₂·e* = {a2 - c2 * e_star:.2f}\n"
        #                     f"  低类型若模仿净收益 = a₂ - c₁·e* = {a2 - c1 * e_star:.2f} < a₁，因而不会模仿。\n")
        # else:
        #     self.log.insert("end",
        #                     "⚠ 无分离均衡：高低类型无法用教育水平区分，可能出现混同均衡。\n"
        #                     "原因：工资差不足或成本差过小。可尝试增大 a₂−a₁ 或 c₁−c₂ 再计算。\n")
        #     e_star = None
        #     # 讨论问题
        if separating:
            e_star = (e_L + e_H) / 2  # 选中点，可改为用户自定义
            self.log.insert("end", f"存在分离均衡区间 ({e_L:.3f}, {e_H:.3f})，推荐 e* = {e_star:.3f}\n")
        else:
            self.log.insert("end", "⚠ 无分离均衡（可能为混同或无信号）。\n")
            e_star = None
        self.log.see("end")

        self.log.see("end")

        # ---------- 绘图
        self._draw_plot(a1, a2, c1, c2, e_max, e_L, e_H, e_star, separating)

    # ---------------------------------------------------------------- draw
    def _draw_plot(self, a1, a2, c1, c2, e_max, e_L, e_H, e_star, separating):
        xs = np.linspace(0, e_max, 400)
        cost_low = c1 * xs
        cost_high = c2 * xs
        wage_diff = np.full_like(xs, a2 - a1)

        self.ax.clear()
        # 成本线 & 收益线 --------------------------------------------------
        self.ax.plot(xs, cost_low, label="成本：低类型 c1e", linestyle="--")
        self.ax.plot(xs, cost_high, label="成本：高类型 c2e", linestyle=":")
        self.ax.plot(xs, wage_diff, label="工资差 a2-a1", linewidth=1.2)

        # 阈值 & e* --------------------------------------------------------
        self.ax.axvline(e_L, color="grey", linestyle="-.", label="e_L")
        self.ax.axvline(e_H, color="grey", linestyle="-.", label="e_H")
        if separating and e_star is not None:
            self.ax.axvline(e_star, color="red", linestyle="-", label="推荐 e*")

        # ### >>> 信号教学 4：注释阈值
        self.ax.text(e_L, wage_diff[0] * 1.05, "低类型此处无利可图", rotation=90, va="bottom")
        self.ax.text(e_H, wage_diff[0] * 1.05, "高类型仍有利", rotation=90, va="bottom")
        if separating and e_star is not None:
            self.ax.text(e_star, wage_diff[0] * 0.5, "推荐 e*", color="red",
                         rotation=90, va="center")

        # 坐标轴 & legend ---------------------------------------------------
        self.ax.set_xlim(0, e_max)
        ymax = max(wage_diff.max(), cost_low.max(), cost_high.max()) * 1.05
        self.ax.set_ylim(0, ymax)
        self.ax.set_xlabel("教育水平 e")
        self.ax.set_ylabel("成本 / 收益")
        title = "分离均衡" if separating else "无分离均衡"
        self.ax.set_title(f"教育信号成本收益图 ({title})")
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()

class ReportView(ttk.Frame):
    """集中查看与导出各模块仿真日志的视图"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # —— 顶部工具栏 ——————————————————————————
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=5)

        ttk.Button(bar, text="汇总报告", command=self._collect_logs).pack(side="left", padx=4)
        ttk.Button(bar, text="导出为 TXT", command=self._export_txt).pack(side="left", padx=4)
        ttk.Button(bar, text="清空", command=lambda: self.report.delete("1.0", "end")
                   ).pack(side="left", padx=4)
        ttk.Button(bar, text="返回主菜单",
                   command=lambda: controller.show_frame(MainMenu)
                   ).pack(side="right", padx=4)

        # —— 报告显示区 ——————————————————————————
        self.report = scrolledtext.ScrolledText(self, width=100, height=40)
        self.report.pack(fill="both", expand=True, padx=10, pady=5)

    # ==============================================================
    #  汇总所有含有 .log 组件的模块日志
    # ==============================================================
    def _collect_logs(self):
        parts = []
        for frame in self.controller.frames.values():
            if hasattr(frame, "log"):
                content = frame.log.get("1.0", "end").strip()
                if content:
                    title = getattr(frame, "module_name", frame.__class__.__name__)
                    parts.append(f"{'=' * 18}  {title}  {'=' * 18}\n{content}\n")
        if not parts:
            messagebox.showinfo("提示", "暂未找到任何模块日志，可先到各模块进行仿真。")
            return
        self.report.delete("1.0", "end")
        self.report.insert("end", "\n".join(parts))
        self.report.see("end")

    # ==============================================================
    #  保存为 txt 文件，文件名：时间戳 + 100-999 随机数
    # ==============================================================
    def _export_txt(self):
        text = self.report.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("提示", "没有可导出的内容，请先点击“汇总报告”。")
            return

        # 让用户挑选目录；取消则返回
        dir_path = filedialog.askdirectory(title="选择保存目录")
        if not dir_path:  # 用户点了取消
            return

        # 生成文件名（使用 controller 提供的方法）
        base_name = self.controller.generate_report_filename()  # e.g. 20250508_153210_847.txt
        full_path = os.path.join(dir_path, base_name)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("成功", f"报告已保存至：\n{full_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")

if __name__ == '__main__':
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            windll.user32.SetProcessDPIAware()
        except:
            pass
    app = App()
    app.mainloop()
