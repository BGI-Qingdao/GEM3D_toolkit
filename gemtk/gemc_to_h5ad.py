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
Usage : GEM_toolkit.py gem_to_h5ad  -i <xxx.gemc>  \\
                                    -o <prefix> \\
""")

def gemc_to_h5ad_main(argv:[]):
    prefix=''
    ingemc=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","input=","output="])
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

    if ingemc == "" or prefix== "" :
        gemc_to_h5ad_usage()
        sys.exit(3)

    print("input gemc is {}".format(ingemc))
    print("output prefix is {}".format(prefix))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print('loading gemc now...')
    sdf = slice_dataframe()
    sdf.init_from_file(ingemc)
    if not sdf.cellbin:
        print('ERROR: input GEMC file fail to detect cellbin result. exit...',flush=True)
        sys.exit(1)
    print('prepare dataframe now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    genes, genemap = sdf.get_gene_ids()
    cells, cellmap = sdf.get_cellbins()
    obs = pd.DataFrame()
    obs['cellid'] = cells
    obs['cellname'] = obs.apply(lambda row: f'cell{row["cellid"]}',axis=1)
    obs = obs.set_index('cellname')
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
    data = AnnData(X=sparseMatrix,obs=obs,var=var)
    print(f'iter done for #cell={ncell}, #gene={ngene}.',flush=True)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print('save h5ad now...')
    data.write(f'{prefix}.h5ad',compression='gzip')
    print('chopgems all done')