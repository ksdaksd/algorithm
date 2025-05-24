#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random

class RiskPreferenceModel:
    """
    用于模拟三种风险态度下的效用函数、期望效用及基本决策。
    - 风险厌恶: 常用对数效用 / 指数效用等
    - 风险中性: 效用函数 ~ 线性(U(x) = x)
    - 风险偏好: 可能使用二次方函数等（示例里演示单一写法）
    """

    def __init__(self, attitude="risk_averse", risk_aversion=1.0):
        """
        :param attitude: 字符串，'risk_averse'（风险厌恶）、'risk_neutral'（风险中性）或 'risk_preferring'（风险偏好）
        :param risk_aversion: 风险厌恶系数 (对风险厌恶时起作用); 数值越大，越厌恶风险
        """
        self.attitude = attitude
        self.risk_aversion = risk_aversion

    def utility(self, x):
        """
        单次收益 x 对应的效用值。
        不同风险态度对应不同的效用函数示例:
          1) 风险厌恶 (risk_averse): 指数/对数等
             - 对数效用: U(x) = ln(1 + x)
             - 指数效用: U(x) = 1 - exp(-a * x)
          2) 风险中性 (risk_neutral): U(x) = x
          3) 风险偏好 (risk_preferring): 这里示例用 U(x) = x^2 (或其他递增更快的函数)
        """
        if x < 0:
            # 确保对数/指数时不出错，简单地把负收益时做边界处理
            x_clamped = max(x, -0.9999)
        else:
            x_clamped = x

        if self.attitude == "risk_averse":
            # 示例1: 对数效用
            # return math.log(1 + max(0, x_clamped))
            # 示例2: 指数效用(常用)
            # U(x) = 1 - exp(-a * x)
            # a = self.risk_aversion
            # return 1.0 - math.exp(-a * x_clamped)
            #
            # 这里任选一个示例，这里用指数效用:
            a = self.risk_aversion
            return 1.0 - math.exp(-a * x_clamped)

        elif self.attitude == "risk_neutral":
            # 线性函数
            return x_clamped

        elif self.attitude == "risk_preferring":
            # 一个简单的凸函数
            return (x_clamped + 1.0)**2 - 1.0
        else:
            # 默认视为风险中性
            return x_clamped

    def expected_utility(self, outcomes, probs):
        """
        计算给定若干离散结果的期望效用:
        :param outcomes: list/tuple，每个元素是一次可能的收益数值
        :param probs: list/tuple，对应outcomes的概率
        :return: 期望效用值
        """
        eu = 0.0
        for x, p in zip(outcomes, probs):
            eu += self.utility(x) * p
        print("-----0---",eu)
        return eu

    def best_choice(self, choice_list):
        """
        简单决策：给定一系列选择，每个选择包含若干个离散收益及其概率，
        返回期望效用最高的选择。
        :param choice_list: [
            { "name":"方案1", "outcomes":[10, -5], "probs":[0.3, 0.7] },
            { "name":"方案2", "outcomes":[3, 2, -8], "probs":[0.5, 0.4, 0.1] },
            ...
        ]
        :return: (best_name, best_eu_value)
        """
        best_name = None
        best_eu = -1e9
        for c in choice_list:
            eu = self.expected_utility(c["outcomes"], c["probs"])
            if eu > best_eu:
                best_eu = eu
                best_name = c["name"]
        return best_name, best_eu

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

#------------------ 测试与演示 -------------------------
if __name__ == "__main__":
    # 演示：初始化3种不同风险态度
    aversion_model = RiskPreferenceModel(attitude="risk_averse", risk_aversion=0.8)
    neutral_model = RiskPreferenceModel(attitude="risk_neutral")
    preferring_model = RiskPreferenceModel(attitude="risk_preferring")

    # 1) 对比一次离散收益
    outcomes = [10, -5]  # 收益10或亏损5
    probs = [0.3, 0.7]
    print("-----一次离散收益(10|-5, prob=0.3/0.7)的期望效用对比-----")
    print("风险厌恶:", aversion_model.expected_utility(outcomes, probs))
    print("风险中性:", neutral_model.expected_utility(outcomes, probs))
    print("风险偏好:", preferring_model.expected_utility(outcomes, probs))

    # 2) 多方案选择
    print("\n-----多方案选择-----")
    choice_list = [
        {"name":"方案A","outcomes":[10, -5],"probs":[0.3,0.7]},
        {"name":"方案B","outcomes":[2, 2, -1],"probs":[0.3,0.5,0.2]}
    ]
    print("风险厌恶:", aversion_model.best_choice(choice_list))
    print("风险中性:", neutral_model.best_choice(choice_list))
    print("风险偏好:", preferring_model.best_choice(choice_list))

    # 3) 投资场景模拟
    print("\n-----模拟投资决策-----")
    invest_amount = 5.0
    success_prob = 0.4
    success_gain = 10.0
    failure_loss = 6.0
    eu_i, eu_n, dec = aversion_model.simulate_one_scenario(invest_amount, success_prob, success_gain, failure_loss)
    print(f"风险厌恶: EU_invest={eu_i:.3f}, EU_not_invest={eu_n:.3f}, 决策={dec}")
    eu_i, eu_n, dec = neutral_model.simulate_one_scenario(invest_amount, success_prob, success_gain, failure_loss)
    print(f"风险中性: EU_invest={eu_i:.3f}, EU_not_invest={eu_n:.3f}, 决策={dec}")
    eu_i, eu_n, dec = preferring_model.simulate_one_scenario(invest_amount, success_prob, success_gain, failure_loss)
    print(f"风险偏好: EU_invest={eu_i:.3f}, EU_not_invest={eu_n:.3f}, 决策={dec}")
