#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于开题报告与test7.py界面要求的界面原型示例
仅实现各模块功能界面，不包含具体的仿真计算逻辑
"""

import tkinter as tk
from tkinter import ttk, messagebox


def not_implemented():
    messagebox.showinfo("提示", "该功能尚未实现。")


class SimAppUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 界面原型")
        self.geometry("1200x800")

        # 创建Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # 添加各模块Tab
        self.create_risk_preference_tab()
        self.create_principal_agent_tab()
        self.create_lemons_market_tab()
        self.create_insurance_tab()
        self.create_education_signal_tab()

        # 底部“查看报告”按钮（共用）
        btn_report = ttk.Button(self, text="查看报告", command=not_implemented)
        btn_report.pack(side=tk.BOTTOM, pady=10)

    def create_risk_preference_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="风险偏好")

        # 左侧参数输入区
        frame_input = ttk.Frame(tab, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        # 风险偏好选择
        ttk.Label(frame_input, text="请选择风险偏好：").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.var_risk_choice = tk.StringVar(value="风险中性")
        cb_risk = ttk.Combobox(frame_input, textvariable=self.var_risk_choice, state="readonly",
                               values=["风险厌恶", "风险中性", "风险偏好"], width=12)
        cb_risk.grid(row=0, column=1, pady=5)

        # 投资金额
        ttk.Label(frame_input, text="投资金额：").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.var_invest = tk.DoubleVar(value=1000)
        ttk.Entry(frame_input, textvariable=self.var_invest, width=10).grid(row=1, column=1, pady=5)

        # 模拟决策按钮
        btn_simulate = ttk.Button(frame_input, text="模拟决策", command=not_implemented)
        btn_simulate.grid(row=2, column=0, columnspan=2, pady=10)

        # 右侧结果显示区（例如绘图或文本）
        frame_output = ttk.Frame(tab, padding=10, relief="solid")
        frame_output.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_output, text="【风险偏好模块】图表/结果区域", font=("Arial", 14)).pack(expand=True)

    def create_principal_agent_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="委托代理")

        frame_input = ttk.Frame(tab, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        # 外部效用
        ttk.Label(frame_input, text="外部效用(U0)：").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.var_u0 = tk.DoubleVar(value=0.0)
        ttk.Entry(frame_input, textvariable=self.var_u0, width=8).grid(row=0, column=1, pady=5)

        # 努力成本系数
        ttk.Label(frame_input, text="成本系数(c)：").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.var_c = tk.DoubleVar(value=0.1)
        ttk.Entry(frame_input, textvariable=self.var_c, width=8).grid(row=1, column=1, pady=5)

        # 产出价格
        ttk.Label(frame_input, text="产出价格(P)：").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.var_p = tk.DoubleVar(value=2.0)
        ttk.Entry(frame_input, textvariable=self.var_p, width=8).grid(row=2, column=1, pady=5)

        # w范围输入
        ttk.Label(frame_input, text="w范围 [min,max,step]：").grid(row=3, column=0, sticky=tk.E, pady=5)
        self.var_wmin = tk.DoubleVar(value=0.0)
        self.var_wmax = tk.DoubleVar(value=20.0)
        self.var_wstep = tk.DoubleVar(value=2.0)
        frame_w = ttk.Frame(frame_input)
        ttk.Entry(frame_w, textvariable=self.var_wmin, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_w, textvariable=self.var_wmax, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_w, textvariable=self.var_wstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_w.grid(row=3, column=1, sticky=tk.W, pady=5)

        # b范围输入
        ttk.Label(frame_input, text="b范围 [min,max,step]：").grid(row=4, column=0, sticky=tk.E, pady=5)
        self.var_bmin = tk.DoubleVar(value=0.0)
        self.var_bmax = tk.DoubleVar(value=5.0)
        self.var_bstep = tk.DoubleVar(value=1.0)
        frame_b = ttk.Frame(frame_input)
        ttk.Entry(frame_b, textvariable=self.var_bmin, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_b, textvariable=self.var_bmax, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_b, textvariable=self.var_bstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_b.grid(row=4, column=1, sticky=tk.W, pady=5)

        # 可视化类型
        ttk.Label(frame_input, text="可视化类型：").grid(row=5, column=0, sticky=tk.E, pady=5)
        self.var_chart = tk.StringVar(value="利润-3D")
        cb_chart = ttk.Combobox(frame_input, textvariable=self.var_chart, state="readonly",
                                values=["利润-3D", "利润-热力图", "效用-3D", "效用-热力图"], width=12)
        cb_chart.grid(row=5, column=1, pady=5)

        # 扫描按钮
        btn_scan = ttk.Button(frame_input, text="扫描 & 可视化", command=not_implemented)
        btn_scan.grid(row=6, column=0, columnspan=2, pady=10)

        # 右侧图表展示区域
        frame_plot = ttk.Frame(tab, padding=10, relief="solid")
        frame_plot.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_plot, text="【委托代理模块】图表区域", font=("Arial", 14)).pack(expand=True)

    def create_lemons_market_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="柠檬市场")

        frame_input = ttk.Frame(tab, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(frame_input, text="车辆数量：").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.var_ncars = tk.IntVar(value=50)
        ttk.Entry(frame_input, textvariable=self.var_ncars, width=8).grid(row=0, column=1, pady=5)

        ttk.Label(frame_input, text="初始HQ概率：").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.var_phq = tk.DoubleVar(value=0.3)
        ttk.Entry(frame_input, textvariable=self.var_phq, width=8).grid(row=1, column=1, pady=5)

        ttk.Label(frame_input, text="启用检测：").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.var_check = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_input, variable=self.var_check).grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame_input, text="检测准确度：").grid(row=3, column=0, sticky=tk.E, pady=5)
        self.var_acc = tk.DoubleVar(value=0.7)
        ttk.Entry(frame_input, textvariable=self.var_acc, width=8).grid(row=3, column=1, pady=5)

        ttk.Label(frame_input, text="买方学习率：").grid(row=4, column=0, sticky=tk.E, pady=5)
        self.var_lr = tk.DoubleVar(value=0.2)
        ttk.Entry(frame_input, textvariable=self.var_lr, width=8).grid(row=4, column=1, pady=5)

        ttk.Label(frame_input, text="模拟轮次：").grid(row=5, column=0, sticky=tk.E, pady=5)
        self.var_rounds = tk.IntVar(value=5)
        ttk.Entry(frame_input, textvariable=self.var_rounds, width=8).grid(row=5, column=1, pady=5)

        btn_sim = ttk.Button(frame_input, text="多轮模拟 & 绘图", command=not_implemented)
        btn_sim.grid(row=6, column=0, columnspan=2, pady=10)

        # 输出区域（可用于显示文字或图表）
        frame_output = ttk.Frame(tab, padding=10, relief="solid")
        frame_output.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_output, text="【柠檬市场模块】图表/结果区域", font=("Arial", 14)).pack(expand=True)

    def create_insurance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="保险")

        frame_input = ttk.Frame(tab, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(frame_input, text="失窃基准(p0)：").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.var_p0 = tk.DoubleVar(value=0.3)
        ttk.Entry(frame_input, textvariable=self.var_p0, width=8).grid(row=0, column=1, pady=5)

        ttk.Label(frame_input, text="alpha：").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.var_alpha = tk.DoubleVar(value=0.05)
        ttk.Entry(frame_input, textvariable=self.var_alpha, width=8).grid(row=1, column=1, pady=5)

        ttk.Label(frame_input, text="保费：").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.var_prem = tk.DoubleVar(value=10.0)
        ttk.Entry(frame_input, textvariable=self.var_prem, width=8).grid(row=2, column=1, pady=5)

        ttk.Label(frame_input, text="coverage：").grid(row=3, column=0, sticky=tk.E, pady=5)
        self.var_cov = tk.DoubleVar(value=100.0)
        ttk.Entry(frame_input, textvariable=self.var_cov, width=8).grid(row=3, column=1, pady=5)

        ttk.Label(frame_input, text="免赔额：").grid(row=4, column=0, sticky=tk.E, pady=5)
        self.var_deduct = tk.DoubleVar(value=0.0)
        ttk.Entry(frame_input, textvariable=self.var_deduct, width=8).grid(row=4, column=1, pady=5)

        ttk.Label(frame_input, text="风险模型：").grid(row=5, column=0, sticky=tk.E, pady=5)
        self.var_risk_model = tk.StringVar(value="linear")
        cb_risk_model = ttk.Combobox(frame_input, textvariable=self.var_risk_model, state="readonly",
                                     values=["linear", "power"], width=8)
        cb_risk_model.grid(row=5, column=1, pady=5)

        ttk.Label(frame_input, text="努力扫描范围 [min,max,step]：").grid(row=6, column=0, sticky=tk.E, pady=5)
        self.var_emin = tk.DoubleVar(value=0.0)
        self.var_emax = tk.DoubleVar(value=1.0)
        self.var_estep = tk.DoubleVar(value=0.1)
        frame_escan = ttk.Frame(frame_input)
        ttk.Entry(frame_escan, textvariable=self.var_emin, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_escan, textvariable=self.var_emax, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_escan, textvariable=self.var_estep, width=5).pack(side=tk.LEFT, padx=2)
        frame_escan.grid(row=6, column=1, sticky=tk.W, pady=5)

        btn_scan = ttk.Button(frame_input, text="扫描 & 绘图", command=not_implemented)
        btn_scan.grid(row=7, column=0, columnspan=2, pady=10)

        # 图表展示区域
        frame_plot = ttk.Frame(tab, padding=10, relief="solid")
        frame_plot.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_plot, text="【保险模块】图表区域", font=("Arial", 14)).pack(expand=True)

    def create_education_signal_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="教育信号")

        frame_input = ttk.Frame(tab, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(frame_input, text="学生数量：").grid(row=0, column=0, sticky=tk.E, pady=5)
        self.var_stu_num = tk.IntVar(value=3)
        ttk.Entry(frame_input, textvariable=self.var_stu_num, width=5).grid(row=0, column=1, pady=5)

        ttk.Label(frame_input, text="阈值扫描范围 [start,end,step]：").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.var_smin = tk.DoubleVar(value=0.0)
        self.var_smax = tk.DoubleVar(value=5.0)
        self.var_sstep = tk.DoubleVar(value=1.0)
        frame_thresh = ttk.Frame(frame_input)
        ttk.Entry(frame_thresh, textvariable=self.var_smin, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_thresh, textvariable=self.var_smax, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(frame_thresh, textvariable=self.var_sstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_thresh.grid(row=1, column=1, sticky=tk.W, pady=5)

        btn_create = ttk.Button(frame_input, text="创建学生输入框", command=not_implemented)
        btn_create.grid(row=2, column=0, columnspan=2, pady=5)

        btn_scan = ttk.Button(frame_input, text="阈值扫描 & 可视化", command=not_implemented)
        btn_scan.grid(row=3, column=0, columnspan=2, pady=10)

        # 学生输入及图表显示区域
        frame_student = ttk.Frame(tab, padding=10, relief="solid")
        frame_student.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_student, text="【教育信号模块】学生输入及图表区域", font=("Arial", 14)).pack(expand=True)


def main():
    app = SimAppUI()
    app.mainloop()


if __name__ == "__main__":
    main()