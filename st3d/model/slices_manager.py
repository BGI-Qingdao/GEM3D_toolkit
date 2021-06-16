"""A datahub for one model ( like a brain or a heart ) with multiply slices.

   One slices_manager for one model.
"""

import numpy as np
from st3d.model.slice_dataframe import slice_dataframe
from st3d.model.slice_xyz import slice_xyz

class slices_manager:
    """
    Brief   :
            class to provide uniform interface for all slices in the same model.
    """

    def __init__(self):
        self.slices_num = 0
        self.slices=[]

    def add_slice(self,gem_file_name,z_index,aff_mat):
        one_slice = slice_dataframe(gem_file_name,self.slices_num,move_x,move_y,-rotate)
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
