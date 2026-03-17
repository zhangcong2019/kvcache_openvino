# LiveCodeBench Code Generation Evaluation Results Report

## 📊 Data Overview

| Model | Framework | Pass@1 |
|------|------|--------|
| Qwen3-30B-A3B-Instruct-2507 | vllm | **0.683** |
| Qwen2.5-7B-Instruct | vllm | 0.367 |
| Qwen2.5-7B-Instruct | eviction | 0.325 |
| Qwen2.5-7B-Instruct | kvcrush | 0.310 |
| Qwen2.5-7B-Instruct | ovgenai | 0.297 |
| Qwen2.5-7B-Instruct | sparcity | 0.280 |

---

## 📈 Visualization Analysis

![Pass@1 Results](results.png)



### Qwen2.5-7B Framework Performance Rankings

```
1st  eviction   ████████████████████ 0.325  +16.1%
2nd  kvcrush    ███████████████████  0.310  +10.7%
3rd  ovgenai    ██████████████████   0.297   +6.1%
4th  sparcity   █████████████████    0.280   (baseline)
```

---

## 🔍 Key Findings

### 1. Model Size Impact is Significant
- **Qwen3-30B (vllm)** achieves **68.3%** Pass@1, leading Qwen2.5-7B by approximately **31.6 percentage points**
- Large models show clear advantages in code generation tasks


---

## 📝 Conclusions

1. **vllm** framework performs best on code generation tasks
2. Large models (30B) significantly outperform small models (7B)
3. Among 7B models, sparsification schemes rank as **eviction** > **kvcrush** > **ovgenai** > **sparcity**
4. OpenVINO still has a **11%-24%** performance gap compared to vllm, possibly because vllm uses FP16 models while OpenVINO GenAI uses INT8 models

---

*Report generated: 2026-03-17*
