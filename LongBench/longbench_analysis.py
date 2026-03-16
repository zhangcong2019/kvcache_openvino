import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取数据
df = pd.read_csv('benchmark_results.csv')

print("=" * 60)
print("LongBench Benchmark Analysis")
print("=" * 60)

# 数据概览
print("\n--- Data Overview ---")
print(df.to_string(index=False))

# 按 Framework 和 Max_input_token 分组
print("\n--- Performance by Framework and Max Input Token ---")
summary = df.groupby(['Framework', 'Max_input_token']).agg({
    'Overall': 'mean',
    'Easy': 'mean',
    'Hard': 'mean',
    'Short': 'mean',
    'Medium': 'mean',
    'Long': 'mean'
}).reset_index()
print(summary.to_string(index=False))

# 10k 数据对比
print("\n--- 10k: Framework Comparison ---")
df_10k = df[df['Max_input_token'] == '10k'].sort_values('Overall', ascending=False)
print(df_10k[['Framework', 'Overall', 'Easy', 'Hard', 'Short', 'Medium', 'Long']].to_string(index=False))

# 30k 数据对比
print("\n--- 30k: Framework Comparison ---")
df_30k = df[df['Max_input_token'] == '30k'].sort_values('Overall', ascending=False)
print(df_30k[['Framework', 'Overall', 'Easy', 'Hard', 'Short', 'Medium', 'Long']].to_string(index=False))

# vllm 10k vs 30k 对比
print("\n--- vllm: 10k vs 30k ---")
vllm_10k = df[(df['Framework']=='vllm') & (df['Max_input_token']=='10k')].iloc[0]
vllm_30k = df[(df['Framework']=='vllm') & (df['Max_input_token']=='30k')].iloc[0]
for col in ['Overall', 'Easy', 'Hard', 'Short', 'Medium', 'Long']:
    diff = vllm_30k[col] - vllm_10k[col]
    print(f"  {col}: 10k={vllm_10k[col]}, 30k={vllm_30k[col]}, diff={diff:+.1f}")

# ovgenai 10k vs 30k 对比
print("\n--- ovgenai: 10k vs 30k ---")
ovgenai_10k = df[(df['Framework']=='ovgenai') & (df['Max_input_token']=='10k')].iloc[0]
ovgenai_30k = df[(df['Framework']=='ovgenai') & (df['Max_input_token']=='30k')].iloc[0]
for col in ['Overall', 'Easy', 'Hard', 'Short', 'Medium', 'Long']:
    diff = ovgenai_30k[col] - ovgenai_10k[col]
    print(f"  {col}: 10k={ovgenai_10k[col]}, 30k={ovgenai_30k[col]}, diff={diff:+.1f}")

# ========== 绘图 ==========
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 图1: 10k 各框架对比
ax1 = axes[0]
x = np.arange(6)
width = 0.15
metrics = ['Overall', 'Easy', 'Hard', 'Short', 'Medium', 'Long']
frameworks_10k = ['vllm', 'ovgenai', 'sparsity', 'eviction', 'kvcrush']
colors = ['steelblue', 'coral', 'green', 'purple', 'orange']

for i, fw in enumerate(frameworks_10k):
    row = df[(df['Framework']==fw) & (df['Max_input_token']=='10k')]
    if len(row) > 0:
        values = [row[m].values[0] for m in metrics]
        ax1.bar(x + i*width, values, width, label=fw, color=colors[i])

ax1.set_xlabel('Metrics', fontsize=12)
ax1.set_ylabel('Score', fontsize=12)
ax1.set_title('10k: Framework Comparison', fontsize=14)
ax1.set_xticks(x + width*2)
ax1.set_xticklabels(metrics)
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 图2: 30k 各框架对比
ax2 = axes[1]
frameworks_30k = ['vllm', 'ovgenai', 'sparsity']
for i, fw in enumerate(frameworks_30k):
    row = df[(df['Framework']==fw) & (df['Max_input_token']=='30k')]
    if len(row) > 0:
        values = [row[m].values[0] for m in metrics]
        ax2.bar(x + i*width, values, width, label=fw, color=colors[i])

ax2.set_xlabel('Metrics', fontsize=12)
ax2.set_ylabel('Score', fontsize=12)
ax2.set_title('30k: Framework Comparison', fontsize=14)
ax2.set_xticks(x + width)
ax2.set_xticklabels(metrics)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('longbench_comparison.png', dpi=150)
print("\n\nChart saved: longbench_comparison.png")

# ========== Overall Score 对比图 ==========
fig2, ax3 = plt.subplots(figsize=(10, 6))

# 准备数据
frameworks = ['vllm', 'ovgenai', 'sparsity', 'eviction', 'kvcrush']
x = np.arange(len(frameworks))
width = 0.35

overall_10k = []
overall_30k = []
for fw in frameworks:
    row_10k = df[(df['Framework']==fw) & (df['Max_input_token']=='10k')]
    row_30k = df[(df['Framework']==fw) & (df['Max_input_token']=='30k')]
    overall_10k.append(row_10k['Overall'].values[0] if len(row_10k) > 0 else 0)
    overall_30k.append(row_30k['Overall'].values[0] if len(row_30k) > 0 else 0)

ax3.bar(x - width/2, overall_10k, width, label='10k', color='steelblue')
ax3.bar(x + width/2, overall_30k, width, label='30k', color='coral')

ax3.set_xlabel('Framework', fontsize=12)
ax3.set_ylabel('Overall Score', fontsize=12)
ax3.set_title('Overall Score: 10k vs 30k', fontsize=14)
ax3.set_xticks(x)
ax3.set_xticklabels(frameworks)
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# 添加数值标签
for i, (v10, v30) in enumerate(zip(overall_10k, overall_30k)):
    ax3.text(i - width/2, v10 + 0.3, f'{v10}', ha='center', va='bottom', fontsize=10)
    if v30 > 0:
        ax3.text(i + width/2, v30 + 0.3, f'{v30}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('longbench_overall.png', dpi=150)
print("Chart saved: longbench_overall.png")

# ========== 难度维度分析 ==========
fig3, ax4 = plt.subplots(figsize=(10, 6))

# Easy vs Hard 对比
frameworks_all = ['vllm', 'ovgenai', 'sparsity', 'eviction', 'kvcrush']
x = np.arange(len(frameworks_all))
width = 0.35

easy_scores = []
hard_scores = []
for fw in frameworks_all:
    row = df[(df['Framework']==fw) & (df['Max_input_token']=='10k')]
    if len(row) > 0:
        easy_scores.append(row['Easy'].values[0])
        hard_scores.append(row['Hard'].values[0])
    else:
        easy_scores.append(0)
        hard_scores.append(0)

ax4.bar(x - width/2, easy_scores, width, label='Easy', color='green', alpha=0.7)
ax4.bar(x + width/2, hard_scores, width, label='Hard', color='red', alpha=0.7)

ax4.set_xlabel('Framework', fontsize=12)
ax4.set_ylabel('Score', fontsize=12)
ax4.set_title('Easy vs Hard (10k)', fontsize=14)
ax4.set_xticks(x)
ax4.set_xticklabels(frameworks_all)
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('longbench_difficulty.png', dpi=150)
print("Chart saved: longbench_difficulty.png")

# ========== 总结 ==========
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("""
Key Findings:

1. 10k Overall 排名:
   - eviction = kvcrush = 28.4 (最高)
   - ovgenai = 28.2
   - vllm = 27.6
   - sparsity = 25.2 (最低)

2. 30k Overall 排名:
   - ovgenai = 30 (最高)
   - vllm = 29
   - sparsity = 26.4

3. 10k vs 30k 变化:
   - vllm: 27.6 -> 29 (+1.4)
   - ovgenai: 28.2 -> 30 (+1.8)
   - 两者在 30k 都表现更好

4. Easy vs Hard:
   - 所有框架 Easy 都比 Hard 高 4-8 分
   - eviction/kvcrush 在 Easy 上表现最好

5. 结论:
   - ovgenai 在 30k 场景最优
   - eviction/kvcrush 在 10k 场景最优
   - sparsity 整体表现最差
   - vllm 作为基线表现稳定
""")
