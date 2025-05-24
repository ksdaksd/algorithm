import tkinter as tk
from tkinter import ttk, messagebox


def not_implemented():
    messagebox.showinfo("提示", "该功能尚未实现。")

"""
车辆保险模块

失窃基准 p0（var_p0）：输入框，设定初始的失窃（或事故）基准概率。
alpha（var_alpha）：输入框，用于风险模型中修正失窃概率的参数。
保费（var_prem）：输入框，设置保险合同中投保人需支付的保费金额。
coverage（var_cov）：输入框，表示保险合同的最高赔偿金额。
免赔额（var_deduct）：输入框，用于设定赔付前投保人自负的部分。
风险模型（var_risk_model）：下拉框，允许用户选择风险计算模型（例如“linear”或“power”）。
努力扫描范围（var_emin、var_emax、var_estep）：三个输入框，分别用于定义扫描过程中努力（e）的最小值、最大值和步长。
"""
class Insurance(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        frame_input = ttk.Frame(self, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(frame_input, text="参数1：").grid(row=1, column=0, sticky=tk.E, pady=5)
        self.var_para1 = tk.DoubleVar(value=0)
        ttk.Entry(frame_input, textvariable=self.var_para1, width=12).grid(row=1, column=1, pady=5)

        ttk.Label(frame_input, text="参数2：").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.var_para2 = tk.DoubleVar(value=0)
        ttk.Entry(frame_input, textvariable=self.var_para2, width=12).grid(row=2, column=1, pady=5)

        ttk.Label(frame_input, text="参数3：").grid(row=3, column=0, sticky=tk.E, pady=5)
        self.var_para3 = tk.DoubleVar(value=0)
        ttk.Entry(frame_input, textvariable=self.var_para3, width=12).grid(row=3, column=1, pady=5)

        ttk.Label(frame_input, text="参数4：").grid(row=4, column=0, sticky=tk.E, pady=5)
        self.var_para4 = tk.DoubleVar(value=0)
        ttk.Entry(frame_input, textvariable=self.var_para4, width=12).grid(row=4, column=1, pady=5)

        btn_simulate = ttk.Button(frame_input, text="模拟决策", command=not_implemented)
        btn_simulate.grid(row=5, column=0, columnspan=2, pady=10)

        # ttk.Label(frame_input, text="失窃基准(p0)：").grid(row=0, column=0, sticky=tk.E, pady=5)
        # self.var_p0 = tk.DoubleVar(value=0.3)
        # ttk.Entry(frame_input, textvariable=self.var_p0, width=8).grid(row=0, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="alpha：").grid(row=1, column=0, sticky=tk.E, pady=5)
        # self.var_alpha = tk.DoubleVar(value=0.05)
        # ttk.Entry(frame_input, textvariable=self.var_alpha, width=8).grid(row=1, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="保费：").grid(row=2, column=0, sticky=tk.E, pady=5)
        # self.var_prem = tk.DoubleVar(value=10.0)
        # ttk.Entry(frame_input, textvariable=self.var_prem, width=8).grid(row=2, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="coverage：").grid(row=3, column=0, sticky=tk.E, pady=5)
        # self.var_cov = tk.DoubleVar(value=100.0)
        # ttk.Entry(frame_input, textvariable=self.var_cov, width=8).grid(row=3, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="免赔额：").grid(row=4, column=0, sticky=tk.E, pady=5)
        # self.var_deduct = tk.DoubleVar(value=0.0)
        # ttk.Entry(frame_input, textvariable=self.var_deduct, width=8).grid(row=4, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="风险模型：").grid(row=5, column=0, sticky=tk.E, pady=5)
        # self.var_risk_model = tk.StringVar(value="linear")
        # cb_risk_model = ttk.Combobox(frame_input, textvariable=self.var_risk_model, state="readonly",
        #                              values=["linear", "power"], width=8)
        # cb_risk_model.grid(row=5, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="努力扫描范围 [min,max,step]：").grid(row=6, column=0, sticky=tk.E, pady=5)
        # self.var_emin = tk.DoubleVar(value=0.0)
        # self.var_emax = tk.DoubleVar(value=1.0)
        # self.var_estep = tk.DoubleVar(value=0.1)
        # frame_escan = ttk.Frame(frame_input)
        # ttk.Entry(frame_escan, textvariable=self.var_emin, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_escan, textvariable=self.var_emax, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_escan, textvariable=self.var_estep, width=5).pack(side=tk.LEFT, padx=2)
        # frame_escan.grid(row=6, column=1, sticky=tk.W, pady=5)
        #
        # btn_scan = ttk.Button(frame_input, text="扫描 & 绘图", command=not_implemented)
        # btn_scan.grid(row=7, column=0, columnspan=2, pady=10)

        # 图表展示区域
        frame_plot = ttk.Frame(self, padding=10, relief="solid")
        frame_plot.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_plot, text="【车辆保险模块】图表区域", font=("Arial", 14)).pack(expand=True)
