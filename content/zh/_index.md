---
title: 'Knockoff Pipeline'
cascade:
  type: docs
---

## Knockoff 方法简介

Knockoff 是一种用于 **控制假发现率(FDR)** 的统计框架，特别适用于高维数据中的变量选择问题。在 GWAS 分析中，传统的多重检验校正（如 Bonferroni）过于保守，而 Knockoff 方法通过构造"仿制变量"（knockoff copies）来精确控制 FDR，在保持统计效力的同时降低假阳性率。

### 核心思想

1. **构造 Knockoff 变量**：为每个原始 SNP 构造一个"仿制"变量，该变量与原始变量高度相关，但与表型无关
2. **特征重要性比较**：同时对原始变量和 knockoff 变量建模，计算重要性统计量 W
3. **FDR 控制**：通过比较原始变量与 knockoff 变量的重要性，自动确定阈值并控制假发现率

## Citation

He, Z., Liu, L., Wang, C. *et al.* Identification of putative causal loci in whole-genome sequencing data via knockoff statistics. *Nature Communications* **12**, 3152 (2021). https://doi.org/10.1038/s41467-021-22889-4

Ma, S., Wang, C., Khan, A. *et al.* BIGKnock: fine-mapping gene-based associations via knockoff analysis of biobank-scale data. *Genome Biol* **24**, 24 (2023). https://doi.org/10.1186/s13059-023-02864-6

He, Z., Liu, L., Belloy, M. E. *et al.* GhostKnockoff inference empowers identification of putative causal variants in genome-wide association studies. *Nature Communications* **13**, 7209 (2022). https://doi.org/10.1038/s41467-022-34932-z

Ma, S., Wang, Y. *et al.* Local genetic correlation via knockoffs reduces confounding due to cross-trait assortative mating. *The American Journal of Human Genetics* **111**(12), 2839–2848 (2024). https://doi.org/10.1016/j.ajhg.2024.10.012

## License

This software is licensed under GPLv3.