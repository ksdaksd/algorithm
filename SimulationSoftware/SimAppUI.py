#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仿真软件GUI界面主界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import EducationSignalModule
import InsuranceModule
import LemonsMarketModule
import PrincipalAgentModule
import IncentiveMechanismModule
import RiskPreferenceModule

def not_implemented():
    messagebox.showinfo("提示", "该功能尚未实现。")

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("信息经济学仿真软件")
        self.geometry("1200x800")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # 创建各模块实例并添加到Notebook中
        self.risk_pref_module = RiskPreferenceModule.RiskPreference(self.notebook)
        self.notebook.add(self.risk_pref_module, text="风险偏好")

        self.principal_agent_module = PrincipalAgentModule.PrincipalAgent(self.notebook)
        self.notebook.add(self.principal_agent_module, text="委托代理")

        self.incentive_mechanism_module = IncentiveMechanismModule.IncentiveMechanism(self.notebook)
        self.notebook.add(self.incentive_mechanism_module,text="激励机制")

        self.lemons_market_module = LemonsMarketModule.LemonsMarket(self.notebook)
        self.notebook.add(self.lemons_market_module, text="柠檬市场")

        self.insurance_module = InsuranceModule.Insurance(self.notebook)
        self.notebook.add(self.insurance_module, text="车辆保险")

        self.education_signal_module = EducationSignalModule.EducationSignal(self.notebook)
        self.notebook.add(self.education_signal_module, text="教育信号")

        # 共用的查看报告按钮
        btn_report = ttk.Button(self, text="查看报告", command=not_implemented)
        btn_report.pack(side=tk.BOTTOM, pady=10)

if __name__ == '__main__':
    app = App()
    app.mainloop()