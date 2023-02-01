########
#
#   Stereo_seurat.R
#   
#   1. load stereo-seq format matrix and convert to seurat object
#   2. add code to do seurat process,
#
########

### Get the parameters
parser = argparse::ArgumentParser(description = 'Script for converting Stereo-seq matrix to seurat format')
parser$add_argument('-i', '--input', dest = 'input', help = 'input tsv filename')
parser$add_argument('-b', '--binsize', dest = 'binsize', default = 1, type = 'integer', help = 'bin size to binning, your input should be in binSize1 if you set this')
parser$add_argument('-s', '--sample', dest = 'sample', help = 'sample ID, will be used as output prefix and seurat object ident')
parser$add_argument('-t', '--tissue', dest = 'tissue', help = 'csv format file listed cell ID which can be used to lasso, should in x_y format')
parser$add_argument('-o', '--out', dest = 'outdir', help = 'directory where to save the output files, all output files will be indexed by sample ID')

opts = parser$parse_args()

library(Seurat)
library(SeuratObject)
library(SeuratDisk)
library(data.table)
library(Matrix)
library(rjson)

opts$sample <- paste0('sample_', gsub('-', '_', opts$sample))
opts$pointSize <- as.numeric(opts$pointSize)

dir.create(opts$outdir, recursive=TRUE)

data <- fread(file = opts$input)

#' group counts into bins
data$x <- trunc(data$x / opts$binsize) * opts$binsize
data$y <- trunc(data$y / opts$binsize) * opts$binsize

if ('MIDCounts' %in% colnames(data)) {
    data <- data[, .(counts=sum(MIDCounts)), by = .(geneID, x, y)]
} else {
    data <- data[, .(counts=sum(UMICount)), by = .(geneID, x, y)]
}

#' create sparse matrix from stereo
data$cell <- paste0(opts$sample, ':', data$x, '_', data$y)
data$geneIdx <- match(data$geneID, unique(data$geneID))
data$cellIdx <- match(data$cell, unique(data$cell))

if (! is.null(opts$binsize)){
    write.table(data, file = paste0(opts$outdir, '/', opts$sample, '_bin', opts$binsize, '.tsv'), 
                quote = FALSE, sep = '\t', row.names = FALSE )
}

mat <- sparseMatrix(i = data$geneIdx, j = data$cellIdx, x = data$counts, 
                    dimnames = list(unique(data$geneID), unique(data$cell)))
cell_coords <- unique(data[, c('cell', 'x', 'y')])

rownames(cell_coords) <- cell_coords$cell

seurat_spatialObj <- CreateSeuratObject(counts = mat, project = 'Stereo', assay = 'Spatial', 
                                        names.delim = ':', meta.data = cell_coords)

#' create pseudo image
cell_coords$x <- cell_coords$x - min(cell_coords$x) + 1
cell_coords$y <- cell_coords$y - min(cell_coords$y) + 1

tissue_lowres_image <- matrix(1, max(cell_coords$y), max(cell_coords$x))

tissue_positions_list <- data.frame(row.names = cell_coords$cell,
                                    tissue = 1,
                                    row = cell_coords$y, col = cell_coords$x,
                                    imagerow = cell_coords$y, imagecol = cell_coords$x)


scalefactors_json <- toJSON(list(fiducial_diameter_fullres = opts$binsize,
                                 tissue_hires_scalef = 1,
                                 tissue_lowres_scalef = 1))

#' function to create image object
generate_spatialObj <- function(image, scale.factors, tissue.positions, filter.matrix = TRUE){
    if (filter.matrix) {
        tissue.positions <- tissue.positions[which(tissue.positions$tissue == 1), , drop = FALSE]
    }

    unnormalized.radius <- scale.factors$fiducial_diameter_fullres * scale.factors$tissue_lowres_scalef

    spot.radius <- unnormalized.radius / max(dim(x = image))

    return(new(Class = 'VisiumV1', 
               image = image, 
               scale.factors = scalefactors(spot = scale.factors$tissue_hires_scalef, 
                                            fiducial = scale.factors$fiducial_diameter_fullres, 
                                            hires = scale.factors$tissue_hires_scalef, 
                                            lowres = scale.factors$tissue_lowres_scalef), 
               coordinates = tissue.positions, 
               spot.radius = spot.radius))
}

spatialObj <- generate_spatialObj(image = tissue_lowres_image, 
                                  scale.factors = fromJSON(scalefactors_json), 
                                  tissue.positions = tissue_positions_list)

#' import image into seurat object
spatialObj <- spatialObj[Cells(x = seurat_spatialObj)]
DefaultAssay(spatialObj) <- 'Spatial'

seurat_spatialObj[['slice1']] <- spatialObj

#' filter out empty cell
seurat_spatialObj <- subset(seurat_spatialObj, subset = nCount_Spatial > 0)

saveRDS(seurat_spatialObj, file = paste0(opts$outdir, '/', opts$sample, '_bin', opts$binsize, '_seurat.rds'))
