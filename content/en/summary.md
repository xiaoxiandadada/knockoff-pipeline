---
title: 'Summary Statistics Pipeline'
---


## Summary Statistics Pipeline

Traditional Knockoff requires individual-level genotype data, but GWAS typically only release summary statistics (Z-scores, p-values, etc.). This pipeline uses **GhostKnockoff** and **LAVA-Knock** to perform Knockoff analyses based solely on summary statistics:

- **GhostKnockoff**: Reconstructs knockoff statistics from summary data using LD structure from a reference panel.
- **LAVA-Knock**: Extends to local genetic correlation analyses and supports joint multi-trait analysis.
- **No individual data required**: Runs with only Z-scores and a reference panel (e.g., 1000 Genomes).

## Main Features

- Variable selection (`--mode select`): GhostKnockoff + LAVAKnock FDR control, outputs significant variants.
- Local genetic correlation (`--mode correl`): LAVA-Knock bivariate window analysis, outputs window-level local correlations and knockoff-filtered results.

## Pipeline Versions: Standard vs Fast

| Version | Trigger | Main Difference |
| --- | --- | --- |
| Standard (default) | omit `--py_accel` | All computations performed in R; suitable for general environments. |
| Fast | append `--py_accel` to command | Uses NumPy/Numba in `accelerator.py` to accelerate correlation and LD redundancy removal. |

If the Python environment cannot be loaded, the pipeline will automatically fall back to the standard implementation.

## Quick Start

The following commands can be run from the repository root. The default reference panel is the 1000 Genomes `g1000_eur`. Users may provide their own panel or genotype data. Provide a zscore file `zscore.txt`, and the pipeline will chunk based on the specified genome coordinate system `GRCh37` or `GRCh38`.

### 1) Install dependencies

```bash
Rscript install_packages.R
```

### 2) Variable selection (reference panel)

```bash
Rscript run_pipeline.R --mode select \
  --zscore zscore.txt \
  --panel g1000_eur \
  --ld_coord GRCh37 \
  --py_accel -v -o results
```

- Automatically parses `chr:pos:ref:alt` or `CHR/POS` columns in `zscore.txt`, matching to the reference panel by `CHR+POS`.
- `--panel` can be omitted (default `g1000_eur/g1000_eur`).
- `--ld_coord` must explicitly specify LD block coordinates (`GRCh37` or `GRCh38`).

### 3) Variable selection (real genotypes)

```bash
Rscript run_pipeline.R --mode select \
  --zscore zscore.txt \
  --geno_plink genotype \
  --ld_coord GRCh37 \
  -o results -v
```

### 4) Local genetic correlation (example)

```bash
Rscript run_pipeline.R --mode correl \
  --zscore zscore.txt \
  --panel g1000_eur/g1000_eur \
  --py_accel -v -o results
```

> To scale to the whole genome, iterate over chromosomes 1–22 (or generate specific windows using `scripts/build_info_from_plink.R`).

## Input Formats and Auto-detection

- Variant info: CSV with columns `rsid, chr, pos_bp`. Can be generated from a PLINK panel using `scripts/build_info_from_plink.R`.
- GWAS summary:
  - Standard: `CHR, POS, Z`.
  - `rsid + value` only: automatically converted via `normalize_gwas_table()`; use `scripts/convert_zscore_to_gwas.R` for batch preprocessing.
  - Multi-trait: `--multi_gwas <file> --zcols col1,col2`.
- Genotypes / reference panel:
  - `--geno_rds`: RDS matrix (column names `rsid` or `chr:pos`).
  - `--geno_csv`: CSV with `--geno_format samples_by_snps|snps_by_samples`.
  - `--geno_plink`: PLINK prefix, read via `snpStats::read.plink`.
  - If real genotypes are not provided, `--ref_plink` is used automatically (default `g1000_eur/g1000_eur`).

## Output Description

### Selection mode

Output file: `results/selection/<info>_<pheno>_selection.csv`

Columns include:
- `id, rsid, chr, pos`
- `pval.orginal, pval.knockoff*`
- `W, Qvalue, selected`
- `geno_source`

If chunking by LD blocks (`--ld_coord`), an additional `<prefix>_chunk_summary.csv` is produced, recording for each chunk:
- range
- source (ld_block/fallback)
- number selected

### Correlation mode

Output files:
- `results/correlation/<info>_<pheno1>__<pheno2>_bivariate.csv`
- `results/correlation/<info>_<pheno1>__<pheno2>_significant_windows.csv`

## Directory Overview

```
g1000_eur/                    # default reference panel (.bed/.bim/.fam/.synonyms)
demo_chr10_10_20Mb.*          # example real genotypes (PLINK)
info_chr10_10_20Mb.csv        # example Info extracted from reference panel
zscore_chr10_10_20Mb.tsv      # example GWAS subset
zscore_formatted.tsv          # converted standard format
results/                      # analysis outputs
  ├── selection/              # variable selection results
  └── correlation/            # local genetic correlation results
```