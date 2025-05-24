import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import datetime
plt.rcParams["font.family"] = "FangSong"  # 仿宋
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件")
        self.geometry("960x800")
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
        self.frames[cls].tkraise()

    def generate_report_filename(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{ts}_{random.randint(100,999)}.txt"

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
        self.out1 = tk.DoubleVar(value=100)
        self.out2 = tk.DoubleVar(value=50)
        params = ttk.Frame(self)
        params.pack(side="left", fill="y", padx=15, pady=15)
        ttk.Label(params, text="风险偏好参数").pack(pady=5)
        for label, var in [("概率 p:", self.prob_var), ("支付 o1:", self.out1), ("支付 o2:", self.out2)]:
            ttk.Label(params, text=label).pack(anchor="w")
            ttk.Entry(params, textvariable=var).pack(fill="x")
        btns = ttk.Frame(params)
        btns.pack(pady=10)
        ttk.Button(btns, text="计算期望效用", command=self.compute).pack(side="left", padx=5)
        ttk.Button(btns, text="绘制图像", command=self.plot).pack(side="left", padx=5)
        self.log = scrolledtext.ScrolledText(params, width=35, height=12)
        self.log.pack(pady=5)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    def compute(self):
        p, o1, o2 = self.prob_var.get(), self.out1.get(), self.out2.get()
        u = lambda x: np.log(x)
        eu = p * u(o1) + (1 - p) * u(o2)
        msg = f"期望效用={eu:.4f}\n"
        self.log.insert("end", msg)
        self.log.see("end")

    def plot(self):
        p, maxo = self.prob_var.get(), max(self.out1.get(), self.out2.get())
        xs = np.linspace(1e-6, maxo * 1.2, 200)
        u = lambda x: np.log(x)
        ys = p * u(xs) + (1 - p) * u(xs[::-1])
        self.ax.clear()
        self.ax.plot(xs, ys)
        self.ax.set(title="期望效用曲线", xlabel="支付", ylabel="效用")
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
        self.controller.show_frame(PrincipalPage if self.role.get() == "principal" else AgentPage)

class PrincipalPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="委托人界面", font=(None, 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill="x")
        params = ["R_high", "R_low", "p_high", "p_low", "c_high", "c_low", "U_res"]
        self.vars = {}
        for i, name in enumerate(params):
            ttk.Label(frame, text=f"{name}: ").grid(row=i, column=0, sticky="e", pady=2)
            var = tk.DoubleVar(value=0.5 if name in ("p_high", "p_low") else 0.0)
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="w", pady=2)
            self.vars[name] = var
        ttk.Label(frame, text="--- 合同条款 ---").grid(row=0, column=2, padx=20)
        self.w1_var = tk.DoubleVar()
        self.w2_var = tk.DoubleVar()
        ttk.Label(frame, text="w_high: ").grid(row=1, column=2, sticky="e")
        ttk.Entry(frame, textvariable=self.w1_var).grid(row=1, column=3, sticky="w")
        ttk.Label(frame, text="w_low: ").grid(row=2, column=2, sticky="e")
        ttk.Entry(frame, textvariable=self.w2_var).grid(row=2, column=3, sticky="w")
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="提交合同", command=self.evaluate_contract).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="一键最优合同", command=self.optimal_contract).pack(side="left", padx=5)
        self.log = scrolledtext.ScrolledText(self, width=80, height=12)
        self.log.pack(pady=5)

    def evaluate_contract(self):
        R1 = self.vars['R_high'].get(); R2 = self.vars['R_low'].get()
        p1 = self.vars['p_high'].get(); p2 = self.vars['p_low'].get()
        c1 = self.vars['c_high'].get(); c0 = self.vars['c_low'].get()
        U0 = self.vars['U_res'].get(); w1 = self.w1_var.get(); w2 = self.w2_var.get()
        UA1 = p1 * w1 + (1 - p1) * w2 - c1
        UA0 = p2 * w1 + (1 - p2) * w2 - c0
        IC = UA1 - UA0
        PC = UA1 - U0
        UP = p1 * R1 + (1 - p1) * R2 - (p1 * w1 + (1 - p1) * w2)
        msg = (f"代理人效用(努力): {UA1:.2f}, 偷懒: {UA0:.2f}, IC: {IC:.2f}, PC: {PC:.2f}\n"
               f"委托人收益: {UP:.2f}\n")
        self.log.insert("end", msg)
        self.log.see("end")

    def optimal_contract(self):
        c1 = self.vars['c_high'].get(); U0 = self.vars['U_res'].get(); c0 = self.vars['c_low'].get()
        w1 = U0 + c1
        w2 = w1 - (c1 - c0)
        self.w1_var.set(round(w1, 2)); self.w2_var.set(round(w2, 2))
        self.evaluate_contract()

class AgentPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="代理人界面", font=(None, 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill="x")
        params = ["c_high", "c_low", "U_res", "p_high", "p_low"]
        self.varsA = {}
        for i, name in enumerate(params):
            ttk.Label(frame, text=f"{name}: ").grid(row=i, column=0, sticky="e", pady=2)
            var = tk.DoubleVar(value=0.0)
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="w", pady=2)
            self.varsA[name] = var
        ttk.Label(frame, text="--- 合同 ---").grid(row=0, column=2, padx=20)
        self.w1A = tk.DoubleVar(); self.w2A = tk.DoubleVar()
        ttk.Label(frame, text="w_high: ").grid(row=1, column=2, sticky="e")
        ttk.Entry(frame, textvariable=self.w1A).grid(row=1, column=3, sticky="w")
        ttk.Label(frame, text="w_low: ").grid(row=2, column=2, sticky="e")
        ttk.Entry(frame, textvariable=self.w2A).grid(row=2, column=3, sticky="w")
        btnf = ttk.Frame(self); btnf.pack(pady=5)
        ttk.Button(btnf, text="接受合同", command=self.accept_contract).pack(side="left", padx=5)
        ttk.Button(btnf, text="拒绝合同", command=self.reject_contract).pack(side="left", padx=5)
        self.effort = tk.StringVar(value="high")
        ttk.Radiobutton(self, text="努力(high)", variable=self.effort, value="high").pack(pady=2)
        ttk.Radiobutton(self, text="偷懒(low)", variable=self.effort, value="low").pack(pady=2)
        self.logA = scrolledtext.ScrolledText(self, width=80, height=10); self.logA.pack(pady=5)
    def accept_contract(self):
        self.logA.insert("end", "合同已接受\n"); self.logA.see("end")
    def reject_contract(self):
        self.logA.insert("end", "合同被拒绝\n"); self.logA.see("end"); self.controller.show_frame(PrincipalAgentModule)

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
        h = self.high_count.get(); l = self.low_count.get()
        hv = self.high_val.get(); lv = self.low_val.get()
        step = self.step.get()
        rounds = []
        high_list = []
        low_list = []
        r = 0
        while r < 1000 and h > 0:
            rounds.append(r)
            high_list.append(h)
            low_list.append(l)
            exp_price = (h * hv + l * lv) / (h + l)
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
        ttk.Label(self, text="道德风险：汽车保险", font=(None,16)).pack(pady=10)
        frame = ttk.Frame(self); frame.pack(padx=10, pady=10, fill="x")
        labels = ["初始财富 W","汽车价值 d","原始盗窃概率 p","设备后概率 p_dev","设备成本 c_dev","麻痹后概率 q"]
        self.vars = {}
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label+":").grid(row=i, column=0, sticky="e", pady=2)
            var = tk.DoubleVar(value=0.0)
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="w", pady=2)
            self.vars[label] = var
        ttk.Button(self, text="模拟决策", command=self.simulate).pack(pady=5)
        self.log = scrolledtext.ScrolledText(self, width=85, height=15); self.log.pack(pady=5)
    def simulate(self):
        v = self.vars; W, d, p, p_dev, c_dev, q = [v[k].get() for k in v]
        U = lambda x: np.log(x)
        a = d * p
        U_ins = U(W - a)
        EU_no_ins = (1-p)*U(W) + p*U(W-d)
        EU_no_ins_dev = (1-p_dev)*U(W - c_dev) + p_dev*U(W - c_dev - d)
        EU_ins_no_dev = U_ins
        EU_ins_dev = U(W - a - c_dev)
        EU_ins_hazard = (1-q)*U(W - a) + q*U(W - a - d)
        out = []
        out.append(f"1. 购买保险效用 {U_ins:.4f}, 无保险期望效用 {EU_no_ins:.4f}. 建议: {('购买' if U_ins>EU_no_ins else '不购买')}\n")
        out.append(f"2. 无保险时装置效用 {EU_no_ins_dev:.4f}, 不装置 {EU_no_ins}: . 建议: {('装置' if EU_no_ins_dev>EU_no_ins else '不装置')}\n")
        out.append(f"3. 有保险后装置效用 {EU_ins_dev:.4f}, 不装置 {EU_ins_no_dev:.4f}. 建议: {('装置' if EU_ins_dev>EU_ins_no_dev else '不装置')}\n")
        out.append(f"4. 投保后麻痹效用 {EU_ins_hazard:.4f}, 原保险效用 {U_ins:.4f}. 损失 {U_ins - EU_ins_hazard:.4f}\n")
        self.log.delete("1.0","end")
        self.log.insert("end","".join(out))

class SignalingModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="信号发送：教育信号", font=(None,16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill="x")
        labels = ["高生产率教育成本 c2", "低生产率教育成本 c1", "低产者工资 a1", "高产者工资 a2", "最大教育水平 e_max"]
        self.vars_s = {}
        defaults = [20000, 40000, 100000, 200000, 10]
        for i, (label, default) in enumerate(zip(labels, defaults)):
            ttk.Label(frame, text=label+":").grid(row=i, column=0, sticky="e", pady=2)
            var = tk.DoubleVar(value=default)
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="w", pady=2)
            self.vars_s[label] = var
        ttk.Button(self, text="模拟决策", command=self.simulate).pack(pady=5)
        self.fig3, self.ax3 = plt.subplots()
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self)
        self.canvas3.get_tk_widget().pack(side="right", fill="both", expand=True)

    def simulate(self):
        c2 = self.vars_s["高生产率教育成本 c2"].get()
        c1 = self.vars_s["低生产率教育成本 c1"].get()
        a1 = self.vars_s["低产者工资 a1"].get()
        a2 = self.vars_s["高产者工资 a2"].get()
        e_max = self.vars_s["最大教育水平 e_max"].get()
        e = np.linspace(0, e_max, 200)
        net_low = a2 - c1 * e
        net_high = a2 - c2 * e
        const_low = a1 * np.ones_like(e)
        e_star_low = (a2 - a1) / c1 if c1 != 0 else np.nan
        e_star_high = (a2 - a1) / c2 if c2 != 0 else np.nan
        self.ax3.clear()
        self.ax3.plot(e, net_low, label="低生产率净收益")
        self.ax3.plot(e, net_high, label="高生产率净收益")
        self.ax3.plot(e, const_low, '--', label="不教育收益")
        if 0 <= e_star_low <= e_max:
            self.ax3.axvline(e_star_low, linestyle=':', label=f"低阈值 e*={e_star_low:.2f}")
        if 0 <= e_star_high <= e_max:
            self.ax3.axvline(e_star_high, linestyle='-.', label=f"高阈值 e*={e_star_high:.2f}")
        self.ax3.set_title("教育信号模型")
        self.ax3.set_xlabel("教育水平 e")
        self.ax3.set_ylabel("收益")
        self.ax3.legend()
        self.canvas3.draw()

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
