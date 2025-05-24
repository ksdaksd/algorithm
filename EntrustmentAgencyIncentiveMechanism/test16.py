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
        self.frames[cls].tkraise()

    def generate_report_filename(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{ts}_{random.randint(100, 999)}.txt"


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

    ...  # 同前


class PrincipalPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="请选择角色", font=(None, 16)).pack(pady=20)
        self.role = tk.StringVar(value="principal")
        ttk.Radiobutton(self, text="委托人 (Principal)", variable=self.role, value="principal").pack(pady=5)
        ttk.Radiobutton(self, text="代理人 (Agent)", variable=self.role, value="agent").pack(pady=5)
        ttk.Button(self, text="确认", width=15, command=self.go_to_role).pack(pady=15)

    def go_to_role(self):
        self.controller.show_frame(PrincipalPage if self.role.get() == "principal" else AgentPage)

    ...


class AgentPage(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="请选择角色", font=(None, 16)).pack(pady=20)
        self.role = tk.StringVar(value="principal")
        ttk.Radiobutton(self, text="委托人 (Principal)", variable=self.role, value="principal").pack(pady=5)
        ttk.Radiobutton(self, text="代理人 (Agent)", variable=self.role, value="agent").pack(pady=5)
        ttk.Button(self, text="确认", width=15, command=self.go_to_role).pack(pady=15)

    def go_to_role(self):
        self.controller.show_frame(PrincipalPage if self.role.get() == "principal" else AgentPage)

    ...


class AdverseSelectionModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="请选择角色", font=(None, 16)).pack(pady=20)
        self.role = tk.StringVar(value="principal")
        ttk.Radiobutton(self, text="委托人 (Principal)", variable=self.role, value="principal").pack(pady=5)
        ttk.Radiobutton(self, text="代理人 (Agent)", variable=self.role, value="agent").pack(pady=5)
        ttk.Button(self, text="确认", width=15, command=self.go_to_role).pack(pady=15)

    def go_to_role(self):
        self.controller.show_frame(PrincipalPage if self.role.get() == "principal" else AgentPage)

    ...


class MoralHazardModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="道德风险：汽车保险", font=(None, 16)).pack(pady=10)
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill="x")
        labels = ["初始财富 W", "汽车价值 d", "原始盗窃概率 p", "设备后概率 p_dev", "设备成本 c_dev", "麻痹后概率 q"]
        self.vars = {}
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e", pady=2)
            var = tk.DoubleVar(value=0.0)
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="w", pady=2)
            self.vars[label] = var
        ttk.Button(self, text="模拟决策", command=self.simulate).pack(pady=5)
        self.log = scrolledtext.ScrolledText(self, width=85, height=15)
        self.log.pack(pady=5)

    def simulate(self):
        v = self.vars
        W, d, p, p_dev, c_dev, q = [v[k].get() for k in v]
        U = lambda x: np.log(x)
        a = d * p
        # 1. 是否购买保险
        U_ins = U(W - a)
        EU_no_ins = (1 - p) * U(W) + p * U(W - d)
        # 2. 无保险时是否装置
        EU_no_ins_no_dev = EU_no_ins
        EU_no_ins_dev = (1 - p_dev) * U(W - c_dev) + p_dev * U(W - c_dev - d)
        # 3. 有保险后是否装置
        EU_ins_no_dev = U_ins
        EU_ins_dev = U(W - a - c_dev)
        # 4. 麻痹后风险
        EU_ins_hazard = (1 - q) * U(W - a) + q * U(W - a - d)
        out = []
        out.append(f"1. 购买保险效用 {U_ins:.4f}, 无保险期望效用 {EU_no_ins:.4f}. 建议: {('购买' if U_ins > EU_no_ins else '不购买')}\n")
        out.append(
            f"2. 无保险时装置效用 {EU_no_ins_dev:.4f}, 不装置 {EU_no_ins_no_dev:.4f}. 建议: {('装置' if EU_no_ins_dev > EU_no_ins_no_dev else '不装置')}\n")
        out.append(
            f"3. 有保险后装置效用 {EU_ins_dev:.4f}, 不装置 {EU_ins_no_dev:.4f}. 建议: {('装置' if EU_ins_dev > EU_ins_no_dev else '不装置')}\n")
        out.append(f"4. 投保后麻痹效用 {EU_ins_hazard:.4f}, 原保险效用 {U_ins:.4f}.损失 {U_ins - EU_ins_hazard:.4f}\n")
        self.log.delete("1.0", "end")
        self.log.insert("end", "".join(out))


class SignalingModule(BaseModule):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="信号发送：教育信号模拟 - 待实现").pack(pady=50)

    ...


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
    ...


if __name__ == '__main__':
    app = App()
    app.mainloop()
