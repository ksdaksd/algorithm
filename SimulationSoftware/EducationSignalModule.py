import tkinter as tk
from tkinter import ttk, messagebox


def not_implemented():
    messagebox.showinfo("提示", "该功能尚未实现。")

"""
教育信号模块

学生数量（var_stu_num）：输入框，指定参与模拟的学生数。
阈值扫描范围（var_smin、var_smax、var_sstep）：三个输入框，用于定义不同阈值（signal threshold）的扫描区间，进而观察不同阈值下学生和企业的效用或收益。
创建学生输入框按钮：虽然按钮本身调用了未实现的功能，但其目的是在界面上生成针对每个学生的详细参数输入区（例如：ability、cost、wage、invest），以便进行多学生对比模拟。
"""
class EducationSignal(ttk.Frame):
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

        # ttk.Label(frame_input, text="学生数量：").grid(row=0, column=0, sticky=tk.E, pady=5)
        # self.var_stu_num = tk.IntVar(value=3)
        # ttk.Entry(frame_input, textvariable=self.var_stu_num, width=5).grid(row=0, column=1, pady=5)
        #
        # ttk.Label(frame_input, text="阈值扫描范围 [start,end,step]：").grid(row=1, column=0, sticky=tk.E, pady=5)
        # self.var_smin = tk.DoubleVar(value=0.0)
        # self.var_smax = tk.DoubleVar(value=5.0)
        # self.var_sstep = tk.DoubleVar(value=1.0)
        # frame_thresh = ttk.Frame(frame_input)
        # ttk.Entry(frame_thresh, textvariable=self.var_smin, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_thresh, textvariable=self.var_smax, width=5).pack(side=tk.LEFT, padx=2)
        # ttk.Entry(frame_thresh, textvariable=self.var_sstep, width=5).pack(side=tk.LEFT, padx=2)
        # frame_thresh.grid(row=1, column=1, sticky=tk.W, pady=5)
        #
        # btn_create = ttk.Button(frame_input, text="创建学生输入框", command=not_implemented)
        # btn_create.grid(row=2, column=0, columnspan=2, pady=5)
        #
        # btn_scan = ttk.Button(frame_input, text="阈值扫描 & 可视化", command=not_implemented)
        # btn_scan.grid(row=3, column=0, columnspan=2, pady=10)

        # 学生信息输入及图表展示区域
        frame_student = ttk.Frame(self, padding=10, relief="solid")
        frame_student.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ttk.Label(frame_student, text="【教育信号模块】学生输入及图表区域", font=("Arial", 14)).pack(expand=True)
