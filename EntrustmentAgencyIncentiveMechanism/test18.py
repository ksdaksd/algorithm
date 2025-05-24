import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PrincipalAgentModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.user_role = None
        self.principalAI = PrincipalAI()
        self.agentAI = AgentAI()
        self.vars = {}
        self.count = 0
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self)
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
        self.count += 1
        self.clear_content()
        self.clear_button()
        # 情景说明标签
        ttk.Label(self.content_frame, text="情景背景：股东（委托人）雇佣经理（代理人）管理企业。由于信息不对称，股东无法直接观察经理的努力程度，需要设计激励合同约束经理行为。", wraplength=600).pack(pady=5)
        # 自然参数输入
        ttk.Label(self.content_frame, text="请设置自然变量：", font=(None, 12, 'bold')).pack(pady=10)
        self.rev_high_var = tk.DoubleVar(value=100)
        self.rev_low_var = tk.DoubleVar(value=20)
        self.p_high_var   = tk.DoubleVar(value=0.8)
        self.p_low_var    = tk.DoubleVar(value=0.4)
        for text, var in [('高产出收益', self.rev_high_var),
                          ('低产出收益', self.rev_low_var),
                          ('努力时高产出概率', self.p_high_var),
                          ('偷懒时高产出概率', self.p_low_var)]:
            row = ttk.Frame(self.content_frame)
            row.pack(pady=5)
            ttk.Label(row, text=f"{text}：").pack(side='left', padx=2)
            ttk.Entry(row, textvariable=var, width=8).pack(side='left')
        # 系统随机生成代理人努力成本
        self.agentAI.cost_set(self.rev_high_var.get(), self.rev_low_var.get())
        # 角色选择单选按钮
        ttk.Label(self.content_frame, text="\n请选择您的角色：", font=(None, 12, 'bold')).pack(pady=10)
        self.role_var = tk.StringVar(value='principal')
        ttk.Radiobutton(self.content_frame, text="股东(委托人)", variable=self.role_var, value='principal').pack()
        ttk.Radiobutton(self.content_frame, text="经理(代理人)", variable=self.role_var, value='agent').pack()
        ttk.Button(self.btn_frame, text="确认", command=self.on_role_confirm).pack(pady=10)

    def on_role_confirm(self):
        self.user_role = self.role_var.get()
        # 获取参数
        self.vars = {
            '高产出收益': self.rev_high_var.get(),
            '低产出收益': self.rev_low_var.get(),
            '努力时高产出概率': self.p_high_var.get(),
            '偷懒时高产出概率': self.p_low_var.get()
        }
        # 记录日志：角色选择
        role_label = "股东(委托人)" if self.user_role=='principal' else "经理(代理人)"
        self.log.insert('end', f"第{self.count}次实验，您选择了角色：{role_label}\n")
        self.log.insert('end', f"高产出收益: {self.vars['高产出收益']}\n低产出收益: {self.vars['低产出收益']}\n努力时高产出概率: {self.vars['努力时高产出概率']}\n偷懒时高产出概率: {self.vars['偷懒时高产出概率']}\n\n")
        self.log.see('end')
        self.after(500, self.render_contract_design)

    def render_contract_design(self):
        self.clear_button()
        self.clear_content()
        # 委托人界面
        if self.user_role == 'principal':
            ttk.Label(self.content_frame, text="股东(委托人)界面", font=(None, 16, 'bold')).grid(row=0, column=2, pady=10)
            params = ["高产出收益", "低产出收益", "努力时高产出概率", "偷懒时高产出概率"]
            ttk.Label(self.content_frame, text="--- 自然信息 ---", font=(None, 10, 'bold')).grid(row=1, column=0, padx=10)
            for i, name in enumerate(params):
                ttk.Label(self.content_frame, text=f"{name}: ").grid(row=i+2, column=0, sticky="e", pady=5)
                var = self.vars[name]
                ttk.Label(self.content_frame, text=f"{var}").grid(row=i+2, column=1, sticky="w", pady=5)
            # 合同条款输入
            ttk.Label(self.content_frame, text="--- 合同条款 ---", font=(None, 10, 'bold')).grid(row=1, column=2, padx=20)
            self.w_high_var = tk.DoubleVar(value=60)
            self.w_low_var  = tk.DoubleVar(value=10)
            ttk.Label(self.content_frame, text="高产出工资: ").grid(row=2, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.w_high_var, width=8).grid(row=2, column=3, sticky="w")
            ttk.Label(self.content_frame, text="低产出工资: ").grid(row=3, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.w_low_var, width=8).grid(row=3, column=3, sticky="w")
            # 将参数传给AI
            self.set_AI_var(self.rev_high_var.get(), self.rev_low_var.get(),
                            self.p_high_var.get(), self.p_low_var.get())
            self.agent_information()
            ttk.Button(self.btn_frame, text="提交合同", command=self.on_submit_contract).pack(padx=10)
        else:
            # 代理人界面
            ttk.Label(self.content_frame, text="经理(代理人)界面", font=(None, 16, 'bold')).grid(row=0, column=2, pady=10)
            params = ["高产出收益", "低产出收益", "努力时高产出概率", "偷懒时高产出概率"]
            ttk.Label(self.content_frame, text="--- 自然信息 ---", font=(None, 10, 'bold')).grid(row=1, column=0, padx=10)
            for i, name in enumerate(params):
                ttk.Label(self.content_frame, text=f"{name}: ").grid(row=i+2, column=0, sticky="e", pady=5)
                var = self.vars[name]
                ttk.Label(self.content_frame, text=f"{var}").grid(row=i+2, column=1, sticky="w", pady=5)
            ttk.Label(self.content_frame, text="--- 经理信息 ---", font=(None, 10, 'bold')).grid(row=1, column=2, padx=10)
            self.cost_high_var = tk.DoubleVar(value=10)
            self.cost_low_var  = tk.DoubleVar(value=5)
            self.reserve_var   = tk.DoubleVar(value=0)
            ttk.Label(self.content_frame, text="努力成本: ").grid(row=2, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.cost_high_var, width=8).grid(row=2, column=3, sticky="w")
            ttk.Label(self.content_frame, text="偷懒成本: ").grid(row=3, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.cost_low_var, width=8).grid(row=3, column=3, sticky="w")
            ttk.Label(self.content_frame, text="保留效用: ").grid(row=4, column=2, sticky="e")
            ttk.Entry(self.content_frame, textvariable=self.reserve_var, width=8).grid(row=4, column=3, sticky="w")
            self.set_AI_var(self.rev_high_var.get(), self.rev_low_var.get(),
                            self.p_high_var.get(), self.p_low_var.get())
            ttk.Button(self.btn_frame, text="提交信息", command=self.system_propose_contract).pack(padx=10)

    # 将自然信息传给AI
    def set_AI_var(self, rev_high, rev_low, p_high, p_low):
        self.agentAI.set(rev_high, rev_low, p_high, p_low)
        self.principalAI.set(rev_high, rev_low, p_high, p_low)

    def on_submit_contract(self):
        w1, w2 = self.w_high_var.get(), self.w_low_var.get()
        if w1 < w2:
            messagebox.showinfo("错误", "高产出工资不应小于低产出工资！")
            self.render_contract_design()
        else:
            self.w1_sys, self.w2_sys = w1, w2
            self.log.insert('end', f"您提交合同: w_high={w1}, w_low={w2}\n系统(代理人)正在评估...\n")
            self.log.see('end')
            self.after(1000, lambda: self.system_evaluate_contract(w1, w2))

    def agent_information(self):
        # 日志中显示代理人（经理）的成本与保留效用
        cost_high = self.agentAI.cost_high_var
        cost_low  = self.agentAI.cost_low_var
        reserve   = self.agentAI.U_res
        self.log.insert('end', f"经理的成本信息如下:\n努力成本: {cost_high}\n偷懒成本: {cost_low}\n保留效用: {reserve}\n")
        self.log.see('end')

    # （省略 system_evaluate_contract、on_accept_contract 等原有方法实现）
    # ...

    def render_result(self):
        self.clear_content()
        self.clear_button()
        # 显示最终收益
        self.log.insert('end', f"您最后的收益为 {self.income}\n\n\n\n\n")
        # 显示提示文字
        ttk.Label(self.content_frame, text="仿真结束，详情见日志").pack(pady=10)
        # 绘制收益-效用图表
        # 准备数据：以高产出工资为横轴
        rev_high = self.rev_high_var.get()
        rev_low  = self.rev_low_var.get()
        p_high   = self.p_high_var.get()
        p_low    = self.p_low_var.get()
        cost_high = self.agentAI.cost_high_var
        cost_low  = self.agentAI.cost_low_var
        w_values = np.linspace(0, rev_high*1.2, 100)
        profits = []
        utils = []
        # 计算每个工资水平下的股东收益和经理效用
        # 假设低产出工资 w_L = 0（示意可视化效果）
        for w in w_values:
            U_high = p_high * w + (1 - p_high) * 0 - cost_high
            U_low  = p_low  * w + (1 - p_low)  * 0 - cost_low
            if U_high >= U_low:
                # 经理选择努力
                profit = p_high * (rev_high - w) + (1 - p_high) * (rev_low - 0)
                util   = U_high
            else:
                # 经理选择偷懒
                profit = p_low  * (rev_high - w) + (1 - p_low)  * (rev_low - 0)
                util   = U_low
            profits.append(profit)
            utils.append(util)
        # 绘制图表
        fig, ax = plt.subplots(figsize=(5,4))
        ax.plot(w_values, profits, label="股东收益")
        ax.plot(w_values, utils,   label="经理效用")
        ax.axvline((cost_high - cost_low)/(p_high - p_low) if (p_high-p_low)>0 else 0,
                   color='gray', linestyle='--', label="切换阈值")
        ax.set_xlabel("高产出工资")
        ax.set_ylabel("收益 / 效用")
        ax.legend()
        ax.set_title("股东收益与经理效用随合同的变化")
        # 将图表嵌入Tkinter界面
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        # 重新开始按钮
        ttk.Button(self.btn_frame, text="重新开始", command=self.render_role_selection).pack(pady=5)
