import sys
import time
import getopt
import json
from scipy.sparse import csr_matrix
import anndata 
import pandas as pd
import numpy as np
from anndata import AnnData


# usage

def affine_h5ad_usage():
    print("""
Usage : affine_h5ad.py -i <input.h5ad>
                -o <output.h5ad>
                -x [column of x,default new_x]
                -y [column of y,default new_y]
                -B [backward (reverse) affine matrix] 
                -F [forward affine matrix]

Sample : affine_h5ad.py -i input.h5ad \\
              -o output.h5ad \\
              -x 'new_x'    \\
              -y 'new_y'    \\
              -F '[[1,0,10],[0,1,0],[0.0, 0.0, 1.0]]'    
Notice: please provide one of [ -B , -F ], if both present, the later one will overwrite previous one.
    """,flush=True)

def affine_h5ad_main(argv:[]):
    inputh5ad=''
    prefix=''
    affine=''
    column_x='new_x'
    column_y='new_y'
    try:
        opts , args = getopt.getopt(argv,"hi:o:x:y:F:B:",["help",
                                    "input=",
                                    "output="])
    except getopt.GetoptError:
        affine_h5ad_usage()
        sys.exit(2)
    for opt,arg in opts:
        if opt in ("-h","--help"):
            affine_h5ad_usage()
            sys.exit(0)
        elif opt in ("-i","--inputtf"):
            inputh5ad=arg
        elif opt in ("-o","--output"):
            prefix=arg
        elif opt in ("-x"):
            column_x=arg
        elif opt in ("-y"):
            column_y=arg
        elif opt in ("-F",):
            affine = np.matrix(np.array(json.loads(arg)))
        elif opt in ("-B",):
            affine = np.matrix(np.array(json.loads(arg))).I
    if inputh5ad=="" or prefix=="" or affine=="":
        affine_h5ad_usage()
        sys.exit(2)
    h5ad=anndata.read(inputh5ad)
    h5adxy=np.array(h5ad.obs[["x",'y']])
    h5adxy=np.insert(h5adxy,2,values=np.ones((h5adxy.shape[0],)),axis=1)
    affine_result=np.dot(affine,h5adxy.T)[0:2,:]
    h5ad.obs[column_x]=np.array(affine_result[0:1,:].T)
    h5ad.obs[column_y]=np.array(affine_result[1:2,:].T)
    h5ad.write(prefix,compression='gzip')
