#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
委托代理与激励机制仿真实验
-----------------------------
要求：
1. 学生可选择扮演委托人（Principal）或代理人（Agent）
2. 在委托人端：设定产出、努力概率、代理人努力成本、代理人保留效用及工资区间，
   程序利用网格搜索求解在满足参与约束和激励相容约束条件下的最优合同，并绘制委托人利润热图，同时可模拟一次交易。
3. 在代理人端：输入合同工资与系统参数后，可选择接受合同（并选择高/低努力），
   模拟随机产出、计算代理人效用和委托人利润；也可拒绝合同以获得保留效用。

技术栈选用：python，tkinter，matplotlib，numpy，random
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

matplotlib.rcParams["font.family"] = "FangSong"
matplotlib.rcParams["axes.unicode_minus"] = False  # 正常显示负号
###############################################
# 模型类：MoralHazardModel
###############################################
class MoralHazardModel:
    def __init__(self, R=100, p_H=0.8, p_L=0.2, C_h=20, U_A0=0):
        """
        参数说明：
          R     ：工作产出（收益）
          p_H   ：代理人选择高努力时，高产出的概率
          p_L   ：代理人选择低努力时，高产出的概率
          C_h   ：代理人选择高努力的成本（低努力成本默认为0）
          U_A0  ：代理人的保留效用（参与约束要求至少获得此效用）
        """
        self.R = R
        self.p_H = p_H
        self.p_L = p_L
        self.C_h = C_h
        self.U_A0 = U_A0

    def agent_util_high(self, w_H, w_L):
        """代理人若选择高努力，其期望效用 = p_H*w_H + (1-p_H)*w_L - C_h"""
        return self.p_H * w_H + (1 - self.p_H) * w_L - self.C_h

    def agent_util_low(self, w_H, w_L):
        """代理人若选择低努力（无努力成本），其期望效用 = p_L*w_H + (1-p_L)*w_L"""
        return self.p_L * w_H + (1 - self.p_L) * w_L

    def principal_profit(self, w_H, w_L, effort="high"):
        """
        委托人利润：
           如果代理人选择高努力，则期望利润 = p_H*(R - w_H) + (1-p_H)*(R - w_L)
           如果代理人选择低努力，则利润 = p_L*(R - w_H) + (1-p_L)*(R - w_L)
        """
        if effort == "high":
            return self.p_H * (self.R - w_H) + (1 - self.p_H) * (self.R - w_L)
        else:
            return self.p_L * (self.R - w_H) + (1 - self.p_L) * (self.R - w_L)

    def grid_search_contract(self, w_H_min, w_H_max, w_H_step, w_L_min, w_L_max, w_L_step):
        """
        在给定 w_H 与 w_L 的区间内进行网格搜索，
        寻找满足参加约束（U_A^H >= U_A0）和激励相容约束（U_A^H >= U_A^L）条件下，
        使委托人利润最大的合同
        返回值：最优合同以及网格数据（便于后续热图绘制）
        """
        best_profit = -np.inf
        best_contract = None
        ws = np.arange(w_H_min, w_H_max + w_H_step / 2, w_H_step)
        wl = np.arange(w_L_min, w_L_max + w_L_step / 2, w_L_step)
        profit_mat = np.empty((len(wl), len(ws)))
        profit_mat[:] = np.nan
        for i, w_L in enumerate(wl):
            for j, w_H in enumerate(ws):
                U_A_H = self.agent_util_high(w_H, w_L)
                U_A_L = self.agent_util_low(w_H, w_L)
                # 满足参加约束和激励相容约束
                if U_A_H >= self.U_A0 and U_A_H >= U_A_L:
                    profit = self.principal_profit(w_H, w_L, "high")
                    profit_mat[i, j] = profit
                    if profit > best_profit:
                        best_profit = profit
                        best_contract = (w_H, w_L, U_A_H, U_A_L, profit)
        return best_contract, ws, wl, profit_mat

    def simulate_outcome(self, effort, w_H, w_L):
        """
        模拟代理人选择努力后，随机实现的产出与工资支付
          若努力 = "high"，有成本 C_h 且高产出概率为 p_H
          若努力 = "low"，成本为0且高产出概率为 p_L
        返回：(产出状态，高工资或低工资支付, 代理人效用, 委托人利润)
        """
        if effort == "high":
            prob = self.p_H
            cost = self.C_h
        elif effort == "low":
            prob = self.p_L
            cost = 0
        else:
            return None
        outcome = "高产出" if random.random() < prob else "低产出"
        wage_received = w_H if outcome == "高产出" else w_L
        agent_utility = wage_received - cost
        principal_profit = self.R - wage_received
        return outcome, wage_received, agent_utility, principal_profit


###############################################
# 界面模块：委托人仿真界面
###############################################
class PrincipalFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # 标题
        ttk.Label(self, text="委托人（Principal）模拟", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, pady=5)

        # 模型参数输入
        ttk.Label(self, text="产出 R:").grid(row=1, column=0, sticky=tk.E)
        self.R_var = tk.DoubleVar(value=100)
        ttk.Entry(self, textvariable=self.R_var, width=8).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self, text="高努力产出概率 p_H:").grid(row=1, column=2, sticky=tk.E)
        self.pH_var = tk.DoubleVar(value=0.8)
        ttk.Entry(self, textvariable=self.pH_var, width=8).grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(self, text="低努力产出概率 p_L:").grid(row=2, column=0, sticky=tk.E)
        self.pL_var = tk.DoubleVar(value=0.2)
        ttk.Entry(self, textvariable=self.pL_var, width=8).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="高努力成本 C_h:").grid(row=2, column=2, sticky=tk.E)
        self.C_var = tk.DoubleVar(value=20)
        ttk.Entry(self, textvariable=self.C_var, width=8).grid(row=2, column=3, padx=5, pady=2)

        ttk.Label(self, text="代理人保留效用 U0:").grid(row=3, column=0, sticky=tk.E)
        self.U0_var = tk.DoubleVar(value=0)
        ttk.Entry(self, textvariable=self.U0_var, width=8).grid(row=3, column=1, padx=5, pady=2)

        # 工资合同搜索参数
        ttk.Label(self, text="工资(高)区间 w_H_min:").grid(row=4, column=0, sticky=tk.E)
        self.wH_min_var = tk.DoubleVar(value=0)
        ttk.Entry(self, textvariable=self.wH_min_var, width=8).grid(row=4, column=1, padx=5, pady=2)

        ttk.Label(self, text="工资(高)上限 w_H_max:").grid(row=4, column=2, sticky=tk.E)
        self.wH_max_var = tk.DoubleVar(value=100)
        ttk.Entry(self, textvariable=self.wH_max_var, width=8).grid(row=4, column=3, padx=5, pady=2)

        ttk.Label(self, text="步长:").grid(row=5, column=0, sticky=tk.E)
        self.wH_step_var = tk.DoubleVar(value=5)
        ttk.Entry(self, textvariable=self.wH_step_var, width=8).grid(row=5, column=1, padx=5, pady=2)

        ttk.Label(self, text="工资(低)区间 w_L_min:").grid(row=5, column=2, sticky=tk.E)
        self.wL_min_var = tk.DoubleVar(value=0)
        ttk.Entry(self, textvariable=self.wL_min_var, width=8).grid(row=5, column=3, padx=5, pady=2)

        ttk.Label(self, text="工资(低)上限 w_L_max:").grid(row=6, column=0, sticky=tk.E)
        self.wL_max_var = tk.DoubleVar(value=100)
        ttk.Entry(self, textvariable=self.wL_max_var, width=8).grid(row=6, column=1, padx=5, pady=2)

        ttk.Label(self, text="步长:").grid(row=6, column=2, sticky=tk.E)
        self.wL_step_var = tk.DoubleVar(value=5)
        ttk.Entry(self, textvariable=self.wL_step_var, width=8).grid(row=6, column=3, padx=5, pady=2)

        # 操作按钮
        self.optimal_contract_btn = ttk.Button(self, text="求最优合同", command=self.compute_optimal_contract)
        self.optimal_contract_btn.grid(row=7, column=0, columnspan=2, pady=5)

        self.simulate_btn = ttk.Button(self, text="模拟交易", command=self.simulate_transaction)
        self.simulate_btn.grid(row=7, column=2, columnspan=2, pady=5)

        self.plot_btn = ttk.Button(self, text="绘制利润图", command=self.plot_profit_heatmap)
        self.plot_btn.grid(row=8, column=0, columnspan=4, pady=5)

        # 显示结果的文本框
        self.result_text = tk.Text(self, width=60, height=6)
        self.result_text.grid(row=9, column=0, columnspan=4, padx=5, pady=5)

        # 利润热图：使用 matplotlib 绘制
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=4, rowspan=10, padx=10, pady=5)

    def compute_optimal_contract(self):
        R = self.R_var.get()
        p_H = self.pH_var.get()
        p_L = self.pL_var.get()
        C_h = self.C_var.get()
        U0 = self.U0_var.get()
        model = MoralHazardModel(R, p_H, p_L, C_h, U0)
        wH_min = self.wH_min_var.get()
        wH_max = self.wH_max_var.get()
        wH_step = self.wH_step_var.get()
        wL_min = self.wL_min_var.get()
        wL_max = self.wL_max_var.get()
        wL_step = self.wL_step_var.get()
        optimal, ws, wl, profit_mat = model.grid_search_contract(wH_min, wH_max, wH_step,
                                                                 wL_min, wL_max, wL_step)
        if optimal is None:
            msg = "没有满足约束条件的合同组合。"
        else:
            msg = (f"最优合同:\n 高工资 w_H = {optimal[0]:.2f}\n 低工资 w_L = {optimal[1]:.2f}\n"
                   f"代理人高努力效用 = {optimal[2]:.2f}\n 代理人低努力效用 = {optimal[3]:.2f}\n"
                   f"预计委托人利润 = {optimal[4]:.2f}\n")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, msg)
        self.optimal_contract = optimal  # 保存最优合同

        # 同时保存网格数据用于绘图
        self.grid_ws = ws
        self.grid_wl = wl
        self.profit_mat = profit_mat

    def simulate_transaction(self):
        if not hasattr(self, "optimal_contract") or self.optimal_contract is None:
            messagebox.showwarning("警告", "请先求解最优合同！")
            return
        # 假设代理人接受合同并选择高努力
        model = MoralHazardModel(self.R_var.get(), self.pH_var.get(),
                                 self.pL_var.get(), self.C_var.get(), self.U0_var.get())
        w_H, w_L = self.optimal_contract[0], self.optimal_contract[1]
        outcome, wage_received, agent_util, principal_profit = model.simulate_outcome("high", w_H, w_L)
        msg = (f"模拟交易结果（高努力）：\n 产出: {outcome}\n 代理人工资: {wage_received:.2f}\n"
               f"代理人效用: {agent_util:.2f}\n 委托人利润: {principal_profit:.2f}")
        messagebox.showinfo("交易模拟", msg)

    def plot_profit_heatmap(self):
        if not hasattr(self, "profit_mat"):
            messagebox.showwarning("警告", "请先求解最优合同以生成利润数据！")
            return
        self.ax.clear()
        # 利用网格数据绘制利润热图
        X, Y = np.meshgrid(self.grid_ws, self.grid_wl)
        cp = self.ax.contourf(X, Y, self.profit_mat, cmap="viridis")
        self.ax.set_xlabel("高工资 w_H")
        self.ax.set_ylabel("低工资 w_L")
        self.ax.set_title("委托人利润热图")
        self.fig.colorbar(cp, ax=self.ax)
        self.canvas.draw()


###############################################
# 界面模块：代理人仿真界面
###############################################
class AgentFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="代理人（Agent）模拟", font=("Arial", 14)) \
            .grid(row=0, column=0, columnspan=4, pady=5)

        # 合同参数输入：由委托人制定的合同工资
        ttk.Label(self, text="合同：高工资 w_H:").grid(row=1, column=0, sticky=tk.E)
        self.wH_var = tk.DoubleVar(value=80)
        ttk.Entry(self, textvariable=self.wH_var, width=8).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(self, text="低工资 w_L:").grid(row=1, column=2, sticky=tk.E)
        self.wL_var = tk.DoubleVar(value=20)
        ttk.Entry(self, textvariable=self.wL_var, width=8).grid(row=1, column=3, padx=5, pady=2)

        # 系统参数输入（应与委托人设定一致）
        ttk.Label(self, text="产出 R:").grid(row=2, column=0, sticky=tk.E)
        self.R_var = tk.DoubleVar(value=100)
        ttk.Entry(self, textvariable=self.R_var, width=8).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="高努力概率 p_H:").grid(row=2, column=2, sticky=tk.E)
        self.pH_var = tk.DoubleVar(value=0.8)
        ttk.Entry(self, textvariable=self.pH_var, width=8).grid(row=2, column=3, padx=5, pady=2)

        ttk.Label(self, text="低努力概率 p_L:").grid(row=3, column=0, sticky=tk.E)
        self.pL_var = tk.DoubleVar(value=0.2)
        ttk.Entry(self, textvariable=self.pL_var, width=8).grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self, text="高努力成本 C_h:").grid(row=3, column=2, sticky=tk.E)
        self.C_var = tk.DoubleVar(value=20)
        ttk.Entry(self, textvariable=self.C_var, width=8).grid(row=3, column=3, padx=5, pady=2)

        ttk.Label(self, text="代理人保留效用 U0:").grid(row=4, column=0, sticky=tk.E)
        self.U0_var = tk.DoubleVar(value=0)
        ttk.Entry(self, textvariable=self.U0_var, width=8).grid(row=4, column=1, padx=5, pady=2)

        # 代理人的决策按钮
        self.hard_effort_btn = ttk.Button(self, text="接受合同并选择高努力",
                                          command=lambda: self.simulate("high"))
        self.hard_effort_btn.grid(row=5, column=0, columnspan=2, pady=5)

        self.low_effort_btn = ttk.Button(self, text="接受合同但选择低努力",
                                         command=lambda: self.simulate("low"))
        self.low_effort_btn.grid(row=5, column=2, columnspan=2, pady=5)

        self.reject_btn = ttk.Button(self, text="拒绝合同", command=self.reject_contract)
        self.reject_btn.grid(row=6, column=0, columnspan=4, pady=5)

    def simulate(self, effort):
        model = MoralHazardModel(self.R_var.get(), self.pH_var.get(),
                                 self.pL_var.get(), self.C_var.get(), self.U0_var.get())
        w_H = self.wH_var.get()
        w_L = self.wL_var.get()
        outcome, wage_received, agent_util, principal_profit = model.simulate_outcome(effort, w_H, w_L)
        msg = (f"模拟结果（{'高努力' if effort == 'high' else '低努力'}）：\n 产出: {outcome}\n"
               f"代理人工资: {wage_received:.2f}\n代理人效用: {agent_util:.2f}\n"
               f"委托人利润: {principal_profit:.2f}")
        messagebox.showinfo("代理人模拟", msg)

    def reject_contract(self):
        msg = f"合同被拒绝，代理人获得保留效用 U0 = {self.U0_var.get():.2f}"
        messagebox.showinfo("代理人模拟", msg)


###############################################
# 主界面：通过 Notebook 提供角色切换
###############################################
class MoralHazardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("委托代理与激励机制仿真")
        self.geometry("1000x600")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)
        self.principal_frame = PrincipalFrame(self.notebook)
        self.agent_frame = AgentFrame(self.notebook)
        self.notebook.add(self.principal_frame, text="委托人模拟")
        self.notebook.add(self.agent_frame, text="代理人模拟")


if __name__ == "__main__":
    app = MoralHazardApp()
    app.mainloop()