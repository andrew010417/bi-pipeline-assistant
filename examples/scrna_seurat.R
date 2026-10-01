# scRNA-seq basic clustering with Seurat (PBMC 3k style)
library(Seurat)
library(dplyr)

# 1. Load data
counts <- Read10X(data.dir = "data/filtered_gene_bc_matrices/hg19/")
seu <- CreateSeuratObject(counts = counts, project = "pbmc3k", min.cells = 3, min.features = 200)

# 2. QC
seu[["percent.mt"]] <- PercentageFeatureSet(seu, pattern = "^MT-")
seu <- subset(seu, subset = nFeature_RNA > 200 & nFeature_RNA < 2500 & percent.mt < 5)

# 3. Normalization and HVG
seu <- NormalizeData(seu, normalization.method = "LogNormalize", scale.factor = 10000)
seu <- FindVariableFeatures(seu, selection.method = "vst", nfeatures = 2000)

# 4. Scaling and PCA
seu <- ScaleData(seu, features = rownames(seu))
seu <- RunPCA(seu, features = VariableFeatures(object = seu))

# 5. Clustering
seu <- FindNeighbors(seu, dims = 1:10)
seu <- FindClusters(seu, resolution = 0.5)
seu <- RunUMAP(seu, dims = 1:10)

# 6. Markers
markers <- FindAllMarkers(seu, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
top10 <- markers %>% group_by(cluster) %>% slice_max(n = 10, order_by = avg_log2FC)

write.csv(markers, "results/markers.csv")
saveRDS(seu, "results/pbmc3k.rds")
