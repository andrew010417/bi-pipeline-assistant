"""scRNA-seq clustering with scanpy, following the scverse best-practices tutorial."""

import scanpy as sc

# 1. Load data
adata = sc.read_10x_mtx("data/filtered_gene_bc_matrices/hg19/", var_names="gene_symbols", cache=True)
adata.var_names_make_unique()

# 2. QC
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.n_genes_by_counts < 2500, :]
adata = adata[adata.obs.pct_counts_mt < 5, :].copy()

# 3. Doublet detection
sc.pp.scrublet(adata, expected_doublet_rate=0.06)
adata = adata[~adata.obs.predicted_doublet, :].copy()

# 4. Normalization and HVG
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat_v3", layer="counts")

# 5. Regress out and scale
sc.pp.regress_out(adata, ["total_counts", "pct_counts_mt"])
sc.pp.scale(adata, max_value=10)

# 6. PCA, neighbors, clustering
sc.tl.pca(adata, svd_solver="arpack", n_comps=50)
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
sc.tl.leiden(adata, resolution=0.8, flavor="igraph", n_iterations=2)
sc.tl.umap(adata, min_dist=0.5)

# 7. Markers
sc.tl.rank_genes_groups(adata, "leiden", method="wilcoxon")
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False, save="_markers.png")

adata.write_h5ad("results/pbmc3k.h5ad")
