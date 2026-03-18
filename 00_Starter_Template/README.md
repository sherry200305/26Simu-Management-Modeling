# 🪐 Project 1: Uniswap V3 State Machine (Starter Template)

> 欢迎来到你的个人量化创业车间。这是你构建商业帝国的地基。

## 🎯 你的任务 (Your Mission)
1. 把你在 `02_Lectures` 和 `04_Resources` 里学到的底层物理知识（Q64.96 定点数算法）移植进 `src/simulator.py` 中。
2. 疯狂地在 `tests/test_invariants.py` 中写能够把系统搞死（触发底板击穿）的测试断言。
3. 按照 `spec.yaml` 填写你做实验的初始假设条件。

## 🚀 启动指北 (How to Run)

**1. 布置环境 (Install Environment)**
```bash
python -m pip install -r requirements.txt
```

**2. 呼叫日常断言法官 (Run CI Tests)**
在推送到 Github 之前，请务必在本地确认测试全绿：
```bash
pytest tests/ -v
```

**3. 启动流水线大循环 (Run Experiments)**
```bash
python experiments/run_all.py
```

## 📝 CEO Memo / 分析报告 (请在这里写下你的发现)

*(在此处删去占位符，说明在极限断言测试和你的策略推演后：V3 单池在极度失衡情况下的资金死亡滑点在哪个阈值？)*
