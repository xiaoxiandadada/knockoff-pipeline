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