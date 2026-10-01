# 예제 파이프라인

PBMC 3k 데이터로 같은 분석을 하는 두 파이프라인입니다. 비교 데모가 되도록 일부러 다르게 짰습니다.

| | `scrna_seurat.R` | `scrna_scanpy.py` |
|---|---|---|
| Doublet 제거 | 없음 | scrublet |
| 공변량 regression | 없음 | total_counts, pct_counts_mt |
| HVG | vst | seurat_v3 |
| PC 개수 | 10 | 40 |
| 클러스터링 | Louvain, resolution 0.5 | Leiden, resolution 0.8 |

데이터: https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz
(`data/` 아래에 압축 해제)
