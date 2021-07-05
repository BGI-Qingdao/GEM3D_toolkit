"""Model of gene-expression matrix.

One slice_dataframe object corresponding to one gem file
"""
import time
import numpy as np
import pandas as pd
from sklearn import preprocessing
from st3d.model.slice_xyz import slice_xyz
from st3d.model.rect_bin import bins_of_slice
#from  _thread import *
import threading

#from multiprocessing import Pool

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

class muti_thread_helper(threading.Thread):
    def __init__(self, slice_data,gen_map,bos,mtx, thread_id:int, threads:int):
        threading.Thread.__init__(self)
        self.slice_data = slice_data
        self.gene_map   = gen_map
        self.bos        = bos
        self.mtx        = mtx
        self.thread_id  = thread_id
        self.threads    = threads

    def run(self):
        for i in range(self.thread_id ,len(self.slice_data.m_dataframe),self.threads):
            row=self.slice_data.m_dataframe.loc[i]
            bin_x,bin_y,bin_index=self.slice_data.m_xyz.bin_coord_from_spot(
                row['x'],
                row['y'],
                self.slice_data.slice_info.binsize,
                self.slice_data.slice_info.binwidth)

            self.bos.set_valid(bin_index)
            bid = self.bos.get_bin(bin_index).bin_id
            count=row['MIDCounts']
            gid=self.gene_map[row['geneID']]
            self.mtx.loc[i]=[gid,bid,count]

class slice_dataframe:
    """
    Brief   :
        class slice_dataframe to provide easy-access interfaces for visualization.

    Motivation  :
        most of the time we only want to see one aspect of the slice at one time.
    """

    def __init__(self,gem_file_name:str, slice_index ):
        self.m_dataframe=pd.read_csv(gem_file_name,sep='\t')
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
        #np.savetxt("test.txt",data_array,"%d")
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

    def get_gene(self,gene_name : str) -> np.ndarray :
        """
        Return : rectangar matrix with gene expression value
        """
        #TODO
    def get_uniq_genes(self) -> []:
        return self.m_dataframe['geneID'].unique().tolist()

    def get_factor(self,factor_item) -> np.ndarray :
        """
        Return : rectangar matrix with factor strength value
        """
        #TODO

    def get_bins_of_slice(self,  bin_min :int,binsize=50):
        """
        @input  bin_min , binsize 
        @return meta data of slice , bins of slices
        """
        bos = bins_of_slice(self.slice_index,bin_min)
        bin_w, bin_h = self.m_xyz.get_bin_wh(binsize)
        bin_xy = self.m_xyz.get_bins(binsize)
        bos.init_bins(bin_xy)
        slice_meta = slice_meta_data(self.slice_index,
                                     self.m_xyz.spot_min_x,
                                     self.m_xyz.spot_min_y, 
                                     self.m_xyz.spot_width,
                                     self.m_xyz.spot_height)
        slice_meta.assign_bininfo(binsize,bin_w,bin_h)
        self.slice_info = slice_meta
        return slice_meta , bos

    def get_mtx( self, gen_map, bos:bins_of_slice ,threads=4) :
        mtx=pd.DataFrame(columns=('gid','bid','count'),index=range(0,len(self.m_dataframe)))
        print("hanle a gem : foreach in {} threads".format(threads))
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        #print(mtx.loc[0])
        #print(mtx.loc[1])
        #mhelper = muti_thread_helper(self,gen_map,bos,mtx)
        #with Pool(threads) as p:
        #    p.map(mhelper,range(0,len(self.m_dataframe)))
        works=[]
        for i in range(0,threads):
            t=muti_thread_helper(self,gen_map,bos,mtx,i,threads)
            t.start()
            works.append(t)
        for x in works:
            x.join()
        #print(mtx.loc[0])
        #print(mtx.loc[1])
        #print(mtx.loc[100])
        #print('mtx length  : {}'.format(len(mtx)))
        print('hanle a gem : groupby ')
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        mtx=mtx.groupby(['gid','bid']).agg({'count': ['sum']}).reset_index()
        print('mtx length  : {}'.format(len(mtx)))
        mtx.columns=['gid','bid','count']
        print('hanle a gem : done')
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        return mtx,bos.valid_bin_num()

