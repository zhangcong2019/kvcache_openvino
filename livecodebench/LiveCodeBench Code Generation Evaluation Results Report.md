# LiveCodeBench Code Generation Evaluation Results Report

## 📊 Data Overview

| Model                       | Framework | Pass@1    |
| --------------------------- | --------- | --------- |
| Qwen3-30B-A3B-Instruct-2507 | vllm      | **0.683** |
| Qwen2.5-7B-Instruct         | vllm      | 0.367     |
| Qwen2.5-7B-Instruct         | eviction  | 0.325     |
| Qwen2.5-7B-Instruct         | kvcrush   | 0.310     |
| Qwen2.5-7B-Instruct         | ovgenai   | 0.297     |
| Qwen2.5-7B-Instruct         | sparcity  | 0.280     |

---

## 📈 Visualization Analysis

![Pass@1 Results](results.png)



### Qwen2.5-7B OpenVINO Performance Rankings

```
1st  eviction   ████████████████████ 0.325  
2nd  kvcrush    ███████████████████  0.310  
3rd  ovgenai    ██████████████████   0.297   
4th  sparcity   █████████████████    0.280   
```

---

## 📝 Conclusions

1. LiveCodeBench: hundreds input token, hundred - thousand output token
2. 7B model, sparsification schemes rank as **eviction** > **kvcrush** > **ovgenai** > **sparcity**
3. Large models (30B) significantly outperform small models (7B)
4. OpenVINO still has a **11%** performance gap compared to vllm, possibly because vllm uses FP16 models while OpenVINO GenAI uses INT8 models

---

*Report generated: 2026-03-17*
