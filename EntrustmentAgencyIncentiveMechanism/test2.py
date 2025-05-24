#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息经济学课程仿真软件 (扩展版)
--------------------------------
此示例代码在之前的基础上，拓展了以下功能/思路：
1. 为委托代理模块增加了一个简单的“最优合约搜索”功能，允许用户点击按钮尝试在给定范围内做穷举搜索；
2. 在二手车（柠檬市场）模块中，增加多轮迭代模拟，以观看市场价格和车况演化；
3. 在保险与道德风险模块中，允许用户设置多人决策（N位投保人），并查看总体市场情况；
4. 在教育/招聘信号模块中，增加一个可视化对比，将不同阈值、多名学生的教育投资结果集中在图表中呈现。

技术栈：
- Python 3
- Tkinter 作为GUI
- Matplotlib 辅助可视化

声明：
示例示意性代码，不保证完全健壮或高效，真实应用需做更严谨的封装与测试。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

# 可选：导入matplotlib做简单可视化
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


##############################
# 数据/模型层 (核心逻辑与算法)
##############################

class PrincipalAgentModel:
    """
    委托代理与激励机制模块：
    - 代理人效用: U_A = w + b*e - c e^2
    - 主人利润: π = P*e - (w + b*e)
    """
    def __init__(self, wage=10.0, bonus=0.2, price=2.0, cost_factor=0.1):
        self.wage = wage
        self.bonus = bonus
        self.price = price
        self.cost_factor = cost_factor

    def best_effort(self):
        """风险中性、线性产出时，代理人最优努力 e* = b / (2c) (若 b>0)"""
        if self.bonus <= 0:
            return 0.0
        return self.bonus / (2.0 * self.cost_factor)

    def agent_utility(self, effort):
        return self.wage + self.bonus * effort - self.cost_factor * effort**2

    def principal_profit(self, effort):
        return self.price * effort - (self.wage + self.bonus * effort)

    def simulate(self):
        e_star = self.best_effort()
        u_a = self.agent_utility(e_star)
        pi = self.principal_profit(e_star)
        return e_star, u_a, pi


class LemonsMarketModel:
    """
    二手车柠檬市场：
    - n_cars 辆车，每辆车高质量(HQ)或低质量(LQ)
    - 若信息不对称(无检测)，市场均价会下降 -> 逆向选择
    - 可进行多轮模拟, 观察市场演化
    """
    def __init__(self, n_cars=100, p_high_quality=0.3, check_quality=False):
        self.n_cars = n_cars
        self.p_high_quality = p_high_quality  # HQ车占比
        self.check_quality = check_quality
        self.reset()

    def reset(self):
        self.cars = []
        self.generate_cars()

    def generate_cars(self):
        self.cars.clear()
        for _ in range(self.n_cars):
            # 生成(HQ)或(LQ)
            quality = "HQ" if (random.random() < self.p_high_quality) else "LQ"
            self.cars.append(quality)

    def one_round(self):
        """
        多轮模拟的一轮：根据模式来决定买家定价和交易过程。
        返回 (avg_price, frac_HQ_sold, sold_count)
        """
        total_price = 0.0
        sold_count = 0
        hq_sold = 0

        for quality in self.cars:
            if self.check_quality:
                # 假设70%概率识别质量
                if random.random() < 0.7:
                    # 准确识别
                    if quality == "HQ":
                        price = 10
                    else:
                        price = 4
                else:
                    # 无法识别 -> 出个中间价
                    price = 6.0
            else:
                # 无检测 -> 出中间价5.0
                price = 5.0

            # 车主最低接受价: HQ=8, LQ=3 (简化)
            if quality == "HQ":
                threshold = 8.0
            else:
                threshold = 3.0

            if price >= threshold:
                sold_count += 1
                total_price += price
                if quality == "HQ":
                    hq_sold += 1

        if sold_count > 0:
            avg_price = total_price / sold_count
            frac_hq = hq_sold / sold_count
        else:
            avg_price = 0
            frac_hq = 0

        return avg_price, frac_hq, sold_count


class InsuranceRiskModel:
    """
    保险与道德风险：
    - 投保人努力 e -> 失窃概率 p(e) = max(0, p0 - alpha* e)
    - 保费 premium, 赔付 coverage
    - 可模拟多人市场
    """
    def __init__(self, base_theft_prob=0.3, alpha=0.05, premium=10.0, coverage=100.0, n_people=1):
        self.p0 = base_theft_prob
        self.alpha = alpha
        self.premium = premium
        self.coverage = coverage
        self.n_people = n_people  # 同时参与投保的人数

    def theft_probability(self, effort):
        p = self.p0 - self.alpha * effort
        return max(0.0, min(1.0, p))

    def simulate_once(self, effort):
        """单个投保人模拟"""
        p = self.theft_probability(effort)
        # 投保人期望收益
        # 车价值=100（假设）
        bicycle_value = 100.0
        exp_return = -self.premium + (1 - p)*bicycle_value + p*self.coverage
        # 保险公司利润
        company_profit = self.premium - p*self.coverage
        return p, exp_return, company_profit

    def simulate_group(self, effort_list):
        """
        多人决策场景：传入effort_list，每人努力不同
        返回： (平均失窃率, 全体投保人平均收益, 保险公司总利润)
        """
        total_prob = 0.0
        total_user_utility = 0.0
        total_company_profit = 0.0
        for eff in effort_list:
            p, u, profit = self.simulate_once(eff)
            total_prob += p
            total_user_utility += u
            total_company_profit += profit

        avg_prob = total_prob / len(effort_list)
        avg_utility = total_user_utility / len(effort_list)
        return avg_prob, avg_utility, total_company_profit


class EducationSignalingModel:
    """
    教育/招聘信号：
    - 学生决定教育投资 e_invest
    - 企业筛选门槛 s
    - 若 e_invest >= s，则学生得到工资W - cost(e_invest)
      cost(e_invest) = c * e_invest^2
      企业获得 (产出 - 工资)，简化: 产出= (能力 + 10) - c'*( some function ), 此处随意
    """
    def __init__(self, ability=1.0, cost_factor=0.1, wage=50.0):
        self.ability = ability
        self.c = cost_factor
        self.wage = wage

    def labor_utility(self, invest, threshold):
        if invest >= threshold:
            return self.wage * self.ability - self.c*invest**2
        else:
            return - self.c*invest**2

    def firm_payoff(self, invest, threshold):
        if invest >= threshold:
            # 雇佣 -> 产出 （假设 ability*10 + 10?）- wage
            produce = (self.ability * 10) + 10
            return produce - self.wage
        else:
            return 0.0

    def simulate(self, invest, threshold):
        """
        返回 (labor_util, firm_util)
        """
        lu = self.labor_utility(invest, threshold)
        fu = self.firm_payoff(invest, threshold)
        return lu, fu


################################
# 数据处理/结果记录/报表生成层
################################
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
        lines.append("===== 仿真报告 (扩展版) =====\n")
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


##############################
# 界面层 - 使用Tkinter + Matplotlib
##############################
class InfoEconExtendedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 扩展版")
        self.geometry("1100x700")
        self.recorder = SimulationDataRecorder()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=1, fill=tk.BOTH)

        # 各模块Tab
        self.build_tab_principal_agent()
        self.build_tab_lemons()
        self.build_tab_insurance()
        self.build_tab_signaling()

        # 底部按钮
        frame_bottom = ttk.Frame(self)
        frame_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        btn_report = ttk.Button(frame_bottom, text="查看报告", command=self.show_report)
        btn_report.pack(side=tk.LEFT, padx=10, pady=5)

    # ————— Tab 1：委托代理 ————— #
    def build_tab_principal_agent(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="委托代理(扩展)")

        label_title = tk.Label(tab, text="委托代理：最优合约搜索", font=("Arial", 12, "bold"))
        label_title.grid(row=0, column=0, columnspan=3, pady=5)

        # 输入参数
        row_index = 1
        tk.Label(tab, text="产出价格(P):").grid(row=row_index, column=0, sticky=tk.E)
        self.var_price = tk.DoubleVar(value=2.0)
        tk.Entry(tab, textvariable=self.var_price).grid(row=row_index, column=1, padx=5)

        row_index += 1
        tk.Label(tab, text="努力成本系数(c):").grid(row=row_index, column=0, sticky=tk.E)
        self.var_c = tk.DoubleVar(value=0.1)
        tk.Entry(tab, textvariable=self.var_c).grid(row=row_index, column=1, padx=5)

        row_index += 1
        tk.Label(tab, text="工资搜索范围 [w_min, w_max] Step:").grid(row=row_index, column=0, sticky=tk.E)
        frame_w = tk.Frame(tab)
        frame_w.grid(row=row_index, column=1, sticky=tk.W)
        self.var_w_min = tk.DoubleVar(value=0.0)
        tk.Entry(frame_w, width=5, textvariable=self.var_w_min).pack(side=tk.LEFT, padx=2)
        self.var_w_max = tk.DoubleVar(value=30.0)
        tk.Entry(frame_w, width=5, textvariable=self.var_w_max).pack(side=tk.LEFT, padx=2)
        self.var_w_step = tk.DoubleVar(value=2.0)
        tk.Entry(frame_w, width=5, textvariable=self.var_w_step).pack(side=tk.LEFT, padx=2)

        row_index += 1
        tk.Label(tab, text="绩效系数搜索范围 [b_min, b_max] Step:").grid(row=row_index, column=0, sticky=tk.E)
        frame_b = tk.Frame(tab)
        frame_b.grid(row=row_index, column=1, sticky=tk.W)
        self.var_b_min = tk.DoubleVar(value=0.0)
        tk.Entry(frame_b, width=5, textvariable=self.var_b_min).pack(side=tk.LEFT, padx=2)
        self.var_b_max = tk.DoubleVar(value=1.0)
        tk.Entry(frame_b, width=5, textvariable=self.var_b_max).pack(side=tk.LEFT, padx=2)
        self.var_b_step = tk.DoubleVar(value=0.1)
        tk.Entry(frame_b, width=5, textvariable=self.var_b_step).pack(side=tk.LEFT, padx=2)

        row_index += 1
        btn_search = ttk.Button(tab, text="最优合约搜索", command=self.run_optimal_contract_search)
        btn_search.grid(row=row_index, column=0, columnspan=2, pady=5)

        row_index += 1
        self.label_agent_result = tk.Label(tab, text="结果将在此显示...", fg="blue")
        self.label_agent_result.grid(row=row_index, column=0, columnspan=3, pady=10)

    def run_optimal_contract_search(self):
        P = self.var_price.get()
        c = self.var_c.get()
        w_min = self.var_w_min.get()
        w_max = self.var_w_max.get()
        w_step = self.var_w_step.get()
        b_min = self.var_b_min.get()
        b_max = self.var_b_max.get()
        b_step = self.var_b_step.get()

        best_profit = -9999999
        best_tuple = (0, 0, 0)  # (w*, b*, profit)
        for w in self.frange(w_min, w_max, w_step):
            for b in self.frange(b_min, b_max, b_step):
                # 计算
                pa = PrincipalAgentModel(w, b, P, c)
                e_star, u_a, pi = pa.simulate()
                if pi > best_profit:
                    best_profit = pi
                    best_tuple = (w, b, pi)

        w_star, b_star, pi_star = best_tuple
        text_res = f"最优合同：w*={w_star:.2f}, b*={b_star:.2f}, 主人利润={pi_star:.2f}"
        self.label_agent_result.config(text=text_res)

        self.recorder.log("委托代理(最优合约搜索)",
                          {
                              "P": P,"c":c,
                              "w_range":[w_min, w_max, w_step],
                              "b_range":[b_min, b_max, b_step]
                          },
                          {
                              "w_star": w_star, "b_star":b_star, "max_profit":pi_star
                          })

    def frange(self, start, stop, step):
        # 辅助方法：浮点数范围遍历
        val = start
        while val <= stop + 1e-9:
            yield val
            val += step

    # ————— Tab 2：柠檬市场 ————— #
    def build_tab_lemons(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="二手车多轮模拟")

        frame_input = tk.Frame(tab)
        frame_input.pack(anchor=tk.NW, padx=10, pady=10)

        tk.Label(frame_input, text="车辆数量:").grid(row=0, column=0, sticky=tk.E)
        self.var_n_cars = tk.IntVar(value=50)
        tk.Entry(frame_input, textvariable=self.var_n_cars, width=5).grid(row=0, column=1)

        tk.Label(frame_input, text="HQ车概率(0.0~1.0):").grid(row=1, column=0, sticky=tk.E)
        self.var_phq = tk.DoubleVar(value=0.3)
        tk.Entry(frame_input, textvariable=self.var_phq, width=5).grid(row=1, column=1)

        tk.Label(frame_input, text="启用第三方检测:").grid(row=2, column=0, sticky=tk.E)
        self.var_check = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_input, variable=self.var_check).grid(row=2, column=1, sticky=tk.W)

        tk.Label(frame_input, text="模拟轮次:").grid(row=3, column=0, sticky=tk.E)
        self.var_rounds = tk.IntVar(value=5)
        tk.Entry(frame_input, textvariable=self.var_rounds, width=5).grid(row=3, column=1)

        btn_run = ttk.Button(frame_input, text="开始多轮模拟", command=self.run_lemons_sim)
        btn_run.grid(row=4, column=0, columnspan=2, pady=5)

        # 结果可视化
        self.fig_lemons = Figure(figsize=(5,3), dpi=100)
        self.ax_lemons = self.fig_lemons.add_subplot(111)
        self.canvas_lemons = FigureCanvasTkAgg(self.fig_lemons, master=tab)
        self.canvas_lemons.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_lemons_sim(self):
        n_cars = self.var_n_cars.get()
        p_hq = self.var_phq.get()
        check = self.var_check.get()
        n_rounds = self.var_rounds.get()

        model = LemonsMarketModel(n_cars, p_hq, check)
        avg_prices = []
        frac_HQs = []
        sold_counts = []

        for _ in range(n_rounds):
            avg_p, frac_hq, sold = model.one_round()
            avg_prices.append(avg_p)
            frac_HQs.append(frac_hq)
            sold_counts.append(sold)

        # 记录
        self.recorder.log("柠檬市场(多轮)",
                          {"n_cars":n_cars, "p_hq":p_hq, "check": check, "rounds": n_rounds},
                          {"avg_prices": avg_prices, "frac_HQs": frac_HQs, "sold_counts": sold_counts})

        # 更新可视化
        self.ax_lemons.clear()
        self.ax_lemons.set_title("柠檬市场 - 多轮模拟")
        self.ax_lemons.set_xlabel("Round")
        rounds = range(1, n_rounds+1)
        self.ax_lemons.plot(rounds, avg_prices, label="Avg Price", marker='o')
        self.ax_lemons.plot(rounds, [f*10 for f in frac_HQs], label="HQ fraction(*10)", marker='s')
        self.ax_lemons.set_ylim([0, 12])
        self.ax_lemons.legend()
        self.canvas_lemons.draw()

    # ————— Tab 3：保险与道德风险 ————— #
    def build_tab_insurance(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="保险与道德风险(多人)")

        frame_input = tk.Frame(tab)
        frame_input.pack(anchor=tk.NW, padx=10, pady=10)

        tk.Label(frame_input, text="基准失窃概率p0:").grid(row=0, column=0, sticky=tk.E)
        self.var_p0 = tk.DoubleVar(value=0.3)
        tk.Entry(frame_input, textvariable=self.var_p0, width=5).grid(row=0, column=1)

        tk.Label(frame_input, text="努力影响alpha:").grid(row=1, column=0, sticky=tk.E)
        self.var_alpha = tk.DoubleVar(value=0.05)
        tk.Entry(frame_input, textvariable=self.var_alpha, width=5).grid(row=1, column=1)

        tk.Label(frame_input, text="保险保费premium:").grid(row=2, column=0, sticky=tk.E)
        self.var_premium = tk.DoubleVar(value=10.0)
        tk.Entry(frame_input, textvariable=self.var_premium, width=5).grid(row=2, column=1)

        tk.Label(frame_input, text="赔付coverage:").grid(row=3, column=0, sticky=tk.E)
        self.var_coverage = tk.DoubleVar(value=100.0)
        tk.Entry(frame_input, textvariable=self.var_coverage, width=5).grid(row=3, column=1)

        tk.Label(frame_input, text="投保人数:").grid(row=4, column=0, sticky=tk.E)
        self.var_people = tk.IntVar(value=5)
        tk.Entry(frame_input, textvariable=self.var_people, width=5).grid(row=4, column=1)

        self.efforts = []  # 存储N个努力水平
        self.effort_vars = []
        frame_effort = tk.LabelFrame(tab, text="投保人努力列表(在此处输入)", padx=5, pady=5)
        frame_effort.pack(anchor=tk.NW, fill=tk.X, padx=10, pady=5)

        self.frame_effort_inputs = frame_effort
        # 默认先建5人
        self.build_effort_inputs()

        btn_run = ttk.Button(tab, text="多人保险模拟", command=self.run_insurance_multi)
        btn_run.pack(pady=10, anchor=tk.NW)

        self.label_ins_result = tk.Label(tab, text="结果将在此显示...", fg="blue")
        self.label_ins_result.pack(anchor=tk.NW, padx=10, pady=5)

    def build_effort_inputs(self):
        """根据self.var_people生成多个努力输入框"""
        for child in self.frame_effort_inputs.winfo_children():
            child.destroy()

        n = self.var_people.get()
        self.effort_vars.clear()

        # 头label
        tk.Label(self.frame_effort_inputs, text="请在此输入每位投保人的努力水平:").pack(anchor=tk.W)

        for i in range(n):
            var = tk.DoubleVar(value=1.0)
            self.effort_vars.append(var)
            tk.Entry(self.frame_effort_inputs, textvariable=var, width=5).pack(side=tk.LEFT, padx=2)

    def run_insurance_multi(self):
        p0 = self.var_p0.get()
        alpha = self.var_alpha.get()
        premium = self.var_premium.get()
        coverage = self.var_coverage.get()

        # 获取每位投保人的努力
        efforts = [var.get() for var in self.effort_vars]
        model = InsuranceRiskModel(p0, alpha, premium, coverage, len(efforts))
        avg_p, avg_u, total_profit = model.simulate_group(efforts)

        text_res = (f"平均失窃概率: {avg_p:.2f}, "
                    f"平均投保人收益: {avg_u:.2f}, "
                    f"保险公司总利润: {total_profit:.2f}")
        self.label_ins_result.config(text=text_res)

        self.recorder.log(
            "保险与道德风险(多人)",
            {"p0":p0, "alpha":alpha, "premium":premium, "coverage":coverage, "efforts": efforts},
            {"avg_theft_prob":avg_p, "avg_user_utility":avg_u, "company_total_profit":total_profit}
        )

    # ————— Tab 4：教育/招聘信号 ————— #
    def build_tab_signaling(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="教育信号(对比)")

        frame_input = tk.Frame(tab)
        frame_input.pack(anchor=tk.NW, padx=10, pady=10)

        tk.Label(frame_input, text="企业筛选门槛(s):").grid(row=0, column=0, sticky=tk.E)
        self.var_threshold = tk.DoubleVar(value=2.0)
        tk.Entry(frame_input, textvariable=self.var_threshold, width=5).grid(row=0, column=1)

        tk.Label(frame_input, text="学生人数:").grid(row=1, column=0, sticky=tk.E)
        self.var_students = tk.IntVar(value=5)
        tk.Entry(frame_input, textvariable=self.var_students, width=5).grid(row=1, column=1)

        btn_build_input = ttk.Button(frame_input, text="更新学生输入框", command=self.build_student_inputs)
        btn_build_input.grid(row=2, column=0, columnspan=2, pady=5)

        btn_run = ttk.Button(frame_input, text="开始招聘筛选对比", command=self.run_signaling_compare)
        btn_run.grid(row=3, column=0, columnspan=2, pady=5)

        self.frame_students_input = tk.LabelFrame(tab, text="学生【能力, 教育投入成本系数c, 教育投资e, 工资w】")
        self.frame_students_input.pack(anchor=tk.NW, fill=tk.X, padx=10, pady=5)

        self.label_signaling_result = tk.Label(tab, text="结果将在此显示...", fg="blue")
        self.label_signaling_result.pack(anchor=tk.NW, padx=10, pady=5)

        # matplot
        self.fig_signaling = Figure(figsize=(5,3), dpi=100)
        self.ax_signaling = self.fig_signaling.add_subplot(111)
        self.canvas_signaling = FigureCanvasTkAgg(self.fig_signaling, master=tab)
        self.canvas_signaling.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 默认先建N个输入
        self.student_list_vars = []
        self.build_student_inputs()

    def build_student_inputs(self):
        for child in self.frame_students_input.winfo_children():
            child.destroy()

        self.student_list_vars.clear()

        tk.Label(self.frame_students_input, text="序号").grid(row=0, column=0)
        tk.Label(self.frame_students_input, text="ability").grid(row=0, column=1)
        tk.Label(self.frame_students_input, text="cost_c").grid(row=0, column=2)
        tk.Label(self.frame_students_input, text="invest_e").grid(row=0, column=3)
        tk.Label(self.frame_students_input, text="wage").grid(row=0, column=4)

        n = self.var_students.get()
        for i in range(n):
            tk.Label(self.frame_students_input, text=f"{i+1}").grid(row=i+1, column=0)
            var_ability = tk.DoubleVar(value=1.0)
            var_c = tk.DoubleVar(value=0.1)
            var_invest = tk.DoubleVar(value=2.0)
            var_wage = tk.DoubleVar(value=50.0)

            self.student_list_vars.append((var_ability, var_c, var_invest, var_wage))

            tk.Entry(self.frame_students_input, textvariable=var_ability, width=5).grid(row=i+1, column=1)
            tk.Entry(self.frame_students_input, textvariable=var_c, width=5).grid(row=i+1, column=2)
            tk.Entry(self.frame_students_input, textvariable=var_invest, width=5).grid(row=i+1, column=3)
            tk.Entry(self.frame_students_input, textvariable=var_wage, width=5).grid(row=i+1, column=4)

    def run_signaling_compare(self):
        threshold = self.var_threshold.get()
        n = self.var_students.get()

        data_points = []
        # (student_index, labor_utility, firm_utility)
        for i, vars_4 in enumerate(self.student_list_vars):
            ability, cost_c, invest_e, wage = [v.get() for v in vars_4]
            model = EducationSignalingModel(ability, cost_c, wage)
            lu, fu = model.simulate(invest_e, threshold)
            data_points.append((i+1, ability, cost_c, invest_e, wage, lu, fu))

        # 记录
        self.recorder.log(
            "教育信号(多学生对比)",
            {"threshold": threshold, "num_students": n},
            {"data_points": data_points}
        )

        # 在界面显示
        lines = ["学生  教育投资-> 劳动力效用 / 企业收益"]
        for dp in data_points:
            idx, ab, cc, ie, w, lu, fu = dp
            lines.append(f"学生{idx}: e={ie:.1f} => U_labor={lu:.2f}, U_firm={fu:.2f}")
        self.label_signaling_result.config(text="\n".join(lines))

        # 可视化: 以 (index) vs (labor_utility / firm_utility)
        self.ax_signaling.clear()
        self.ax_signaling.set_title("教育信号 - 学生对比")
        xs = [dp[0] for dp in data_points]
        labor_ys = [dp[5] for dp in data_points]
        firm_ys = [dp[6] for dp in data_points]
        self.ax_signaling.plot(xs, labor_ys, marker='o', label='Labor utility')
        self.ax_signaling.plot(xs, firm_ys, marker='s', label='Firm payoff')
        self.ax_signaling.set_xticks(xs)
        self.ax_signaling.legend()
        self.canvas_signaling.draw()

    def show_report(self):
        report_text = self.recorder.generate_report_text()
        messagebox.showinfo("仿真报告", report_text)


def main():
    app = InfoEconExtendedApp()
    app.mainloop()


if __name__ == "__main__":
    main()