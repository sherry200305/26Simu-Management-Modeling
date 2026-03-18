"""
🚨 核心原则 (Core Rule):
在这个文件里，严禁使用 float 或者 decimal.Decimal 来表示价格或流动性。
必须严格使用大整数 (BigInt - Python内置的 int) 和按位截断 (//) 来模拟 Solidity 物理法则。

请参考 04_Resources/Project1_V3_Math_CheatSheet.md 的公式来写你的代码。
"""

# V3 魔法常数 Q96
Q96 = 2**96

class V3PoolStateMachine:
    def __init__(self, initial_sqrtp_x96: int, initial_liquidity: int):
        """
        初始化池子状态
        """
        # --- [CEO 的红线] ---
        # 你知道这下面应该定义哪些变量吗？比如 fee_growth_global, current_tick 等。
        self.sqrtp_current_x96 = initial_sqrtp_x96
        self.liquidity = initial_liquidity
        
        # TODO: 初始化 Ticks 字典和手续费累计值
        pass

    def swap_exact_input(self, zero_for_one: bool, amount_in: int) -> int:
        """
        用户砸盘主函数。
        :param zero_for_one: True 代表卖 Token0 换 Token1，False 则反之
        :param amount_in: 砸入的数量 (整数 Wei)
        :return: 换出的数量 amount_out (整数 Wei)
        """
        # TODO: 你的核心战场
        # 1. 扣除 0.3% 手续费 (把它加在 fee_growth_global 里)
        # 2. 跟据 Q64.96 公式推导价格下跌/上涨
        # 3. 如果价格跌破了 current_tick，要怎么跨区间？
        
        # 这是一个让你能通过第一个 Assert 的占位符：
        if amount_in == 0:
            return 0
            
        raise NotImplementedError("CTO 还没把 V3 的数学翻译完！")
