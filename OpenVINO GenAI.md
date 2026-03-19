 **OpenVINO GenAI** is specifically designed for LLM and GenAI workloads. It provides APIs for LLM inference and generation, filling the gap between OpenVINO—originally designed for CNN models—and modern LLM frameworks.
 
![](Pasted%20image%2020260317161826.png)

---

# Why OV GenAI?
Sparsity and eviction are not yet widely integrated in mainstream frameworks such as vLLM and llama.cpp.
OV GenAI implements several sparsity and eviction algorithms, likely because OpenVINO was originally optimized for vision workloads, while multimodal workloads require handling massive token counts and KV cache usage.

---

# Optimizations in OV GenAI:
- **Sparsity**: XAttention (XAttention CM kernel implemented by the PRC team), Triangle
- **Eviction**: H2O, SnapKV, R-KV
- **KVCrush**: additional optimization built on top of eviction (designed by Intel)
- Speculative decoding
- Continuous batching
- Visual token pruning: CDPruner

---

# Benchmark Configuration
Hardware: B60
Software: openvino_genai-2026.1
Model: Qwen2.5-7B-Instruct, INT8
Configurations:
- ovgenai (default configuration)
- sparse
- eviction
- kvcrush


# Benchark result:

- [LiveCodeBench Code Generation Evaluation Results Report](./livecodebench/LiveCodeBench%20Code%20Generation%20Evaluation%20Results%20Report.md)
- [LongBench Benchmark Analysis](./LongBench/LongBench%20Benchmark%20Analysis.md)
- [KV Cache Strategy Performance Benchmark Analysis vs Prompt Tokens](./benchmark_analysis/KV%20Cache%20Strategy%20Performance%20Benchmark%20Analysis%20vs%20prompt%20tokens.md)
- [Output Tokens Impact Analysis](./output_tokens_4k/Output%20Tokens%20Impact%20Analysis)
- [Max Batch Performance Test Report](./max_batch_4k/Max%20Batch%20Performance%20Test%20Report.md)

# Conclusion:
- sparse (XAttention), compared with original ovgenai
	- performance is ~3x TTFT, ~1.5x TPOT
	- LiveCodeBench and LongBench v2 is ~10% worse （-3 points）
- eviction (H2O, SnapKV, R-KV) 
	- TPOT is better, but TTFT is ~10x slower
	- LiveCodeBench and LongBench v2, comparable to ov genai
	- Performance needs optimization. Eviction is implemented in ov genai, but attention kernel is implemented in ov gpu plugin. Eviction should be integrated into flash attention kernel
![](Pasted%20image%2020260318152526.png)
- kvcrush improvement upon eviction is negligible on LiveCodeBench and LongBench v2
- LLM attention kernel is fast evolving, require kernel enabling effort to support new models.