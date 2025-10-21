---
title: 'Knockoff Pipeline'
cascade:
  type: docs
---

## Knockoff Method Overview

Knockoff is a statistical framework for controlling the false discovery rate (FDR), particularly suited for variable selection in high-dimensional data. In GWAS analyses, traditional multiple testing corrections (such as Bonferroni) are often overly conservative. The Knockoff method constructs "knockoff copies"—counterpart variables—that enable precise FDR control while maintaining statistical power and reducing false positives.

### Core Ideas

1. Construct knockoff variables: For each original SNP, construct a "replica" variable that is highly correlated with the original but independent of the phenotype.
2. Compare feature importance: Jointly model the original and knockoff variables and compute an importance statistic W.
3. FDR control: Determine a threshold by comparing the importance of original variables and their knockoffs to automatically control the false discovery rate.

## Citation

He, Z., Liu, L., Wang, C. *et al.* Identification of putative causal loci in whole-genome sequencing data via knockoff statistics. *Nature Communications* **12**, 3152 (2021). https://doi.org/10.1038/s41467-021-22889-4

Ma, S., Wang, C., Khan, A. *et al.* BIGKnock: fine-mapping gene-based associations via knockoff analysis of biobank-scale data. *Genome Biol* **24**, 24 (2023). https://doi.org/10.1186/s13059-023-02864-6

He, Z., Liu, L., Belloy, M. E. *et al.* GhostKnockoff inference empowers identification of putative causal variants in genome-wide association studies. *Nature Communications* **13**, 7209 (2022). https://doi.org/10.1038/s41467-022-34932-z

Ma, S., Wang, Y. *et al.* Local genetic correlation via knockoffs reduces confounding due to cross-trait assortative mating. *The American Journal of Human Genetics* **111**(12), 2839–2848 (2024). https://doi.org/10.1016/j.ajhg.2024.10.012

## License

This software is licensed under GPLv3.