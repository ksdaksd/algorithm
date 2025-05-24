# from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv
import random
import datetime
import math
import os

plt.rcParams["font.family"] = "FangSong"  # 仿宋
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
# 可选引入现代主题库（如 ttkbootstrap）
from ttkbootstrap import Style


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # 应用现代主题和全局样式
        self.style = Style(theme="flatly")  # 选择 flatly 主题（可选 cosmo、morph 等）:contentReference[oaicite:7]{index=7}
        self.style.configure('.', font=("Microsoft YaHei", 11))  # 设置全局统一字体
        self.title("信息经济学仿真软件")
        self.geometry("1000x940")
        self.configure(background=self.style.colors.light)  # 窗口背景使用主题的浅色

        # 顶部标题栏
        header_frame = ttk.Frame(self, style="primary.TFrame")
        header_frame.pack(side="top", fill="x")
        ttk.Label(header_frame, text="信息经济学仿真平台", anchor="center",
                  font=("Microsoft YaHei", 16, "bold"),
                  foreground="white", background=self.style.colors.primary
                 ).pack(pady=10, fill="x")
        # ↑ 注：将顶栏背景设为主题主色(primary)，字体白色，加粗显示应用标题

        # 中央内容区容器（卡片容器布局）
        content_area = ttk.Frame(self, style="light.TFrame")
        content_area.pack(fill="both", expand=True, padx=20, pady=10)
        # ↑ content_area 使用浅色底，周围留白，作为承载各模块页面的容器

        # 底部工具栏
        footer_frame = ttk.Frame(self, style="secondary.TFrame")
        footer_frame.pack(side="bottom", fill="x")
        # 可在底部工具栏放置全局按钮（例如关于或状态信息等），此处简化省略

        # 初始化各模块页面 Frame，并使用网格堆叠它们
        self.frames = {}
        for F in (MainMenu, RiskPreferenceModule, PrincipalAgentModule,
                  AdverseSelectionModule, MoralHazardModule, SignalingModule, ReportView):
            frame = F(content_area, self)
            # 为每个模块Frame应用卡片样式：浅背景色，细边框
            frame.configure(style="TFrame")  # ttkbootstrap 默认 TFrame 背景为主题 bg 色
            frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.frames[F] = frame

        self.show_frame(MainMenu)

    def show_frame(self, page):
        """切换显示指定的模块页面"""
        self.frames[page].tkraise()

class BaseModule(ttk.Frame):
    """各功能模块页面的基类，提供统一的布局结构"""
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")  # 基础Frame使用主题样式
        # 主内容区（卡片内容），在子类中向其中添加控件
        # self.content = ttk.Frame(self, style="Card.TFrame")  # Card.TFrame 自定义样式
        # self.content.pack(fill="both", expand=True, padx=15, pady=10)
        # ↑ 给 content Frame 设置较浅背景和圆角边框，以实现卡片视觉效果
        #   可通过 Style.configure("Card.TFrame", borderwidth=1, relief="solid", bordercolor=...) 来定制边框:contentReference[oaicite:8]{index=8}

        # 底部导航工具栏（返回主菜单、查看报告等按钮）
        toolbar = ttk.Frame(self)
        toolbar.pack(side="bottom", fill="x", pady=5)
        ttk.Button(toolbar, text="返回主菜单", bootstyle="secondary-outline",
                   command=lambda: controller.show_frame(MainMenu)
                  ).pack(side="left", padx=5)
        ttk.Button(toolbar, text="查看报告", bootstyle="secondary-outline",
                   command=lambda: controller.show_frame(ReportView)
                  ).pack(side="right", padx=5)
        # ↑ 使用 bootstyle="secondary-outline" 创建浅色圆角边框按钮:contentReference[oaicite:9]{index=9}，悬停时会高亮，风格统一

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        # 主菜单界面内容布局
        ttk.Label(self, text="请选择一个模块：", font=("Microsoft YaHei", 12)).pack(pady=20)
        menu_buttons = [
            ("风险偏好", RiskPreferenceModule),
            ("委托代理与激励机制", PrincipalAgentModule),
            ("逆向选择：柠檬市场", AdverseSelectionModule),
            ("道德风险：汽车保险", MoralHazardModule),
            ("信号发送：教育信号", SignalingModule),
            ("仿真报告", ReportView)
        ]
        for txt, FrameClass in menu_buttons:
            ttk.Button(self, text=txt, bootstyle="primary", width=30,
                       command=lambda f=FrameClass: controller.show_frame(f)
                      ).pack(pady=8)
        # ↑ 主菜单按钮使用主题 primary 色填充样式，统一宽度


class RiskPreferenceModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # 风险偏好参数
        self.eu_count = 0
        self.prob_var = tk.DoubleVar(value=0.5)
        self.outcome1_var = tk.DoubleVar(value=100)
        self.outcome2_var = tk.DoubleVar(value=50)
        # 1) 风险偏好类型 & γ 参数
        pref_frame = ttk.LabelFrame(self, text="风险偏好类型")
        pref_frame.pack(fill="x", padx=15, pady=5)
        self.pref_var = tk.StringVar(value="neutral")
        self.gamma_var = tk.DoubleVar(value=1.0)
        for val, text in [("averse", "风险规避"), ("neutral", "风险中性"), ("preferring", "风险偏好")]:
            ttk.Radiobutton(pref_frame, text=text, variable=self.pref_var, value=val,
                            command=self.on_pref_change).pack(side="left", padx=5)
        param_frame = ttk.Frame(self)
        param_frame.pack(fill="x", padx=15, pady=5)
        ttk.Label(param_frame, text="效用参数 γ:").pack(side="left")
        ttk.Entry(param_frame, textvariable=self.gamma_var, width=8).pack(side="left", padx=5)

        # 2) 概率 & 支付 输入
        params = ttk.Frame(self)
        params.pack(side="left", fill="y", padx=15, pady=15)
        ttk.Label(params, text="风险偏好参数").pack(pady=5)
        ttk.Label(params, text="概率 p:").pack(anchor="w")
        ttk.Entry(params, textvariable=self.prob_var).pack(fill="x")
        ttk.Label(params, text="收益1:").pack(anchor="w")
        ttk.Entry(params, textvariable=self.outcome1_var).pack(fill="x")
        ttk.Label(params, text="收益2:").pack(anchor="w")
        ttk.Entry(params, textvariable=self.outcome2_var).pack(fill="x")

        # 3) 操作按钮
        btn_frame = ttk.Frame(params)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="计算期望效用", command=self.compute_utility).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="绘制图像", command=self.plot_utility).pack(side="left", padx=5)

        # 4) 日志 & 绘图区
        self.log = scrolledtext.ScrolledText(params, width=35, height=12)
        self.log.pack(pady=5)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    def on_pref_change(self):
        # 根据选择的类型，设置 γ 默认值（但仍可手动修改）
        defaults = {"averse": 2.0, "neutral": 1.0, "preferring": 0.5}
        self.gamma_var.set(defaults[self.pref_var.get()])

    def compute_utility(self):
        self.eu_count += 1
        self.log.insert("end", f"第{self.eu_count}次计算\n")
        p = self.prob_var.get()
        o1 = self.outcome1_var.get()
        o2 = self.outcome2_var.get()
        γ = self.gamma_var.get()
        # CRRA 效用：γ→1 时退化为 ln(x)
        e = p * o1 + (1 - p) * o2
        self.log.insert("end", f"收益1概率为：{p}\n收益1值为：{o1}\n收益2值为：{o2}\n")
        self.log.insert("end", f"期望收益 = {e:.4f}\n")
        if abs(γ - 1.0) < 1e-6:
            u = lambda x: np.log(x)
        else:
            u = lambda x: (x ** (1 - γ) - 1) / (1 - γ)
        eu = p * u(o1) + (1 - p) * u(o2)
        self.log.insert("end", f"期望效用 = {eu:.4f}  (γ={γ})\n\n")
        self.log.see("end")

    def plot_utility(self):
        p = self.prob_var.get()
        o1 = self.outcome1_var.get()
        o2 = self.outcome2_var.get()
        γ = self.gamma_var.get()
        max_o = max(o1, o2)
        xs = np.linspace(1e-6, max_o * 1.2, 200)
        if abs(γ - 1.0) < 1e-6:
            u = lambda x: np.log(x)
        else:
            u = lambda x: (x ** (1 - γ)) / (1 - γ)
        ys = p * u(xs) + (1 - p) * u(xs[::-1])
        self.ax.clear()
        self.ax.plot(xs, ys)
        self.ax.set_title(f"期望效用曲线 (γ={γ})")
        self.ax.set_xlabel("支付金额")
        self.ax.set_ylabel("期望效用")
        self.canvas.draw()


class PrincipalAI:
    def __init__(self):
        self.reject_rev = 0
        self.w = 0

    def set(self, res_high, res_low, p_high, p_low, U_res=0):
        self.res_high, self.res_low = res_high, res_low
        self.p_high, self.p_low = p_high, p_low
        self.U_res = U_res

    def propose_contract(self, c_high, c_low):
        # 最优合同时满足参与约束和激励相容
        self.cost_high_var = c_high
        self.cost_low_var = c_low
        if self.w == 0:
            self.w_high = self.U_res + c_high
        else:
            self.w_high = self.w
        self.w = random.randint(round(self.w_high), self.res_high)
        self.w_low = self.w_high - (c_high - c_low)
        return round(self.w_high, 2), round(self.w_low, 2)

    def agent_income(self, effort):
        if effort == '努力':
            return self.p_high * (self.w_high - self.cost_high_var) + (1 - self.p_high) * (
                        self.w_low - self.cost_high_var)
        else:
            return self.p_low * (self.w_high - self.cost_low_var) + (1 - self.p_low) * (self.w_low - self.cost_low_var)


class AgentAI:
    def __init__(self):
        self.cost_high_var = 0
        self.cost_low_var = 0
        self.U_res = 0

    def cost_set(self,res_high,res_low):
        self.cost_high_var = random.randint(round(res_low), round(res_high))
        self.cost_low_var = random.randint(0, round(res_low))

    def set(self, res_high, res_low, p_high, p_low, U_res=0):
        self.p_high, self.p_low = p_high, p_low
        self.res_high, self.res_low = res_high, res_low
        self.U_res = U_res


    def evaluate_contract(self, w_high, w_low):
        self.w_high = self.p_high * (w_high - self.cost_high_var) + (1 - self.p_high) * (w_low - self.cost_high_var)
        self.w_low = self.p_low * (w_high - self.cost_low_var) + (1 - self.p_low) * (w_low - self.cost_low_var)
        accept = self.w_high >= self.U_res and self.w_high >= self.w_low
        return accept

    def choose_effort(self):
        return '努力' if self.w_high >= self.w_low else '偷懒'

    def principal_income(self, effort):
        if effort == '努力':
            return self.p_high * (self.res_high - self.w_high) + (1 - self.p_high) * (self.res_low - self.w_low)
        else:
            return self.p_low + (self.res_high - self.w_high) + (1 - self.p_low) * (self.res_low - self.w_low)


class PrincipalAgentModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.user_role = None
        self.principalAI = PrincipalAI()
        self.agentAI = AgentAI()
        self.vars = {}
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
        # self.title_label = ttk.Label(self.main_frame,text='', font=(None, 16)).pack(pady=10)
        self.main_frame.pack(padx=10, pady=10, fill="x")
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(padx=10, pady=10, fill="x")

        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(padx=10, pady=10, fill="x")

        log_frame = ttk.Frame(self.main_frame)
        log_frame.pack(side='bottom', fill='x')
        self.log = scrolledtext.ScrolledText(log_frame, width=80, height=12)
        self.log.pack(fill='x', padx=5, pady=5)
        self.render_role_selection()

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def clear_button(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()

    def render_role_selection(self):
        self.clear_content()
        self.clear_button()
        ttk.Label(self.content_frame, text="请设置自然变量：", font=(None, 12, 'bold')).pack(pady=10)
        self.rev_high_var = tk.DoubleVar(value=100)
        self.rev_low_var = tk.DoubleVar(value=20)
        self.p_high_var = tk.DoubleVar(value=0.8)
        self.p_low_var = tk.DoubleVar(value=0.4)
        for text, var in [('高产出收益', self.rev_high_var),
                          ('低产出收益', self.rev_low_var),
                          ('努力时高产出概率', self.p_high_var),
                          ('偷懒时高产出概率', self.p_low_var)]:
            row = ttk.Frame(self.content_frame)
            row.pack(pady=5)
            ttk.Label(row, text=text + '：').pack(side='left', padx=2)
            ttk.Entry(row, textvariable=var, width=8).pack(side='left')
        self.agentAI.cost_set(self.rev_high_var.get(),self.rev_low_var.get())
        ttk.Label(self.content_frame, text="\n请选择您的角色：", font=(None, 12, 'bold')).pack(pady=10)
        self.role_var = tk.StringVar(value='principal')
        ttk.Radiobutton(self.content_frame, text="委托人", variable=self.role_var, value='principal').pack()
        ttk.Radiobutton(self.content_frame, text="代理人", variable=self.role_var, value='agent').pack()
        ttk.Button(self.btn_frame, text="确认", command=self.on_role_confirm).pack(pady=10)

    def on_role_confirm(self):
        self.user_role = self.role_var.get()
        # 默认模型参数
        self.vars = {'高产出收益': self.rev_high_var.get(),
                     '低产出收益': self.rev_low_var.get(),
                     '努力时高产出概率': self.p_high_var.get(),
                     '偷懒时高产出概率': self.p_low_var.get()}
        self.log.insert('end', f"您选择了角色：{self.user_role}\n")
        self.log.see('end')
        self.after(500, self.render_contract_design)

    def render_contract_design(self):
        self.clear_button()
        self.clear_content()
        if self.user_role == 'principal':
            ttk.Label(self.content_frame, text="委托人界面\n", font=(None, 16, 'bold')).grid(row=0, column=2, sticky="n",
                                                                                        pady=10)
            # self.title_label.config(text = "委托人界面")
            params = ["高产出收益", "低产出收益", "努力时高产出概率", "偷懒时高产出概率"]
            ttk.Label(self.content_frame, text="--- 自然信息 ---", font=(None, 10, 'bold')).grid(row=1, column=0, padx=10)
            for i, name in enumerate(params):
                ttk.Label(self.content_frame, text=f"{name}: ").grid(row=i + 2, column=0, sticky="e", pady=5)
                var = self.vars[name]
                ttk.Label(self.content_frame, text=f"{var}").grid(row=i + 2, column=1, sticky="w", pady=5)

            ttk.Label(self.content_frame, text="--- 合同条款 ---", font=(None, 10, 'bold')).grid(row=1, column=2, padx=20)
            self.w_high_var = tk.DoubleVar(value=60)
            self.w_low_var = tk.DoubleVar(value=10)

            ttk.Label(self.content_frame, text="高产出工资: ").grid(row=2, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.w_high_var).grid(row=2, column=3, sticky="w")
            ttk.Label(self.content_frame, text="低产出工资: ").grid(row=3, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.w_low_var).grid(row=3, column=3, sticky="w")

            self.set_AI_var(self.rev_high_var.get(), self.rev_low_var.get(), self.p_high_var.get(),
                            self.p_low_var.get())
            self.agent_information()

            ttk.Button(self.btn_frame, text="提交合同", command=self.on_submit_contract).pack(padx=10)
        else:
            ttk.Label(self.content_frame, text="代理人界面\n", font=(None, 16, 'bold')).grid(row=0, column=2, sticky="n",
                                                                                        pady=10)
            params = ["高产出收益", "低产出收益", "努力时高产出概率", "偷懒时高产出概率"]
            ttk.Label(self.content_frame, text="--- 自然信息 ---", font=(None, 10, 'bold')).grid(row=1, column=0, padx=10)
            for i, name in enumerate(params):
                ttk.Label(self.content_frame, text=f"{name}: ").grid(row=i + 2, column=0, sticky="e", pady=5)
                var = self.vars[name]
                ttk.Label(self.content_frame, text=f"{var}").grid(row=i + 2, column=1, sticky="w", pady=5)

            ttk.Label(self.content_frame, text="--- 代理人信息 ---", font=(None, 10, 'bold')).grid(row=1, column=2, padx=10)
            self.cost_high_var = tk.DoubleVar(value=10)
            self.cost_low_var = tk.DoubleVar(value=5)
            self.reserve_var = tk.DoubleVar(value=0)

            ttk.Label(self.content_frame, text="努力成本: ").grid(row=2, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.cost_high_var).grid(row=2, column=3, sticky="w")
            ttk.Label(self.content_frame, text="偷懒成本: ").grid(row=3, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.cost_low_var).grid(row=3, column=3, sticky="w")
            ttk.Label(self.content_frame, text="保留效用: ").grid(row=4, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.reserve_var).grid(row=4, column=3, sticky="w")

            self.set_AI_var(self.rev_high_var.get(), self.rev_low_var.get(), self.p_high_var.get(),
                            self.p_low_var.get())

            ttk.Button(self.btn_frame, text="提交信息", command=self.system_propose_contract).pack(padx=10)

    # 将自然信息的值传给自定义的系统AI
    def set_AI_var(self, rev_high_var, rev_low_var, p_high_var, p_low_var):
        self.agentAI.set(rev_high_var, rev_low_var, p_high_var, p_low_var)
        self.principalAI.set(rev_high_var, rev_low_var, p_high_var, p_low_var)

    # 委托人提交合同
    def on_submit_contract(self):
        w1, w2 = self.w_high_var.get(), self.w_low_var.get()
        # print(w1,w2)
        # print(type(w1),type(w2))
        # 保存合同以供后续决策
        self.w1_sys, self.w2_sys = w1, w2
        self.log.insert('end', f"您提交合同: w_high={w1}, w_low={w2}\n系统(代理人)正在评估...\n")
        self.log.see('end')
        self.after(1000, lambda: self.system_evaluate_contract(w1, w2))

    # 代理人信息
    def agent_information(self):
        cost_high_var = self.agentAI.cost_high_var
        cost_low_var = self.agentAI.cost_low_var
        reserve_var = self.agentAI.U_res
        self.log.insert('end', f"代理人的信息如下:\n努力成本：{cost_high_var}\n偷懒成本：{cost_low_var}\n保留效用: {reserve_var}\n")

    # 代理人查看系统给的合同并进行选择
    def system_propose_contract(self):
        self.clear_button()
        self.log.insert('end', "系统(委托人)正在设计合同...\n")
        self.log.see('end')
        self.after(1000)
        w1, w2 = self.principalAI.propose_contract(self.cost_high_var.get(), self.cost_low_var.get())
        self.w1_sys, self.w2_sys = w1, w2
        self.log.insert('end', f"系统提出合同: 高产出的工资为：{w1}, 低产出的工资为：{w2}\n")
        self.log.see('end')
        ttk.Button(self.btn_frame, text="接受合同", command=self.on_accept_contract).pack(pady=5)
        ttk.Button(self.btn_frame, text="拒绝合同", command=self.on_reject_contract).pack(pady=5)

    # 委托人重新填写合同
    def system_evaluate_contract(self, w1, w2):
        accept = self.agentAI.evaluate_contract(w1, w2)
        self.log.insert('end', f"系统(代理人){'接受' if accept else '拒绝'}合同\n")
        self.log.see('end')
        if accept:
            self.after(500, self.render_effort_stage)
        else:
            self.after(500, self.render_contract_design)

    # 代理人接受合同情况
    def on_accept_contract(self):
        self.log.insert('end', "您接受了合同，请选择努力/偷懒...\n")
        self.log.see('end')
        self.after(1000, self.render_effort_stage)

    # 代理人拒绝合同情况
    def on_reject_contract(self):
        self.log.insert('end', "您拒绝了合同，返回合同设计\n")
        self.log.see('end')
        self.after(500, self.render_contract_design)

    def render_effort_stage(self):
        self.clear_content()
        self.clear_button()
        if self.user_role == 'principal':
            self.log.insert('end', "系统(代理人)正在选择努力/偷懒...\n")
            self.log.see('end')
            self.after(1000, self.system_choose_effort)
        else:
            ttk.Label(self.content_frame, text="请选择您的努力水平：").pack(pady=10)
            self.effort_var = tk.StringVar(value='努力')
            ttk.Radiobutton(self.content_frame, text="努力", variable=self.effort_var, value='努力').pack()
            ttk.Radiobutton(self.content_frame, text="偷懒", variable=self.effort_var, value='偷懒').pack()
            ttk.Button(self.btn_frame, text="提交选择", command=self.on_submit_effort).pack(pady=10)

    def system_choose_effort(self):
        effort = self.agentAI.choose_effort()
        self.log.insert('end', f"系统(代理人)选择: {effort}\n")
        self.log.see('end')
        self.income = self.agentAI.principal_income(effort)
        self.after(500, self.render_result)

    def on_submit_effort(self):
        effort = self.effort_var.get()
        self.log.insert('end', f"您选择: {effort}\n系统(委托人)正在计算结果...\n")
        self.log.see('end')
        self.income = self.principalAI.agent_income(effort)
        self.after(1000, self.render_result)

    def render_result(self):
        self.clear_content()
        self.clear_button()
        self.log.insert('end', f"您最后的收益为{self.income}\n")
        ttk.Label(self.content_frame, text="仿真结束，详情见日志").pack(pady=20)
        ttk.Button(self.btn_frame, text="重新开始", command=self.render_role_selection).pack(pady=5)
        ttk.Button(self.btn_frame, text="退出", command=self.destroy).pack(pady=5)


class PrincipalPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)


class AgentPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)


class LemonMarketSimulator:
    """Discrete‑time simulator for Akerlof's lemon market with adaptive trust."""

    def __init__(
            self,
            total_cars: int = 100,
            q0: float = 0.5,
            V_high: float = 2000,
            V_low: float = 1000,
            beta: float = 0.3,
            gamma: float = 0.2,
            steps: int = 30,
            seed: int | None = None,
    ) -> None:
        if seed is not None:
            np.random.seed(seed)
        self.total_cars = total_cars
        self.high = int(round(total_cars * q0))
        self.low = total_cars - self.high
        self.tau = q0
        self.Vh, self.Vl = V_high, V_low
        self.beta, self.gamma = beta, gamma
        self.steps = steps
        # history containers --------------------------------------------------
        self.history: dict[str, list[float]] = {
            "high": [], "low": [], "q": [], "tau": [], "price": []}

    # ---------------------------------------------------------------------
    def _step(self) -> None:
        q_t = self.high / max(self.high + self.low, 1)
        p_t = self.tau * self.Vh + (1 - self.tau) * self.Vl
        # High‑quality sellers exit proportionally if p_t below reservation.
        if p_t < self.Vh and self.high > 0:
            exit_ratio = self.gamma * (1 - p_t / self.Vh)
            exit_num = max(1, int(round(self.high * exit_ratio)))
            self.high -= min(exit_num, self.high)
        # Buyers update trust towards *observed* share of good cars.
        self.tau += self.beta * (q_t - self.tau)
        # clamp tau to [0,1].
        self.tau = max(0.0, min(1.0, self.tau))
        # log ----------------------------------------------------------------
        self.history["high"].append(self.high)
        self.history["low"].append(self.low)
        self.history["q"].append(q_t)
        self.history["tau"].append(self.tau)
        self.history["price"].append(p_t)

    # ---------------------------------------------------------------------
    def run(self) -> dict[str, list[float]]:
        for _ in range(self.steps):
            # stop early if no good cars remain or trust collapsed
            if self.high == 0:
                self._log_terminal("高质量汽车已全部退出！")
                break
            self._step()
        return self.history

    # ---------------------------------------------------------------------
    def _log_terminal(self, msg: str) -> None:  # helper for silent mode
        self.history.setdefault("terminal", []).append(msg)


# ---------------------------------------------------------------------------
#  Tkinter view‑controller
# ---------------------------------------------------------------------------
class AdverseSelectionModule(BaseModule):
    """UI & controller for the lemon market simulation."""

    # ---------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_left_panel()
        self._build_right_panel()
        self.sim_data: dict[str, list[float]] | None = None

    # ------------------------------------------------------------------ UI
    def _build_left_panel(self) -> None:
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=12, pady=10)

        # ------ title
        ttk.Label(left, text="柠檬市场参数设置", font=(None, 12, "bold")).pack(pady=4)

        self.total_var = tk.IntVar(value=100)
        self.q0_var = tk.DoubleVar(value=0.5)
        # self.tau0_var = tk.DoubleVar(value=0.5)
        self.Vh_var = tk.DoubleVar(value=2400)
        self.Vl_var = tk.DoubleVar(value=1200)
        self.beta_var = tk.DoubleVar(value=0.3)
        self.gamma_var = tk.DoubleVar(value=0.2)
        self.T_var = tk.IntVar(value=30)

        _rows = [
            ("总车辆数", self.total_var, 10, 500, 1),
            ("初始高质量比例", self.q0_var, 0.0, 1.0, 0.01),
            ("高质量价值", self.Vh_var, 500, 5000, 50),
            ("低质量价值", self.Vl_var, 0, 4000, 50),
            ("信任调整速度", self.beta_var, 0.05, 1.0, 0.05),
            ("卖家退出敏感", self.gamma_var, 0.05, 1.0, 0.05),
            ("仿真周期数", self.T_var, 5, 200, 1),
        ]
        for label, var, frm, to, inc in _rows:
            ttk.Label(left, text=label).pack(anchor="w", pady=1)
            if isinstance(var, tk.IntVar):
                ttk.Spinbox(left, from_=frm, to=to, textvariable=var,
                            increment=inc, width=10).pack(fill="x")
            else:
                ttk.Scale(left, from_=frm, to=to, orient="horizontal",
                          variable=var).pack(fill="x")
                ttk.Entry(left, textvariable=var, width=8).pack(anchor="e")

        # ---------- action buttons
        btns = ttk.Frame(left)
        btns.pack(pady=8)
        ttk.Button(btns, text="开始模拟", command=self._on_run).pack(side="left", padx=4)
        ttk.Button(btns, text="导出 CSV", command=self._export_csv).pack(side="left", padx=4)

        # ----------- log box
        ttk.Label(left, text="日志").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(left, height=12, width=34)
        self.log.pack(fill="both", expand=False)

    # ------------------------------------------------------------------ UI
    def _build_right_panel(self) -> None:
        right = ttk.Frame(self)
        right.pack(side="right", fill="both", expand=True, padx=5)
        self.fig, self.ax1 = plt.subplots(figsize=(6, 4))
        self.ax2 = self.ax1.twinx()
        self.ax1.set_xlabel("周期 t")
        self.ax1.set_ylabel("车辆数量")
        self.ax2.set_ylabel("价格(p)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------------------------------------------------------- run
    def _on_run(self) -> None:
        # Read parameters ---------------------------------------------------
        sim = LemonMarketSimulator(
            total_cars=self.total_var.get(),
            q0=self.q0_var.get(),
            # tau0=self.tau0_var.get(),
            V_high=self.Vh_var.get(),
            V_low=self.Vl_var.get(),
            beta=self.beta_var.get(),
            gamma=self.gamma_var.get(),
            steps=self.T_var.get(),
        )
        self.log.insert("end", f"[INFO] 开始仿真…\n")
        self.sim_data = sim.run()
        self._draw()
        self.log.insert("end", f"[OK] 完成，共记录 {len(self.sim_data['q'])} 期。\n\n")
        self.log.see("end")

    # ---------------------------------------------------------------- draw
    def _draw(self) -> None:
        if not self.sim_data:
            return
        t = np.arange(1, len(self.sim_data["q"]) + 1)
        self.ax1.clear();
        self.ax2.clear()
        self.ax1.plot(t, self.sim_data["high"], label="高质量", linestyle="-", marker="o")
        self.ax1.plot(t, self.sim_data["low"], label="低质量", linestyle="--", marker="x")
        self.ax1.legend(loc="upper left")
        self.ax1.set_xlabel("周期 t");
        self.ax1.set_ylabel("车辆数量")
        # self.ax2.plot(t, self.sim_data["tau"], label="买家信任 τ", linestyle=":")
        self.ax2.plot(t, self.sim_data["price"], label="价格 p", linestyle="-")
        self.ax2.legend(loc="upper right")
        self.ax2.set_ylabel("信任(τ) / 价格(p)")
        self.fig.tight_layout()
        self.canvas.draw()

    # --------------------------------------------------------------- export
    def _export_csv(self) -> None:
        if not self.sim_data:
            messagebox.showinfo("提示", "请先运行一次模拟！")
            return
        fname = filedialog.asksaveasfilename(
            title="保存仿真结果",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")],
            initialfile=datetime.datetime.now().strftime("lemon_%Y%m%d_%H%M%S.csv"),
        )
        if not fname:
            return
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = ["t", "high", "low", "q", "tau", "price"]
            writer.writerow(headers)
            for i in range(len(self.sim_data["q"])):
                row = [i + 1] + [self.sim_data[k][i] for k in headers[1:]]
                writer.writerow(row)
        messagebox.showinfo("成功", f"结果已保存至 {fname}")


class MoralHazardModule(BaseModule):
    """Hidden‑action moral hazard simulator with variable risk preference."""

    # ------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_ui()

    # ---------------------------- UI ----------------------------------
    def _build_ui(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=14, pady=10)

        ttk.Label(left, text="参数设置", font=(None, 12, "bold")).pack(pady=4)

        # model parameters vars
        self.w_var    = tk.DoubleVar(value=100_000)
        self.d_var    = tk.DoubleVar(value=20_000)
        self.p_var    = tk.DoubleVar(value=0.25)
        self.pd_var   = tk.DoubleVar(value=0.15)
        self.c_var    = tk.DoubleVar(value=1_950)
        self.q_var    = tk.DoubleVar(value=0.00)
        self.gamma_var= tk.DoubleVar(value=1.00)   # CRRA coefficient γ

        _rows = [
            ("初始财富 w",     self.w_var),
            ("汽车价值 d",     self.d_var),
            ("盗窃概率 p",     self.p_var),
            ("装置后概率 p_d", self.pd_var),
            ("装置成本 c_d",   self.c_var),
            ("风险偏好 γ",     self.gamma_var),
        ]
        for label, var in _rows:
            row = ttk.Frame(left); row.pack(fill="x", pady=2)
            ttk.Label(row, text=label+"：", width=13, anchor="e").pack(side="left")
            ttk.Entry(row, textvariable=var, width=10).pack(side="left", padx=3)

        _rows = [
            ("道德风险 Δp", self.q_var, 0.05, 1.0, 0.05),
        ]
        for label, var, frm, to, inc in _rows:
            ttk.Label(left, text=label).pack(anchor="w", pady=1)
            if isinstance(var, tk.IntVar):
                ttk.Spinbox(left, from_=frm, to=to, textvariable=var,
                            increment=inc, width=10).pack(fill="x")
            else:
                ttk.Scale(left, from_=frm, to=to, orient="horizontal",
                          variable=var).pack(fill="x")
                ttk.Entry(left, textvariable=var, width=8).pack(anchor="e")

        ttk.Button(left, text="模拟决策",      command=self._simulate).pack(pady=8, fill="x")
        ttk.Button(left, text="随机演示一次",  command=self._random_demo).pack(pady=2, fill="x")

        # right pane: output
        self.log = scrolledtext.ScrolledText(self, width=62, height=32)
        self.log.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self._write_intro()

    # --------------------------- intro --------------------------------
    def _write_intro(self):
        intro = (
            "【模块说明】\n"
            "  本工具演示完全保险导致的隐藏行动道德风险：投保后张三不再主动安装防盗装置，使盗窃概率回升 (加上 Δp)。\n"
            "  您可通过风险厌恶系数 γ 观察不同风险偏好对“是否投保 / 是否安装装置”决策的影响。\n"
            "  γ=1 为对数效用，γ>1 更谨慎，γ=0 风险中性，γ<0 风险偏好。\n\n"
        )
        self.log.insert("end", intro)
        self.log.see("end")

    # --------------------------- utility ------------------------------
    @staticmethod
    def _utility(w, gamma):
        if w <= 0:
            return -float('inf')  # disallow non‑positive wealth
        if abs(gamma - 1.0) < 1e-8:
            return math.log(w)
        else:
            return (w**(1 - gamma) - 1) / (1 - gamma)

    # --------------------------- simulation ---------------------------
    def _simulate(self):
        # read parameters
        w, d, p, p_d, c_d, q, gamma = (self.w_var.get(), self.d_var.get(), self.p_var.get(),
                                       self.pd_var.get(), self.c_var.get(), self.q_var.get(),
                                       self.gamma_var.get())
        # fair premium (insurer assumes no device, prob=p)
        premium = d * p

        util = lambda wealth: self._utility(wealth, gamma)

        # ------ decisions if No insurance --------------------------------
        EU_no_dev = (1 - p)   * util(w)         + p   * util(w - d)
        EU_dev    = (1 - p_d) * util(w - c_d)   + p_d * util(w - d - c_d)
        install_no_ins = EU_dev > EU_no_dev
        EU_no_ins_opt  = max(EU_no_dev, EU_dev)

        # ------ Full insurance decisions ---------------------------------
        U_no_dev = util(w - premium)
        U_dev    = util(w - premium - c_d)
        install_ins = U_dev > U_no_dev   # still unlikely

        would_insure = U_no_dev >= EU_no_ins_opt  # compare with optimal uninsured

        # ------ moral hazard extra loss ----------------------------------
        base_prob = p_d if install_ins else p
        prob_actual = min(max(base_prob + q, 0.0), 1.0)
        extra_loss = d * (prob_actual - p) if prob_actual > p else 0.0

        # ------------------- print report --------------------------------
        out = ["———— 模拟结果 ————\n"]
        out.append(f"风险偏好 γ = {gamma:.2f}\n")
        out.append(f"公平保费 (d×p) = {premium:.2f}\n\n")

        out.append("[无保险]\n")
        out.append(f"  ▸ 最优策略：{'安装装置' if install_no_ins else '不安装装置'}\n")
        out.append(f"  ▸ 期望效用 EU = {EU_no_ins_opt:.4f}\n\n")

        out.append("[全额保险]\n")
        out.append(f"  ▸ 张三将{'购买' if would_insure else '拒绝'}保险\n")
        out.append(f"  ▸ 投保后张三{'仍安装' if install_ins else '不安装'}防盗装置\n")
        out.append(f"  ▸ 投保后效用 U = {U_dev if install_ins else U_no_dev:.4f}\n")

        if q != 0:
            out.append("\n[道德风险对保险公司]\n")
            out.append(f"  ▸ 定价盗窃概率 p = {p:.2%}\n")
            out.append(f"  ▸ 实际盗窃概率 = {prob_actual:.2%}\n")
            out.append(f"  ▸ 额外预期赔付 Δ = {extra_loss:.2f}\n")
        out.append("-"*48 + "\n\n")
        self.log.insert("end", "".join(out))
        self.log.see("end")

        # store for demo
        self._cached_decision = {
            "insured": would_insure,
            "install": install_no_ins if not would_insure else install_ins,
            "premium": premium,
            "prob_unins": p_d if install_no_ins else p,
            "prob_ins": p_d if install_ins else p,
            "gamma": gamma,
            "util": util,
            "params": (w, d, c_d, q)
        }

    # ------------------------ random demo -----------------------------
    def _random_demo(self):
        if not hasattr(self, "_cached_decision"):
            self.log.insert("end", "请先点击“模拟决策”再进行演示\n")
            self.log.see("end")
            return
        cd = self._cached_decision
        w, d, c_d, q = cd["params"]
        insured = cd["insured"]
        install = cd["install"]
        premium = cd["premium"] if insured else 0.0
        base_p  = cd["prob_ins"] if insured else cd["prob_unins"]
        p_theft = min(max(base_p + (q if insured else 0.0),0.0),1.0)
        theft   = random.random() < p_theft
        wealth_end = (w - premium - (c_d if install else 0)) + (d if (theft and insured) else 0) - (d if (theft and not insured) else 0)
        scenario = "投保" if insured else "未投保"
        self.log.insert("end", f"[随机演示] {scenario} | 盗窃概率 {p_theft:.1%} → {'被盗' if theft else '未被盗'}\n")
        self.log.insert("end", f"张三最终财富: {wealth_end:.2f}\n\n")
        self.log.see("end")


class SignalingModule(BaseModule):
    """教育信号发送（Spence 信号模型）可视化模块。

    左侧：参数输入 + 日志；右侧：成本‑收益与信号阈值图。
    支持判定分离 / 混同均衡并绘制关键阈值 e_L, e_H 及推荐 e*。
    """

    # ------------------------------------------------------------------
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # Matplotlib 中文 & 负号正常
        plt.rcParams.setdefault("font.family", "FangSong")
        plt.rcParams.setdefault("axes.unicode_minus", False)

        self._build_left_panel()
        self._build_right_panel()

    # ------------------------------------------------------------------ UI
    def _build_left_panel(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=12, pady=10)

        ttk.Label(left, text="教育信号模型参数", font=(None, 12, "bold")).pack(pady=4)

        # ------------------------- 参数变量
        self.a1_var = tk.DoubleVar(value=1.0)
        self.a2_var = tk.DoubleVar(value=2.0)
        self.c1_var = tk.DoubleVar(value=1.5)
        self.c2_var = tk.DoubleVar(value=1.0)
        self.e_max_var = tk.DoubleVar(value=3.0)

        _rows = [
            ("低类型工资 a1", self.a1_var, 0.0, 20.0, 0.1),
            ("高类型工资 a2", self.a2_var, 0.1, 20.0, 0.1),
            ("低类型单位成本 c1", self.c1_var, 0.1, 10.0, 0.1),
            ("高类型单位成本 c2", self.c2_var, 0.05, 10.0, 0.1),
            ("教育水平上限 e_max", self.e_max_var, 1.0, 50.0, 1.0),
        ]

        for label, var, frm, to, inc in _rows:
            ttk.Label(left, text=label).pack(anchor="w", pady=2)
            if isinstance(var, tk.DoubleVar):
                ttk.Spinbox(left, from_=frm, to=to, textvariable=var,
                             increment=inc, width=10).pack(anchor="w")

        # ---------- action buttons
        btns = ttk.Frame(left)
        btns.pack(pady=6)
        ttk.Button(btns, text="计算 / 绘制", command=self._on_calculate).pack(side="left", padx=2)
        ttk.Button(btns, text="清空日志", command=lambda: self.log.delete("1.0", "end")).pack(side="left", padx=2)

        # ----------- log box
        ttk.Label(left, text="日志").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(left, height=14, width=34)
        self.log.pack(fill="both", expand=False)

    # ------------------------------------------------------------------ UI
    def _build_right_panel(self):
        right = ttk.Frame(self)
        right.pack(side="right", fill="both", expand=True, padx=5)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.fig.tight_layout()

    # ---------------------------------------------------------------- calc
    def _on_calculate(self):
        a1, a2 = self.a1_var.get(), self.a2_var.get()
        c1, c2 = self.c1_var.get(), self.c2_var.get()
        e_max = max(1e-3, self.e_max_var.get())

        # --- 参数合法性检查
        if a2 <= a1:
            messagebox.showerror("参数错误", "必须满足 a2 > a1 (学历溢价)！")
            return
        if c1 <= c2:
            messagebox.showerror("参数错误", "必须满足 c1 > c2 (单交叉条件)！")
            return

        delta_a = a2 - a1
        e_L = delta_a / c1  # 低类型伪装阈值 (cost > benefit)
        e_H = delta_a / c2  # 高类型激励阈值 (benefit > cost)

        # ---------- 日志输出
        self.log.insert("end", f"\n[计算] a₂-a₁ = {delta_a:.3f},  e_L = {e_L:.3f},  e_H = {e_H:.3f}\n")

        separating = e_L < e_H
        if separating:
            e_star = (e_L + e_H) / 2  # 选中点，可改为用户自定义
            self.log.insert("end", f"存在分离均衡区间 ({e_L:.3f}, {e_H:.3f})，推荐 e* = {e_star:.3f}\n")
        else:
            self.log.insert("end", "⚠ 无分离均衡（可能为混同或无信号）。\n")
            e_star = None
        self.log.see("end")

        # ---------- 绘图
        self._draw_plot(a1, a2, c1, c2, e_max, e_L, e_H, e_star, separating)

    # ---------------------------------------------------------------- draw
    def _draw_plot(self, a1, a2, c1, c2, e_max, e_L, e_H, e_star, separating):
        xs = np.linspace(0, e_max, 400)
        cost_low = c1 * xs
        cost_high = c2 * xs
        wage_diff = np.full_like(xs, a2 - a1)

        self.ax.clear()
        # 成本线 & 收益线 --------------------------------------------------
        self.ax.plot(xs, cost_low, label="成本：低类型 c1e", linestyle="--")
        self.ax.plot(xs, cost_high, label="成本：高类型 c2e", linestyle=":")
        self.ax.plot(xs, wage_diff, label="工资差 a2-a1", linewidth=1.2)

        # 阈值 & e* --------------------------------------------------------
        self.ax.axvline(e_L, color="grey", linestyle="-.", label="e_L")
        self.ax.axvline(e_H, color="grey", linestyle="-.", label="e_H")
        if separating and e_star is not None:
            self.ax.axvline(e_star, color="red", linestyle="-", label="推荐 e*")

        # 坐标轴 & legend ---------------------------------------------------
        self.ax.set_xlim(0, e_max)
        ymax = max(wage_diff.max(), cost_low.max(), cost_high.max()) * 1.05
        self.ax.set_ylim(0, ymax)
        self.ax.set_xlabel("教育水平 e")
        self.ax.set_ylabel("成本 / 收益")
        title = "分离均衡" if separating else "无分离均衡"
        self.ax.set_title(f"教育信号成本收益图 ({title})")
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()



class ReportView(ttk.Frame):
    """集中查看与导出各模块仿真日志的视图"""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # —— 顶部工具栏 ——————————————————————————
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=5)

        ttk.Button(bar, text="汇总报告", command=self._collect_logs).pack(side="left", padx=4)
        ttk.Button(bar, text="导出为 TXT", command=self._export_txt).pack(side="left", padx=4)
        ttk.Button(bar, text="清空", command=lambda: self.report.delete("1.0", "end")
                   ).pack(side="left", padx=4)
        ttk.Button(bar, text="返回主菜单",
                   command=lambda: controller.show_frame(MainMenu)
                   ).pack(side="right", padx=4)

        # —— 报告显示区 ——————————————————————————
        self.report = scrolledtext.ScrolledText(self, width=100, height=40)
        self.report.pack(fill="both", expand=True, padx=10, pady=5)

    # ==============================================================
    #  汇总所有含有 .log 组件的模块日志
    # ==============================================================
    def _collect_logs(self):
        parts = []
        for frame in self.controller.frames.values():
            if hasattr(frame, "log"):
                content = frame.log.get("1.0", "end").strip()
                if content:
                    title = getattr(frame, "module_name", frame.__class__.__name__)
                    parts.append(f"{'='*18}  {title}  {'='*18}\n{content}\n")
        if not parts:
            messagebox.showinfo("提示", "暂未找到任何模块日志，可先到各模块进行仿真。")
            return
        self.report.delete("1.0", "end")
        self.report.insert("end", "\n".join(parts))
        self.report.see("end")

    # ==============================================================
    #  保存为 txt 文件，文件名：时间戳 + 100-999 随机数
    # ==============================================================
    def _export_txt(self):
        text = self.report.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("提示", "没有可导出的内容，请先点击“汇总报告”。")
            return

        # 让用户挑选目录；取消则返回
        dir_path = filedialog.askdirectory(title="选择保存目录")
        if not dir_path:  # 用户点了取消
            return

        # 生成文件名（使用 controller 提供的方法）
        base_name = self.controller.generate_report_filename()  # e.g. 20250508_153210_847.txt
        full_path = os.path.join(dir_path, base_name)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("成功", f"报告已保存至：\n{full_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")


if __name__ == '__main__':
    app = App()
    app.mainloop()