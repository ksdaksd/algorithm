import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import datetime

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件")
        self.geometry("900x650")
        self.frames = {}

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        for F in (MainMenu, RiskPreferenceModule, PrincipalAgentModule,
                  PrincipalPage, AgentPage,
                  AdverseSelectionModule, MoralHazardModule, SignalingModule,
                  ReportView):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)

    def show_frame(self, cls):
        frame = self.frames[cls]
        frame.tkraise()

    def generate_report_filename(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        rand = random.randint(100, 999)
        return f"{timestamp}_{rand}.txt"

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="信息经济学仿真软件", font=(None, 24)).pack(pady=30)
        buttons = [
            ("风险偏好", RiskPreferenceModule),
            ("委托代理与激励机制", PrincipalAgentModule),
            ("逆向选择：柠檬市场", AdverseSelectionModule),
            ("道德风险：汽车保险", MoralHazardModule),
            ("信号发送：教育信号", SignalingModule),
            ("仿真报告", ReportView)
        ]
        for txt, frame in buttons:
            ttk.Button(self, text=txt, width=30,
                       command=lambda f=frame: controller.show_frame(f)).pack(pady=8)

class BaseModule(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=5)
        ttk.Button(toolbar, text="返回", command=lambda: controller.show_frame(MainMenu)).pack(side="left", padx=5)
        ttk.Button(toolbar, text="返回主菜单", command=lambda: controller.show_frame(MainMenu)).pack(side="left", padx=5)
        ttk.Button(toolbar, text="查看报告", command=lambda: controller.show_frame(ReportView)).pack(side="right", padx=5)

class RiskPreferenceModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.prob_var = tk.DoubleVar(value=0.5)
        self.outcome1_var = tk.DoubleVar(value=100)
        self.outcome2_var = tk.DoubleVar(value=50)
        params = ttk.Frame(self)
        params.pack(side="left", fill="y", padx=15, pady=15)
        ttk.Label(params, text="风险偏好参数").pack(pady=5)
        ttk.Label(params, text="概率 p: ").pack(anchor="w")
        ttk.Entry(params, textvariable=self.prob_var).pack(fill="x")
        ttk.Label(params, text="支付 o1: ").pack(anchor="w")
        ttk.Entry(params, textvariable=self.outcome1_var).pack(fill="x")
        ttk.Label(params, text="支付 o2: ").pack(anchor="w")
        ttk.Entry(params, textvariable=self.outcome2_var).pack(fill="x")
        btn_frame = ttk.Frame(params)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="计算期望效用", command=self.compute_utility).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="绘制图像", command=self.plot_utility).pack(side="left", padx=5)
        self.log = scrolledtext.ScrolledText(params, width=35, height=12)
        self.log.pack(pady=5)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True)
    def compute_utility(self):
        p = self.prob_var.get(); o1 = self.outcome1_var.get(); o2 = self.outcome2_var.get()
        u = lambda x: np.log(x)
        eu = p*u(o1) + (1-p)*u(o2)
        msg = f"计算结果: 概率={p}, 支付1={o1}, 支付2={o2}, 期望效用={eu:.4f}\n"
        self.log.insert("end", msg); self.log.see("end")
    def plot_utility(self):
        p = self.prob_var.get(); max_o = max(self.outcome1_var.get(), self.outcome2_var.get())
        o_range = np.linspace(1e-6, max_o*1.2, 200); u=lambda x: np.log(x)
        eu = p*u(o_range) + (1-p)*u(o_range[::-1])
        self.ax.clear(); self.ax.plot(o_range, eu)
        self.ax.set_title("期望效用曲线"); self.ax.set_xlabel("支付金额"); self.ax.set_ylabel("期望效用")
        self.canvas.draw()

class PrincipalAgentModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="请选择角色", font=(None, 16)).pack(pady=20)
        self.role = tk.StringVar(value="principal")
        ttk.Radiobutton(self, text="委托人 (Principal)", variable=self.role, value="principal").pack(pady=5)
        ttk.Radiobutton(self, text="代理人 (Agent)", variable=self.role, value="agent").pack(pady=5)
        ttk.Button(self, text="确认", width=15, command=self.go_to_role).pack(pady=15)
    def go_to_role(self):
        self.controller.show_frame(PrincipalPage if self.role.get()=="principal" else AgentPage)

class PrincipalPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="委托人界面", font=(None, 16)).pack(pady=10)
        frame = ttk.Frame(self); frame.pack(padx=10, pady=10, fill="x")
        params = ["R_high","R_low","p_high","p_low","c_high","c_low","U_res"]
        self.vars={}
        for i,name in enumerate(params):
            ttk.Label(frame, text=f"{name}: ").grid(row=i,column=0,sticky="e",pady=2)
            var=tk.DoubleVar(value=0.0 if name not in ("p_high","p_low") else 0.5)
            ttk.Entry(frame,textvariable=var).grid(row=i,column=1,sticky="w",pady=2)
            self.vars[name]=var
        ttk.Label(frame, text="--- 合同条款 ---").grid(row=0,column=2,padx=20)
        self.w1_var, self.w2_var = tk.DoubleVar(), tk.DoubleVar()
        ttk.Label(frame, text="w_high: ").grid(row=1,column=2,sticky="e"); ttk.Entry(frame,textvariable=self.w1_var).grid(row=1,column=3,sticky="w")
        ttk.Label(frame, text="w_low: ").grid(row=2,column=2,sticky="e"); ttk.Entry(frame,textvariable=self.w2_var).grid(row=2,column=3,sticky="w")
        btn_frame=ttk.Frame(self); btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="提交合同", command=self.evaluate_contract).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="一键最优合同", command=self.optimal_contract).pack(side="left", padx=5)
        self.log = scrolledtext.ScrolledText(self, width=80, height=12); self.log.pack(pady=5)
    def evaluate_contract(self):
        R1,R2=self.vars['R_high'].get(),self.vars['R_low'].get()
        p1,p2=self.vars['p_high'].get(),self.vars['p_low'].get()
        c1,c0=self.vars['c_high'].get(),self.vars['c_low'].get()
        U0=self.vars['U_res'].get(); w1,w2=self.w1_var.get(),self.w2_var.get()
        UA1=p1*w1+(1-p1)*w2-c1; UA0=p2*w1+(1-p2)*w2-c0
        IC=UA1-UA0; PC=UA1-U0
        UP=p1*R1+(1-p1)*R2-(p1*w1+(1-p1)*w2)
        msg=f"代理人效用(努力):{UA1:.2f},偷懒:{UA0:.2f},IC:{IC:.2f},PC:{PC:.2f}\n委托人收益:{UP:.2f}\n"
        self.log.insert("end",msg); self.log.see("end")
    def optimal_contract(self):
        c1=self.vars['c_high'].get(); U0=self.vars['U_res'].get(); c0=self.vars['c_low'].get()
        w1=U0+c1; w2=w1-(c1-c0)
        self.w1_var.set(round(w1,2)); self.w2_var.set(round(w2,2)); self.evaluate_contract()

class AgentPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="代理人界面", font=(None, 16)).pack(pady=10)
        frame=ttk.Frame(self); frame.pack(padx=10,pady=10,fill="x")
        params=["c_high","c_low","U_res","p_high","p_low"]; self.varsA={}
        for i,name in enumerate(params):
            ttk.Label(frame, text=f"{name}: ").grid(row=i,column=0,sticky="e",pady=2)
            var=tk.DoubleVar(value=0.0); ttk.Entry(frame,textvariable=var).grid(row=i,column=1,sticky="w",pady=2)
            self.varsA[name]=var
        ttk.Label(frame, text="--- 合同 ---").grid(row=0,column=2,padx=20)
        self.w1A, self.w2A = tk.DoubleVar(), tk.DoubleVar()
        ttk.Label(frame, text="w_high: ").grid(row=1,column=2,sticky="e"); ttk.Entry(frame,textvariable=self.w1A).grid(row=1,column=3,sticky="w")
        ttk.Label(frame, text="w_low: ").grid(row=2,column=2,sticky="e"); ttk.Entry(frame,textvariable=self.w2A).grid(row=2,column=3,sticky="w")
        btnf=ttk.Frame(self); btnf.pack(pady=5)
        ttk.Button(btnf, text="接受合同", command=self.accept_contract).pack(side="left",padx=5)
        ttk.Button(btnf, text="拒绝合同", command=self.reject_contract).pack(side="left",padx=5)
        self.effort=tk.StringVar(value="high")
        ttk.Radiobutton(self, text="努力(high)", variable=self.effort, value="high").pack(pady=2)
        ttk.Radiobutton(self, text="偷懒(low)", variable=self.effort, value="low").pack(pady=2)
        self.logA=scrolledtext.ScrolledText(self,width=80,height=10);self.logA.pack(pady=5)
    def accept_contract(self): self.logA.insert("end","合同已接受\n");self.logA.see("end")
    def reject_contract(self): self.logA.insert("end","合同被拒绝\n");self.logA.see("end");self.controller.show_frame(PrincipalAgentModule)

class AdverseSelectionModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.high_count = tk.IntVar(value=100)
        self.low_count = tk.IntVar(value=100)
        self.high_val = tk.DoubleVar(value=2400)
        self.low_val = tk.DoubleVar(value=1200)
        self.step = tk.IntVar(value=1)
        params = ttk.Frame(self)
        params.pack(side="left", fill="y", padx=15, pady=15)
        ttk.Label(params, text="柠檬市场参数").pack(pady=5)
        for label, var in [("高质量数量:", self.high_count), ("低质量数量:", self.low_count),
                           ("高质量价值:", self.high_val), ("低质量价值:", self.low_val),
                           ("每步移除高质量量:", self.step)]:
            ttk.Label(params, text=label).pack(anchor="w")
            ttk.Entry(params, textvariable=var).pack(fill="x")
        ttk.Button(params, text="市场模拟决策", command=self.simulate_market).pack(pady=10)
        self.fig2, self.ax2 = plt.subplots()
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)
        self.canvas2.get_tk_widget().pack(side="right", fill="both", expand=True)

    def simulate_market(self):
        h = self.high_count.get(); l = self.low_count.get();
        hv = self.high_val.get(); lv = self.low_val.get();
        step = self.step.get()
        rounds = []
        high_list = []
        low_list = []
        r = 0
        while r < 1000 and h > 0:
            rounds.append(r)
            high_list.append(h)
            low_list.append(l)
            exp_price = (h*hv + l*lv) / (h + l)
            if exp_price >= hv:
                break
            h = max(h - step, 0)
            r += 1
        rounds.append(r); high_list.append(h); low_list.append(l)
        self.ax2.clear()
        self.ax2.plot(rounds, high_list, label="高质量数量")
        self.ax2.plot(rounds, low_list, label="低质量数量")
        self.ax2.set_title("柠檬市场数量变化")
        self.ax2.set_xlabel("轮次")
        self.ax2.set_ylabel("数量")
        self.ax2.legend()
        self.canvas2.draw()

class MoralHazardModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="道德风险：汽车保险模拟 - 待实现").pack(pady=50)

class SignalingModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="信号发送：教育信号模拟 - 待实现").pack(pady=50)

class ReportView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="仿真报告查看", font=(None, 16)).pack(pady=10)
        self.text = scrolledtext.ScrolledText(self, width=85, height=25)
        self.text.pack(pady=5)
        ttk.Button(self, text="导出报告", command=self.export_report).pack(pady=5)
        ttk.Button(self, text="返回主菜单", command=lambda: controller.show_frame(MainMenu)).pack()
        self.controller = controller

    def export_report(self):
        content = self.text.get("1.0", "end")
        filename = self.controller.generate_report_filename()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("导出成功", f"报告已导出到 {filename}")

if __name__ == '__main__':
    app = App()
    app.mainloop()
