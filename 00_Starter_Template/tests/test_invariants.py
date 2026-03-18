import pytest
import os
import sys

# 把 src 目录加进环境变量，让 pytest 找得到你的代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from simulator import V3PoolStateMachine

def test_initial_zero_swap_invariant():
    """
    【物理断言第一课】
    如果一个用户向池子砸入 0 个代币，池子的价格必须丝毫未动，且换出的代币必须为 0。
    """
    # 假设池子初始价格是 2500 (对应转换为以下的 Q96 长整数)
    initial_sqrtp = 3961408125713216879677197516800
    L = 10**18
    
    pool = V3PoolStateMachine(initial_sqrtp, L)
    
    # 执行 0 金额交易
    amount_out = pool.swap_exact_input(zero_for_one=True, amount_in=0)
    
    # [红线 1]：宇宙什么都没发生，当然换不出钱
    assert amount_out == 0, "致命错误：拿 0 块钱换出了钱！"
    
    # [红线 2]：池子底层价格刻度不能有哪怕 1 的偏移
    assert pool.sqrtp_current_x96 == initial_sqrtp, "致命错误：无交易导致大盘价格偏移！"

# TODO: 请自行添加更多的断言！比如：
# - Swap 之后的 X * Y 是否总是 >= K ?
# - 跨区间击穿时的手续费累计是否准确无误漂移？
