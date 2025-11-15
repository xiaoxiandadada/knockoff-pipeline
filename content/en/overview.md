---
title: Overview
weight: 1
---

## Knockoff Pipeline Overview

This pipeline provides multiple statistical methods for variable selection and genetic analysis using knockoff statistics:

```mermaid
flowchart TD
    A[Input Data] --> B{Data Type}
    
    B -->|Individual-level Genotype Data| C[Individual Statistics Pipeline]
    B -->|GWAS Summary Statistics| D[Summary Statistics Pipeline]
    
    C --> E{Sample Type}
    E -->|IID Samples| F[GLM-based Methods]
    E -->|Related Samples| G[GLMM-based Methods]
    
    F --> H{Analysis Level}
    H -->|SNP-based| I[KnockoffScreen - SNP-based]
    H -->|Window-based| J[KnockoffScreen - Window-based]
    H -->|Gene-based| K[GeneScan3DKnock]
    
    G --> L[Calculate GRM Matrix]
    L --> M[Fit GLMM model]
    M --> N[BIGKnock - Gene-based]
    
    D --> O{Analysis Mode}
    O -->|Variable Selection| P[GhostKnockoff]
    O -->|Local Genetic Correlation| Q[LAVA-Knock]
    
    I --> R[SNP-level Variable Selection]
    J --> S[Window-level Variable Selection]
    K --> T[Gene-level Variable Selection]
    N --> U[Gene-level Variable Selection]
    
    P --> V[Knockoff Z-scores Construction]
    V --> W[FDR-controlled Variable Selection]
    
    Q --> X[Bivariate Local Correlation]
    X --> Y[Multi-trait Analysis]
    Y --> Z[Pleiotropy Investigation]
    
    style A fill:#e1f5fe
    style R fill:#c8e6c9
    style S fill:#c8e6c9
    style T fill:#c8e6c9
    style U fill:#c8e6c9
    style W fill:#ffecb3
    style Z fill:#f8bbd9
    
    classDef method fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef result fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    
    class I,J,K,L,P,Q method
    class R,S,T,U,W,Z result
```

## Key Methods

### Individual-level Data Methods
- **KnockoffScreen**: Supports both SNP-based and window-based analysis using GLM for IID samples
- **GeneScan3DKnock**: Gene-based analysis using GLM for IID samples
- **BIGKnock**: Gene-based analysis using GLMM for related samples, requires GRM matrix calculation

### Summary Statistics Methods
- **GhostKnockoff**: Constructs knockoff Z-scores from GWAS summary statistics for variable selection
- **LAVA-Knock**: Extends GhostKnockoff for local genetic correlation analysis and pleiotropy investigation
