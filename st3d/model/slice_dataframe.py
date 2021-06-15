"""Model of gene-expression matrix.

One slice_dataframe object corresponding to one gem file
"""

import numpy as np
import pandas as pd
from sklearn import preprocessing
from  st3d.model.slice_xyz import slice_xyz

class slice_dataframe:
    """
    Brief   :
        class slice_dataframe to provide easy-access interfaces for visualization.

    Motivation  :
        most of the time we only want to see one aspect of the slice at one time.
    """

    def __init__(self,gem_file_name:str, slice_index : int  , move_x =0  , move_y=0 , rotate=0 ):
        self.m_dataframe=pd.read_csv(gem_file_name,sep='\t')
        min_x=np.min(self.m_dataframe.x)
        max_x=np.max(self.m_dataframe.x)
        min_y=np.min(self.m_dataframe.y)
        max_y=np.max(self.m_dataframe.y)
        # init slice_xyz
        self.m_xyz=slice_xyz(max_x-min_x+1,max_y-min_y+1, min_x,max_y)
        self.m_xyz.set_alignment_info(slice_index,move_x,move_y,rotate)
        # init mask
        self.m_mask = np.zeros((self.m_xyz.spot_width,self.m_xyz.spot_height))
        #print(self.m_mask.shape)
        for _,row in self.m_dataframe.iterrows():
            slice_x , slice_y = self.m_xyz.slice_index_from_spot(row['x'],row['y'])
            self.m_mask[slice_x,slice_y]=1

    def get_mask(self,binsize=50) -> np.ndarray:
        """
        Return : rectangar matrix with 1 for valid spot, 0 for invalid spot
        """
        if binsize == 1:
            return self.m_mask.copy()
        else :
            xyz = self.m_xyz
            draw_width , draw_height  = xyz.get_bin_wh(binsize)
            coords=np.zeros((draw_width,draw_height))

            for x in range(xyz.spot_width):
                for y in range(xyz.spot_height):
                    if self.m_mask[x,y] == 1 : 
                        bin_x = x // binsize 
                        bin_y = y // binsize
                        coords[bin_x,bin_y]=1
            return coords

    def get_expression_count(self,binsize=50) -> np.ndarray:
        """
        Return : rectangar matrix with UMI counts
        """
        xyz = self.m_xyz
        draw_width , draw_height  = xyz.get_bin_wh(binsize)
        coords=np.zeros((draw_height,draw_width))
        for _,row in self.m_dataframe.iterrows():
            x , y = self.m_xyz.slice_index_from_spot(row['x'],row['y'])
            bin_x = x // binsize
            bin_y = y // binsize
            coords[bin_y,bin_x]+= row['MIDCounts']
        return coords

    def get_mask3d(self,binsize=50) -> np.ndarray:
        """
        Return :  (x,y,z) coords for all valid spots
        """
        mask_value = self.get_mask(binsize)
        mask_coord = self.m_xyz.model3D_coordinate_of_slice(binsize)
        return mask_coord[mask_value.reshape(-1)==1,:]

    def get_expression_count2d(self,binsize=50) -> np.ndarray:
        """
        Return :  (x,y,z,v) matrix for all valid spots. v represent total UMI number.
        """
        mask_value = self.get_expression_count(binsize)
        #return mask_value;
        mask_coord = self.m_xyz.model2D_coordinate_of_slice(binsize)
        data_array = np.hstack( ( mask_coord,mask_value.reshape(-1,1) ) )
        np.savetxt("test.txt",data_array,"%d")
        return data_array

    def get_expression_count3d(self,binsize=50) -> np.ndarray:
        """
        Return :  (x,y,z,v) matrix for all valid spots. v represent total UMI number.
        """
        mask_value = self.get_expression_count(binsize)
        mask_value = mask_value.reshape(-1)
        mask_value = preprocessing.normalize([mask_value])
        mask_value *=1000
        mask_value = mask_value.astype(int)
        mask_coord = self.m_xyz.model3D_coordinate_of_slice(binsize)
        
        data_array = np.hstack( ( mask_coord,mask_value.reshape(-1,1) ) )
        return data_array[mask_value.reshape(-1)>0,:]

    def get_xyz(self) -> slice_xyz:
        return self.m_xyz

    def get_gene(gene_name : str) -> np.ndarray :
        """
        Return : rectangar matrix with gene expression value
        """
        #TODO

    def get_factor(factor_item) -> np.ndarray :
        """
        Return : rectangar matrix with factor strength value
        """
        #TODO
