#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
融合改进后的数理模型、Tkinter GUI 与 Matplotlib 可视化的示例代码
--------------------------------------------------------------------
功能要点：
1. 在之前的改进版 GUI 基础上，加入 Matplotlib 画布，实现基本的可视化展示。
2. 二手车柠檬市场模块中，进行多轮模拟时实时记录成交均价和 HQ 占比，绘制折线图。
3. 可以同理在委托代理、保险、教育信号等模块中添加更多可视化，视需求扩展。

注意：
• 若要正常显示中文，需要安装中文字体并在 matplotlib 中设定相关字体参数（在代码开头 rcParams 配置）。
• 代码仅示例展示核心思路，实际项目可进一步封装和优化。
• 请确保已安装 numpy、matplotlib 等依赖库。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # 在 Tkinter 中嵌入 Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


##################################
# 改进后的核心逻辑类（与之前相同）
##################################

class ImprovedPrincipalAgentModel:
    def __init__(self,
                 outside_option=0.0,
                 cost_factor=0.1,
                 price=2.0,
                 w_min=0.0, w_max=20.0, w_step=1.0,
                 b_min=0.0, b_max=5.0, b_step=0.5):
        self.outside_option = outside_option
        self.c = cost_factor
        self.P = price
        self.w_min, self.w_max, self.w_step = w_min, w_max, w_step
        self.b_min, self.b_max, self.b_step = b_min, b_max, b_step

    def agent_best_effort(self, w, b):
        if b <= 0: return 0.0
        return b / (2.0 * self.c)

    def agent_utility(self, w, b, e):
        return w + b*e - self.c*(e**2)

    def principal_profit(self, w, b, e):
        return self.P*e - (w + b*e)

    def find_optimal_contract(self):
        best_w, best_b, best_pi = None, None, -1e9
        best_e, best_UA = 0.0, 0.0

        ws = np.arange(self.w_min, self.w_max + 1e-9, self.w_step)
        bs = np.arange(self.b_min, self.b_max + 1e-9, self.b_step)
        for w in ws:
            for b in bs:
                e_star = self.agent_best_effort(w, b)
                ua = self.agent_utility(w, b, e_star)
                if ua < self.outside_option:
                    continue  # 不满足参与约束
                pi = self.principal_profit(w, b, e_star)
                if pi > best_pi:
                    best_pi = pi
                    best_w = w
                    best_b = b
                    best_e = e_star
                    best_UA = ua
        return (best_w, best_b, best_pi, best_e, best_UA)


class ImprovedLemonsMarket:
    def __init__(self,
                 n_cars=100,
                 init_prob_HQ=0.3,
                 check_quality=False,
                 check_accuracy=0.7,
                 buyer_learning_rate=0.2):
        self.n_cars = n_cars
        self.init_prob_HQ = init_prob_HQ
        self.check_quality = check_quality
        self.check_accuracy = check_accuracy
        self.buyer_learning_rate = buyer_learning_rate

        self.cars = []
        self.buyer_belief = self.init_prob_HQ
        self.generate_cars()

    def generate_cars(self):
        self.cars.clear()
        for _ in range(self.n_cars):
            if random.random() < self.init_prob_HQ:
                self.cars.append("HQ")
            else:
                self.cars.append("LQ")

    def buyer_offer_price(self):
        # HQ=10, LQ=4
        return self.buyer_belief*10 + (1 - self.buyer_belief)*4

    def simulate_one_round(self):
        offer_price = self.buyer_offer_price()
        n_sold = 0
        total_price = 0.0
        sold_hq = 0

        for quality in self.cars:
            if self.check_quality:
                if random.random() < self.check_accuracy:
                    price = 10.0 if quality == "HQ" else 4.0
                else:
                    price = offer_price
            else:
                price = offer_price

            threshold = 8.0 if quality == "HQ" else 3.0

            if price >= threshold:
                n_sold += 1
                total_price += price
                if quality == "HQ":
                    sold_hq += 1

        if n_sold == 0:
            avg_price = 0.0
            frac_hq = 0.0
        else:
            avg_price = total_price / n_sold
            frac_hq = sold_hq / n_sold

        # belief update
        self.buyer_belief = (1 - self.buyer_learning_rate)*self.buyer_belief + self.buyer_learning_rate*frac_hq
        return avg_price, frac_hq, n_sold, self.buyer_belief


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
            p = self.p0 * ((1 - effort)**self.alpha)
        else:
            p = self.p0 - self.alpha*effort
        return max(0.0, min(1.0, p))

    def simulate_one(self, effort):
        p = self.theft_probability(effort)
        bicycle_value = 100.0
        actual_coverage = max(0, self.coverage - self.deductible)
        exp_return = - self.premium + (1 - p)*bicycle_value + p*(actual_coverage)
        company_profit = self.premium - p*actual_coverage
        return p, exp_return, company_profit


class ImprovedEducationSignaling:
    def __init__(self,
                 ability=1.0,
                 cost_factor=0.1,
                 wage=50.0,
                 outside_option=0.0):
        self.ability = ability
        self.c = cost_factor
        self.wage = wage
        self.outside_option = outside_option

    def labor_utility(self, invest, threshold):
        if invest < 0: invest = 0
        if invest >= threshold:
            return self.wage*self.ability - self.c*(invest**2)
        else:
            return - self.c*(invest**2)

    def firm_payoff(self, invest, threshold):
        if invest < threshold:
            return 0.0
        else:
            produce = 10 + 10*self.ability
            return produce - self.wage

    def simulate(self, invest, threshold):
        lu = self.labor_utility(invest, threshold)
        fu = self.firm_payoff(invest, threshold)
        return lu, fu

    @staticmethod
    def find_optimal_threshold(ability_list, cost_list, wage_list):
        best_s = 0.0
        best_profit = -1e9
        thr_candidates = np.arange(0.0, 10.0, 0.5)
        for s in thr_candidates:
            total_firm = 0
            for i in range(len(ability_list)):
                ed = ImprovedEducationSignaling(ability_list[i],
                                                cost_list[i],
                                                wage_list[i])
                invest = s
                _, fu = ed.simulate(invest, s)
                total_firm += fu
            if total_firm > best_profit:
                best_profit = total_firm
                best_s = s
        return best_s, best_profit


##########################################
# 数据记录器(简易) + GUI交互逻辑 + 可视化
##########################################

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
        lines.append("===== 信息经济学仿真报告 (可视化改进) =====\n")
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


class InfoEconApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 改进版(含可视化)")
        self.geometry("1100x700")

        self.recorder = SimulationDataRecorder()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.build_tab_pa()
        self.build_tab_lemons()   # 带可视化
        self.build_tab_insurance()
        self.build_tab_signaling()

        btn_report = ttk.Button(self, text="查看仿真报告", command=self.show_report)
        btn_report.pack(side=tk.BOTTOM, pady=5)

    ################################
    # 1. 委托代理(改进)
    ################################
    def build_tab_pa(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="委托代理(改进)")

        row_idx = 0
        tk.Label(tab, text="外部机会效用(U0):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_u0 = tk.DoubleVar(value=0.0)
        tk.Entry(tab, textvariable=self.var_pa_u0, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(tab, text="努力成本系数(c):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_c = tk.DoubleVar(value=0.1)
        tk.Entry(tab, textvariable=self.var_pa_c, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(tab, text="产出价格(P):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_p = tk.DoubleVar(value=2.0)
        tk.Entry(tab, textvariable=self.var_pa_p, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(tab, text="[w_min, w_max, step]:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_w = ttk.Frame(tab)
        self.var_pa_wmin = tk.DoubleVar(value=0.0)
        self.var_pa_wmax = tk.DoubleVar(value=20.0)
        self.var_pa_wstep = tk.DoubleVar(value=1.0)
        tk.Entry(frame_w, textvariable=self.var_pa_wmin, width=6).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_pa_wmax, width=6).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_pa_wstep, width=6).pack(side=tk.LEFT, padx=2)
        frame_w.grid(row=row_idx, column=1, sticky=tk.W, pady=2)
        row_idx += 1

        tk.Label(tab, text="[b_min, b_max, step]:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_b = ttk.Frame(tab)
        self.var_pa_bmin = tk.DoubleVar(value=0.0)
        self.var_pa_bmax = tk.DoubleVar(value=5.0)
        self.var_pa_bstep = tk.DoubleVar(value=0.5)
        tk.Entry(frame_b, textvariable=self.var_pa_bmin, width=6).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_pa_bmax, width=6).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_pa_bstep, width=6).pack(side=tk.LEFT, padx=2)
        frame_b.grid(row=row_idx, column=1, sticky=tk.W, pady=2)
        row_idx += 1

        btn_run_pa = ttk.Button(tab, text="搜索最优合同", command=self.run_pa_opt)
        btn_run_pa.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.label_pa_result = tk.Label(tab, text="结果将在此显示...")
        self.label_pa_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

    def run_pa_opt(self):
        u0 = self.var_pa_u0.get()
        c = self.var_pa_c.get()
        P = self.var_pa_p.get()
        w_min = self.var_pa_wmin.get()
        w_max = self.var_pa_wmax.get()
        w_step = self.var_pa_wstep.get()
        b_min = self.var_pa_bmin.get()
        b_max = self.var_pa_bmax.get()
        b_step = self.var_pa_bstep.get()

        model = ImprovedPrincipalAgentModel(
            outside_option= u0,
            cost_factor= c,
            price=P,
            w_min=w_min, w_max=w_max, w_step=w_step,
            b_min=b_min, b_max=b_max, b_step=b_step
        )

        w_star, b_star, pi_star, e_star, u_star = model.find_optimal_contract()

        text = (f"最优合同: w*={w_star:.2f}, b*={b_star:.2f},\n"
                f"主人利润={pi_star:.2f}, 代理人努力={e_star:.2f}, 代理人效用={u_star:.2f}")
        self.label_pa_result.config(text=text)

        self.recorder.log(
            "委托代理(改进)",
            {
                "u0":u0, "c":c, "P":P,
                "w_range":[w_min,w_max,w_step],
                "b_range":[b_min,b_max,b_step]
            },
            {
                "w_star":w_star, "b_star":b_star, "profit":pi_star,
                "e_star":e_star, "u_agent":u_star
            }
        )

    ################################
    # 2. 二手车(柠檬市场) + 可视化
    ################################
    def build_tab_lemons(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="柠檬市场(改进)")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx = 0
        tk.Label(frame_input, text="车辆数量:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_n_cars = tk.IntVar(value=50)
        tk.Entry(frame_input, textvariable=self.var_n_cars, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="初始HQ概率:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_phq = tk.DoubleVar(value=0.3)
        tk.Entry(frame_input, textvariable=self.var_phq, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="启用检测?").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_check = tk.BooleanVar(value=False)
        tk.Checkbutton(frame_input, variable=self.var_check).grid(row=row_idx, column=1, sticky=tk.W)
        row_idx+=1

        tk.Label(frame_input, text="检测准确度:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_acc = tk.DoubleVar(value=0.7)
        tk.Entry(frame_input, textvariable=self.var_acc, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="买方学习率:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_lr = tk.DoubleVar(value=0.2)
        tk.Entry(frame_input, textvariable=self.var_lr, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="模拟轮次:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_rounds = tk.IntVar(value=5)
        tk.Entry(frame_input, textvariable=self.var_rounds, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        btn_lemon = ttk.Button(frame_input, text="多轮模拟 & 绘图", command=self.run_lemons)
        btn_lemon.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        self.label_lemons_result = tk.Label(frame_input, text="输出将在此显示...")
        self.label_lemons_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 右侧放置画布
        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_lemons = Figure(figsize=(5,4), dpi=100)
        self.ax_lemons = self.fig_lemons.add_subplot(111)
        self.canvas_lemons = FigureCanvasTkAgg(self.fig_lemons, master=frame_plot)
        self.canvas_lemons.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_lemons(self):
        n_cars = self.var_n_cars.get()
        phq = self.var_phq.get()
        checkq = self.var_check.get()
        acc = self.var_acc.get()
        lr = self.var_lr.get()
        rounds = self.var_rounds.get()

        model = ImprovedLemonsMarket(n_cars, phq, checkq, acc, lr)

        avg_prices = []
        hq_fracs = []
        lines = []
        for r in range(rounds):
            avg_p, frac_hq, sold, new_belief = model.simulate_one_round()
            avg_prices.append(avg_p)
            hq_fracs.append(frac_hq)
            lines.append(
                f"第{r+1}轮: 成交均价={avg_p:.2f}, HQ占比={frac_hq*100:.1f}%, "
                f"成交量={sold}, 新信念={new_belief:.2f}"
            )

        result_text = "\n".join(lines)
        self.label_lemons_result.config(text=result_text)

        # 记录
        self.recorder.log(
            "二手车柠檬市场(改进)",
            {"n_cars":n_cars, "phq":phq, "check":checkq, "acc":acc, "lr":lr, "rounds":rounds},
            {"detailed_result": lines}
        )

        # 绘图
        self.ax_lemons.clear()
        self.ax_lemons.set_title("柠檬市场多轮模拟")
        self.ax_lemons.set_xlabel("回合数")
        self.ax_lemons.set_ylabel("成交均价 / HQ占比(×10)")
        rr = range(1, rounds+1)
        self.ax_lemons.plot(rr, avg_prices, marker='o', label='均价')
        # 为了让HQ占比可视化在同一个坐标轴上，可乘以10
        hq_scaled = [f*10 for f in hq_fracs]
        self.ax_lemons.plot(rr, hq_scaled, marker='s', label='HQ占比×10')
        self.ax_lemons.legend()
        self.canvas_lemons.draw()

    ################################
    # 3. 保险与道德风险(改进)
    ################################
    def build_tab_insurance(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="保险(改进)")

        row_idx = 0
        tk.Label(tab, text="基准失窃概率p0:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_p0 = tk.DoubleVar(value=0.3)
        tk.Entry(tab, textvariable=self.var_p0, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="努力影响alpha:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_alpha = tk.DoubleVar(value=0.05)
        tk.Entry(tab, textvariable=self.var_alpha, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="保险保费:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_premium = tk.DoubleVar(value=10.0)
        tk.Entry(tab, textvariable=self.var_premium, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="赔付coverage:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_cov = tk.DoubleVar(value=100.0)
        tk.Entry(tab, textvariable=self.var_cov, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="免赔额deductible:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_deduct = tk.DoubleVar(value=0.0)
        tk.Entry(tab, textvariable=self.var_deduct, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="risk_model(线性/幂):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_risk = tk.StringVar(value='linear')
        tk.Entry(tab, textvariable=self.var_risk, width=10).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="投保人努力(0~1):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_effort = tk.DoubleVar(value=0.5)
        tk.Entry(tab, textvariable=self.var_effort, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        btn_ins = ttk.Button(tab, text="模拟保险", command=self.run_insurance_once)
        btn_ins.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        self.label_ins_result = tk.Label(tab, text="结果将在此显示...")
        self.label_ins_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

    def run_insurance_once(self):
        p0 = self.var_p0.get()
        alpha = self.var_alpha.get()
        premium = self.var_premium.get()
        cov = self.var_cov.get()
        deduct = self.var_deduct.get()
        risk = self.var_risk.get()
        eff = self.var_effort.get()

        model = ImprovedInsuranceRiskModel(p0, alpha, premium, cov, deduct, risk)
        theft_prob, user_ret, comp_profit = model.simulate_one(eff)

        text = (f"失窃概率={theft_prob:.2f}, 投保人收益={user_ret:.2f}, "
                f"保险公司利润={comp_profit:.2f}")
        self.label_ins_result.config(text=text)

        self.recorder.log(
            "保险与道德风险(改进)",
            {
                "p0":p0, "alpha":alpha, "premium":premium,
                "coverage":cov,"deductible":deduct,"risk_model":risk,
                "effort":eff
            },
            {
                "theft_prob":theft_prob,
                "user_return":user_ret,
                "company_profit":comp_profit
            }
        )

    ################################
    # 4. 教育信号(改进)
    ################################
    def build_tab_signaling(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="教育信号(改进)")

        row_idx = 0
        tk.Label(tab, text="学生能力(ability):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ability = tk.DoubleVar(value=1.0)
        tk.Entry(tab, textvariable=self.var_ability, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="教育成本系数(c):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_csign = tk.DoubleVar(value=0.1)
        tk.Entry(tab, textvariable=self.var_csign, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="工资(wage):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_wage = tk.DoubleVar(value=50.0)
        tk.Entry(tab, textvariable=self.var_wage, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="教育投资(e):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_invest = tk.DoubleVar(value=2.0)
        tk.Entry(tab, textvariable=self.var_invest, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(tab, text="企业筛选阈值(s):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_threshold = tk.DoubleVar(value=3.0)
        tk.Entry(tab, textvariable=self.var_threshold, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        btn_sig = ttk.Button(tab, text="模拟教育投资", command=self.run_signaling_once)
        btn_sig.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        self.label_sig_result = tk.Label(tab, text="结果将在此显示...")
        self.label_sig_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

    def run_signaling_once(self):
        ab = self.var_ability.get()
        c = self.var_csign.get()
        w = self.var_wage.get()
        invest = self.var_invest.get()
        s = self.var_threshold.get()

        model = ImprovedEducationSignaling(ab, c, w)
        lu, fu = model.simulate(invest, s)

        text = f"劳动力效用={lu:.2f}, 企业收益={fu:.2f}"
        self.label_sig_result.config(text=text)

        self.recorder.log(
            "教育信号(改进)",
            {"ability":ab, "c":c, "wage":w, "invest":invest, "threshold":s},
            {"labor_utility":lu, "firm_payoff":fu}
        )

    ################################
    #  查看报告
    ################################
    def show_report(self):
        report_text = self.recorder.generate_report_text()
        messagebox.showinfo("仿真报告", report_text)


def main():
    # 如果要在Matplotlib中使用中文，可以在这设置字体(需系统安装中文字体)
    # 例如：
    # from matplotlib import rcParams
    # rcParams['font.sans-serif'] = ['SimHei']
    # rcParams['axes.unicode_minus'] = False

    app = InfoEconApp()
    app.mainloop()

if __name__ == "__main__":
    main()