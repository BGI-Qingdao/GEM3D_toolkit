"""A datahub for one model ( like a brain or a heart ) with multiply slices.

   One slices_manager for one model.
"""

import numpy as np
import pandas as pd
from multiprocessing import Pool
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
        #xyz = one_slice.get_xyz()
        self.slices_num=self.slices_num+1

