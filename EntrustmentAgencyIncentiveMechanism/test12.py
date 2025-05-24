import math
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "FangSong"
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

class EducationSignalingModel:
    """
    教育信号模型：模拟高低生产率劳动者在信号发送下的分离均衡。
    模型假设：
    1. 劳动者分为两种类型：
       - 低类型（low）：单位教育成本为 c1，产出（或市场价值）为 R_low。
       - 高类型（high）：单位教育成本为 c2，产出为 R_high，且 c1 > c2。
    2. 教育不影响实际生产率，只作为信号使用。
    3. 雇主根据观察到的教育水平支付工资：
       - 如果观察到教育为 e = 0，则支付 R_low；
       - 如果观察到教育达到一定水平 e_H，则支付 R_high。

    为实现分离均衡，低类型选择 e_L = 0，
    高类型选择 e_H，使得低类型不模仿：
       激励相容条件： R_low ≥ R_high - c1 * e_H  →  e_H ≥ (R_high - R_low)/c1.
    同时，高类型自身也要求：
       R_high - c2 * e_H ≥ R_low  →  e_H ≤ (R_high - R_low)/c2.
    因为 c1 > c2，上述区间非空，常选取 e_H = (R_high - R_low)/c1（即低类型边缘不模仿时的最低界限）。
    """

    def __init__(self, R_high, R_low, c1, c2):
        """
        :param R_high: 高类型劳动者的产出或市场价值 (例如2400)
        :param R_low: 低类型劳动者的产出或市场价值 (例如1200)
        :param c1: 低类型单位教育成本 (较高，例如 1.0)
        :param c2: 高类型单位教育成本 (较低，例如 0.5)
        """
        self.R_high = R_high
        self.R_low = R_low
        self.c1 = c1
        self.c2 = c2

    def compute_equilibrium(self):
        """
        计算分离均衡下的合同：
         - 低类型劳动者选择教育水平 e_L = 0，工资为 R_low；
         - 高类型劳动者选择教育水平 e_H = (R_high - R_low) / c1，工资为 R_high。
        :return: 字典形式返回均衡结果
        """
        e_low = 0.0
        wage_low = self.R_low

        e_high = (self.R_high - self.R_low) / self.c1
        wage_high = self.R_high

        # 验证激励相容性
        # 高类型自愿性：R_high - c2 * e_high 应大于或等于 R_low
        if self.R_high - self.c2 * e_high < self.R_low:
            print("警告：高类型激励相容性不满足！")
        return {"low": {"education": e_low, "wage": wage_low},
                "high": {"education": e_high, "wage": wage_high}}

    def type_utility(self, typ, e):
        """
        计算给定类型在选择教育水平 e 时的净效用（工资扣除教育成本）。
        工资基于分离均衡合同安排：若低类型则工资为 R_low，若高类型则工资为 R_high。
        :param typ: "low" 或 "high"
        :param e: 教育水平
        :return: 净效用 = wage - (成本系数)*e
        """
        if typ == "high":
            wage = self.R_high
            cost = self.c2 * e
        else:
            wage = self.R_low
            cost = self.c1 * e
        return wage - cost

    def plot_equilibrium(self):
        """
        绘制不同教育水平下，两种类型的净效用曲线（工资减去教育成本），以展示分离均衡中的策略差异。
        横坐标为教育水平 e，纵坐标为净效用 U(e)。
        并标记出均衡点：
          - 低类型：e = 0, U = R_low
          - 高类型：e = e_H, U = R_high - c2 * e_H
        """
        eq = self.compute_equilibrium()
        e_high = eq["high"]["education"]

        # 在 e 取值范围 [0, 1.5 * e_H] 内计算净效用曲线
        e_vals = np.linspace(0, 1.5 * e_high, 200)
        U_low_vals = [self.R_low - self.c1 * e for e in e_vals]
        U_high_vals = [self.R_high - self.c2 * e for e in e_vals]

        plt.figure(figsize=(6, 4))
        plt.plot(e_vals, U_low_vals, label="低类型效用 (U = R_low - c1*e)", color="blue")
        plt.plot(e_vals, U_high_vals, label="高类型效用 (U = R_high - c2*e)", color="red")
        # 标记均衡点
        plt.scatter([0], [self.R_low], color="blue", marker="o", s=80, label=f"低类型: (0, {self.R_low})")
        plt.scatter([e_high], [self.R_high - self.c2 * e_high],
                    color="red", marker="s", s=80,
                    label=f"高类型: ({e_high:.2f}, {self.R_high - self.c2 * e_high:.2f})")
        plt.xlabel("教育水平 e")
        plt.ylabel("净效用")
        plt.title("教育信号模型的分离均衡")
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    # 示例参数：设高类型产出为2400, 低类型为1200
    # 单位教育成本：低类型 c1 = 1.0, 高类型 c2 = 0.5 （满足 c1 > c2）
    R_high = 2400
    R_low = 1200
    c1 = 1.0
    c2 = 0.5

    model = EducationSignalingModel(R_high, R_low, c1, c2)
    equilibrium = model.compute_equilibrium()
    print("分离均衡结果：")
    print("低类型：教育水平 = ", equilibrium["low"]["education"], "工资 = ", equilibrium["low"]["wage"])
    print("高类型：教育水平 = ", equilibrium["high"]["education"], "工资 = ", equilibrium["high"]["wage"])

    # 绘制效用曲线，展示两类劳动者的净效用随教育变化情况
    model.plot_equilibrium()