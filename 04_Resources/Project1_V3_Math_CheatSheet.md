# 🧮 Project 1 军火库：V3 核心数学与 Python 映射作弊纸 (Math Cheat Sheet)

## 📌 警示：为什么大模型写给你的 V3 数学公式一跑就崩？

当你在做 Project 1 (Uniswap V3 状态机仿真) 时，你一定会去问 ChatGPT 或 Claude：“请用 Python 帮我写一个 Uniswap V3 的池子内交换公式”。
它们通常会非常贴心地丢给你这样一段代码：
```python
# ❌ 典型的 AI 幻觉和“商科式”仿真代码
import math
from decimal import Decimal

# 假设价格 P = 2000
price = Decimal('2000.0')
sqrt_price = price.sqrt()

# 某人投入了 1 个 ETH (dx = 1)，计算能换出多少 USDC (dy)
dy = dx * current_liquidity / sqrt_price # ... 后面跟一堆浮点数运算
```
**千万不要用这种代码去交作业！你的 CI 极压测试会死得非常惨。**

### 这是致命的降维错误 (The Decimal Hallucination)：
以太坊虚拟机（EVM）以及 Solidity 根本**不懂什么是小数点**。以太坊世界的物理法则是：世界上只有最大长达 256 位的二进制大整数 (`uint256`)。
为了表示 $0.5$ 这个概念，V3 使用了一种叫做 **$Q64.96$ 定点数** 的黑科技：它把整数强行向右平移 96个二进制位（相当于乘上 $2^{96}$）。
如果你的底层计算环境图省事用了 `decimal.Decimal` 甚至系统原生浮点数 `float` 去模拟交易，在极细微的交叉流动性计算中，Python 的十进制四舍五入规则会和 Solidity 中苛刻的**整数截断取整（Truncation）**产生 $10^{-18}$ 级别的漂移差异。
在动辄千万美金的 TVL 面前，这 $10^{-18}$ 的缝隙，就会演变成大模型生造出来的 **“不存在的无风险套利提款机”**。你的模型会判定策略 A 赚钱，但实际上丢到链上一秒钟就会被黑客清算成渣。

---

## ⚔️ 唯一真理：用 Python 原生 `int` 像素级还原 EVM 物理法则

作为全球极少数原生**自带无限精度大整数（Arbitrary-precision BigInt）**的语言，Python 的内建原生 `int` 无缝等价于以太坊的 `uint256`。

**二阶建模法则：** 
**所有的底层状态运算（算账），强制使用 `int` 与按位移运算。`Decimal` 这把牛刀必须且只能用来在图表中把天书翻译给 CEO 看。**

下面是你在撰写 `src/simulator.py` 时，**必须直接复制/参考**的几个核心防弹公式：

### 1. 魔法数字：$2^{96}$ 到底是个啥？
在代码文件的最开头，必须定义好这个将主宰你 8 周命运的宏：
```python
# 魔法常数 2^96，用来把普通数字变形成 Q64.96 定点数
Q96 = 2**96

# 你可以先感受一下它的庞大：
# Q96 = 79228162514264337593543950336
```

### 2. [会议室层] -> [机房层]：把人类价格转换为 V3 状态机价格
作为上帝视角的你，设定了开盘价 $P = 2500$ USDC/ETH。怎么把它塞进系统？
$$ \text{sqrtPriceX96} = \sqrt{P} \times 2^{96} $$

```python
import math

def price_to_sqrtpx96(p: float) -> int:
    """
    仅在初始化（如设置起始环境）时调用此函数。
    把人类世界直观的价格 P 转化为底层的 uint256 状态变量。
    """
    return int(math.sqrt(p) * Q96)

# 测试：
# sqrtp_x96 = price_to_sqrtpx96(2500)
# >>> 3961408125713216879677197516800  <-- Это才是存在系统里的真实物理长相！
```

### 3. [机房层] -> [会议室层]：把天书解释给 CEO
在 `metrics.csv` 落表或使用 `matplotlib` 画图时，你需要把那一长串天书转回人话：
$$ P = \left(\frac{\text{sqrtPriceX96}}{2^{96}}\right)^2 $$

```python
from decimal import Decimal, getcontext
getcontext().prec = 30 # 给 CEO 出具报告时，30位精度足够了

def sqrtpx96_to_price(sqrtpx96: int) -> Decimal:
    """
    只在最后收集数据（DataCollector）或可视化时使用！
    """
    # 先做除法，再平方
    ratio = Decimal(sqrtpx96) / Decimal(Q96)
    return ratio ** 2
```

### 4. 🧮 核心战役方程式：根据买单 $\Delta x$ 计算价格移动和能拿回多少货 $\Delta y$
*警告：在 V3 的单一价格区间内计算 Swap，不准使用乘法和普通的除法，必须使用按位推导！*
假设某个用户用市价砸盘卖出了 `amount_in` 数量的代币 $X$。此刻池子中当前的流动性是 `L`，当前价格是 `sqrtp_current_x96`。

**公式推导（请核对 V3 白皮书 Eq. 6.13 与 6.15）：**
卖出 $X$ 意味着 $X$ 的储量增加，价格将下跌（$\sqrt{P}$ 变小）。
新的价格边界为：$$ \sqrt{P_{next}} = \frac{\sqrt{P} \cdot L}{\Delta X \cdot \sqrt{P} + L} $$

**把它翻译成 Python 里的 EVM 等效代码（必须是全整数碰撞）：**
```python
def get_next_sqrt_price_from_amount0_in(sqrtp_current_x96: int, liquidity: int, amount_in: int) -> int:
    """
    精确模拟 Solidity 底下的整数除法，找出砸盘后秒针停在哪个价格。
    """
    # 按照公式展开时，所有分子分母都要带着 Q96 漂移
    numerator1 = liquidity << 96 # 等效于 liquidity * 2**96
    numerator2 = sqrtp_current_x96
    
    # 模拟 Solidity 的底板除法（// 向零截断）以确保不产生幻觉金额
    denominator = (liquidity << 96) + (amount_in * sqrtp_current_x96)
    
    # 如果分母算出来是个不可理喻的数，直接抛出红线（这极压测试就起作用了）
    assert denominator > 0, "INVARIANT BROKEN: Math Underflow"
    
    # Solidity 中的机制： 先乘后除保证精度不提前丢失
    next_sqrtp_x96 = (numerator1 * numerator2) // denominator
    return next_sqrtp_x96
```

---

## 💡 Sprint 1 生存终极建议
当你在做 Project 1 以及极压测试（`test_invariants.py`）时，**所有的 Assert（断言），必须去 Assert 你通过上面这些纯整数函数算出来的结果**，千万不要把两边转成 `float` 去对比大小，那毫无技术含金量。

你的红线代码应该是这样的铁血面孔：
```python
def test_buy_zero_should_not_move_price():
    initial_sqrtp = 3961408125713216879677197516800
    liquidity = 10**18
    # 极压测试：输入 0 个币砸盘
    next_price = get_next_sqrt_price_from_amount0_in(initial_sqrtp, liquidity, 0)
    
    # 物理断言：在底层整数级，世界必须未动分毫
    assert next_price == initial_sqrtp
```

有了这份作弊纸，大模型再写出 `math.sqrt()` 或 `float(P)` 这种弱智代码时，你作为 CEO 就拥有了把它的代码打回重写的生杀大权。祝武运昌隆！
