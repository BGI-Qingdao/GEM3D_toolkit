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
def gemc_to_h5ad_usage():
    print("""
Usage : GEM_toolkit.py gemc_to_h5ad  -i <xxx.gemc>  \\
                                     -o <prefix> \\
                                     -m [xxx.cellmask]
""")

def gemc_to_h5ad_main(argv:[]):
    prefix=''
    ingemc=''
    cellmask=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:",["help","input=","output="])
    except getopt.GetoptError:
        gemc_to_h5ad_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gemc_to_h5ad_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            ingemc = arg
        elif opt in ("-m"):
            cellmask = arg

    if ingemc == "" or prefix== "" :
        gemc_to_h5ad_usage()
        sys.exit(3)

    print("input gemc is {}".format(ingemc))
    print("output prefix is {}".format(prefix))
    if cellmask != '':
        print("cell mask file is {}".format(cellmask))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print('loading gemc now...')
    sdf = slice_dataframe()
    sdf.init_from_file(ingemc)
    if not sdf.cellbin:
        print('ERROR: input GEMC file fail to detect cellbin result. exit...',flush=True)
        sys.exit(1)
    print('prepare dataframe now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    cells, cellmap = sdf.get_cellbins()
    cellxy = sdf.getxy_cellbins()
    cellarea = sdf.getarea_cellbins()
    if sdf.spatial3d:
        cell3dxyz = sdf.get3dxyz_cellbins()
    obs = pd.DataFrame()
    obs['cellid'] = cells
    if cellmask != '':
        masks = np.loadtxt(cellmask,dtype=int,delimiter=' ')
        unique, counts = np.unique(masks, return_counts=True)
        maper = dict(zip(unique, counts))
        obs['nArea'] = obs.apply(lambda row: maper[row['cellid']],axis=1)
    obs['cellname'] = obs.apply(lambda row: f'cell{row["cellid"]}',axis=1)
    obs = obs.set_index('cellid')
    #print(obs.head(),flush=True)
    #print(cellxy.head(),flush=True)
    obs['x'] = cellxy['x']
    obs['y'] = cellxy['y']
    #print(cellarea.head(),flush=True)
    obs['nSpots'] = cellarea['nSpots']
    if sdf.spatial3d:
        obs['spatial3d_x'] = cell3dxyz['spatial3d_x']
        obs['spatial3d_y'] = cell3dxyz['spatial3d_y']
        obs['spatial3d_z'] = cell3dxyz['spatial3d_z']
    obs = obs.set_index('cellname')
    genes, genemap = sdf.get_gene_ids()
    var = pd.DataFrame()
    var['genename'] = genes
    var = var.set_index('genename')
    ngene = len(genes)
    ncell = len(cells)
    densityarray = np.zeros((ncell, ngene),dtype = int)
    for row in sdf.m_dataframe.itertuples():
        densityarray[cellmap[row.cell],genemap[row.geneID]] = densityarray[cellmap[row.cell],genemap[row.geneID]]+row.MIDCounts
    yidx,xidx = np.nonzero(densityarray)
    sparseMatrix = csr_matrix((densityarray[yidx,xidx],(yidx,xidx)), shape=(ncell,ngene))
    data = AnnData(X=sparseMatrix,dtype=sparseMatrix.dtype,obs=obs,var=var)
    data.obsm['spatial'] = obs[['x','y']].to_numpy()
    if sdf.spatial3d:
        data.obsm['spatial3d'] = obs[['spatial3d_x','spatial3d_y','spatial3d_z']].to_numpy()
    ###############################################
    # stats for UMI, Gene and Spot
    ###############################################
    num_genes = np.sum(densityarray>0,axis=1)
    num_umi = np.sum(densityarray,axis=1)
    data.obs['nGenes'] = num_genes
    data.obs['nUMI'] = num_umi
    print(f'iter done for #cell={ncell}, #gene={ngene}.',flush=True)
    print(f'total gene = {ngene}')
    print(f'total cell = {ncell}')
    print(f'average spot = {np.mean(obs["nSpots"])}')
    print(f'median spot = {np.median(obs["nSpots"])}')
    print(f'average gene = {np.mean(num_genes)}')
    print(f'median gene = {np.median(num_genes)}')
    print(f'average umi = {np.mean(num_umi)}')
    print(f'median umi = {np.median(num_umi)}')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print('save h5ad now...')
    data.write(f'{prefix}.h5ad',compression='gzip')
    print('all done')
