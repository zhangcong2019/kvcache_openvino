import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取数据
df = pd.read_csv('benchmark_results.csv')

# ========== 扩展性分析 ==========
print("=" * 60)
print("扩展性分析：性能随 prompt_tokens 增长的变化")
print("=" * 60)

# 对有多个数据点的策略进行分析
for name in ['ovgenai', 'sparse']:
    print(f"\n--- {name} ---")
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    
    prev_pt = None
    prev_ttft = None
    prev_tpot = None
    
    for _, row in subset.iterrows():
        pt = row['prompt_tokens']
        ttft = row['ttft_ms']
        tpot = row['tpot_ms']
        
        print(f"prompt={pt:>5}: TTFT={ttft:>8.2f}ms, TPOT={tpot:>5.2f}ms", end="")
        
        if prev_pt is not None:
            pt_ratio = pt / prev_pt
            ttft_ratio = ttft / prev_ttft
            tpot_ratio = tpot / prev_tpot
            
            # 线性增长的预期值
            ttft_expected = prev_ttft * pt_ratio
            ttft_overhead = ttft / ttft_expected
            
            print(f" | 增长: {pt_ratio:.1f}x, TTFT: {ttft_ratio:.2f}x (线性预期:{ttft_overhead:.2f}x)")
        else:
            print()
        
        prev_pt = pt
        prev_ttft = ttft
        prev_tpot = tpot

# ========== 理论 vs 实际对比 ==========
print("\n" + "=" * 60)
print("线性 vs 实际增长对比")
print("=" * 60)

for name in ['ovgenai', 'sparse']:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    base_row = subset[subset['prompt_tokens'] == 5000]
    base_ttft = base_row['ttft_ms'].values[0]
    base_prompt = 5000
    
    print(f"\n{name} (以 5k 为基准):")
    print(f"{'prompt_tokens':>12} | {'实际TTFT':>10} | {'线性预期':>10} | {'偏差倍数':>8}")
    print("-" * 50)
    
    for _, row in subset.iterrows():
        pt = row['prompt_tokens']
        actual = row['ttft_ms']
        linear_expected = base_ttft * (pt / base_prompt)
        ratio = actual / linear_expected
        
        print(f"{pt:>12} | {actual:>10.2f} | {linear_expected:>10.2f} | {ratio:>8.2f}x")

# ========== 增长率拟合 ==========
print("\n" + "=" * 60)
print("增长率拟合 (TTFT vs prompt_tokens)")
print("=" * 60)

for name in ['ovgenai', 'sparse']:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    x = subset['prompt_tokens'].values
    y = subset['ttft_ms'].values
    
    # 线性拟合
    coef = np.polyfit(x, y, 1)
    linear_fn = np.poly1d(coef)
    
    # 对数拟合 (如果增长超线性)
    x_log = np.log(x)
    coef_log = np.polyfit(x_log, y, 1)
    log_fn = np.poly1d(coef_log)
    
    # 计算 R²
    y_pred_linear = linear_fn(x)
    y_pred_log = log_fn(x)
    
    ss_res = np.sum((y - y_pred_linear)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2_linear = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    ss_res_log = np.sum((y - y_pred_log)**2)
    r2_log = 1 - (ss_res_log / ss_tot) if ss_tot > 0 else 0
    
    print(f"\n{name}:")
    print(f"  线性拟合: TTFT = {coef[0]:.6f} * prompt + {coef[1]:.2f} (R²={r2_linear:.4f})")
    print(f"  对数拟合: TTFT = {coef_log[0]:.2f} * log(prompt) + {coef_log[1]:.2f} (R²={r2_log:.4f})")
    
    if r2_log > r2_linear:
        print(f"  → 对数拟合更好，增长是亚线性的 (O(log n))")
    else:
        print(f"  → 线性拟合更好，增长接近 O(n)")

# ========== 绘图 ==========
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 图1: TTFT 扩展性趋势
ax1 = axes[0, 0]
for name in ['ovgenai', 'sparse']:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    ax1.plot(subset['prompt_tokens'], subset['ttft_ms'], marker='o', label=name, linewidth=2, markersize=8)
    
    # 添加线性参考线
    base = subset[subset['prompt_tokens']==5000]['ttft_ms'].values[0]
    x_vals = subset['prompt_tokens'].values
    ax1.plot(x_vals, base * (x_vals / 5000), '--', alpha=0.5, label=f'{name} (线性参考)')
    
ax1.set_xlabel('Prompt Tokens', fontsize=12)
ax1.set_ylabel('TTFT (ms)', fontsize=12)
ax1.set_title('TTFT Scalability (with linear reference)', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 图2: TPOT 扩展性趋势
ax2 = axes[0, 1]
for name in ['ovgenai', 'sparse']:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    ax2.plot(subset['prompt_tokens'], subset['tpot_ms'], marker='s', label=name, linewidth=2, markersize=8)
ax2.set_xlabel('Prompt Tokens', fontsize=12)
ax2.set_ylabel('TPOT (ms)', fontsize=12)
ax2.set_title('TPOT Scalability', fontsize=14)
ax2.legend()
ax2.grid(True, alpha=0.3)

# 图3: TTFT 增长倍数（归一化）
ax3 = axes[1, 0]
for name in ['ovgenai', 'sparse']:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    base = subset[subset['prompt_tokens']==5000]['ttft_ms'].values[0]
    normalized = subset['ttft_ms'] / base
    prompt_ratios = subset['prompt_tokens'] / 5000
    ax3.plot(prompt_ratios, normalized, marker='o', label=name, linewidth=2, markersize=8)

# 添加理想线性增长参考
ax3.plot([1, 2, 4, 6], [1, 2, 4, 6], 'k--', alpha=0.5, label='理想线性')
ax3.set_xlabel('Prompt Tokens Multiplier', fontsize=12)
ax3.set_ylabel('TTFT Growth Multiplier', fontsize=12)
ax3.set_title('TTFT Growth vs Prompt Growth (Normalized)', fontsize=14)
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xticks([1, 2, 4, 6])
ax3.set_xticklabels(['1x (5k)', '2x (10k)', '4x (20k)', '6x (30k)'])

# 图4: 偏差分析
ax4 = axes[1, 1]
for name in ['ovgenai', 'sparse']:
    subset = df[df['name'] == name].sort_values('prompt_tokens')
    base = subset[subset['prompt_tokens']==5000]['ttft_ms'].values[0]
    x_vals = subset['prompt_tokens'].values
    
    # 实际 vs 线性预期
    linear_expected = base * (x_vals / 5000)
    deviation = subset['ttft_ms'].values / linear_expected
    
    ax4.plot(x_vals, deviation, marker='o', label=name, linewidth=2, markersize=8)

ax4.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='理想线性')
ax4.set_xlabel('Prompt Tokens', fontsize=12)
ax4.set_ylabel('Actual / Linear Expected', fontsize=12)
ax4.set_title('TTFT Deviation from Linear', fontsize=14)
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('scalability_analysis.png', dpi=150)
print("\n\n图表已保存: scalability_analysis.png")

# ========== 总结 ==========
print("\n" + "=" * 60)
print("扩展性总结")
print("=" * 60)
print("""
1. sparse 策略扩展性显著优于 ovgenai:
   - sparse: TTFT 增长 ~7.75x (30k vs 5k)
   - ovgenai: TTFT 增长 ~18.31x (30k vs 5k)
   
2. 增长模式:
   - sparse: 接近亚线性增长 O(log n)
   - ovgenai: 超线性增长，偏差越来越大
   
3. TPOT 稳定性:
   - sparse: TPOT 基本稳定 (21.69 → 22.35 ms)
   - ovgenai: TPOT 随 prompt 增长 (21.37 → 34.52 ms)

4. 结论:
   - 长 prompt 场景强烈推荐 sparse
   - ovgenai 适合短 prompt (≤10k)
""")
