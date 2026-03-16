import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取数据
df = pd.read_csv('benchmark_results.csv')

# 按策略和prompt_tokens分组，计算平均值
summary = df.groupby(['name', 'prompt_tokens']).agg({
    'ttft_ms': 'mean',
    'tpot_ms': 'mean',
    'max_num_batched_tokens': 'mean'
}).reset_index()

print("=== 各策略按 prompt_tokens 分组统计 ===")
print(summary.to_string(index=False))

# 透视表：对比 TTFT
ttft_pivot = df.pivot_table(values='ttft_ms', index='prompt_tokens', columns='name')
print("\n=== TTFT (ms) 对比 ===")
print(ttft_pivot.to_string())

# 透视表：对比 TPOT
tpot_pivot = df.pivot_table(values='tpot_ms', index='prompt_tokens', columns='name')
print("\n=== TPOT (ms) 对比 ===")
print(tpot_pivot.to_string())

# 找出最优策略
print("\n=== 各 prompt_tokens 下的最优策略 ===")
for pt in sorted(df['prompt_tokens'].unique()):
    subset = df[df['prompt_tokens'] == pt]
    best_ttft = subset.loc[subset['ttft_ms'].idxmin(), 'name']
    best_tpot = subset.loc[subset['tpot_ms'].idxmin(), 'name']
    print(f"prompt_tokens={pt}: TTFT最优={best_ttft}, TPOT最优={best_tpot}")

# ========== 绘图 ==========
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 图1: TTFT 对比
ax1 = axes[0]
for name in df['name'].unique():
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    ax1.plot(subset['prompt_tokens'], subset['ttft_ms'], marker='o', label=name, linewidth=2, markersize=8)
ax1.set_xlabel('Prompt Tokens', fontsize=12)
ax1.set_ylabel('TTFT (ms)', fontsize=12)
ax1.set_title('TTFT Scalability (with linear reference)', fontsize=14)
ax1.legend()
ax1.set_xticks(sorted(df['prompt_tokens'].unique()))

# 图2: TPOT 对比
ax2 = axes[1]
for name in df['name'].unique():
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    ax2.plot(subset['prompt_tokens'], subset['tpot_ms'], marker='s', label=name, linewidth=2, markersize=8)
ax2.set_xlabel('Prompt Tokens', fontsize=12)
ax2.set_ylabel('TPOT (ms)', fontsize=12)
ax2.set_title('TPOT vs Prompt Tokens by Strategy', fontsize=14)
ax2.legend()
ax2.set_xticks(sorted(df['prompt_tokens'].unique()))

plt.tight_layout()
plt.savefig('strategy_comparison.png', dpi=150)
print("\n图表已保存: strategy_comparison.png")

# ========== 柱状图对比 ==========
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

prompt_tokens_list = sorted(df['prompt_tokens'].unique())
x = np.arange(len(prompt_tokens_list))
width = 0.2

# TTFT 柱状图
ax3 = axes2[0]
for i, name in enumerate(['ovgenai', 'sparse', 'eviction', 'kvcrush']):
    values = [df[(df['prompt_tokens']==pt) & (df['name']==name)]['ttft_ms'].values[0] 
              if len(df[(df['prompt_tokens']==pt) & (df['name']==name)]) > 0 else 0 
              for pt in prompt_tokens_list]
    ax3.bar(x + i*width, values, width, label=name)
ax3.set_xlabel('Prompt Tokens', fontsize=12)
ax3.set_ylabel('TTFT (ms)', fontsize=12)
ax3.set_title('TTFT Comparison', fontsize=14)
ax3.set_xticks(x + width*1.5)
ax3.set_xticklabels(prompt_tokens_list)
ax3.legend()

# TPOT 柱状图
ax4 = axes2[1]
for i, name in enumerate(['ovgenai', 'sparse', 'eviction', 'kvcrush']):
    values = [df[(df['prompt_tokens']==pt) & (df['name']==name)]['tpot_ms'].values[0] 
              if len(df[(df['prompt_tokens']==pt) & (df['name']==name)]) > 0 else 0 
              for pt in prompt_tokens_list]
    ax4.bar(x + i*width, values, width, label=name)
ax4.set_xlabel('Prompt Tokens', fontsize=12)
ax4.set_ylabel('TPOT (ms)', fontsize=12)
ax4.set_title('TPOT Comparison', fontsize=14)
ax4.set_xticks(x + width*1.5)
ax4.set_xticklabels(prompt_tokens_list)
ax4.legend()

plt.tight_layout()
plt.savefig('strategy_bar_chart.png', dpi=150)
print("图表已保存: strategy_bar_chart.png")

# ========== 扩展性分析 ==========
print("\n=== 扩展性分析 (TTFT 增长倍数) ===")
base_ttft = {}
for name in df['name'].unique():
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    if 5000 in subset['prompt_tokens'].values:
        base = subset[subset['prompt_tokens']==5000]['ttft_ms'].values[0]
        base_ttft[name] = base
        print(f"{name}: 5k={base:.2f}ms", end=" ")
        for pt in [10000, 20000, 30000]:
            if pt in subset['prompt_tokens'].values:
                val = subset[subset['prompt_tokens']==pt]['ttft_ms'].values[0]
                ratio = val / base
                print(f" -> {pt}={val:.2f}ms ({ratio:.2f}x)", end=" ")
        print()

print("\n分析完成!")
