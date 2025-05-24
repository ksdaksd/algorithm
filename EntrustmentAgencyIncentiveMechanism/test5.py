#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展可视化：在委托代理、保险、教育信号模块中，也进行多次模拟或参数扫描，并用Matplotlib在Tkinter中展示曲线或柱状图。
------------------------------------------------------------------------------------
功能要点:
1. 不仅二手车(柠檬市场)模块可以多轮模拟, 在以下其他模块中也做“多次模拟/多参数扫描”并将结果可视化:
   - 委托代理(改进): 对一系列(w,b)或其它关键参数进行扫描, 将利润/努力等用曲线图或柱状图展示。
   - 保险与道德风险(改进): 对努力(effort)或其它参数(如premium)进行多点扫描, 显示失窃概率/收益/利润随之变化。
   - 教育信号(改进): 扫描多个threshold, 或多个invest, 再可选显示劳动力效用或企业收益的曲线。

2. 代码示例仅演示思路, 核心逻辑在 Demo 中。实际项目可针对需求灵活调整。
3. 如果要显示中文, 需保证已安装中文字体并在matplotlib中设置rcParams, 详见注释部分。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np

# Matplotlib 嵌入 Tkinter
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


###########################
# 改进后的核心逻辑类
###########################

class ImprovedPrincipalAgentModel:
    def __init__(self,
                 outside_option=0.0,
                 cost_factor=0.1,
                 price=2.0):
        self.outside_option = outside_option
        self.c = cost_factor
        self.P = price

    def agent_best_effort(self, w, b):
        if b <= 0:
            return 0.0
        return b / (2.0 * self.c)

    def agent_utility(self, w, b, e):
        return w + b * e - self.c * (e ** 2)

    def principal_profit(self, w, b, e):
        return self.P * e - (w + b * e)


class ImprovedInsuranceRiskModel:
    def __init__(self,
                 base_theft_prob=0.3,
                 alpha=0.05,
                 premium=10.0,
                 coverage=100.0,
                 deductible=0.0,
                 risk_model='linear'):
        self.p0 = base_theft_prob
        self.alpha = alpha
        self.premium = premium
        self.coverage = coverage
        self.deductible = deductible
        self.risk_model = risk_model

    def theft_probability(self, effort):
        if self.risk_model == 'power':
            p = self.p0 * ((1 - effort) ** self.alpha)
        else:
            p = self.p0 - self.alpha * effort
        return max(0.0, min(1.0, p))

    def simulate_one(self, effort):
        p = self.theft_probability(effort)
        bicycle_value = 100.0
        actual_coverage = max(0, self.coverage - self.deductible)
        exp_return = - self.premium + (1 - p) * bicycle_value + p * actual_coverage
        comp_profit = self.premium - p * actual_coverage
        return p, exp_return, comp_profit


class ImprovedEducationSignaling:
    def __init__(self,
                 ability=1.0,
                 cost_factor=0.1,
                 wage=50.0):
        self.ability = ability
        self.c = cost_factor
        self.wage = wage

    def labor_utility(self, invest, threshold):
        if invest >= threshold:
            return self.wage * self.ability - self.c * (invest ** 2)
        else:
            return - self.c * (invest ** 2)

    def firm_payoff(self, invest, threshold):
        if invest < threshold:
            return 0.0
        else:
            produce = 10 + 10 * self.ability
            return produce - self.wage

    def simulate(self, invest, threshold):
        lu = self.labor_utility(invest, threshold)
        fu = self.firm_payoff(invest, threshold)
        return lu, fu


###########################
#  数据记录器
###########################
class SimulationDataRecorder:
    def __init__(self):
        self.records = []

    def log(self, module_name, param_dict, result_dict):
        self.records.append({
            "module": module_name,
            "params": param_dict,
            "results": result_dict
        })

    def generate_report_text(self):
        lines = []
        lines.append("===== 信息经济学仿真报告(可视化拓展) =====\n")
        for i, rec in enumerate(self.records, start=1):
            lines.append(f"[{i}] 模块：{rec['module']}")
            lines.append("  输入参数：")
            for k, v in rec['params'].items():
                lines.append(f"    {k} = {v}")
            lines.append("  输出结果：")
            for k, v in rec['results'].items():
                lines.append(f"    {k} = {v}")
            lines.append("")
        return "\n".join(lines)


###########################
#  主界面 (带多模块+可视化)
###########################
class InfoEconApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 多参数可视化")
        self.geometry("1300x800")

        self.recorder = SimulationDataRecorder()

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Tabs
        self.build_tab_pa()
        self.build_tab_insurance()
        self.build_tab_signaling()

        # 底部按钮
        btn_report = ttk.Button(self, text="查看报告", command=self.show_report)
        btn_report.pack(side=tk.BOTTOM, pady=5)

    #################################################
    # 1. 委托代理(改进) - 多参数扫描 + 曲线可视化
    #################################################
    def build_tab_pa(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="委托代理 - 扫描可视化")

        # 输入区
        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        row_idx = 0
        # outside_option, cost_factor, price
        tk.Label(frame_input, text="外部效用(U0):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_u0 = tk.DoubleVar(value=0.0)
        tk.Entry(frame_input, textvariable=self.var_pa_u0, width=7).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="努力成本系数(c):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_c = tk.DoubleVar(value=0.1)
        tk.Entry(frame_input, textvariable=self.var_pa_c, width=7).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="产出价格(P):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_p = tk.DoubleVar(value=2.0)
        tk.Entry(frame_input, textvariable=self.var_pa_p, width=7).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        # 扫描范围
        tk.Label(frame_input, text="w_min, w_max, step:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_w = ttk.Frame(frame_input)
        self.var_pa_wmin = tk.DoubleVar(value=0.0)
        self.var_pa_wmax = tk.DoubleVar(value=20.0)
        self.var_pa_wstep = tk.DoubleVar(value=2.0)
        tk.Entry(frame_w, textvariable=self.var_pa_wmin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_pa_wmax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_pa_wstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_w.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        tk.Label(frame_input, text="b_min, b_max, step:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_b = ttk.Frame(frame_input)
        self.var_pa_bmin = tk.DoubleVar(value=0.0)
        self.var_pa_bmax = tk.DoubleVar(value=5.0)
        self.var_pa_bstep = tk.DoubleVar(value=1.0)
        tk.Entry(frame_b, textvariable=self.var_pa_bmin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_pa_bmax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_pa_bstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_b.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        # 扫描按钮
        btn_scan = ttk.Button(frame_input, text="扫描 & 可视化", command=self.run_pa_scan)
        btn_scan.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.label_pa_output = tk.Label(frame_input, text="输出结果将在这里显示...")
        self.label_pa_output.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 右侧放置绘图
        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_pa = Figure(figsize=(5, 4), dpi=100)
        self.ax_pa = self.fig_pa.add_subplot(111)
        self.canvas_pa = FigureCanvasTkAgg(self.fig_pa, master=frame_plot)
        self.canvas_pa.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_pa_scan(self):
        # 获取界面参数
        u0 = self.var_pa_u0.get()
        c = self.var_pa_c.get()
        p = self.var_pa_p.get()
        wmin = self.var_pa_wmin.get()
        wmax = self.var_pa_wmax.get()
        wstep = self.var_pa_wstep.get()
        bmin = self.var_pa_bmin.get()
        bmax = self.var_pa_bmax.get()
        bstep = self.var_pa_bstep.get()

        # 创建模型
        model = ImprovedPrincipalAgentModel(u0, c, p)

        # 扫描网格
        ws = np.arange(wmin, wmax + 1e-9, wstep)
        bs = np.arange(bmin, bmax + 1e-9, bstep)

        # 收集(主人利润, 代理人效用)等指标
        profit_list = []
        effort_list = []
        param_pairs = []
        for w in ws:
            for b in bs:
                e_star = model.agent_best_effort(w, b)
                ua = model.agent_utility(w, b, e_star)
                # 参与约束
                if ua < u0:
                    continue
                pi = model.principal_profit(w, b, e_star)
                profit_list.append(pi)
                effort_list.append(e_star)
                param_pairs.append((w, b))

        if not profit_list:
            self.label_pa_output.config(text="扫描范围内无满足参与约束的合同。")
            return

        # 绘图(示例：将利润列表做一个柱状图 或 散点图)
        self.ax_pa.clear()
        self.ax_pa.set_title("委托代理 - (w,b)网格扫描")
        self.ax_pa.set_xlabel("序号")
        self.ax_pa.set_ylabel("主人利润")

        indices = range(len(profit_list))

        # 可以用柱状图，也可用散点图
        self.ax_pa.bar(indices, profit_list, color='blue', alpha=0.6, label='主人利润')
        self.ax_pa.legend()

        self.canvas_pa.draw()

        # 简要输出(最高利润、对应w,b,e)
        best_idx = np.argmax(profit_list)
        best_pi = profit_list[best_idx]
        best_w, best_b = param_pairs[best_idx]
        best_e = effort_list[best_idx]
        best_text = f"最高利润={best_pi:.2f} 对应(w={best_w:.1f}, b={best_b:.1f}, e*={best_e:.1f})"
        self.label_pa_output.config(text=best_text)

        # 记录
        self.recorder.log(
            "委托代理-多参数扫描",
            {
                "u0": u0, "c": c, "P": p,
                "w_range": [wmin, wmax, wstep],
                "b_range": [bmin, bmax, bstep]
            },
            {
                "num_valid_contracts": len(profit_list),
                "best_profit": best_pi,
                "best_w": best_w,
                "best_b": best_b,
                "best_e": best_e
            }
        )

    #################################################
    # 2. 保险与道德风险 - 多努力扫描 + 可视化
    #################################################
    def build_tab_insurance(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="保险 - 扫描可视化")

        # 输入区
        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        row_idx = 0
        tk.Label(frame_input, text="基准失窃概率p0:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ins_p0 = tk.DoubleVar(value=0.3)
        tk.Entry(frame_input, textvariable=self.var_ins_p0, width=8).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="努力影响alpha:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ins_alpha = tk.DoubleVar(value=0.05)
        tk.Entry(frame_input, textvariable=self.var_ins_alpha, width=8).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="保险保费premium:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ins_prem = tk.DoubleVar(value=10.0)
        tk.Entry(frame_input, textvariable=self.var_ins_prem, width=8).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="赔付coverage:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ins_cov = tk.DoubleVar(value=100.0)
        tk.Entry(frame_input, textvariable=self.var_ins_cov, width=8).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="免赔额deductible:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ins_deduct = tk.DoubleVar(value=0.0)
        tk.Entry(frame_input, textvariable=self.var_ins_deduct, width=8).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="risk_model:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ins_risk = tk.StringVar(value='linear')
        tk.Entry(frame_input, textvariable=self.var_ins_risk, width=8).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="努力(e)扫描区: [e_min,e_max,step]").grid(row=row_idx, column=0, sticky=tk.E)
        frame_e = ttk.Frame(frame_input)
        self.var_ins_emin = tk.DoubleVar(value=0.0)
        self.var_ins_emax = tk.DoubleVar(value=1.0)
        self.var_ins_estep = tk.DoubleVar(value=0.1)
        tk.Entry(frame_e, textvariable=self.var_ins_emin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_e, textvariable=self.var_ins_emax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_e, textvariable=self.var_ins_estep, width=5).pack(side=tk.LEFT, padx=2)
        frame_e.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        btn_ins_scan = ttk.Button(frame_input, text="努力扫描 & 可视化", command=self.run_insurance_scan)
        btn_ins_scan.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.label_ins_output = tk.Label(frame_input, text="输出将在这里显示...")
        self.label_ins_output.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 右侧绘图
        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_ins = Figure(figsize=(5, 4), dpi=100)
        self.ax_ins = self.fig_ins.add_subplot(111)
        self.canvas_ins = FigureCanvasTkAgg(self.fig_ins, master=frame_plot)
        self.canvas_ins.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_insurance_scan(self):
        p0 = self.var_ins_p0.get()
        alpha = self.var_ins_alpha.get()
        prem = self.var_ins_prem.get()
        cov = self.var_ins_cov.get()
        deduct = self.var_ins_deduct.get()
        risk = self.var_ins_risk.get()
        emin = self.var_ins_emin.get()
        emax = self.var_ins_emax.get()
        estep = self.var_ins_estep.get()

        model = ImprovedInsuranceRiskModel(p0, alpha, prem, cov, deduct, risk)

        efforts = np.arange(emin, emax + 1e-9, estep)
        theft_probs = []
        user_util = []
        comp_profit = []

        for e in efforts:
            p, ur, cp = model.simulate_one(e)
            theft_probs.append(p)
            user_util.append(ur)
            comp_profit.append(cp)

        # 绘图(示例: 多条曲线在同一图中)
        self.ax_ins.clear()
        self.ax_ins.set_title("保险-努力扫描")
        self.ax_ins.set_xlabel("努力(e)")
        rr = efforts
        self.ax_ins.plot(rr, theft_probs, 'r-o', label="失窃率")
        self.ax_ins.plot(rr, user_util, 'g-s', label="投保人收益")
        self.ax_ins.plot(rr, comp_profit, 'b-^', label="保险公司利润")
        self.ax_ins.legend()
        self.canvas_ins.draw()

        # 查找使投保人收益最大的点 or 使保险公司利润最大的点
        best_user_idx = np.argmax(user_util)
        best_company_idx = np.argmax(comp_profit)
        text_res = (f"投保人收益最大: e={efforts[best_user_idx]:.2f}, "
                    f"U={user_util[best_user_idx]:.2f}\n"
                    f"公司利润最大: e={efforts[best_company_idx]:.2f}, "
                    f"Profit={comp_profit[best_company_idx]:.2f}")
        self.label_ins_output.config(text=text_res)

        self.recorder.log(
            "保险-努力扫描",
            {
                "p0": p0, "alpha": alpha, "premium": prem, "coverage": cov,
                "deductible": deduct, "risk": risk,
                "effort_range": [emin, emax, estep]
            },
            {
                "best_user_effort": efforts[best_user_idx],
                "best_user_utility": user_util[best_user_idx],
                "best_company_effort": efforts[best_company_idx],
                "best_company_profit": comp_profit[best_company_idx]
            }
        )

    #################################################
    # 3. 教育信号 - 多阈值 or 多投资扫描 + 可视化
    #################################################
    def build_tab_signaling(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="教育信号 - 扫描可视化")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        row_idx = 0
        tk.Label(frame_input, text="学生能力(ability):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_edu_ability = tk.DoubleVar(value=1.0)
        tk.Entry(frame_input, textvariable=self.var_edu_ability, width=7).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="成本系数(c):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_edu_c = tk.DoubleVar(value=0.1)
        tk.Entry(frame_input, textvariable=self.var_edu_c, width=7).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="工资(wage):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_edu_w = tk.DoubleVar(value=50.0)
        tk.Entry(frame_input, textvariable=self.var_edu_w, width=7).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        # 选择扫描模式(扫描threshold还是invest)
        tk.Label(frame_input, text="扫描模式:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_edu_mode = tk.StringVar(value="threshold")
        cb_mode = ttk.Combobox(frame_input, textvariable=self.var_edu_mode,
                               values=["threshold", "invest"], width=8)
        cb_mode.grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="[start, end, step]:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_scan = ttk.Frame(frame_input)
        self.var_edu_start = tk.DoubleVar(value=0.0)
        self.var_edu_end = tk.DoubleVar(value=5.0)
        self.var_edu_step = tk.DoubleVar(value=0.5)
        tk.Entry(frame_scan, textvariable=self.var_edu_start, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_scan, textvariable=self.var_edu_end, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_scan, textvariable=self.var_edu_step, width=5).pack(side=tk.LEFT, padx=2)
        frame_scan.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        btn_edu_scan = ttk.Button(frame_input, text="扫描 & 可视化", command=self.run_edu_scan)
        btn_edu_scan.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.label_edu_output = tk.Label(frame_input, text="输出将在这里显示...")
        self.label_edu_output.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 绘图
        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_edu = Figure(figsize=(5, 4), dpi=100)
        self.ax_edu = self.fig_edu.add_subplot(111)
        self.canvas_edu = FigureCanvasTkAgg(self.fig_edu, master=frame_plot)
        self.canvas_edu.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_edu_scan(self):
        ab = self.var_edu_ability.get()
        c = self.var_edu_c.get()
        w = self.var_edu_w.get()
        mode = self.var_edu_mode.get()
        start_ = self.var_edu_start.get()
        end_ = self.var_edu_end.get()
        step_ = self.var_edu_step.get()

        model = ImprovedEducationSignaling(ab, c, w)

        scan_values = np.arange(start_, end_ + 1e-9, step_)
        labor_utils = []
        firm_utils = []

        # 根据模式, 或者 threshold in scan_values, fix invest
        # 或者 invest in scan_values, fix threshold
        invest_fixed = 2.0
        threshold_fixed = 2.0

        for val in scan_values:
            if mode == "threshold":
                # threshold=val, invest=invest_fixed
                lu, fu = model.simulate(invest_fixed, val)
            else:
                # invest=val, threshold=threshold_fixed
                lu, fu = model.simulate(val, threshold_fixed)
            labor_utils.append(lu)
            firm_utils.append(fu)

        self.ax_edu.clear()
        if mode == "threshold":
            self.ax_edu.set_title("教育信号 - 扫描 threshold")
            self.ax_edu.set_xlabel("threshold")
        else:
            self.ax_edu.set_title("教育信号 - 扫描 invest")
            self.ax_edu.set_xlabel("invest")

        self.ax_edu.set_ylabel("效用/收益")
        self.ax_edu.plot(scan_values, labor_utils, 'r-o', label="劳动力效用")
        self.ax_edu.plot(scan_values, firm_utils, 'b-s', label="企业收益")
        self.ax_edu.legend()
        self.canvas_edu.draw()

        # 找最大值
        best_lab_idx = np.argmax(labor_utils)
        best_firm_idx = np.argmax(firm_utils)
        text_res = (f"劳动力效用最大: x={scan_values[best_lab_idx]:.2f}, "
                    f"U={labor_utils[best_lab_idx]:.2f}\n"
                    f"企业收益最大: x={scan_values[best_firm_idx]:.2f}, "
                    f"Profit={firm_utils[best_firm_idx]:.2f}")

        if mode == "threshold":
            text_res += f"\n(其中invest固定={invest_fixed})"
        else:
            text_res += f"\n(其中threshold固定={threshold_fixed})"

        self.label_edu_output.config(text=text_res)

        self.recorder.log(
            "教育信号-扫描",
            {
                "ability": ab, "cost_factor": c, "wage": w,
                "mode": mode, "scan_range": [start_, end_, step_]
            },
            {
                "best_labor_x": scan_values[best_lab_idx],
                "best_labor_val": labor_utils[best_lab_idx],
                "best_firm_x": scan_values[best_firm_idx],
                "best_firm_val": firm_utils[best_firm_idx]
            }
        )

    #################################################
    #  生成报告
    #################################################
    def show_report(self):
        report = self.recorder.generate_report_text()
        messagebox.showinfo("仿真报告", report)


def main():
    # 若要显示中文, 需保证安装中文字体, 并在这里设置:
    # import matplotlib
    # from matplotlib import rcParams
    # rcParams['font.sans-serif'] = ['SimHei']
    # rcParams['axes.unicode_minus'] = False

    app = InfoEconApp()
    app.mainloop()


if __name__ == "__main__":
    main()