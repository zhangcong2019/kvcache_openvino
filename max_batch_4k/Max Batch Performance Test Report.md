# Max Batch Performance Test Report

## 📊 Test Configuration

- **Prompt Tokens:** 10000
- **Output Tokens:** 1024
- **Tested Frameworks:** ovgenai, sparse, eviction, kvcrush

---

## 📈 TTFT (Time To First Token) Analysis

![TTFT Chart](ttft_chart.png)

### TTFT Summary (ms)

| max_num_batched_tokens | ovgenai | sparse  | eviction | kvcrush |
| ---------------------- | ------- | ------- | -------- | ------- |
| 1                      | 196,927 | 202,266 | 194,634  | 194,529 |
| 4                      | 71,961  | 83,924  | 69,224   | 69,052  |
| 64                     | 7,359   | 8,504   | 21,495   | 21,498  |
| 1024                   | 2,480   | 1,380   | 18,189   | 18,188  |
| 4096                   | 2,257   | 1,268   | -        | -       |

### Key Findings

1. TTFT decreases significantly as batch size increases, drop from 200s at 1 to 2.3s at 4096.
2. **batch=64** is a turning point: ovgenai/sparse begin to improve substantially from this point onward.

---

## ⚡ TPOT (Time Per Output Token) Analysis

![TPOT Chart](tpot_chart.png)

### TPOT Summary (ms)

| max_num_batched_tokens | ovgenai | sparse | eviction | kvcrush |
| ---------------------- | ------- | ------ | -------- | ------- |
| 1                      | 24.00   | 21.79  | 19.42    | 19.49   |
| 4                      | 24.01   | 21.82  | 19.58    | 20.05   |
| 64                     | 24.01   | 21.81  | 19.57    | 20.07   |
| 1024                   | 24.05   | 21.84  | 19.58    | 20.06   |
| 4096                   | 24.02   | 21.83  | -        | -       |

### Key Findings

1. **TPOT is relatively stable**: TPOT across frameworks is minimally affected by batch size.
2. max_num_batched_tokens will affect memory usage, **cause OOM**.

---

## 🎯 Conclusion

Batch token count significantly impacts TTFT. **MTP and speculative decoding** can provide performance gains.

---

*Report updated: 2026-03-17*
