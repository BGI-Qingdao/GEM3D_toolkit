import sys
import time
import numpy as np
import pandas as pd
import anndata
import math
from scipy.sparse import csr_matrix
from anndata import AnnData

class h5ad_dataframe:
    def __init__(self):
        self.h5ad_dataframe=None
        self.min_x=0
        self.min_y=0

    def h5ad_init(self,h5ad_file_name:str,min_x = None, min_y=None):
        self.h5ad_dataframe=anndata.read(h5ad_file_name)
        self.init(min_x,min_y)

    def init(self,min_x=None, min_y=None):
        if min_x is None:
            self.min_x = np.min(self.h5ad_dataframe.obs.x)
        else: 
            self.min_x = min_x
        if min_y is None:
            self.min_y=np.min(self.h5ad_dataframe.obs.y)
        else: 
            self.min_y = min_y
    
    def mask(self,mask_array):
        mask_array = mask_array.astype(int)
        self.h5ad_dataframe.obs['valid'] = self.h5ad_dataframe.obs.apply(lambda row: mask_array[math.ceil(row['x']- self.min_y),
                                                                          math.ceil(row['y'] - self.min_x)],axis=1)
        self.h5ad_dataframe = self.h5ad_dataframe[self.h5ad_dataframe.obs['valid']!=0,:]
        self.h5ad_dataframe.obs= self.h5ad_dataframe.obs.drop(columns=['valid'])

    def printH5ad(self,out_f):
        self.h5ad_dataframe.write(out_f,compression='gzip')