#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息经济学课程仿真软件 - 整体框架示例 (Python 代码)

说明：
1. 以下代码仅为框架示例，展示各功能模块的基本结构与调用关系，适合初步搭建并后续扩展。
2. 代码以面向对象(OOP)的方式，拆分出各个核心子模块的类与函数，便于进一步深入实现。
3. 为了简化，所有逻辑放在一个文件中；实际开发中可将不同模块拆分为独立文件夹和.py文件。
4. 界面层示例基于Tkinter，图表可用matplotlib等库做可视化；此处仅演示核心结构与伪代码。
5. 若要实现更多高级功能（如数据库、网络等），可在此基础上继续拓展。

"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

##############################
# 数据/模型层 (核心逻辑与算法) #
##############################
class PrincipalAgentModel:
    """
    委托代理与激励机制模块示例：
    - 提供最基本的激励合约：固定工资w + 绩效系数b
    - 简化产出函数 Q(e) = e
    - 代理人努力成本函数 C(e) = c * e^2
    - 代理人效用 U_A = w + b*Q(e) - C(e)
    - 主人利润 π = P*Q(e) - (w + b*Q(e))
    """
    def __init__(self, wage=10.0, bonus=0.2, price=2.0, cost_factor=0.1):
        # 合同与模型参数
        self.wage = wage        # 固定工资
        self.bonus = bonus      # 绩效奖金
        self.price = price      # 单位价格
        self.cost_factor = cost_factor  # 努力成本系数

    def agent_best_effort(self):
        """
        代理人在给定(w,b)时的最优努力水平。
        对于简化线性产出 Q(e)=e，U_A = w + b*e - c*e^2
        dU_A/de = b - 2*c*e = 0 => e* = b/(2*c), 如果 b > 0.
        """
        if self.bonus <= 0:
            return 0.0
        return self.bonus / (2.0 * self.cost_factor)

    def agent_utility(self, effort):
        """ 代理人效用 """
        return self.wage + self.bonus * effort - self.cost_factor * (effort ** 2)

    def principal_profit(self, effort):
        """ 主人利润 """
        return self.price * effort - (self.wage + self.bonus * effort)

    def simulate(self):
        """
        返回在当前合同参数(w,b)下：
        - 代理人最优努力 e*
        - 代理人效用 U_A
        - 主人利润 π
        """
        e_star = self.agent_best_effort()
        U_agent = self.agent_utility(e_star)
        pi = self.principal_profit(e_star)
        return e_star, U_agent, pi


class LemonsMarketModel:
    """
    二手车市场 (“柠檬市场”) 模块示例：
    - 假设有高质量车(HQ)、低质量车(LQ)，比例上限N_H、N_L
    - 买方无法完全观察车况，但可设置“第三方检测”或“质保”提高信息透明度
    - 简化模拟：随机生成若干车辆质量并设置信息披露水平 -> 触发价格决策 -> 统计市场均衡
    """
    def __init__(self, n_cars=100, check_quality=False):
        # n_cars: 车辆总数
        # check_quality: 是否启用第三方检测/质保机制
        self.n_cars = n_cars
        self.check_quality = check_quality
        # 用于存储模拟生成的车辆信息
        self.cars = []

    def generate_cars(self):
        """
        随机生成车辆，每辆车有一个质量指标(高/低)。
        为简化：高质量车占比为30%，低质量车占比70%。
        """
        self.cars = []
        for _ in range(self.n_cars):
            # 随机决定此车是高质量(HQ)还是低质量(LQ)
            # 概率 0.3 -> HQ, 0.7 -> LQ
            if random.random() < 0.3:
                self.cars.append("HQ")
            else:
                self.cars.append("LQ")

    def simulate_market(self):
        """
        简化市场模拟：
        1) 如未开启check_quality，则买方只能出一个固定价(估计值) => 导致均价逐渐偏低(逆向选择)
        2) 如果开启check_quality，则系统假设一定概率识别出低质车 => 提高市场均价
        返回: (average_price, fraction_HQ_sold)
        """
        if not self.cars:
            self.generate_cars()

        # 模拟单轮定价
        # baseline: 不检测时，买方只能出一个中间价
        # 若开启检测，能剔除部分LQ或要求低价
        total_price = 0.0
        sold_count = 0
        sale_count_HQ = 0

        for car_quality in self.cars:
            if self.check_quality:
                # 假设有70%几率能识别真实质量
                detect_pass = (random.random() < 0.7)
                if detect_pass:
                    # 如果识别到HQ，出价相对较高; LQ -> 价格较低
                    if car_quality == "HQ":
                        price = 10.0  # HQ车卖价10
                    else:
                        price = 4.0   # LQ车卖价4
                else:
                    # 未识别质量 -> 买方出一个折中价
                    price = 6.0
            else:
                # 无检测机制 -> 买方只能出折中价5
                price = 5.0

            # 车主是否愿意卖？
            # HQ车主期望价 maybe 8，LQ车主期望价 maybe 3（随机示例）
            if car_quality == "HQ":
                threshold = 8.0
            else:
                threshold = 3.0

            if price >= threshold:
                # 成交
                total_price += price
                sold_count += 1
                if car_quality == "HQ":
                    sale_count_HQ += 1

        avg_price = total_price / sold_count if sold_count > 0 else 0.0
        frac_HQ_sold = sale_count_HQ / sold_count if sold_count > 0 else 0.0

        return avg_price, frac_HQ_sold, sold_count


class InsuranceRiskModel:
    """
    保险与道德风险示例(以自行车偷盗保险为例)：
    - 投保后个人努力(防盗措施)可能下降 -> 道德风险
    - 失窃概率 p(effort) = max(0, p0 - alpha*effort)
    - 保险公司利润：保费 - 预期理赔
    """
    def __init__(self, base_theft_prob=0.3, alpha=0.05, insurance_premium=10.0, coverage=100.0):
        # base_theft_prob: 无努力情况下失窃基准概率
        # alpha: 防盗努力对失窃概率的降低敏感度
        # insurance_premium: 保险费率(固定), 简化处理
        # coverage: 最大理赔额
        self.p0 = base_theft_prob
        self.alpha = alpha
        self.premium = insurance_premium
        self.coverage = coverage

    def theft_probability(self, effort):
        """ 失窃概率 p(e) """
        p_e = self.p0 - self.alpha * effort
        return max(0.0, min(1.0, p_e))

    def simulate(self, effort):
        """
        给定投保人努力水平 effort，计算：
        - 失窃概率 p
        - 投保人期望收益
        - 保险公司期望利润
        """
        p = self.theft_probability(effort)
        # 投保人：若车被偷，损失车价值(设为100)但能获得coverage赔付
        # 这里假设自行车价值100
        bicycle_value = 100.0
        # 投保人期望收益 = -(premium) + [ (1-p)*车辆价值 + p*(车辆价值-被盗后 + coverage补偿) ]
        # 但理赔低于车价值 -> 依需求可自行设定
        # 简化：理赔等于coverage(100.0)
        exp_return = - self.premium + (1 - p)*bicycle_value + p*(self.coverage)

        # 保险公司期望利润 = premium - p*coverage
        insurance_profit = self.premium - p*self.coverage

        return p, exp_return, insurance_profit


class EducationSignalingModel:
    """
    教育/招聘市场 - 信号发送与甄别示例：
    - 劳动力(学生)可选择教育投资 e_invest 作为能力信号
    - 企业(用人单位)具有筛选门槛 S
    - 当 e_invest >= S 时录用 -> 获得工资 W，否则工资0
    - 劳动力成本 = C(e_invest)，此处假设 C(e) = c * e_invest^2
    """
    def __init__(self, ability=1.0, c=0.1, wage=50.0):
        # ability: 简化表示学生本身能力(影响其收益)
        # c: 教育投入成本系数
        # wage: 企业录用后的工资
        self.ability = ability
        self.cost_factor = c
        self.base_wage = wage

    def labor_utility(self, e_invest, threshold):
        """
        若 e_invest >= threshold -> 获得 base_wage * ability - cost_factor * e_invest^2
        否则 -> 0 - cost
        这里假设如果没被录用，收入=0，仍要付出教育投资成本 => 如果要贴近现实可调整
        """
        if e_invest >= threshold:
            return self.base_wage * self.ability - self.cost_factor * (e_invest**2)
        else:
            # 也可选: labor_might_not_invest_if...
            return - self.cost_factor * (e_invest**2)

    def firm_payoff(self, e_invest, threshold):
        """
        企业对录用的员工获得某种“产出 - 工资”。
        简化：员工带来的产出 = (base_wage + 10) * ability - cost(可忽略)
        """
        if e_invest >= threshold:
            # 企业雇佣 -> 产出(若简化设为 base_wage + 10 ) - 工资
            produce = (self.base_wage + 10) * self.ability
            payoff = produce - self.base_wage
            return payoff
        else:
            # 未雇佣，不产生收益也无成本
            return 0.0

    def simulate(self, e_invest, threshold):
        """
        单回合模拟给定教育投资 e_invest 与企业筛选门槛 threshold
        返回 (labor_utility, firm_payoff)
        """
        u_labor = self.labor_utility(e_invest, threshold)
        u_firm = self.firm_payoff(e_invest, threshold)
        return u_labor, u_firm


#####################
# 数据处理/分析层示例 #
#####################
class SimulationDataRecorder:
    """
    用于记录和管理各模块模拟输出数据，以便后续统计分析或生成报告。
    """
    def __init__(self):
        self.records = []  # 存储（模块名, 参数, 输出）的列表

    def log(self, module_name, param_dict, result_dict):
        """
        参数：module_name 模块名称，如"PrincipalAgent"
             param_dict   输入参数
             result_dict  输出结果
        """
        self.records.append({
            "module" : module_name,
            "params" : param_dict,
            "results": result_dict
        })

    def generate_report(self):
        """
        简易示例：返回字符串形式的模拟报告；实际可转为HTML/CSV/PDF等
        """
        lines = []
        lines.append("======== 模拟报告 ========")
        for i, record in enumerate(self.records):
            lines.append(f"[{i+1}] 模块: {record['module']}")
            lines.append("    输入参数:")
            for k, v in record['params'].items():
                lines.append(f"      - {k}: {v}")
            lines.append("    模拟结果:")
            for k, v in record['results'].items():
                lines.append(f"      - {k}: {v}")
            lines.append(" ")
        report_text = "\n".join(lines)
        return report_text


##############################
# 界面层 (示例以 Tkinter 实现) #
##############################
class InfoEconSimulatorApp(tk.Tk):
    """
    主界面 - 整合各模拟模块
    """
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 示例版")
        self.geometry("800x600")

        # 数据记录器
        self.recorder = SimulationDataRecorder()

        # 添加界面元素
        self.create_widgets()

    def create_widgets(self):
        # 主菜单/选项卡布局
        tab_control = ttk.Notebook(self)

        # 1. 委托代理模块UI
        self.tab_agent = ttk.Frame(tab_control)
        tab_control.add(self.tab_agent, text="委托代理与激励")
        self.build_principal_agent_tab(self.tab_agent)

        # 2. 二手车柠檬市场
        self.tab_lemons = ttk.Frame(tab_control)
        tab_control.add(self.tab_lemons, text="二手车(柠檬市场)")
        self.build_lemons_tab(self.tab_lemons)

        # 3. 保险与偷盗风险
        self.tab_insurance = ttk.Frame(tab_control)
        tab_control.add(self.tab_insurance, text="保险与道德风险")
        self.build_insurance_tab(self.tab_insurance)

        # 4. 教育/招聘市场(信号发送)
        self.tab_signaling = ttk.Frame(tab_control)
        tab_control.add(self.tab_signaling, text="教育与招聘(信号)")
        self.build_signaling_tab(self.tab_signaling)

        tab_control.pack(expand=1, fill="both")

        # 按钮区：查看报告
        btn_report = ttk.Button(self, text="查看模拟报告", command=self.show_report)
        btn_report.pack(side=tk.BOTTOM, pady=10)

    def build_principal_agent_tab(self, parent):
        # 输入：wage, bonus, price, cost_factor
        frame = ttk.Frame(parent, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="固定工资(w):").grid(row=0, column=0, sticky=tk.E)
        self.var_w = tk.DoubleVar(value=10.0)
        tk.Entry(frame, textvariable=self.var_w).grid(row=0, column=1)

        tk.Label(frame, text="绩效系数(b):").grid(row=1, column=0, sticky=tk.E)
        self.var_b = tk.DoubleVar(value=0.2)
        tk.Entry(frame, textvariable=self.var_b).grid(row=1, column=1)

        tk.Label(frame, text="产品价格(P):").grid(row=2, column=0, sticky=tk.E)
        self.var_p = tk.DoubleVar(value=2.0)
        tk.Entry(frame, textvariable=self.var_p).grid(row=2, column=1)

        tk.Label(frame, text="努力成本系数(c):").grid(row=3, column=0, sticky=tk.E)
        self.var_c = tk.DoubleVar(value=0.1)
        tk.Entry(frame, textvariable=self.var_c).grid(row=3, column=1)

        btn_run = ttk.Button(frame, text="运行委托代理模拟", command=self.run_principal_agent)
        btn_run.grid(row=4, column=0, columnspan=2, pady=10)

        self.label_agent_result = tk.Label(frame, text="结果将在此显示...")
        self.label_agent_result.grid(row=5, column=0, columnspan=2, pady=10)

    def run_principal_agent(self):
        wage = self.var_w.get()
        bonus = self.var_b.get()
        price = self.var_p.get()
        cost_factor = self.var_c.get()

        model = PrincipalAgentModel(wage, bonus, price, cost_factor)
        e_star, u_a, pi = model.simulate()

        result_str = f"最优努力 e* = {e_star:.2f}, 代理人效用 = {u_a:.2f}, 主人利润 = {pi:.2f}"
        self.label_agent_result.config(text=result_str)

        # 记录数据
        self.recorder.log(
            "委托代理",
            {"w": wage, "b": bonus, "P": price, "c": cost_factor},
            {"e_star": e_star, "utility_agent": u_a, "profit_principal": pi}
        )

    def build_lemons_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="车辆总数:").grid(row=0, column=0, sticky=tk.E)
        self.var_num_cars = tk.IntVar(value=100)
        tk.Entry(frame, textvariable=self.var_num_cars).grid(row=0, column=1)

        tk.Label(frame, text="启用检测/质保?").grid(row=1, column=0, sticky=tk.E)
        self.var_check = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, variable=self.var_check).grid(row=1, column=1, sticky=tk.W)

        btn_run = ttk.Button(frame, text="模拟二手车市场", command=self.run_lemons_market)
        btn_run.grid(row=2, column=0, columnspan=2, pady=10)

        self.label_lemons_result = tk.Label(frame, text="结果将在此显示...")
        self.label_lemons_result.grid(row=3, column=0, columnspan=2, pady=10)

    def run_lemons_market(self):
        n_cars = self.var_num_cars.get()
        check_quality = self.var_check.get()
        model = LemonsMarketModel(n_cars, check_quality)
        model.generate_cars()
        avg_price, frac_HQ, sold_count = model.simulate_market()

        result_str = (f"实际成交量: {sold_count}, "
                      f"平均成交价: {avg_price:.2f}, "
                      f"HQ车占比: {frac_HQ*100:.1f}%")
        self.label_lemons_result.config(text=result_str)

        self.recorder.log(
            "二手车柠檬市场",
            {"n_cars": n_cars, "check_quality": check_quality},
            {"sold_count": sold_count, "avg_price": avg_price, "frac_HQ_sold": frac_HQ}
        )

    def build_insurance_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="基准失窃概率 p0:").grid(row=0, column=0, sticky=tk.E)
        self.var_p0 = tk.DoubleVar(value=0.3)
        tk.Entry(frame, textvariable=self.var_p0).grid(row=0, column=1)

        tk.Label(frame, text="努力影响系数 alpha:").grid(row=1, column=0, sticky=tk.E)
        self.var_alpha = tk.DoubleVar(value=0.05)
        tk.Entry(frame, textvariable=self.var_alpha).grid(row=1, column=1)

        tk.Label(frame, text="保险保费:").grid(row=2, column=0, sticky=tk.E)
        self.var_premium = tk.DoubleVar(value=10.0)
        tk.Entry(frame, textvariable=self.var_premium).grid(row=2, column=1)

        tk.Label(frame, text="赔付金额 coverage:").grid(row=3, column=0, sticky=tk.E)
        self.var_coverage = tk.DoubleVar(value=100.0)
        tk.Entry(frame, textvariable=self.var_coverage).grid(row=3, column=1)

        tk.Label(frame, text="投保人努力:").grid(row=4, column=0, sticky=tk.E)
        self.var_effort = tk.DoubleVar(value=1.0)
        tk.Entry(frame, textvariable=self.var_effort).grid(row=4, column=1)

        btn_run = ttk.Button(frame, text="模拟保险与道德风险", command=self.run_insurance)
        btn_run.grid(row=5, column=0, columnspan=2, pady=10)

        self.label_insurance_result = tk.Label(frame, text="结果将在此显示...")
        self.label_insurance_result.grid(row=6, column=0, columnspan=2, pady=10)

    def run_insurance(self):
        p0 = self.var_p0.get()
        alpha = self.var_alpha.get()
        premium = self.var_premium.get()
        coverage = self.var_coverage.get()
        effort = self.var_effort.get()

        model = InsuranceRiskModel(p0, alpha, premium, coverage)
        theft_prob, exp_return, comp_profit = model.simulate(effort)

        result_str = (f"失窃概率: {theft_prob:.2f}, "
                      f"投保人期望收益: {exp_return:.2f}, "
                      f"保险公司利润: {comp_profit:.2f}")
        self.label_insurance_result.config(text=result_str)

        self.recorder.log(
            "保险与道德风险",
            {"p0": p0, "alpha": alpha, "premium": premium, "coverage": coverage, "effort": effort},
            {"theft_prob": theft_prob, "user_utility": exp_return, "company_profit": comp_profit}
        )

    def build_signaling_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="个人能力(ability):").grid(row=0, column=0, sticky=tk.E)
        self.var_ability = tk.DoubleVar(value=1.0)
        tk.Entry(frame, textvariable=self.var_ability).grid(row=0, column=1)

        tk.Label(frame, text="教育成本系数(c):").grid(row=1, column=0, sticky=tk.E)
        self.var_c_sign = tk.DoubleVar(value=0.1)
        tk.Entry(frame, textvariable=self.var_c_sign).grid(row=1, column=1)

        tk.Label(frame, text="工资(wage):").grid(row=2, column=0, sticky=tk.E)
        self.var_wage_sign = tk.DoubleVar(value=50.0)
        tk.Entry(frame, textvariable=self.var_wage_sign).grid(row=2, column=1)

        tk.Label(frame, text="教育投资:").grid(row=3, column=0, sticky=tk.E)
        self.var_e_invest = tk.DoubleVar(value=0.0)
        tk.Entry(frame, textvariable=self.var_e_invest).grid(row=3, column=1)

        tk.Label(frame, text="企业筛选门槛:").grid(row=4, column=0, sticky=tk.E)
        self.var_threshold = tk.DoubleVar(value=1.0)
        tk.Entry(frame, textvariable=self.var_threshold).grid(row=4, column=1)

        btn_run = ttk.Button(frame, text="模拟教育信号与招聘筛选", command=self.run_signaling)
        btn_run.grid(row=5, column=0, columnspan=2, pady=10)

        self.label_signaling_result = tk.Label(frame, text="结果将在此显示...")
        self.label_signaling_result.grid(row=6, column=0, columnspan=2, pady=10)

    def run_signaling(self):
        ability = self.var_ability.get()
        c_factor = self.var_c_sign.get()
        wage = self.var_wage_sign.get()
        e_invest = self.var_e_invest.get()
        threshold = self.var_threshold.get()

        model = EducationSignalingModel(ability, c_factor, wage)
        u_labor, u_firm = model.simulate(e_invest, threshold)
        result_str = (f"劳动力效用: {u_labor:.2f}, 企业收益: {u_firm:.2f}")
        self.label_signaling_result.config(text=result_str)

        self.recorder.log(
            "教育与招聘信号",
            {"ability": ability, "c": c_factor, "wage": wage,
             "invest": e_invest, "threshold": threshold},
            {"labor_utility": u_labor, "firm_payoff": u_firm}
        )

    def show_report(self):
        report_text = self.recorder.generate_report()
        # 弹框显示报告
        messagebox.showinfo("模拟报告", report_text)


##############################
# 主程序入口                 #
##############################
def main():
    app = InfoEconSimulatorApp()
    app.mainloop()

if __name__ == "__main__":
    main()