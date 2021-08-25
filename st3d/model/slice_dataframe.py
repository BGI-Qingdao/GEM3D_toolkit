"""Model of gene-expression matrix.

One slice_dataframe object corresponding to one gem file
"""
import time
import numpy as np
import pandas as pd
from sklearn import preprocessing
from st3d.model.slice_xyz import slice_xyz
from st3d.model.rect_bin import bins_of_slice
import threading

class slice_meta_data:
    def __init__(self, slice_id , slice_min_x , slice_min_y, slice_width, slice_height):
        self.slice_id    = slice_id
        self.slice_min_x = slice_min_x
        self.slice_min_y = slice_min_y
        self.slice_width = slice_width
        self.slice_height= slice_height

    def assign_bininfo(self, binsize, binwidth, binheight):
        self.binsize     = binsize
        self.binwidth 	 = binwidth
        self.binheight   = binheight

        #return self


class slice_dataframe:
    """
    Brief   :
        class slice_dataframe to provide easy-access interfaces for visualization.

    Motivation  :
        most of the time we only want to see one aspect of the slice at one time.
    """

    def __init__(self,gem_file_name:str, slice_index ) :
        self.m_dataframe=pd.read_csv(gem_file_name,sep='\t')
        self.m_dataframe.columns = ['geneID','x','y','MIDCounts']
        #print("{} size of self.m_dataframe".format(len(self.m_dataframe)))
        min_x=np.min(self.m_dataframe.x)
        max_x=np.max(self.m_dataframe.x)
        min_y=np.min(self.m_dataframe.y)
        max_y=np.max(self.m_dataframe.y)
        # init slice_xyz
        self.m_xyz=slice_xyz(max_x-min_x+1,max_y-min_y+1, min_x,min_y)
        #self.m_xyz.set_alignment_info(slice_index,aff_mat)
        self.slice_index = slice_index

    def get_expression_count(self,binsize=50) -> np.ndarray:
        """
        Return : rectangar matrix with UMI counts
        """
        xyz = self.m_xyz
        draw_width , draw_height  = xyz.get_bin_wh(binsize)
        coords=np.zeros((draw_height,draw_width))
        for _,row in self.m_dataframe.iterrows():
            bin_x , bin_y = self.m_xyz.bin_coord_from_spot(row['x'],row['y'],binsize)
            coords[bin_y,bin_x]+= row['MIDCounts']
        return coords

    def get_gene_ids(self) -> []:
        """
        Return : dict {gene_name : gene_id, ...}
        """
        uniq_gene_names=self.m_dataframe['geneID'].unique().tolist()
        gene_ids={}
        for index, name in enumerate(uniq_gene_names):
            gene_ids[name]=index
        return gene_ids

    def get_bins_of_slice(self,  binsize=50):
        """
        @input  bin_min , binsize 
        @return meta data of slice , bins of slices
        """
        bos = bins_of_slice(self.slice_index,0)
        bin_w, bin_h = self.m_xyz.get_bin_wh(binsize)
        bin_xy = self.m_xyz.get_bins(binsize)
        #print(bin_xy.shape)
        bos.init_bins(bin_xy)
        slice_meta = slice_meta_data(self.slice_index,
                                     self.m_xyz.spot_min_x,
                                     self.m_xyz.spot_min_y, 
                                     self.m_xyz.spot_width,
                                     self.m_xyz.spot_height)
        slice_meta.assign_bininfo(binsize,bin_w,bin_h)
        self.slice_info = slice_meta
        #print(len(bos.bins))
        return slice_meta , bos

    def get_mtx_1( self , mtx , gen_map , bos ):
        cache={}
        for _ , row in self.m_dataframe.iterrows():
            bin_x , bin_y =self.m_xyz.bin_coord_from_spot(row['x'],row['y'],self.slice_info.binsize)
            bin_index = bin_x + bin_y*self.slice_info.binwidth
            bos.set_valid(bin_index)
            bid = bos.get_bin(bin_index).bin_id + 1
            count=row['MIDCounts']
            gid= gen_map[row['geneID']] +1
            if not bid in cache:
                cache[bid]={}
            b_cache = cache[bid]
            if gid in b_cache:
                b_cache[gid] += count
            else:
                b_cache[gid] = count

        index=0
        for bid in cache:
            for gid in cache[bid]:
                mtx.loc[index]=[gid,bid,cache[bid][gid]]
                index+=1

    def get_mtx( self, gen_map:{}, bos:bins_of_slice ) :
        mtx=pd.DataFrame(columns=('gid','bid','count'),index=range(0,len(self.m_dataframe)))
        print('#line in gem: {}, slice {}'.format(len(mtx),self.slice_index))
        print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
        self.get_mtx_1(mtx,gen_map,bos)
        mtx.dropna(inplace=True)
        print("hanle a gem : done slice {}".format(self.slice_info))
        print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
        return mtx

