#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息经济学仿真软件 (高级可视化优化版)
-------------------------------------------------------------
功能要点：
1. 在委托代理模块中，通过 (w,b) 扫描构建 3D 曲面图或热力图，展示主人利润以及代理人效用等指标在参数空间的分布。
2. 在教育信号模块中，支持多学生对比；为不同学生设置(ability, cost_factor, wage, invest)等属性，企业则扫描不同threshold，绘制多条曲线或柱状图对比，或通过散点、直方图等方式展示。
3. 新增示例：Radar图(雷达图)、散点图、直方图等多种形式，丰富分析和展示效果。
4. 依然使用Tkinter + Matplotlib嵌入，结合Notebook分Tab。示例仅展示思路，实际可根据需求进行增删与美化。

注意：
• 对于3D或热力图，需要使用 mpl_toolkits.mplot3d 或 matplotlib.pyplot 的相关接口，或 matplotlib.pyplot.imshow() + colorbar 处理二维数组。
• Radar图可以用极坐标绘制，也可借助第三方库(若允许)；此处示例用matplotlib自带极坐标简单示例。
• 中文环境下建议提前安装中文字体并在rcParams或font_manager中进行配置，以免出现missing glyph问题。

运行环境：
- Python 3
- tkinter
- numpy
- matplotlib
- mpl_toolkits (matplotlib自带的3d工具包)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import random
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from mpl_toolkits.mplot3d import Axes3D  # 用于3D曲面/散点
import math


########################################
# 核心数据与模型类(简要)
########################################

class ImprovedPrincipalAgentModel:
    def __init__(self, outside_option=0.0, cost_factor=0.1, price=2.0):
        self.outside_option = outside_option
        self.c = cost_factor
        self.P = price

    # 代理人最优努力
    def agent_best_effort(self, w, b):
        if b <= 0:
            return 0.0
        return b / (2.0 * self.c)

    # 代理人效用
    def agent_utility(self, w, b, e):
        return w + b * e - self.c * (e ** 2)

    # 主人利润
    def principal_profit(self, w, b, e):
        return self.P * e - (w + b * e)


class ImprovedEducationSignaling:
    def __init__(self, ability=1.0, cost_factor=0.1, wage=50.0):
        self.ability = ability
        self.c = cost_factor
        self.wage = wage

    def labor_utility(self, invest, threshold):
        if invest < 0: invest = 0
        if invest >= threshold:
            return self.wage * self.ability - self.c * (invest ** 2)
        else:
            return - self.c * (invest ** 2)

    def firm_payoff(self, invest, threshold):
        if invest < threshold:
            return 0.0
        else:
            produce = 10 + 10 * self.ability
            return produce - self.wage

    def simulate(self, invest, threshold):
        lu = self.labor_utility(invest, threshold)
        fu = self.firm_payoff(invest, threshold)
        return lu, fu


########################################
# 仿真数据记录器
########################################

class SimulationDataRecorder:
    def __init__(self):
        self.records = []

    def log(self, module_name, param_dict, result_dict):
        self.records.append({
            "module": module_name,
            "params": param_dict,
            "results": result_dict
        })

    def generate_report_text(self):
        lines = []
        lines.append("===== 信息经济学仿真报告 (高级可视化优化版) =====\n")
        for i, rec in enumerate(self.records, start=1):
            lines.append(f"[{i}] 模块：{rec['module']}")
            lines.append("  输入参数：")
            for k, v in rec['params'].items():
                lines.append(f"    {k} = {v}")
            lines.append("  输出结果：")
            for k, v in rec['results'].items():
                lines.append(f"    {k} = {v}")
            lines.append("")
        return "\n".join(lines)


########################################
# 主界面 (含高级可视化)
########################################

class AdvancedInfoEconApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件 - 高级可视化优化版")
        self.geometry("1300x900")

        self.recorder = SimulationDataRecorder()

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Tabs
        self.build_tab_agent_3d_heatmap()
        self.build_tab_edu_multistudent()
        self.build_tab_extra_charts()

        # 底部按钮
        btn_report = ttk.Button(self, text="查看报告", command=self.show_report)
        btn_report.pack(side=tk.BOTTOM, pady=5)

    ###########################################################
    #  1) 委托代理(改进) - 3D曲面或二维热力图
    ###########################################################
    def build_tab_agent_3d_heatmap(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="委托代理-3D/热力图")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx = 0
        tk.Label(frame_input, text="外部效用(U0):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_u0 = tk.DoubleVar(value=0.0)
        tk.Entry(frame_input, textvariable=self.var_u0, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="努力成本系数(c):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_c = tk.DoubleVar(value=0.1)
        tk.Entry(frame_input, textvariable=self.var_c, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="价格(P):").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_p = tk.DoubleVar(value=2.0)
        tk.Entry(frame_input, textvariable=self.var_p, width=6).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="w范围 [w_min,w_max,step]:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_w = ttk.Frame(frame_input)
        self.var_wmin = tk.DoubleVar(value=0.0)
        self.var_wmax = tk.DoubleVar(value=20.0)
        self.var_wstep = tk.DoubleVar(value=2.0)
        tk.Entry(frame_w, textvariable=self.var_wmin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_wmax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_w, textvariable=self.var_wstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_w.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        tk.Label(frame_input, text="b范围 [b_min,b_max,step]:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_b = ttk.Frame(frame_input)
        self.var_bmin = tk.DoubleVar(value=0.0)
        self.var_bmax = tk.DoubleVar(value=5.0)
        self.var_bstep = tk.DoubleVar(value=0.5)
        tk.Entry(frame_b, textvariable=self.var_bmin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_bmax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_b, textvariable=self.var_bstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_b.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        # 下拉选择可视化类型(3D曲面/热力图 + 指标：利润or效用)
        tk.Label(frame_input, text="可视化类型:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_vis_type = tk.StringVar(value="3D-利润")
        cb_vis = ttk.Combobox(frame_input, textvariable=self.var_vis_type,
                              values=["3D-利润", "3D-效用", "热力图-利润", "热力图-效用"],
                              width=10)
        cb_vis.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        btn_run = ttk.Button(frame_input, text="绘制", command=self.run_pa_3d_heatmap)
        btn_run.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.label_pa_info = tk.Label(frame_input, text="输出信息...")
        self.label_pa_info.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 右侧放置图
        frame_plot = ttk.Frame(tab)
        frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_pa = Figure(figsize=(6, 5), dpi=100)
        self.ax_pa = self.fig_pa.add_subplot(111, projection='3d')  # 默认先用3d
        self.canvas_pa = FigureCanvasTkAgg(self.fig_pa, master=frame_plot)
        self.canvas_pa.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_pa_3d_heatmap(self):
        # 读取参数
        u0 = self.var_u0.get()
        c = self.var_c.get()
        P = self.var_p.get()
        wmin, wmax, wstep = self.var_wmin.get(), self.var_wmax.get(), self.var_wstep.get()
        bmin, bmax, bstep = self.var_bmin.get(), self.var_bmax.get(), self.var_bstep.get()

        # 数据
        model = ImprovedPrincipalAgentModel(u0, c, P)
        ws = np.arange(wmin, wmax + 1e-9, wstep)
        bs = np.arange(bmin, bmax + 1e-9, bstep)
        X, Y = np.meshgrid(ws, bs)  # X轴对应 w, Y轴对应 b
        Z = np.zeros_like(X)

        # 计算Z(主人利润或代理人效用)
        vis_type = self.var_vis_type.get()

        valid_count = 0
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                w_val = X[i, j]
                b_val = Y[i, j]
                e_star = model.agent_best_effort(w_val, b_val)
                ua = model.agent_utility(w_val, b_val, e_star)
                if ua < u0:
                    # 不满足参与约束 -> 标记为None或负值
                    Z[i, j] = np.nan
                else:
                    valid_count += 1
                    if "利润" in vis_type:
                        Z[i, j] = model.principal_profit(w_val, b_val, e_star)
                    else:
                        Z[i, j] = ua

        self.ax_pa.clear()
        if "3D" in vis_type:
            # 3D曲面
            self.ax_pa.set_projection('3d')
            self.ax_pa.set_title(vis_type)
            self.ax_pa.set_xlabel("w")
            self.ax_pa.set_ylabel("b")
            self.ax_pa.set_zlabel("Z value")
            # 由于有np.nan可能要掩码
            mask = ~np.isnan(Z)
            X_flat = X[mask]
            Y_flat = Y[mask]
            Z_flat = Z[mask]

            # 用plot_trisurf或散点图
            self.ax_pa.plot_trisurf(X_flat, Y_flat, Z_flat, cmap='viridis', edgecolor='none')
        else:
            # 热力图
            self.ax_pa.set_projection(None)  # 取消3D
            self.ax_pa.set_title(vis_type)
            self.ax_pa.set_xlabel("w axis")
            self.ax_pa.set_ylabel("b axis")
            self.ax_pa.imshow(Z, origin='lower', cmap='hot',
                              extent=[wmin, wmax, bmin, bmax],
                              aspect='auto')

            self.fig_pa.colorbar(self.ax_pa.images[0], ax=self.ax_pa, fraction=0.03)

        self.canvas_pa.draw()
        self.label_pa_info.config(text=f"有效网格点数={valid_count}, 其余因U<A外部效用而无效。")

        # 记录
        self.recorder.log("委托代理-3D或热力图",
                          {"u0": u0, "c": c, "P": P, "vis_type": vis_type,
                           "w_range": [wmin, wmax, wstep],
                           "b_range": [bmin, bmax, bstep]},
                          {"valid_points": valid_count})

    ###########################################################
    #  2) 教育/招聘信号 - 多学生对比 & 多阈值可视化
    ###########################################################
    def build_tab_edu_multistudent(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="教育信号-多学生")

        frame_input = ttk.Frame(tab)
        frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row_idx = 0
        tk.Label(frame_input, text="学生个数:").grid(row=row_idx, column=0, sticky=tk.E)
        self.var_num_students = tk.IntVar(value=3)
        tk.Entry(frame_input, textvariable=self.var_num_students, width=5).grid(row=row_idx, column=1, padx=5, pady=2)
        row_idx += 1

        tk.Label(frame_input, text="门槛(s) 范围 & 步长:").grid(row=row_idx, column=0, sticky=tk.E)
        frame_srange = ttk.Frame(frame_input)
        self.var_smin = tk.DoubleVar(value=0.0)
        self.var_smax = tk.DoubleVar(value=5.0)
        self.var_sstep = tk.DoubleVar(value=1.0)
        tk.Entry(frame_srange, textvariable=self.var_smin, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_srange, textvariable=self.var_smax, width=5).pack(side=tk.LEFT, padx=2)
        tk.Entry(frame_srange, textvariable=self.var_sstep, width=5).pack(side=tk.LEFT, padx=2)
        frame_srange.grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1

        btn_build = ttk.Button(frame_input, text="创建学生输入框", command=self.build_student_inputs)
        btn_build.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        btn_run = ttk.Button(frame_input, text="门槛扫描 &可视化", command=self.run_edu_multistudent_scan)
        btn_run.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.label_edu_info = tk.Label(frame_input, text="结果信息...")
        self.label_edu_info.grid(row=row_idx, column=0, columnspan=2, pady=5)

        # 下方(或旁边)放一个框，动态添加学生信息输入
        self.frame_students = ttk.LabelFrame(tab, text="多学生输入区(ability, c, wage, invest)")
        self.frame_students.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 图
        self.fig_edu = Figure(figsize=(6, 5), dpi=100)
        self.ax_edu = self.fig_edu.add_subplot(111)
        self.canvas_edu = FigureCanvasTkAgg(self.fig_edu, master=tab)
        self.canvas_edu.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 存储学生输入tk变量
        self.student_vars = []  # list of (var_ability, var_c, var_wage, var_invest)

    def build_student_inputs(self):
        # 清空旧UI
        for child in self.frame_students.winfo_children():
            child.destroy()

        self.student_vars.clear()

        n = self.var_num_students.get()
        # 标题行
        tk.Label(self.frame_students, text="ID").grid(row=0, column=0)
        tk.Label(self.frame_students, text="ability").grid(row=0, column=1)
        tk.Label(self.frame_students, text="cost_c").grid(row=0, column=2)
        tk.Label(self.frame_students, text="wage").grid(row=0, column=3)
        tk.Label(self.frame_students, text="invest").grid(row=0, column=4)

        for i in range(n):
            tk.Label(self.frame_students, text=f"Student{i + 1}").grid(row=i + 1, column=0)
            var_a = tk.DoubleVar(value=1.0)
            var_c = tk.DoubleVar(value=0.1)
            var_w = tk.DoubleVar(value=50)
            var_inv = tk.DoubleVar(value=2.0)
            self.student_vars.append((var_a, var_c, var_w, var_inv))

            tk.Entry(self.frame_students, textvariable=var_a, width=5).grid(row=i + 1, column=1)
            tk.Entry(self.frame_students, textvariable=var_c, width=5).grid(row=i + 1, column=2)
            tk.Entry(self.frame_students, textvariable=var_w, width=5).grid(row=i + 1, column=3)
            tk.Entry(self.frame_students, textvariable=var_inv, width=5).grid(row=i + 1, column=4)

    def run_edu_multistudent_scan(self):
        smin = self.var_smin.get()
        smax = self.var_smax.get()
        sstep = self.var_sstep.get()

        # 收集学生信息
        student_list = []
        for (va, vc, vw, vinv) in self.student_vars:
            student_list.append([va.get(), vc.get(), vw.get(), vinv.get()])

        thresholds = np.arange(smin, smax + 1e-9, sstep)
        # 想要可视化很多学生 => 每个学生在所有threshold下的(劳动力效用, 企业收益)
        # 可以在同一图上画多条曲线，或画散点/柱状图等

        self.ax_edu.clear()
        self.ax_edu.set_title("多学生 vs. 多阈值")
        self.ax_edu.set_xlabel("threshold")
        self.ax_edu.set_ylabel("效用/收益")

        # 例如：对每个学生画两条线：劳动力效用、企业收益(或者只画劳动力效用)
        for idx, st in enumerate(student_list):
            ab, cc, ww, inv = st
            model = ImprovedEducationSignaling(ab, cc, ww)
            lu_list = []
            fu_list = []
            for s in thresholds:
                lu, fu = model.simulate(inv, s)
                lu_list.append(lu)
                fu_list.append(fu)

            # 在图中画劳动力效用
            self.ax_edu.plot(thresholds, lu_list,
                             label=f"Stu{idx + 1} - LU",
                             marker='o', alpha=0.5)
            # 同时可以画企业收益
            self.ax_edu.plot(thresholds, fu_list,
                             label=f"Stu{idx + 1} - Firm",
                             marker='s', alpha=0.5)

        self.ax_edu.legend()
        self.canvas_edu.draw()

        self.recorder.log("教育信号-多学生对比",
                          {"threshold_range": [smin, smax, sstep]},
                          {"num_students": len(student_list)})

        self.label_edu_info.config(text="多名学生在不同阈值下的LU/Firm收益已绘制。")

    ###########################################################
    #  3) 其他图表示例 (直方图、散点图、雷达图)
    ###########################################################
    def build_tab_extra_charts(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="更多图表示例")

        frame_btn = ttk.Frame(tab)
        frame_btn.pack(side=tk.TOP, fill=tk.X, pady=5)

        btn_hist = ttk.Button(frame_btn, text="随机值直方图", command=self.show_histogram_example)
        btn_hist.pack(side=tk.LEFT, padx=5)

        btn_scatter = ttk.Button(frame_btn, text="散点图示例", command=self.show_scatter_example)
        btn_scatter.pack(side=tk.LEFT, padx=5)

        btn_radar = ttk.Button(frame_btn, text="雷达图示例", command=self.show_radar_example)
        btn_radar.pack(side=tk.LEFT, padx=5)

        self.fig_extra = Figure(figsize=(6, 5), dpi=100)
        self.ax_extra = self.fig_extra.add_subplot(111)
        self.canvas_extra = FigureCanvasTkAgg(self.fig_extra, master=tab)
        self.canvas_extra.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_histogram_example(self):
        self.ax_extra.clear()
        self.ax_extra.set_title("随机值直方图")

        data = np.random.normal(loc=50, scale=10, size=1000)
        self.ax_extra.hist(data, bins=20, color='blue', alpha=0.7)
        self.ax_extra.set_xlabel("Value")
        self.ax_extra.set_ylabel("Frequency")

        self.canvas_extra.draw()

    def show_scatter_example(self):
        self.ax_extra.clear()
        self.ax_extra.set_title("散点图示例")

        x = np.random.rand(50) * 10
        y = np.random.rand(50) * 10
        sizes = np.random.rand(50) * 300
        colors = np.random.rand(50)

        self.ax_extra.scatter(x, y, s=sizes, c=colors, cmap='viridis', alpha=0.7)
        self.ax_extra.set_xlabel("X")
        self.ax_extra.set_ylabel("Y")

        self.canvas_extra.draw()

    def show_radar_example(self):
        # 雷达图: 需要将数据映射到极坐标
        self.ax_extra.clear()
        self.ax_extra.set_title("雷达图示例")

        # 简单示例：评分维度(5个)
        labels = np.array(["质量", "信誉", "效率", "性价比", "可持续性"])
        data = [3.5, 4.2, 3.8, 4.5, 2.9]  # 示例评分
        N = len(data)

        # 闭合
        data = np.concatenate((data, [data[0]]))
        labels = np.concatenate((labels, [labels[0]]))

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))

        self.ax_extra = self.fig_extra.add_subplot(111, polar=True)
        self.ax_extra.plot(angles, data, 'o-', color='r', alpha=0.7)
        self.ax_extra.fill(angles, data, color='r', alpha=0.3)
        self.ax_extra.set_thetagrids(angles[:-1] * 180 / np.pi, labels[:-1])
        self.ax_extra.set_ylim(0, 5)

        self.canvas_extra.draw()

    ###########################################################
    # 查看报告
    ###########################################################
    def show_report(self):
        report_str = self.recorder.generate_report_text()
        messagebox.showinfo("仿真报告", report_str)


def main():
    # 若系统需要中文显示, 请在此设置字体
    # import matplotlib
    # from matplotlib import rcParams
    # rcParams['font.sans-serif'] = ['SimHei']
    # rcParams['axes.unicode_minus'] = False

    app = AdvancedInfoEconApp()
    app.mainloop()


if __name__ == "__main__":
    main()