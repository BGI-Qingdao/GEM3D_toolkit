"""A datahub for one model ( like a brain or a heart ) with multiply slices.

   One slices_manager for one model.
"""

import numpy as np
import pandas as pd
from st3d.model.slice_dataframe import slice_dataframe
from st3d.model.slice_xyz import slice_xyz
from st3d.model.rect_bin import bins_of_slices

class slices_manager:
    """
    Brief   :
            class to provide uniform interface for all slices in the same model.
    """

    def __init__(self):
        self.slices_num = 0
        self.slices=[]

    def add_slice(self,gem_file_name,z_index):
        one_slice = slice_dataframe(gem_file_name,z_index)
        self.slices.append(one_slice)
        xyz = one_slice.get_xyz()
        self.slices_num=self.slices_num+1

    def get_masks3d(self,binsize=50) -> np.ndarray:
        tmp_datas=[]
        for one_slice in self.slices:
            tmp_datas.append( one_slice.get_mask3d(binsize) )
        return np.vstack(tmp_datas)

    def get_borders3d(self) -> []:
        tmp_datas=[]
        for one_slice in self.slices:
            tmp_datas.append( one_slice.m_xyz.border3D_coordinate_of_slice() )
        return tmp_datas

    def get_expression_count3d(self,binsize=50) -> np.ndarray:
        tmp_datas=[]
        for one_slice in self.slices:
            tmp_datas.append( one_slice.get_expression_count3d(binsize) )
        return np.vstack(tmp_datas)

    def get_expression_count2d(self,slice_id : int , binsize=50) -> np.ndarray:
        return self.slices[slice_id].get_expression_count2d(binsize)

    def get_uniq_genes(self) -> [] :
        tmp_datas=[]
        for one_slice in self.slices:
            tmp_datas=tmp_datas+one_slice.get_uniq_genes()
        return list(set(tmp_datas))

    def get_bins_of_slices(self, binsize=50):
        bsos = bins_of_slices()
        meta_of_bins = {}
        for one_slice in self.slices:
            mtb, bos = one_slice.get_bins_of_slice(bsos.bin_num,binsize)
            bsos.add_slice(mtb.slice_id,bos)
            meta_of_bins[mtb.slice_id]=mtb
        return meta_of_bins , bsos

    def get_mtx(self, gen_map, bin_info,threads=4):
        valid_bin_num = 0 ;
        items_num = 0
        mtx=pd.DataFrame(columns=('gid','bid','count'))
        for one_slice in self.slices:
            new_mtx, new_valid_bin_num  = one_slice.get_mtx(gen_map,
                                               bin_info.get_slice(one_slice.slice_index),
                                               threads)
            #print(len(new_mtx))
            valid_bin_num +=new_valid_bin_num
            mtx=pd.concat([mtx,new_mtx])

        items_num =len(mtx)
        #print(items_num)
        return mtx , valid_bin_num ,items_num
