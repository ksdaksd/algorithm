#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
委托代理与激励机制 - 包含激励相容约束(IC)与参与约束的简化模型示例

模型假设：
1. 产出函数 Q(e) = e (可视作 A=1 的线性产出，为示例简化处理)。
2. 代理人(Agent)风险中性，其效用函数 U_A = w + b * Q(e) - C(e)，
   其中 C(e) = c * e^2 表示努力成本，c 为努力成本系数。
3. 主人(Principal)收益（利润）π = P * Q(e) - (w + b * Q(e))，其中 P 为产出的市场价格。
4. 代理人的外部机会效用(U0)表示其不签约时能获得的效用水平(参与约束)。
5. 激励相容约束(IC)：代理人给定(w,b)时，会选择使自身效用最大化的努力水平 e*。
   在此风险中性、简化线性框架下，若 b>0，则 e*(w,b)=b/(2c)，若 b<=0，代理人最优努力为 0。
6. 参与约束(PC)：代理人选择 e* 后的实际效用 U_A(e*) ≥ U0，若不满足则代理人拒绝签约。

该示例通过控制台输入参数，并采用穷举法(grid search)在一段离散区间搜索(w,b)，
在满足激励相容(IC)与参与约束(PC)的情况下，找到使主人利润最大的合约(w*, b*)。
'''

"""
代码简要说明：
在该简化模型中，激励相容条件(IC)直接体现在代理人针对给定的奖金系数 b 使自身效用最大化的策略选择上。
对于风险中性、线性产出的情形，代理人最佳努力 e* = b / (2c)（当 b>0 时）。若 b ≤ 0，则代理人不会选择正努力。
参与约束(PC)要求代理人在最优努力 e* 下的效用 ≥ 其外部机会效用 U₀ (outside_option)。若不满足，则合同无效。
通过 find_optimal_contract 函数，对 (w, b) 在指定的离散网格上进行穷举搜索，每次根据激励相容推导的 e* 计算代理人效用、检查参与约束，然后计算主人的利润 π。
记录其中利润最大的 (w*, b*) 及对应的 e*、U_A(e*)。
main 函数中提供了控制台交互示例，便于在命令行下输入相应参数，观察不同设置对结果的影响。
如需更高精度或更灵活的搜索方式，可将 (w, b) 改为更小的步长，或使用数值优化/解析方法。
若要扩展到不确定产出、代理人风险厌恶甚至多任务委托代理等场景，请在此基础上进一步调整模型和算法。
"""

import numpy as np

def agent_best_response(b, cost_factor):
    # 计算代理人的最优努力水平
    # b: 奖金系数
    # cost_factor: 努力成本系数
    # 返回：e* = b/(2c)（当b>0时）
    if b <= 0:
        return 0.0
    else:
        return b / (2.0 * cost_factor)

def agent_utility(w, b, e, cost_factor):
    # 计算代理人效用
    # U_A = w + b*e - c*e^2
    # w: 固定工资
    # b: 奖金系数
    # e: 努力水平
    return w + b * e - cost_factor * (e**2)

def principal_profit(P, w, b, e):
    # 计算委托人（雇主）利润
    # π = P*e - (w + b*e)
    # P: 市场价格
    return P * e - (w + b * e)

def find_optimal_contract(cost_factor, outside_option, price,
                          w_min, w_max, w_step,
                          b_min, b_max, b_step):
    """
    给定参数后，通过穷举搜索(w, b)以最大化主人利润，
    需分别检查激励相容与参与约束:
      - 激励相容(IC): 代理人最优努力 e*(b, c)
      - 参与约束(PC): U_A(e*) >= outside_option
    返回: (w*, b*, max_profit, best_e, best_utility_A)
    """
    best_w = 0.0
    best_b = 0.0
    best_profit = -1e15
    best_e = 0.0
    best_utility_A = 0.0

    # 生成离散搜索网格
    w_candidates = np.arange(w_min, w_max + w_step, w_step)
    b_candidates = np.arange(b_min, b_max + b_step, b_step)

    for w in w_candidates:
        for b in b_candidates:
            # 根据 b 和 cost_factor 算出代理人的最优努力 e*
            e_star = agent_best_response(b, cost_factor)
            # 代理人最优努力下的效用
            u_agent = agent_utility(w, b, e_star, cost_factor)

            # 参与约束(PC)：u_agent >= outside_option
            if u_agent < outside_option:
                # 不满足参与约束，代理人拒绝签约
                continue

            # 若满足参与约束，再计算主人的利润
            pi = principal_profit(price, w, b, e_star)

            # 记录最优结果
            if pi > best_profit:
                best_profit = pi
                best_w = w
                best_b = b
                best_e = e_star
                best_utility_A = u_agent

    return best_w, best_b, best_profit, best_e, best_utility_A

def main():
    """
    主函数：控制台交互，输入参数后运行搜索最优合约
    """
    print("===== 委托代理：激励相容(IC) + 参与约束(PC) 简化模型示例 =====")
    print("请依次输入以下参数（若不确定可按回车使用示例默认值）:")

    # 1. 读取参数（带默认值）
    try:
        cost_factor = float(input("1. 代理人努力成本系数 c (默认 0.1): ") or 0.1)
        outside_option = float(input("2. 代理人外部机会效用 U0 (默认 0.0): ") or 0.0)
        price = float(input("3. 产出市场价格 P (默认 2.0): ") or 2.0)
        w_min = float(input("4. 固定工资 w 的搜索下限 (默认 0): ") or 0.0)
        w_max = float(input("5. 固定工资 w 的搜索上限 (默认 50): ") or 50.0)
        w_step = float(input("6. 固定工资 w 的步长 (默认 5): ") or 5.0)
        b_min = float(input("7. 绩效奖金 b 的搜索下限 (默认 0): ") or 0.0)
        b_max = float(input("8. 绩效奖金 b 的搜索上限 (默认 10): ") or 10.0)
        b_step = float(input("9. 绩效奖金 b 的步长 (默认 1): ") or 1.0)
    except ValueError:
        print("输入数值格式错误，将使用默认参数进行演示。")
        cost_factor = 0.1
        outside_option = 0.0
        price = 2.0
        w_min, w_max, w_step = 0.0, 50.0, 5.0
        b_min, b_max, b_step = 0.0, 10.0, 1.0

    print("\n开始搜索最优合约...")

    w_star, b_star, pi_star, e_star, u_agent_star = find_optimal_contract(
        cost_factor, outside_option, price,
        w_min, w_max, w_step,
        b_min, b_max, b_step
    )

    # 2. 显示搜索结果
    if pi_star < -1e14:
        print("\n【搜索完成】在当前参数下，未找到满足参与约束(PC)的可行合约。")
    else:
        print("\n【搜索完成】最优合约(满足IC与PC)：")
        print(f"  - w* = {w_star:.4f}")
        print(f"  - b* = {b_star:.4f}")
        print(f"  - 代理人最优努力 e* = {e_star:.4f}")
        print(f"  - 代理人效用 U_A(e*) = {u_agent_star:.4f} (需 >= {outside_option})")
        print(f"  - 主人利润 π* = {pi_star:.4f}")

    print("\n===== 程序结束 =====")

if __name__ == "__main__":
    main()