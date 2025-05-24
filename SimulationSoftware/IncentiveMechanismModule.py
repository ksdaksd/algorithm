import tkinter as tk
from tkinter import ttk, messagebox


def not_implemented():
    messagebox.showinfo("提示", "该功能尚未实现。")


"""
激励机制模块


"""

class IncentiveMechanism(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        # 左侧输入区
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

        # ttk.Label(frame_input, text="外部效用(U0)：").grid(row=0, column=0, sticky=tk.E, pady=5)
        # self.var_u0 = tk.DoubleVar(value=0.0)
        # ttk.Entry(frame_input, textvariable=self.var_u0, width=8).grid(row=0, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="成本系数(c)：").grid(row=1, column=0, sticky=tk.E, pady=5)
        # self.var_c = tk.DoubleVar(value=0.1)
        # ttk.Entry(frame_input, textvariable=self.var_c, width=8).grid(row=1, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="产出价格(P)：").grid(row=2, column=0, sticky=tk.E, pady=5)
        # self.var_p = tk.DoubleVar(value=2.0)
        # ttk.Entry(frame_input, textvariable=self.var_p, width=8).grid(row=2, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="w范围 [min,max,step]：").grid(row=3, column=0, sticky=tk.E, pady=5)
        # self.var_wmin = tk.DoubleVar(value=0.0)
        # self.var_wmax = tk.DoubleVar(value=20.0)
        # self.var_wstep = tk.DoubleVar(value=2.0)
        # frame_w = ttk.Frame(frame_input)
        # ttk.Entry(frame_w, textvariable=self.var_wmin, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_w, textvariable=self.var_wmax, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_w, textvariable=self.var_wstep, width=5).pack(side=tk.LEFT, padx=2)
        # frame_w.grid(row=3, column=1, sticky=tk.W, pady=5)
        #
        # ttk.Label(frame_input, text="b范围 [min,max,step]：").grid(row=4, column=0, sticky=tk.E, pady=5)
        # self.var_bmin = tk.DoubleVar(value=0.0)
        # self.var_bmax = tk.DoubleVar(value=5.0)
        # self.var_bstep = tk.DoubleVar(value=1.0)
        # frame_b = ttk.Frame(frame_input)
        # ttk.Entry(frame_b, textvariable=self.var_bmin, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_b, textvariable=self.var_bmax, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_b, textvariable=self.var_bstep, width=5).pack(side=tk.LEFT, padx=2)
        # frame_b.grid(row=4, column=1, sticky=tk.W, pady=5)

        # ttk.Label(frame_input, text="可视化类型：").grid(row=5, column=0, sticky=tk.E, pady=5)
        # self.var_chart = tk.StringVar(value="利润-3D")
        # cb_chart = ttk.Combobox(frame_input, textvariable=self.var_chart, state="readonly",
        #                         values=["利润-3D", "利润-热力图", "效用-3D", "效用-热力图"], width=12)
        # cb_chart.grid(row=5, column=1, pady=5)

        # btn_scan = ttk.Button(frame_input, text="扫描 & 可视化", command=not_implemented)
        # btn_scan.grid(row=6, column=0, columnspan=2, pady=10)

        # 右侧图表展示区
        frame_plot = ttk.Frame(self, padding=10, relief="solid")
        frame_plot.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_plot, text="【激励机制模块】图表区域", font=("Arial", 14)).pack(expand=True)
