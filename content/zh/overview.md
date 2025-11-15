---
title: Overview
weight: 1
---

## Knockoff pipeline 概览

Knockoff pipeline 提供多种统计方法，使用knockoff统计量进行变量选择和遗传分析：

```mermaid
flowchart TD
    A[输入数据] --> B{数据类型}
    
    B -->|个体水平基因型数据| C[个体统计 pipeline]
    B -->|GWAS汇总统计数据| D[汇总统计 pipeline]
    
    C --> E{样本类型}
    E -->|独立同分布样本| F[基于GLM的方法]
    E -->|相关样本| G[基于GLMM的方法]
    
    F --> H{分析水平}
    H -->|基于SNP| I[KnockoffScreen - 基于SNP]
    H -->|基于窗口| J[KnockoffScreen - 基于窗口]
    H -->|基于基因| K[GeneScan3DKnock]
    
    G --> L[计算GRM矩阵]
    L --> M[拟合GLMM模型]
    M --> N[BIGKnock - 基于基因]
    
    D --> O{分析模式}
    O -->|变量选择| P[GhostKnockoff]
    O -->|局部遗传相关性| Q[LAVA-Knock]
    
    I --> R[SNP水平变量选择]
    J --> S[窗口水平变量选择]
    K --> T[基因水平变量选择]
    N --> U[基因水平变量选择]
    
    P --> V[构建Knockoff Z分数]
    V --> W[FDR控制的变量选择]
    
    Q --> X[双变量局部相关性]
    X --> Y[多性状分析]
    Y --> Z[多效性位点探索]
    
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

## 主要方法

### 个体水平数据方法
- **KnockoffScreen**：支持基于SNP和基于窗口的分析，针对独立同分布样本使用GLM
- **GeneScan3DKnock**：针对独立同分布样本的基于基因的分析，使用GLM
- **BIGKnock**：针对相关样本的基于基因的分析，使用GLMM，需要计算GRM矩阵

### 汇总统计方法
- **GhostKnockoff**：从GWAS汇总统计数据构建knockoff Z分数，用于变量选择
- **LAVA-Knock**：在GhostKnockoff基础上扩展，用于局部遗传相关性分析和多效性位点探索
