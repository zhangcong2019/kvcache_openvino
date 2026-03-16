# KV Cache Strategy Performance Benchmark Analysis

## 1. Data Overview

| name | prompt_tokens | output_tokens | max_num_batched_tokens | ttft_ms | tpot_ms |
|------|--------------|---------------|------------------------|---------|---------|
| ovgenai | 10000 | 1024 | 1024 | 2479.83 | 24.05 |
| sparse | 10000 | 1024 | 1024 | 1379.67 | 21.84 |
| eviction | 10000 | 1024 | 1024 | 18189.45 | 19.58 |
| kvcrush | 10000 | 1024 | 1024 | 18188.34 | 20.06 |
| ovgenai | 20000 | 1024 | 1024 | 7831.55 | 29.28 |
| sparse | 20000 | 1024 | 1024 | 3075.95 | 22.02 |
| ovgenai | 30000 | 1024 | 1024 | 16302.61 | 34.52 |
| sparse | 30000 | 1024 | 1024 | 5105.02 | 22.35 |
| ovgenai | 5000 | 1024 | 1024 | 890.28 | 21.37 |
| sparse | 5000 | 1024 | 1024 | 658.78 | 21.69 |
| eviction | 5000 | 1024 | 1024 | 4788.37 | 19.56 |
| kvcrush | 5000 | 1024 | 1024 | 4786.88 | 20.02 |

---

## 2. Strategy Comparison

### 2.1 TTFT (Time to First Token) Comparison

| prompt_tokens | eviction | kvcrush | ovgenai | sparse |
|--------------|-----------|----------|---------|--------|
| 5000 | 4788.37 | 4786.88 | 890.28 | **658.78** |
| 10000 | 18189.45 | 18188.34 | 2479.83 | **1379.67** |
| 20000 | - | - | 7831.55 | **3075.95** |
| 30000 | - | - | 16302.61 | **5105.02** |

**Best Strategy**: **sparse** has the best TTFT at all prompt lengths.

### 2.2 TPOT (Time Per Output Token) Comparison

| prompt_tokens | eviction | kvcrush | ovgenai | sparse |
|--------------|-----------|----------|---------|--------|
| 5000 | **19.56** | 20.02 | 21.37 | 21.69 |
| 10000 | **19.58** | 20.06 | 24.05 | 21.84 |
| 20000 | - | - | 29.28 | **22.02** |
| 30000 | - | - | 34.52 | **22.35** |

**Best Strategy**:
- Small prompt (5k-10k): **eviction** has the best TPOT
- Large prompt (20k-30k): **sparse** has the best TPOT

---

## 3. Scalability Analysis

### 3.1 Performance vs Prompt Tokens Growth

#### ovgenai
| prompt_tokens | TTFT (ms) | TPOT (ms) | Growth vs Previous |
|--------------|-----------|-----------|-------------------|
| 5000 | 890.28 | 21.37 | (baseline) |
| 10000 | 2479.83 | 24.05 | TTFT: 2.79x |
| 20000 | 7831.55 | 29.28 | TTFT: 3.16x |
| 30000 | 16302.61 | 34.52 | TTFT: 2.08x |

#### sparse
| prompt_tokens | TTFT (ms) | TPOT (ms) | Growth vs Previous |
|--------------|-----------|-----------|-------------------|
| 5000 | 658.78 | 21.69 | (baseline) |
| 10000 | 1379.67 | 21.84 | TTFT: 2.09x |
| 20000 | 3075.95 | 22.02 | TTFT: 2.23x |
| 30000 | 5105.02 | 22.35 | TTFT: 1.66x |

### 3.2 Linear vs Actual Growth

**ovgenai (baseline: 5k)**:

| prompt_tokens | Actual TTFT | Linear Expected | Deviation |
|--------------|-------------|-----------------|-----------|
| 5000 | 890.28 | 890.28 | 1.00x |
| 10000 | 2479.83 | 1780.56 | **1.39x** |
| 20000 | 7831.55 | 3561.12 | **2.20x** |
| 30000 | 16302.61 | 5341.68 | **3.05x** |

**sparse (baseline: 5k)**:

| prompt_tokens | Actual TTFT | Linear Expected | Deviation |
|--------------|-------------|-----------------|-----------|
| 5000 | 658.78 | 658.78 | 1.00x |
| 10000 | 1379.67 | 1317.56 | **1.05x** |
| 20000 | 3075.95 | 2635.12 | **1.17x** |
| 30000 | 5105.02 | 3952.68 | **1.29x** |

### 3.3 Linear Fitting Results

- **ovgenai**: TTFT = 0.618 × prompt - 3172 (R²=0.973)
- **sparse**: TTFT = 0.178 × prompt - 340 (R²=0.996)

sparse has a much smaller slope (0.178) than ovgenai (0.618), indicating better scalability.

---

## 4. TPOT Stability Analysis

| Strategy | 5k TPOT | 30k TPOT | Growth |
|----------|---------|----------|--------|
| sparse | 21.69ms | 22.35ms | +3% |
| ovgenai | 21.37ms | 34.52ms | **+62%** |

**Conclusion**: sparse's TPOT remains stable regardless of prompt length, while ovgenai's TPOT degrades significantly with longer prompts.

---

## 5. TTFT vs TPOT Trade-off Analysis

### 5.1 TTFT/TPOT Ratio by Strategy

| Strategy | Avg TTFT | Best TPOT | TTFT/TPOT Ratio |
|----------|----------|-----------|-----------------|
| sparse | 2554.86ms | 21.69ms | **117.8** |
| ovgenai | 6876.07ms | 21.37ms | 321.8 |
| kvcrush | 11487.61ms | 20.02ms | 573.8 |
| eviction | 11488.91ms | 19.56ms | 587.4 |

**Interpretation**: Lower TTFT/TPOT ratio indicates more balanced first-token and decoding latency.

### 5.2 Scenario Recommendations

#### Real-time Interaction (TTFT weight: 80%, TPOT weight: 20%)

| prompt_tokens | Recommendation Ranking |
|--------------|------------------------|
| 5000 | sparse > ovgenai > eviction > kvcrush |
| 10000 | sparse > ovgenai > eviction > kvcrush |
| 20000 | sparse > ovgenai |
| 30000 | sparse > ovgenai |

#### Batch Generation (TPOT weight: 80%, TTFT weight: 20%)

| prompt_tokens | Recommendation Ranking |
|--------------|------------------------|
| 5000 | eviction > kvcrush > ovgenai > sparse |
| 10000 | eviction > kvcrush > sparse > ovgenai |
| 20000 | sparse > ovgenai |
| 30000 | sparse > ovgenai |

---

## 6. Key Conclusions

### 6.1 Strategy Selection Guide

| Scenario | Recommended Strategy | Reason |
|----------|---------------------|--------|
| Short prompt (≤10k) + TPOT focus | eviction | Lowest TPOT (~19.5ms) |
| Long prompt (≥20k) | sparse | Best TTFT & TPOT balance |
| Best overall | **sparse** | Best TTFT, decent TPOT |
| Avoid | eviction/kvcrush | TTFT too high (4-18s) |

### 6.2 Core Insights

1. **sparse has the best scalability**: TTFT grows only 7.75x from 5k to 30k, while ovgenai grows 18.31x
2. **eviction/kvcrush has the best TPOT** (~20ms), but TTFT is too high (4-18 seconds) - suitable for scenarios where first-token latency is not critical
3. **sparse is the best choice for long prompts**: Balanced TTFT and TPOT performance

### 6.3 Trade-off Summary

| Scenario | Recommended Strategy | Reason |
|----------|---------------------|--------|
| Real-time chat/search | **sparse** | Best TTFT, fast response |
| Batch text generation | **eviction** | Lowest TPOT, high throughput |
| Long text generation | **sparse** | Stable TPOT regardless of length |
| Best balanced | **sparse** | No obvious weaknesses |

---

## 7. Generated Charts

- `strategy_comparison.png` - Line chart comparison
- `strategy_bar_chart.png` - Bar chart comparison
- `scalability_analysis.png` - Scalability analysis charts
- `tradeoff_analysis.png` - TTFT vs TPOT trade-off charts

---

*Analysis Date: 2026-03-16*
