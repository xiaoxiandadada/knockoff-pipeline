---
title: Individual Statistics Pipeline
weight: 3
---

本仓库为使用基于knockoff或基于SCANG的方法进行SNP水平、基于窗口和以基因为中心的关联推断提供了一个统一的界面。它支持**不相关**和**相关**样本，集成了用于混合模型GWAS的SAIGE，并提供自动FDR控制。

### 支持的方法

| 方法        | 输入数据       | 样本类型 |         描述             |
| -------- | ------------- | -------- | -------------------- |
| **KnockoffScreen**  | SNP 基因型            | 不相关   | SNP水平和滑动窗口推断                           |
| **GeneScan3DKnock** | SNP 基因型       | 不相关   | 通过多尺度聚合进行以基因为中心的推断            |
| **BIGKnock** | SNP 基因型 (&GRM) | 相关 | 使用GLMM模型进行以基因为中心的推断         |


## 安装

### 1. 安装 SAIGE (使用 conda 环境)

```bash
conda env create -f environment-RSAIGE.yml
conda activate RSAIGE
FLAGPATH=`which python | sed 's|/bin/python$||'`
export LDFLAGS="-L${FLAGPATH}/lib"
export CPPFLAGS="-I${FLAGPATH}/include"
```

### 2. 安装依赖

```bash
Rscript install_packages.R
```


## 输入要求

#### 必需输入

| 参数                    | 描述                                                     |
| ----------------------- | -------------------------------------------------------- |
| `--pheno_file`          | 包含ID列的表型文件 (CSV/TSV)                             |
| `--geno_file`           | PLINK bed/bim/fam 格式的基因型文件前缀                   |
| `--phenotype`           | 表型的列名                                               |
| `--genome_build`        | "hg19" 或 "hg38"                                         |
| `--sample_uncorrelated` | TRUE/FALSE                                               |

#### 可选输入

| 参数                        | 描述                                                                                                                               | 默认值              |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| `--sliding_window_length`   | 用于基于窗口推断的窗口大小列表（以bp为单位），以逗号分隔。**仅在** `--test_type = "Single_Window"` 时使用。 | `"1000,5000,10000"` |
| `--M`                       | knockoff 副本的数量。                                                                                                              | `5`                 |
| `--geno_missing_imputation` | 缺失基因型插补方法 (`fixed` 或 `mean`)。                                                                                           | `"fixed"`           |
| `--plink_path`              | PLINK 可执行文件的路径。                                                                                                           | `"plink"`           |
| `--genome_build`            | 用于注释和窗口映射的基因组构建 (`hg19`, `hg38`)。                                                                                  | `"hg19"`            |
| `--sample_uncorrelated`     | 样本是否不相关 (TRUE/FALSE)。                                                                                                      | `TRUE`              |
| `--fdr`                     | 目标假发现率。                                                                                                                     | `0.1`               |
| `--grm_file`                | GRM 矩阵 (`.grm` + `.grm.id`) **仅对相关样本方法（如 BIGKnock）需要**。否则忽略。                                                   | `NULL`              |
| `--pheno_id`                | 表型文件中样本ID的列名。当表型表包含类似ID的列时需要。                                                                             | `NULL`              |
| `--covariates`              | 以逗号分隔的协变量名称。对所有方法都是可选的；仅当关联模型中包含协变量时使用。                                                     | `NULL`              |
| `--user_cores`              | 使用的CPU线程数。                                                                                                                  | `1`                 |



## 流水线用法

### SNP水平和基于窗口的推断 (不相关样本)

```bash
Rscript pipeline.R \
  --outdir "result/" \
  --test_type "Single_Window" \
  --pheno_file "$pheno_file" \
  --grm_file "$grm_file" \
  --geno_file "$geno_file" \
  --phenotype "Y" \
  --pheno_id "id" \
  --covariates "X1" \
  --user_cores 4 \
  --sliding_window_length "1000,5000,10000" \
  --geno_missing_imputation "fixed" \
  --plink_path "plink" \
  --M 5 \
  --genome_build "hg19" \
  --sample_uncorrelated TRUE \
  --fdr 0.1
```


### 以基因为中心的推断 (不相关样本)

```bash
Rscript pipeline.R \
  --outdir "result_gene/" \
  --test_type "Gene_Centric_Coding" \
  --pheno_file "$pheno_file" \
  --geno_file "$geno_file" \
  --phenotype "Y" \
  --pheno_id "id" \
  --covariates "X1,X2" \
  --sliding_window_length "20000,50000" \
  --genome_build "hg19" \
  --sample_uncorrelated TRUE \
  --M 10 \
  --fdr 0.1
```


### 以基因为中心的推断 (相关样本)

如果未提供 `--grm_file`，流水线将使用 SAIGE 自动生成 GRM。

```bash
Rscript pipeline.R \
  --outdir "result_bigknock/" \
  --test_type "Gene_Centric_Coding" \
  --pheno_file "$pheno_file" \
  --grm_file "$grm_file" \
  --grm_id_file "$grm_id_file" \
  --geno_file "$geno_file" \
  --phenotype "Y" \
  --pheno_id "id" \
  --covariates "age,sex,PC1,PC2" \
  --genome_build "hg38" \
  --sample_uncorrelated FALSE \
  --M 5 \
  --fdr 0.1
```


## 输出文件

每个流水线运行输出：

#### 对于SNP水平和窗口水平的推断

* `Single_Window_results_chr*.csv`
* 曼哈顿/Q–Q 图

#### 对于以基因为中心的推断

* `Gene_results_chr*.csv`
* 曼哈顿/Q–Q 图


## 示例目录结构

{{< filetree/container >}}
  {{< filetree/folder name="data" state="open" >}}
    {{< filetree/file name="genotype.bed" >}}
    {{< filetree/file name="genotype.bim" >}}
    {{< filetree/file name="genotype.fam" >}}
    {{< filetree/file name="phenotype.txt" >}}
    {{< filetree/folder name="grm" state="closed" >}}
    {{< /filetree/folder >}}
  {{< /filetree/folder >}}
  {{< filetree/folder name="R" state="open" >}}
    {{< filetree/file name="pipeline.R" >}}
    {{< filetree/file name="install_packages.R" >}}
  {{< /filetree/folder >}}
  {{< filetree/folder name="result" state="open" >}}
    {{< filetree/file name="Single_results_chr1.csv" >}}
    {{< filetree/file name="Window_results_chr1.csv" >}}
    {{< filetree/file name="Gene_results_chr1.csv" >}}
  {{< /filetree/folder >}}
{{< /filetree/container >}}
