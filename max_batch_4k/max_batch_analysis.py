import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取数据
df = pd.read_csv('benchmark_results.csv')

print("=" * 60)
print("Max Num Batched Tokens Impact Analysis")
print("=" * 60)

# 数据概览
print("\n--- Data Overview ---")
print(df.to_string(index=False))

# 按策略和max_num_batched_tokens分组
print("\n--- Performance by Strategy and max_num_batched_tokens ---")
summary = df.groupby(['model', 'max_num_batched_tokens']).agg({
    'ttft_ms': 'mean',
    'tpot_ms': 'mean'
}).reset_index()
print(summary.to_string(index=False))

# 变化分析
print("\n--- Impact: max_num_batched_tokens 变化 ---")
for model in sorted(df['model'].unique()):
    print(f"\n{model}:")
    for mb in sorted(df['max_num_batched_tokens'].unique()):
        row = df[(df['model']==model) & (df['max_num_batched_tokens']==mb)]
        if len(row) > 0:
            print(f"  max_batch={mb:>4}: TTFT={row['ttft_ms'].values[0]:>10.2f}ms, TPOT={row['tpot_ms'].values[0]:>5.2f}ms")

# 基准对比 (以 max_batch=1024 为基准)
print("\n--- 相对变化 (以 max_batch=1024 为基准) ---")
base_ttft = {}
for model in df['model'].unique():
    row = df[(df['model']==model) & (df['max_num_batched_tokens']==1024)]
    if len(row) > 0:
        base_ttft[model] = row['ttft_ms'].values[0]

for model in sorted(df['model'].unique()):
    print(f"\n{model} (基准 TTFT@1024 = {base_ttft.get(model, 0):.2f}ms):")
    for mb in sorted(df['max_num_batched_tokens'].unique()):
        row = df[(df['model']==model) & (df['max_num_batched_tokens']==mb)]
        if len(row) > 0:
            ttft = row['ttft_ms'].values[0]
            tpot = row['tpot_ms'].values[0]
            if mb != 1024 and model in base_ttft:
                ttft_ratio = ttft / base_ttft[model]
                print(f"  max_batch={mb:>4}: TTFT={ttft:>10.2f}ms ({ttft_ratio:.2f}x), TPOT={tpot:>5.2f}ms")
            else:
                print(f"  max_batch={mb:>4}: TTFT={ttft:>10.2f}ms (基准), TPOT={tpot:>5.2f}ms")

# ========== 绘图 ==========
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 图1: TTFT 对比
x = np.arange(len(df['max_num_batched_tokens'].unique()))
width = 0.2
batch_vals = sorted(df['max_num_batched_tokens'].unique())

models = ['ovgenai', 'sparse', 'eviction', 'kvcrush']
colors = ['steelblue', 'coral', 'green', 'purple']

ax1 = axes[0]
for i, model in enumerate(models):
    values = []
    for mb in batch_vals:
        val = df[(df['model']==model) & (df['max_num_batched_tokens']==mb)]['ttft_ms'].values
        values.append(val[0] if len(val) > 0 else 0)
    ax1.bar(x + i*width, values, width, label=model, color=colors[i])

ax1.set_xlabel('max_num_batched_tokens', fontsize=12)
ax1.set_ylabel('TTFT (ms)', fontsize=12)
ax1.set_title('TTFT vs max_num_batched_tokens', fontsize=14)
ax1.set_xticks(x + width*1.5)
ax1.set_xticklabels(batch_vals)
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 图2: TPOT 对比
ax2 = axes[1]
for i, model in enumerate(models):
    values = []
    for mb in batch_vals:
        val = df[(df['model']==model) & (df['max_num_batched_tokens']==mb)]['tpot_ms'].values
        values.append(val[0] if len(val) > 0 else 0)
    ax2.bar(x + i*width, values, width, label=model, color=colors[i])

ax2.set_xlabel('max_num_batched_tokens', fontsize=12)
ax2.set_ylabel('TPOT (ms)', fontsize=12)
ax2.set_title('TPOT vs max_num_batched_tokens', fontsize=14)
ax2.set_xticks(x + width*1.5)
ax2.set_xticklabels(batch_vals)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('max_batch_impact.png', dpi=150)
print("\n\nChart saved: max_batch_impact.png")

# ========== 单独看TTFT趋势 ==========
fig2, ax3 = plt.subplots(figsize=(10, 6))

for model in models:
    subset = df[df['model']==model].sort_values('max_num_batched_tokens')
    ax3.plot(subset['max_num_batched_tokens'], subset['ttft_ms'], marker='o', label=model, linewidth=2, markersize=10)

ax3.set_xlabel('max_num_batched_tokens', fontsize=12)
ax3.set_ylabel('TTFT (ms)', fontsize=12)
ax3.set_title('TTFT Trend: max_num_batched_tokens Impact', fontsize=14)
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xscale('log')

plt.tight_layout()
plt.savefig('max_batch_ttft_trend.png', dpi=150)
print("Chart saved: max_batch_ttft_trend.png")

# ========== 总结 ==========
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("""
Key Findings:

1. max_num_batched_tokens=4 时 TTFT 急剧增加:
   - 所有策略在 max_batch=4 时 TTFT 显著增加
   - 相比 max_batch=1024，增加了几十倍
   
2. max_num_batched_tokens=4096 时 TTFT 减少:
   - 相比 max_batch=1024，TTFT 有明显下降
   - sparse: 1379.67 -> 1267.72ms (约8%下降)
   - ovgenai: 2479.83 -> 2256.68ms (约9%下降)

3. TPOT 基本不变:
   - max_num_batched_tokens 变化对 TPOT 影响极小
   - 所有策略的 TPOT 保持在 19-25ms 范围内

4. 结论:
   - 较大的 max_num_batched_tokens 有利于降低 TTFT
   - 过小的 max_num_batched_tokens 会导致 TTFT 急剧增加
   - TPOT 与 max_num_batched_tokens 无关
""")
