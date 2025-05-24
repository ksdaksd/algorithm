#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息经济学仿真软件 - 高级可视化(各模块都有多参数扫描或可视化示例)
-------------------------------------------------------------------
功能要点:
1. 在委托代理、二手车、保险、教育信号等模块中，都加入了可视化功能:
   - 二手车(柠檬市场)原先已有多轮模拟折线图示例, 保留。
   - 委托代理: 添加 (w, b) 网格扫描, 将主人利润或代理人效用做曲面图/热力图等。
   - 保险与道德风险: 扫描努力(effort)、或保费/覆盖等参数, 绘制多条曲线或柱状图。
   - 教育信号: 增加“多学生对比”, 并可视化不同阈值(s)下各学生的(劳动力效用,企业收益)。

2. 若需要中文正常显示, 请安装中文字体并在 main() 函数开头处做 rcParams 配置:
   rcParams['font.sans-serif'] = ['SimHei']
   rcParams['axes.unicode_minus'] = False

3. 示例仅展示思路, 具体可据需求拓展或深度优化。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from mpl_toolkits.mplot3d import Axes3D  # 用于3D曲面/散点
# 默认设置中文字体(如果系统已安装，如SimHei)，否则可注释掉自行测试
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


###################################
#  (一) 核心逻辑类
###################################

class ImprovedPrincipalAgentModel:
    """委托代理(改进)"""
    def __init__(self,
                 outside_option=0.0,
                 cost_factor=0.1,
                 price=2.0,
                 # 如果仅做最优搜索则要 w_min,w_max,b_min,b_max 等
                 w_min=0.0, w_max=20.0, w_step=1.0,
                 b_min=0.0, b_max=5.0, b_step=0.5):
        self.outside_option = outside_option
        self.c = cost_factor
        self.P = price
        self.w_min, self.w_max, self.w_step = w_min, w_max, w_step
        self.b_min, self.b_max, self.b_step = b_min, b_max, b_step

    def agent_best_effort(self, w, b):
        if b <= 0:
            return 0.0
        return b / (2.0 * self.c)

    def agent_utility(self, w, b, e):
        return w + b*e - self.c*(e**2)

    def principal_profit(self, w, b, e):
        return self.P*e - (w + b*e)

    def find_optimal_contract(self):
        """原先网格搜索最优合同示例"""
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
    """二手车柠檬市场(改进)"""
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
        return self.buyer_belief*10 + (1 - self.buyer_belief)*4

    def simulate_one_round(self):
        offer_price = self.buyer_offer_price()
        n_sold = 0
        total_price = 0.0
        sold_hq = 0

        for quality in self.cars:
            if self.check_quality:
                # 以 check_accuracy 准确识别
                if random.random() < self.check_accuracy:
                    price = 10.0 if quality=="HQ" else 4.0
                else:
                    price = offer_price
            else:
                price = offer_price

            threshold = 8.0 if quality=="HQ" else 3.0
            if price >= threshold:
                n_sold += 1
                total_price += price
                if quality=="HQ":
                    sold_hq += 1

        if n_sold==0:
            avg_price = 0.0
            frac_hq = 0.0
        else:
            avg_price = total_price / n_sold
            frac_hq = sold_hq / n_sold

        # 更新信念
        self.buyer_belief = (1 - self.buyer_learning_rate)*self.buyer_belief + self.buyer_learning_rate*frac_hq
        return avg_price, frac_hq, n_sold, self.buyer_belief


class ImprovedInsuranceRiskModel:
    """保险(改进)"""
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
        if self.risk_model=='power':
            p = self.p0 * ((1 - effort)**self.alpha)
        else:
            p = self.p0 - self.alpha*effort
        return max(0.0, min(1.0, p))

    def simulate_one(self, effort):
        p = self.theft_probability(effort)
        bicycle_value = 100.0
        actual_coverage = max(0, self.coverage - self.deductible)
        exp_return = - self.premium + (1 - p)*bicycle_value + p*actual_coverage
        comp_profit = self.premium - p*actual_coverage
        return p, exp_return, comp_profit


class ImprovedEducationSignaling:
    """教育信号(改进)"""
    def __init__(self, ability=1.0, cost_factor=0.1, wage=50.0):
        self.ability = ability
        self.c = cost_factor
        self.wage = wage

    def labor_utility(self, invest, threshold):
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


###################################
#  (二) 数据记录器
###################################

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
        lines.append("===== 信息经济学仿真报告 (高级可视化合集) =====\n")
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


###################################
#  (三) 主GUI程序
###################################

class AdvancedInfoEconApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 优化可视化版")
        self.geometry("1300x900")

        self.recorder = SimulationDataRecorder()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # 构建各Tab
        self.build_tab_pa()       # 委托代理
        self.build_tab_lemons()   # 柠檬市场
        self.build_tab_insurance()# 保险
        self.build_tab_edu()      # 教育信号

        # 报告按钮
        btn_report = ttk.Button(self, text="查看报告", command=self.show_report)
        btn_report.pack(side=tk.BOTTOM, pady=5)

    ################################################
    # 1) 委托代理 - 多参数扫描 + 可视化(热力图/3D)
    ################################################
    def build_tab_pa(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="委托代理 - 可视化")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx = 0
        tk.Label(frame_input, text="外部效用(U0):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pau0 = tk.DoubleVar(value=0.0)
        tk.Entry(frame_input, textvariable=self.var_pau0, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(frame_input, text="努力成本系数(c):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pac = tk.DoubleVar(value=0.1)
        tk.Entry(frame_input, textvariable=self.var_pac, width=6).grid(row=row_idx, column=1, padx=5)
        row_idx+=1

        tk.Label(frame_input, text="产出价格(P):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pap = tk.DoubleVar(value=2.0)
        tk.Entry(frame_input, textvariable=self.var_pap, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        # 网格范围
        tk.Label(frame_input, text="w范围 [min,max,step]").grid(row=row_idx, column=0, sticky=tk.E)
        frame_w = ttk.Frame(frame_input)
        self.var_pawmin = tk.DoubleVar(value=0.0)
        self.var_pawmax = tk.DoubleVar(value=20.0)
        self.var_pawstep = tk.DoubleVar(value=2.0)
        tk.Entry(frame_w, textvariable=self.var_pawmin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_pawmax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_pawstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_w.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx+=1

        tk.Label(frame_input, text="b范围 [min,max,step]").grid(row=row_idx, column=0, sticky=tk.E)
        frame_b = ttk.Frame(frame_input)
        self.var_pabmin = tk.DoubleVar(value=0.0)
        self.var_pabmax = tk.DoubleVar(value=5.0)
        self.var_pabstep = tk.DoubleVar(value=1.0)
        tk.Entry(frame_b, textvariable=self.var_pabmin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_pabmax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_pabstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_b.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx+=1

        # 下拉框选择: "利润-3D", "利润-热力图", "效用-3D", "效用-热力图"
        tk.Label(frame_input, text="可视化类型:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_pa_chart_type = tk.StringVar(value="利润-3D")
        cb_type = ttk.Combobox(frame_input, textvariable=self.var_pa_chart_type,
                               values=["利润-3D","利润-热力图","效用-3D","效用-热力图"], width=10)
        cb_type.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx+=1

        btn_scan = ttk.Button(frame_input, text="扫描 & 可视化", command=self.run_pa_scan)
        btn_scan.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        self.label_pa_result = tk.Label(frame_input, text="可视化结果信息...")
        self.label_pa_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_pa = Figure(figsize=(5,4), dpi=100)
        self.ax_pa = self.fig_pa.add_subplot(111, projection='3d')
        self.canvas_pa = FigureCanvasTkAgg(self.fig_pa, master=frame_plot)
        self.canvas_pa.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_pa_scan(self):
        u0 = self.var_pau0.get()
        c = self.var_pac.get()
        p = self.var_pap.get()
        wmin, wmax, wstep = self.var_pawmin.get(), self.var_pawmax.get(), self.var_pawstep.get()
        bmin, bmax, bstep = self.var_pabmin.get(), self.var_pabmax.get(), self.var_pabstep.get()
        chart_type = self.var_pa_chart_type.get()

        # 清理
        self.fig_pa.clear()
        if "3D" in chart_type:
            self.ax_pa = self.fig_pa.add_subplot(111, projection='3d')
        else:
            self.ax_pa = self.fig_pa.add_subplot(111)

        model = ImprovedPrincipalAgentModel(u0, c, p)

        ws = np.arange(wmin, wmax+1e-9, wstep)
        bs = np.arange(bmin, bmax+1e-9, bstep)
        X, Y = np.meshgrid(ws, bs)  # shape: (len(bs), len(ws))
        Z = np.zeros_like(X)

        valid_count = 0
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                w_val = X[i,j]
                b_val = Y[i,j]
                e_star = model.agent_best_effort(w_val, b_val)
                ua = model.agent_utility(w_val, b_val, e_star)
                if ua < u0:
                    Z[i,j] = np.nan
                else:
                    valid_count +=1
                    if "利润" in chart_type:
                        Z[i,j] = model.principal_profit(w_val, b_val, e_star)
                    else:
                        Z[i,j] = ua

        if "3D" in chart_type:
            mask = ~np.isnan(Z)
            Xf = X[mask]
            Yf = Y[mask]
            Zf = Z[mask]
            self.ax_pa.plot_trisurf(Xf, Yf, Zf, cmap='viridis', edgecolor='none')
            self.ax_pa.set_xlabel("w")
            self.ax_pa.set_ylabel("b")
            self.ax_pa.set_zlabel("Z")
            self.ax_pa.set_title(chart_type)
        else:
            cax = self.ax_pa.imshow(Z, origin="lower", cmap='hot',
                                    extent=[wmin, wmax, bmin, bmax],
                                    aspect='auto')
            self.fig_pa.colorbar(cax, ax=self.ax_pa, fraction=0.03)
            self.ax_pa.set_xlabel("w")
            self.ax_pa.set_ylabel("b")
            self.ax_pa.set_title(chart_type)

        self.canvas_pa.draw()
        self.label_pa_result.config(text=f"有效网格点={valid_count}")

        self.recorder.log("委托代理-多参数可视化",
                          {"u0":u0,"c":c,"price":p,"chart_type":chart_type,
                           "w_range":[wmin,wmax,wstep],
                           "b_range":[bmin,bmax,bstep]},
                          {"valid_points":valid_count})

    ################################################
    # 2) 二手车(柠檬市场) - 多轮模拟(折线图) (保留)
    ################################################
    def build_tab_lemons(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="柠檬市场")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx=0
        tk.Label(frame_input, text="车辆数量:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_ncars = tk.IntVar(value=50)
        tk.Entry(frame_input, textvariable=self.var_ncars, width=6).grid(row=row_idx, column=1)
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

        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_lemons = Figure(figsize=(5,4), dpi=100)
        self.ax_lemons = self.fig_lemons.add_subplot(111)
        self.canvas_lemons = FigureCanvasTkAgg(self.fig_lemons, master=frame_plot)
        self.canvas_lemons.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_lemons(self):
        n_cars = self.var_ncars.get()
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
            lines.append(f"第{r+1}轮: 均价={avg_p:.2f}, HQ占比={frac_hq*100:.1f}%, 成交量={sold}, 新信念={new_belief:.2f}")

        text_res = "\n".join(lines)
        self.label_lemons_result.config(text=text_res)

        # 绘图
        self.ax_lemons.clear()
        self.ax_lemons.set_title("柠檬市场多轮模拟")
        self.ax_lemons.set_xlabel("回合")
        self.ax_lemons.set_ylabel("成交均价 / HQ占比(×10)")
        rr = range(1, rounds+1)
        self.ax_lemons.plot(rr, avg_prices, marker='o', label="均价")
        hq_scaled = [f*10 for f in hq_fracs]
        self.ax_lemons.plot(rr, hq_scaled, marker='s', label="HQ占比×10")
        self.ax_lemons.legend()
        self.canvas_lemons.draw()

        self.recorder.log("柠檬市场(改进)",
                          {"n_cars":n_cars,"pHQ":phq,"checkq":checkq,"acc":acc,
                           "learning_rate":lr,"rounds":rounds},
                          {"lines":lines})

    ################################################
    # 3) 保险(改进) - 努力(e)扫描 画多曲线
    ################################################
    def build_tab_insurance(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="保险 - 可视化")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx=0
        tk.Label(frame_input, text="失窃基准p0:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_p0 = tk.DoubleVar(value=0.3)
        tk.Entry(frame_input, textvariable=self.var_p0, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx+=1

        tk.Label(frame_input, text="alpha:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_alpha = tk.DoubleVar(value=0.05)
        tk.Entry(frame_input, textvariable=self.var_alpha, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="保费premium:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_prem = tk.DoubleVar(value=10.0)
        tk.Entry(frame_input, textvariable=self.var_prem, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="coverage:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_cov = tk.DoubleVar(value=100.0)
        tk.Entry(frame_input, textvariable=self.var_cov, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="免赔额deductible:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_deduct = tk.DoubleVar(value=0.0)
        tk.Entry(frame_input, textvariable=self.var_deduct, width=6).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="风险模型(linear/power):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_risk = tk.StringVar(value="linear")
        tk.Entry(frame_input, textvariable=self.var_risk, width=8).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="努力扫描[e_min,e_max,step]:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_escan = ttk.Frame(frame_input)
        self.var_emin = tk.DoubleVar(value=0.0)
        self.var_emax = tk.DoubleVar(value=1.0)
        self.var_estep = tk.DoubleVar(value=0.1)
        tk.Entry(frame_escan, textvariable=self.var_emin, width=4).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_escan, textvariable=self.var_emax, width=4).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_escan, textvariable=self.var_estep, width=4).pack(side=tk.LEFT, padx=2)
        frame_escan.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx+=1

        btn_ins_scan = ttk.Button(frame_input, text="努力扫描 & 绘图", command=self.run_insurance_scan)
        btn_ins_scan.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        self.label_ins_result = tk.Label(frame_input, text="结果信息...")
        self.label_ins_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_ins = Figure(figsize=(5,4), dpi=100)
        self.ax_ins = self.fig_ins.add_subplot(111)
        self.canvas_ins = FigureCanvasTkAgg(self.fig_ins, master=frame_plot)
        self.canvas_ins.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_insurance_scan(self):
        p0 = self.var_p0.get()
        alpha = self.var_alpha.get()
        prem = self.var_prem.get()
        cov = self.var_cov.get()
        deduct = self.var_deduct.get()
        risk = self.var_risk.get()
        emin, emax, estep = self.var_emin.get(), self.var_emax.get(), self.var_estep.get()

        model = ImprovedInsuranceRiskModel(p0, alpha, prem, cov, deduct, risk)
        efforts = np.arange(emin, emax+1e-9, estep)
        theft_probs = []
        user_utils = []
        comp_profits = []

        for e in efforts:
            p, u, cp = model.simulate_one(e)
            theft_probs.append(p)
            user_utils.append(u)
            comp_profits.append(cp)

        # 绘图
        self.ax_ins.clear()
        self.ax_ins.set_title("保险 - 努力扫描")
        self.ax_ins.set_xlabel("努力(e)")
        self.ax_ins.plot(efforts, theft_probs, 'r-o', label="失窃率")
        self.ax_ins.plot(efforts, user_utils, 'g-s', label="投保人收益")
        self.ax_ins.plot(efforts, comp_profits, 'b-^', label="公司利润")
        self.ax_ins.legend()
        self.canvas_ins.draw()

        best_user_idx = np.argmax(user_utils)
        best_cmp_idx = np.argmax(comp_profits)
        text_res = (f"投保人收益最大:e={efforts[best_user_idx]:.2f},收益={user_utils[best_user_idx]:.2f}\n"
                    f"公司利润最大:e={efforts[best_cmp_idx]:.2f},利润={comp_profits[best_cmp_idx]:.2f}")
        self.label_ins_result.config(text=text_res)

        self.recorder.log("保险-努力扫描",
                          {"p0":p0,"alpha":alpha,"premium":prem,"coverage":cov,"deduct":deduct,"risk":risk,
                           "effort_range":[emin,emax,estep]},
                          {"best_user_index":best_user_idx,"best_company_index":best_cmp_idx})

    ################################################
    # 4) 教育信号 - 多学生对比 & 可视化
    ################################################
    def build_tab_edu(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="教育信号 - 多学生")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx=0
        tk.Label(frame_input, text="学生数量:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_stu_num = tk.IntVar(value=3)
        tk.Entry(frame_input, textvariable=self.var_stu_num, width=5).grid(row=row_idx, column=1)
        row_idx+=1

        tk.Label(frame_input, text="阈值(s)扫描[start,end,step]").grid(row=row_idx, column=0, sticky=tk.E)
        frame_s = ttk.Frame(frame_input)
        self.var_smin = tk.DoubleVar(value=0.0)
        self.var_smax = tk.DoubleVar(value=5.0)
        self.var_sstep = tk.DoubleVar(value=1.0)
        tk.Entry(frame_s, textvariable=self.var_smin, width=4).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_s, textvariable=self.var_smax, width=4).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_s, textvariable=self.var_sstep, width=4).pack(side=tk.LEFT, padx=2)
        frame_s.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx+=1

        btn_build = ttk.Button(frame_input, text="创建学生输入框", command=self.build_students_input)
        btn_build.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        btn_run = ttk.Button(frame_input, text="阈值扫描 & 可视化", command=self.run_edu_many_students)
        btn_run.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx+=1

        self.label_edu_result = tk.Label(frame_input, text="输出信息...")
        self.label_edu_result.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 学生信息输入区
        self.frame_students = ttk.LabelFrame(tab, text="学生信息(ability,cost,wage,invest)")
        self.frame_students.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 图
        self.fig_edu = Figure(figsize=(5,4), dpi=100)
        self.ax_edu = self.fig_edu.add_subplot(111)
        self.canvas_edu = FigureCanvasTkAgg(self.fig_edu, master=tab)
        self.canvas_edu.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.list_student_vars = []

    def build_students_input(self):
        for child in self.frame_students.winfo_children():
            child.destroy()
        self.list_student_vars.clear()

        n = self.var_stu_num.get()
        # 标题行
        tk.Label(self.frame_students, text="ID").grid(row=0, column=0)
        tk.Label(self.frame_students, text="ability").grid(row=0, column=1)
        tk.Label(self.frame_students, text="cost").grid(row=0, column=2)
        tk.Label(self.frame_students, text="wage").grid(row=0, column=3)
        tk.Label(self.frame_students, text="invest").grid(row=0, column=4)

        for i in range(n):
            tk.Label(self.frame_students, text=f"Stu{i+1}").grid(row=i+1, column=0)
            var_a = tk.DoubleVar(value=1.0)
            var_c = tk.DoubleVar(value=0.1)
            var_w = tk.DoubleVar(value=50.0)
            var_inv = tk.DoubleVar(value=2.0)
            self.list_student_vars.append((var_a,var_c,var_w,var_inv))

            tk.Entry(self.frame_students, textvariable=var_a, width=5).grid(row=i+1, column=1)
            tk.Entry(self.frame_students, textvariable=var_c, width=5).grid(row=i+1, column=2)
            tk.Entry(self.frame_students, textvariable=var_w, width=5).grid(row=i+1, column=3)
            tk.Entry(self.frame_students, textvariable=var_inv, width=5).grid(row=i+1, column=4)

    def run_edu_many_students(self):
        smin, smax, sstep = self.var_smin.get(), self.var_smax.get(), self.var_sstep.get()
        thresholds = np.arange(smin, smax+1e-9, sstep)
        # 每个学生(ability,cost,wage,invest) -> 在所有threshold做一遍simulate

        self.ax_edu.clear()
        self.ax_edu.set_title("多学生 - 不同阈值下LU & Firm收益")
        self.ax_edu.set_xlabel("threshold")
        self.ax_edu.set_ylabel("效用/收益")

        for idx, st in enumerate(self.list_student_vars):
            ab, cc, ww, inv = st
            model = ImprovedEducationSignaling(ab.get(), cc.get(), ww.get())
            lu_list = []
            fu_list = []
            for s in thresholds:
                lu, fu = model.simulate(inv.get(), s)
                lu_list.append(lu)
                fu_list.append(fu)

            self.ax_edu.plot(thresholds, lu_list, marker='o', label=f"Stu{idx+1}-LU", alpha=0.6)
            self.ax_edu.plot(thresholds, fu_list, marker='s', label=f"Stu{idx+1}-Firm", alpha=0.6)

        self.ax_edu.legend()
        self.canvas_edu.draw()
        self.label_edu_result.config(text=f"已完成对 {len(self.list_student_vars)} 位学生的多阈值扫描")

        self.recorder.log("教育-多学生对比",
                          {"num_students": len(self.list_student_vars),
                           "threshold_range":[smin,smax,sstep]},
                          {})

    ################################################
    #  查看报告
    ################################################
    def show_report(self):
        rpt = self.recorder.generate_report_text()
        messagebox.showinfo("仿真报告", rpt)


def main():
    # 如果需要中文显示:
    # from matplotlib import rcParams
    # rcParams['font.sans-serif'] = ['SimHei']
    # rcParams['axes.unicode_minus'] = False

    app = AdvancedInfoEconApp()
    app.mainloop()

if __name__ == "__main__":
    main()