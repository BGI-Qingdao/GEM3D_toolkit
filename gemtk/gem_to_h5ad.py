import sys
import time
import getopt
from scipy.sparse import csr_matrix
from gemtk.slice_dataframe import slice_dataframe
import anndata as ad
import pandas as pd
import numpy as np
from anndata import AnnData
#############################################################################
# usage
def gem_to_h5ad_usage():
    print("""
Usage : GEM_toolkit.py gem_to_h5ad  -i <xxx.gemc>  \\
                                    -o <prefix> \\
                                    -b <binsize> 
""")

def gem_to_h5ad_main(argv:[]):
    prefix = ''
    ingemc = ''
    binsize = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:b:",["help","input=","output=","binsize="])
    except getopt.GetoptError:
        gem_to_h5ad_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem_to_h5ad_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            ingemc = arg
        elif opt in ("-b", "--binsize"):
            binsize = int(arg)

    if ingemc == "" or prefix== "" or binsize <1 :
        gem_to_h5ad_usage()
        sys.exit(3)

    print("input gemc is {}".format(ingemc))
    print("output prefix is {}".format(prefix))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print('loading gemc now...')
    sdf = slice_dataframe()
    sdf.init_from_file(ingemc)
    print('prepare dataframe now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    genes, genemap = sdf.get_gene_ids()
    cells, cellmap = sdf.get_bins(binsize = binsize)
    cellxy = sdf.getxy_bins()
    if sdf.spatial3d:
        cell3dxyz = sdf.get3dxyz_bins()
    obs = pd.DataFrame()
    obs['cellid'] = cells
    obs['binname'] = obs.apply(lambda row: f'cell{row["cellid"]}',axis=1)
    obs = obs.set_index('cellid')
    obs['x'] = cellxy['x']
    obs['y'] = cellxy['y']
    if sdf.spatial3d:
        obs['spatial3d_x'] = cell3dxyz['spatial3d_x']
        obs['spatial3d_y'] = cell3dxyz['spatial3d_y']
        obs['spatial3d_z'] = cell3dxyz['spatial3d_z']
    obs = obs.set_index('binname')
    var = pd.DataFrame()
    var['genename'] = genes
    var = var.set_index('genename')
    ngene = len(genes)
    ncell = len(cells)
    densityarray = np.zeros((ncell, ngene),dtype = int)
    for row in sdf.m_dataframe.itertuples():
        densityarray[cellmap[row.bin_name],genemap[row.geneID]] = densityarray[cellmap[row.bin_name],genemap[row.geneID]]+row.MIDCounts
    yidx,xidx = np.nonzero(densityarray)
    sparseMatrix = csr_matrix((densityarray[yidx,xidx],(yidx,xidx)), shape=(ncell,ngene))
    data = AnnData(X=sparseMatrix, dtype=sparseMatrix.dtype, obs=obs, var=var)
    data.obsm['spatial'] = obs[['x','y']].to_numpy()
    if sdf.spatial3d:
        data.obsm['spatial3d'] = obs[['spatial3d_x','spatial3d_y','spatial3d_z']].to_numpy()
    print(f'iter done for #cell={ncell}, #gene={ngene}.',flush=True)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print('save h5ad now...')
    num_genes = np.sum(densityarray>0,axis=1)
    num_umi = np.sum(densityarray,axis=1)
    data.obs['nGenes'] = num_genes
    data.obs['nUMI'] = num_umi
    print(f'iter done for #cell={ncell}, #gene={ngene}.',flush=True)
    print(f'average gene = {np.mean(num_genes)}')
    print(f'median gene = {np.median(num_genes)}')
    print(f'average umi = {np.mean(num_umi)}')
    print(f'median umi = {np.median(num_umi)}')
    data.write(f'{prefix}.h5ad',compression='gzip')
    print('all done')
