"""Model of gene-expression matrix.

One slice_dataframe object corresponding to one gem file
"""
import time
import numpy as np
import pandas as pd
from sklearn import preprocessing

"""Model for manipulate the coordinate of spots in one slice

One slice_xyz object corresponding to one gem file
"""
class slice_xyz:
    """
    Brief   :
    """

    ###########################################################################
    # Init and configuare functions 
    ##########################################################################

    def __init__(self, width : int , height : int, min_x: int , min_y : int):
        """Init the rectangle area of the slice"""
        self.spot_width = width
        self.spot_height= height
        self.spot_min_x = min_x
        self.spot_min_y = min_y

    ###########################################################################
    # overall interfaces
    ##########################################################################

    def get_bin_wh(self, binsize=50) -> (int ,int):
        draw_width = self.spot_width//binsize
        draw_height = self.spot_height//binsize
        if self.spot_width % binsize > 0:
            draw_width = draw_width + 1
        if self.spot_height % binsize > 0:
            draw_height = draw_height + 1
        return draw_width ,draw_height

    def get_bins(self,binsize=50) ->np.ndarray :
        draw_width ,draw_height = self.get_bin_wh(binsize)
        coords=np.zeros((draw_width*draw_height,2))
        for y in range(draw_height):
            for x in range(draw_width):
                index=y*draw_width+x
                bin_mid_x = x*binsize + self.spot_min_x 
                bin_mid_y = y*binsize + self.spot_min_y
                coords[index][0],coords[index][1]= bin_mid_x , bin_mid_y
        return coords

class slice_dataframe:
    """
    Brief   :
        class slice_dataframe to provide easy-access interfaces for visualization.

    Motivation  :
        most of the time we only want to see one aspect of the slice at one time.
    """

    def __init__(self): 
        self.m_dataframe=None
        self.m_xyz=None
        self.slice_index=-1

    def init_from_file(self,gem_file_name:str, slice_index):
        df = pd.read_csv(gem_file_name, sep='\t', header=0, compression='infer', comment='#')
        self.init(df,slice_index)

    def init(self, df , slice_index ):
        self.m_dataframe = df
        if len(self.m_dataframe.columns) == 4 :
            self.m_dataframe.columns = ['geneID','x','y','MIDCounts']
        elif len(self.m_dataframe.columns) == 5:
            self.m_dataframe.columns = ['geneID','x','y','MIDCounts','ExonCount']
        self.min_x=np.min(self.m_dataframe.x)
        max_x=np.max(self.m_dataframe.x)
        self.min_y=np.min(self.m_dataframe.y)
        max_y=np.max(self.m_dataframe.y)
        self.m_xyz=slice_xyz(max_x-self.min_x+1,max_y-self.min_y+1, self.min_x,self.min_y)
        self.slice_index = slice_index

    def chop(self, x1 , y1, width,height ,binsize=1) :
        new_df = slice_dataframe()
        x_coords = self.m_dataframe['x'] - self.min_x
        if binsize>1:
            x_coords = x_coords // binsize
        y_coords = self.m_dataframe['y'] - self.min_y
        if binsize>1:
            y_coords = y_coords // binsize
        coords=pd.DataFrame(x_coords,columns=['x'])
        coords['y']=y_coords
        choped_df = self.m_dataframe[ (( coords['x'] >= x1) & ( coords['x']  < x1+width  ) & (coords['y'] >= y1) & (coords['y']< y1 + height ) )]
        new_df.init(choped_df.copy(),self.slice_index)
        return new_df

    def printGEM(self,out_f):
        self.m_dataframe.to_csv(out_f,sep='\t',header=True,index=False)

    def get_expression_count_vector(self,binsize=50) -> np.ndarray:
        """
        Return : rectangar matrix with UMI counts

        Notice : this function will modify the orignial GEM dataframe
        """
        xyz = self.m_xyz
        draw_width , draw_height  = xyz.get_bin_wh(binsize)
        coords=np.zeros((draw_height,draw_width))

        df = self.m_dataframe
        df['x'] = df['x'] - df['x'].min()
        df['y'] = df['y'] - df['y'].min()
        df['x'] = (df['x'] / binsize).astype(int)
        df['y'] = (df['y'] / binsize).astype(int)
        df = df.groupby(['x', 'y']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()

        if df['x'].max() +1 != draw_width or df['y'].max() +1 != draw_height :
            print("ERROR : heatmap wh error ")
            exit(1001)

        coords[df['y'], df['x']] = df['UMI_sum']

        return coords
