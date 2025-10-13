---
title: 'Summary Statistics Pipeline'
---

## Summary Statistics Pipeline

传统 Knockoff 需要个体级基因型数据，但 GWAS 通常只公开汇总统计量（Z-score、P值等）。本 Pipeline 采用 **GhostKnockoff** 和 **LAVA-Knock** 方法，实现了仅基于汇总统计量的 Knockoff 分析：

- **GhostKnockoff**：利用参考面板的 LD 结构，从汇总统计量中重构 knockoff 统计量
- **LAVA-Knock**：扩展到局部遗传相关分析，支持多表型联合分析
- **无需个体数据**：仅需 Z-score 和参考面板（如 1000 Genomes）即可运行


## 主要功能

- **变量选择** (`--mode select`): GhostKnockoff + LAVAKnock FDR 控制，输出显著变异。
- **局部遗传相关** (`--mode correl`): LAVA-Knock 双表型窗口分析，输出窗口级局部相关与 knockoff 过滤结果。

## Pipeline 版本：Standard vs Fast

| 版本 | 触发方式 | 主要差异 |
| --- | --- | --- |
| Standard (默认) | 不加 `--py_accel` | 全部计算在 R 中完成，适合通用环境。 |
| Fast | 命令后追加 `--py_accel` | 使用 `accelerator.py` 中的 NumPy/Numba 加速相关系数和 LD 去冗余运算。 |

无法加载 Python 环境时，会自动回退到标准实现。

## 快速开始

以下命令可直接在仓库根目录执行。默认的参考面板是1000geno的 `g1000_eur`，用户也可以自己提供或者使用基因型数据，用户需要提供zscore文件 `zscore.txt` 与，再依据用户指定的基因型坐标`GRCh37` 或 `GRCh38`进行切块。

### 1) 安装依赖

```bash
Rscript install_packages.R
```

### 2) 变量选择（参考面板）

```bash
Rscript run_pipeline.R --mode select \
  --zscore zscore.txt \
  --panel g1000_eur \
  --ld_coord GRCh37 \
  --py_accel -v -o results
```

- 自动解析 `zscore.txt` 中的 `chr:pos:ref:alt` 或 `CHR/POS` 列，与参考面板按 `CHR+POS` 匹配。
- `--panel` 可省略（默认 `g1000_eur/g1000_eur`）。
- `--ld_coord` 必须显式指定 LD block 坐标（`GRCh37` 或 `GRCh38`）。

### 3) 变量选择（真实基因型）

```bash
Rscript run_pipeline.R --mode select \
  --zscore zscore.txt \
  --geno_plink genotype \
  --ld_coord GRCh37 \
  -o results -v
```

### 4) 局部遗传相关（示例）

```bash
Rscript run_pipeline.R --mode correl \
  --zscore zscore.txt \
  --panel g1000_eur/g1000_eur \
  --py_accel -v -o results
```

> 扩展到全基因组时，可对 1–22 号染色体循环运行（如需特定窗口，可继续使用 `scripts/build_info_from_plink.R` 手动生成 Info）。

## 输入格式与自动识别

- **变异信息**：CSV，列包含 `rsid, chr, pos_bp`。可使用 `scripts/build_info_from_plink.R` 从 PLINK 面板生成。
- **GWAS 汇总**：
  - 标准：`CHR, POS, Z`。
  - 仅 `rsid + 数值列`：通过 `normalize_gwas_table()` 自动转换；脚本 `scripts/convert_zscore_to_gwas.R` 可提前批量处理。
  - 多表型：`--multi_gwas <file> --zcols col1,col2`。
- **基因型 / 参考面板**：
  - `--geno_rds`：RDS matrix（列名为 `rsid` 或 `chr:pos`）。
  - `--geno_csv`：CSV，配合 `--geno_format samples_by_snps|snps_by_samples`。
  - `--geno_plink`：PLINK 前缀，使用 `snpStats::read.plink` 读取。
  - 未提供真实基因型时，自动启用 `--ref_plink`（默认 `g1000_eur/g1000_eur`）。

## 输出说明

### Selection 模式

输出文件：`results/selection/<info>_<pheno>_selection.csv`

列包含：
- `id, rsid, chr, pos`
- `pval.orginal, pval.knockoff*`
- `W, Qvalue, selected`
- `geno_source`

若按 LD blocks 切块（`--ld_coord`），会额外生成 `<prefix>_chunk_summary.csv`，记录每个分块的：
- 范围
- 来源（ld_block/fallback）
- 选择数

### Correlation 模式

输出文件：
- `results/correlation/<info>_<pheno1>__<pheno2>_bivariate.csv`
- `results/correlation/<info>_<pheno1>__<pheno2>_significant_windows.csv`

## 目录速览

```
g1000_eur/                    # 默认参考面板 (.bed/.bim/.fam/.synonyms)
demo_chr10_10_20Mb.*          # 示例真实基因型（PLINK）
info_chr10_10_20Mb.csv        # 由参考面板提取的示例 Info
zscore_chr10_10_20Mb.tsv      # 示例 GWAS 子集
zscore_formatted.tsv          # 转换后的标准格式
results/                      # 分析输出目录
  ├── selection/              # 变量选择结果
  └── correlation/            # 局部遗传相关结果
```
