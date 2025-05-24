import tkinter as tk
from tkinter import ttk, messagebox
import math
import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from sympy import *

plt.rcParams["font.family"] = "FangSong"  # 仿宋
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号


def not_implemented(text="该功能尚未实现。"):
    messagebox.showinfo("提示", text)


# -------------------------------
# 风险偏好模块
# -------------------------------
class RiskPreference(ttk.Frame):
    def __init__(self, parent):
        """
        :param attitude: 字符串，'risk_averse'（风险厌恶）、'risk_neutral'（风险中性）或 'risk_preferring'（风险偏好）
        :param risk_aversion: 风险厌恶系数 (对风险厌恶时起作用); 数值越大，越厌恶风险
        """

        super().__init__(parent, padding=10)
        frame_input = ttk.Frame(self, padding=10)
        frame_input.pack(side=tk.LEFT, fill=tk.Y)
        # 参数输入区
        row = 0
        column = 0
        ttk.Label(frame_input, text="请选择个人风险偏好：").grid(row=row, column=0, sticky=tk.E, pady=5)
        self.var_risk_choice = tk.StringVar(value="风险中性")
        cb_risk = ttk.Combobox(frame_input, textvariable=self.var_risk_choice, state="readonly",
                               values=["风险厌恶", "风险中性", "风险偏好"], width=12)
        cb_risk.grid(row=0, column=1, pady=5)

        # ttk.Label(frame_input, text="风险厌恶系数：").grid(row=1, column=0, sticky=tk.E, pady=5)
        # self.var_risk_aversion = tk.DoubleVar(value=1.0)
        # ttk.Entry(frame_input, textvariable=self.var_risk_aversion, width=12).grid(row=1, column=1, pady=5)

        ttk.Label(frame_input, text="报酬：").grid(row=2, column=0, sticky=tk.E, pady=5)
        self.var_outcome1 = tk.DoubleVar(value=10)
        ttk.Entry(frame_input, textvariable=self.var_outcome1, width=12).grid(row=2, column=1, pady=5)

        ttk.Label(frame_input, text="报酬：").grid(row=3, column=0, sticky=tk.E, pady=5)
        self.var_outcome2 = tk.DoubleVar(value=20)
        ttk.Entry(frame_input, textvariable=self.var_outcome2, width=12).grid(row=3, column=1, pady=5)

        ttk.Label(frame_input, text="概率：").grid(row=4, column=0, sticky=tk.E, pady=5)
        self.var_prob1 = tk.DoubleVar(value=0.5)
        ttk.Entry(frame_input, textvariable=self.var_prob1, width=12).grid(row=4, column=1, pady=5)

        ttk.Label(frame_input, text="概率：").grid(row=5, column=0, sticky=tk.E, pady=5)
        self.var_prob2 = tk.DoubleVar(value=0.5)
        ttk.Entry(frame_input, textvariable=self.var_prob2, width=12).grid(row=5, column=1, pady=5)

        self.outcomes = [self.var_outcome1.get(), self.var_outcome2.get()]
        self.probs = [self.var_prob1.get(), self.var_prob2.get()]

        btn_simulate = ttk.Button(frame_input, text="计算期望效用", command=self.test)
        btn_simulate.grid(row=6, column=0, columnspan=2, pady=10)

        btn_plot = ttk.Button(frame_input, text="绘制三种风险态度曲线", command=self.plot_utility_curves)
        btn_plot.grid(row=7, column=0, columnspan=2, pady=10)

        # ========== 右侧图表 / 结果 显示区 ==========
        self.frame_output = ttk.Frame(self, padding=10, relief="solid")
        self.frame_output.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # 放一行标题文字
        lab_title = ttk.Label(self.frame_output, font=("Arial", 14))
        lab_title.pack(anchor=tk.N, pady=5)

        # 初始化属性
        self.attitude = "risk_neutral"  # 默认

    def on_calculate_eu(self):
        """
        当点击“计算期望效用”按钮时的处理：
        读取界面的报酬 & 概率，计算期望效用并在控制台打印结果。
        后续可以把结果放在一个Label或Text里显示。
        """
        # 1) 将文本框的值读进来
        outcome1 = self.var_outcome1.get()
        outcome2 = self.var_outcome2.get()
        prob1 = self.var_prob1.get()
        prob2 = self.var_prob2.get()

        # 要求概率和相等
        if prob1 < 0 or prob2 < 0:
            not_implemented("存在一个概率小于0")
            return
        flag = prob1 + prob2
        if flag != 1:
            not_implemented("输入的概率和不等于1")
            return

        # 2) 根据用户下拉选择的文本, 决定 attitude
        if self.var_risk_choice.get() == "风险厌恶":
            self.attitude = "risk_averse"
        elif self.var_risk_choice.get() == "风险中性":
            self.attitude = "risk_neutral"
        else:
            self.attitude = "risk_preferring"

        # 3) 计算期望效用
        # 从小到大排序
        if outcome1 > outcome2:
            tmp = outcome1
            outcome1 = outcome2
            outcome2 = tmp
        self.outcomes = [outcome1, outcome2]
        self.probs = [prob1, prob2]
        eu = self.expected_utility(self.outcomes, self.probs)

        # 在控制台打印结果（或改为 Tkinter Label 显示） -目前是控制台显示
        print("\n--- 期望效用计算 ---")
        print(f"态度: {self.attitude}")
        print(f"outcomes={self.outcomes}, probs={self.probs}, EU={eu:.4f}")
        messagebox.showinfo("计算结果", f"期望效用 = {eu:.4f}")

    def utility(self, x,nature = 0):
        """
        单次收益 x 对应的效用值。
        nature为自然状态，等于1时计算的是自然的期望效用
        """
        if x < 0:
            # 确保对数/指数时不出错，简单地把负收益时做边界处理
            x_clamped = max(x, -0.9999)
        else:
            x_clamped = x

        y1 = self.outcomes[0]
        y2 = self.outcomes[1]
        x1, x2 = y1, y2

        # 归一化
        x_clamped = (x_clamped - x1) / (x2 - x1)

        if nature==1:
            # 画图时要用来化自然下的效用
            fx = x_clamped
        elif self.attitude == "risk_averse":
            # 指数小于1次方的幂函数或者对数函数
            fx = math.pow(x_clamped, 1 / 2)

        elif self.attitude == "risk_neutral":
            # 线性函数
            k = (y1 - y2) / (x1 - x2)
            fx = x_clamped

        elif self.attitude == "risk_preferring":
            # 一个简单的凸函数，指数大于1次方的幂函数或者指数函数
            fx = math.pow(x_clamped, 2)
        else:
            # 默认视为风险中性
            fx = x_clamped

        # 进行仿射变换
        ux = y1 + (y2 - y1) * fx
        return ux

    def expected_utility(self, outcomes, probs):
        """
        计算给定若干离散结果的期望效用:
        :param outcomes: list，每个元素是一次可能的收益数值
        :param probs: list，对应outcomes的概率
        :return: 期望效用值
        """
        eu = 0.0
        for x, p in zip(outcomes, probs):
            eu += self.utility(x) * p
        return eu

    def simulate_one_scenario(self, invest_amount, success_prob, success_gain, failure_loss):
        """
        简易模拟：假设某投资决策，两种结果：成功 or 失败
        成功得到 success_gain； 失败损失 failure_loss；成功概率 success_prob
        计算期望效用并返回是否值得投资(若期望效用>不投资的效用则投资)。
        :param invest_amount: 投资金额(仅做展示，可决定其在收益计算中影响)
        :param success_prob: 成功概率(0~1)
        :param success_gain: 成功时收益(可自定义)
        :param failure_loss: 失败时损失(可自定义)
        :return: (EU_invest, EU_not_invest, decision)
        """
        # 收益情景
        outcomes = [success_gain, -failure_loss]  # 成功、失败分别的收益
        probs = [success_prob, 1.0 - success_prob]

        eu_invest = self.expected_utility(outcomes, probs)
        eu_not_invest = self.utility(0.0)  # 不投资视为收益=0
        decision = "投资" if eu_invest > eu_not_invest else "不投"
        return eu_invest, eu_not_invest, decision

    def plot_utility_curves(self):
        """
        在 frame_output 上绘制：三种风险态度(厌恶/中性/偏好) 的效用函数曲线对比。
        横坐标：x = outcomes[0]~outcomes[1] （可扩大）
        纵坐标：U(x)
        使用嵌入Tkinter的方式，不弹出新窗口。
        """
        # ---- 先清空 frame_output 里旧的图表控件 (若之前已经画过) ----
        for widget in self.frame_output.winfo_children():
            # 除了最上方的标题 Label 不删除
            if widget is not self.frame_output.children.get('!label'):
                widget.destroy()

        # ---- 准备绘图 ----
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        # 准备 x 范围
        range = self.outcomes[-1] - self.outcomes[0]

        x_values = np.linspace(self.outcomes[0], self.outcomes[-1], int((range // 2) * 100))  # 这里强转了，后续如果输错的话就不会报错提示

        # 三种态度
        attitudes = ["risk_averse", "risk_neutral", "risk_preferring"]
        labels = ["风险厌恶", "风险中性", "风险偏好"]
        colors = ["red", "green", "blue"]
        indexs = [i for i, value in enumerate(attitudes) if value == self.attitude]
        label = labels[indexs[0]]
        color = colors[indexs[0]]

        # 求期望效用，画图
        y = [self.utility(x) for x in x_values]
        y_nature = [self.utility(x,nature=1) for x in x_values]
        # print(y2)
        ax.plot(x_values, y, label=label, color=color)
        ax.plot(x_values, y_nature,label="自然",color="yellow")

        ax.set_title("三种风险态度的效用函数曲线")
        ax.set_xlabel("财富 / 收益 (x)")
        ax.set_ylabel("效用 U(x)")
        ax.grid(True)
        ax.legend()

        # ---- 将图表嵌入 frame_output ----
        canvas = FigureCanvasTkAgg(fig, master=self.frame_output)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def test(self):
        # 测试方法
        self.on_calculate_eu()
        # print(self.outcomes[1]-self.outcomes[0])
        # print(self.outcomes[1],self.outcomes[0])
