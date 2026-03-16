import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取数据
df = pd.read_csv('benchmark_results.csv')

# ========== TTFT vs TPOT 权衡分析 ==========
print("=" * 60)
print("TTFT vs TPOT 权衡分析")
print("=" * 60)

# 筛选有完整数据的策略
strategies = df['name'].unique()

# 创建权衡分析表
print("\n--- 各策略 TTFT vs TPOT 对比 ---")
for name in sorted(strategies):
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    avg_ttft = subset['ttft_ms'].mean()
    avg_tpot = subset['tpot_ms'].min()  # 取最优TPOT
    ratio = avg_ttft / avg_tpot
    print(f"{name:>10}: 平均TTFT={avg_ttft:>8.2f}ms, 最优TPOT={avg_tpot:>5.2f}ms, TTFT/TPOT={ratio:.1f}")

# ========== 场景分析 ==========
print("\n" + "=" * 60)
print("场景分析")
print("=" * 60)

# 实时交互场景 (看重TTFT)
print("\n【实时交互场景】TTFT 排名（越小越好）:")
for pt in sorted(df['prompt_tokens'].unique()):
    subset = df[df['prompt_tokens'] == pt]
    if len(subset) > 0:
        ranked = subset.sort_values('ttft_ms')
        print(f"  prompt={pt}: " + " > ".join([f"{r['name']}({r['ttft_ms']:.0f}ms)" for _, r in ranked.iterrows()]))

# 批量生成场景 (看重TPOT)
print("\n【批量生成场景】TPOT 排名（越小越好）:")
for pt in sorted(df['prompt_tokens'].unique()):
    subset = df[df['prompt_tokens'] == pt]
    if len(subset) > 0:
        ranked = subset.sort_values('tpot_ms')
        print(f"  prompt={pt}: " + " > ".join([f"{r['name']}({r['tpot_ms']:.1f}ms)" for _, r in ranked.iterrows()]))

# ========== 综合评分 ==========
print("\n" + "=" * 60)
print("综合评分 (TTFT权重 vs TPOT权重)")
print("=" * 60)

# 不同场景的权重
scenarios = {
    "实时交互 (TTFT:80%, TPOT:20%)": (0.8, 0.2),
    "均衡 (TTFT:50%, TPOT:50%)": (0.5, 0.5),
    "批量生成 (TTFT:20%, TPOT:80%)": (0.2, 0.8),
}

for scenario, (w_ttft, w_tpot) in scenarios.items():
    print(f"\n{scenario}:")
    # 按 prompt_tokens 分组计算
    results = []
    for pt in sorted(df['prompt_tokens'].unique()):
        subset = df[df['prompt_tokens'] == pt]
        if len(subset) > 0:
            # 归一化分数
            min_ttft = subset['ttft_ms'].min()
            max_ttft = subset['ttft_ms'].max()
            min_tpot = subset['tpot_ms'].min()
            max_tpot = subset['tpot_ms'].max()
            
            for _, row in subset.iterrows():
                ttft_score = (max_ttft - row['ttft_ms']) / (max_ttft - min_ttft) if max_ttft > min_ttft else 1.0
                tpot_score = (max_tpot - row['tpot_ms']) / (max_tpot - min_tpot) if max_tpot > min_tpot else 1.0
                total_score = w_ttft * ttft_score + w_tpot * tpot_score
                results.append({
                    'name': row['name'],
                    'prompt_tokens': pt,
                    'score': total_score,
                    'ttft_ms': row['ttft_ms'],
                    'tpot_ms': row['tpot_ms']
                })
    
    results_df = pd.DataFrame(results)
    for pt in sorted(results_df['prompt_tokens'].unique()):
        pt_results = results_df[results_df['prompt_tokens'] == pt].sort_values('score', ascending=False)
        print(f"  prompt={pt}: " + " > ".join([f"{r['name']}({r['score']:.2f})" for _, r in pt_results.iterrows()]))

# ========== 绘图 ==========
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 图1: TTFT vs TPOT 散点图
ax1 = axes[0, 0]
colors = {'ovgenai': 'blue', 'sparse': 'green', 'eviction': 'red', 'kvcrush': 'orange'}
for name in strategies:
    subset = df[df['name'] == name]
    ax1.scatter(subset['ttft_ms'], subset['tpot_ms'], label=name, s=100, alpha=0.7, c=colors.get(name, 'gray'))
ax1.set_xlabel('TTFT (ms)', fontsize=12)
ax1.set_ylabel('TPOT (ms)', fontsize=12)
ax1.set_title('TTFT vs TPOT Trade-off', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 图2: 按 prompt_tokens 分组的条形图
ax2 = axes[0, 1]
prompt_tokens_list = sorted(df['prompt_tokens'].unique())
x = np.arange(len(prompt_tokens_list))
width = 0.2

for i, name in enumerate(['ovgenai', 'sparse', 'eviction', 'kvcrush']):
    values = []
    for pt in prompt_tokens_list:
        val = df[(df['prompt_tokens']==pt) & (df['name']==name)]['tpot_ms'].values
        values.append(val[0] if len(val) > 0 else 0)
    ax2.bar(x + i*width, values, width, label=name)
ax2.set_xlabel('Prompt Tokens', fontsize=12)
ax2.set_ylabel('TPOT (ms)', fontsize=12)
ax2.set_title('TPOT by Strategy and Prompt Length', fontsize=14)
ax2.set_xticks(x + width*1.5)
ax2.set_xticklabels(prompt_tokens_list)
ax2.legend()

# 图3: 帕累托前沿分析
ax3 = axes[1, 0]
for name in strategies:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    ax3.plot(subset['ttft_ms'], subset['tpot_ms'], marker='o', label=name, linewidth=2, markersize=8)
    
# 标注最优点
ax3.axhline(y=19.5, color='gray', linestyle='--', alpha=0.5, label='Best TPOT')
ax3.axvline(x=700, color='gray', linestyle=':', alpha=0.5, label='Best TTFT')
ax3.set_xlabel('TTFT (ms) - Lower is Better', fontsize=12)
ax3.set_ylabel('TPOT (ms) - Lower is Better', fontsize=12)
ax3.set_title('Pareto Frontier Analysis', fontsize=14)
ax3.legend()
ax3.grid(True, alpha=0.3)

# 图4: 场景推荐热力图
ax4 = axes[1, 1]
# 计算各策略在各场景的推荐度
scenario_data = []
for pt in [5000, 10000, 20000, 30000]:
    subset = df[df['prompt_tokens'] == pt]
    if len(subset) > 0:
        for _, row in subset.iterrows():
            # 综合分数 (TTFT权重0.5, TPOT权重0.5)
            min_ttft = subset['ttft_ms'].min()
            max_ttft = subset['ttft_ms'].max()
            min_tpot = subset['tpot_ms'].min()
            max_tpot = subset['tpot_ms'].max()
            
            ttft_score = (max_ttft - row['ttft_ms']) / (max_ttft - min_ttft) if max_ttft > min_ttft else 1.0
            tpot_score = (max_tpot - row['tpot_ms']) / (max_tpot - min_tpot) if max_tpot > min_tpot else 1.0
            score = 0.5 * ttft_score + 0.5 * tpot_score
            
            scenario_data.append({
                'name': row['name'],
                'prompt': pt,
                'score': score
            })

# 简化的场景分析 - 按策略平均
strategy_scores = df.groupby('name').agg({
    'ttft_ms': 'mean',
    'tpot_ms': 'mean'
}).reset_index()

# 计算综合得分 (归一化后)
min_ttft = strategy_scores['ttft_ms'].min()
max_ttft = strategy_scores['ttft_ms'].max()
min_tpot = strategy_scores['tpot_ms'].min()
max_tpot = strategy_scores['tpot_ms'].max()

strategy_scores['ttft_score'] = (max_ttft - strategy_scores['ttft_ms']) / (max_ttft - min_ttft)
strategy_scores['tpot_score'] = (max_tpot - strategy_scores['tpot_ms']) / (max_tpot - min_tpot)
strategy_scores['balanced'] = 0.5 * strategy_scores['ttft_score'] + 0.5 * strategy_scores['tpot_score']
strategy_scores['realtime'] = 0.8 * strategy_scores['ttft_score'] + 0.2 * strategy_scores['tpot_score']
strategy_scores['batch'] = 0.2 * strategy_scores['ttft_score'] + 0.8 * strategy_scores['tpot_score']

# 绘制场景推荐条形图
x = np.arange(len(strategy_scores))
width = 0.25
ax4.bar(x - width, strategy_scores['realtime'], width, label='Realtime (TTFT focus)', color='blue', alpha=0.7)
ax4.bar(x, strategy_scores['balanced'], width, label='Balanced', color='green', alpha=0.7)
ax4.bar(x + width, strategy_scores['batch'], width, label='Batch (TPOT focus)', color='orange', alpha=0.7)
ax4.set_xlabel('Strategy', fontsize=12)
ax4.set_ylabel('Score (higher is better)', fontsize=12)
ax4.set_title('Scenario Recommendations', fontsize=14)
ax4.set_xticks(x)
ax4.set_xticklabels(strategy_scores['name'])
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('tradeoff_analysis.png', dpi=150)
print("\n\n图表已保存: tradeoff_analysis.png")

# ========== 总结 ==========
print("\n" + "=" * 60)
print("TTFT vs TPOT 权衡总结")
print("=" * 60)
print("""
【实时交互场景】推荐:
  - prompt ≤ 10k: sparse (TTFT最优且TPOT不差)
  - prompt ≥ 20k: sparse (唯一选择)

【批量生成场景】推荐:
  - prompt ≤ 10k: eviction (TPOT最优~19.5ms)
  - prompt ≥ 20k: sparse (TPOT稳定~22ms)

【综合最优】:
  - sparse: 在所有场景下都保持均衡，没有明显短板
  - eviction: TPOT最低，但TTFT太高，不适合首延迟敏感场景
  
【关键洞察】:
  1. 没有"万能最优"策略，需要根据场景选择
  2. sparse 是"万金油"，各方面都中等偏上
  3. 如果极致追求TPOT且能容忍TTFT，选eviction
""")
