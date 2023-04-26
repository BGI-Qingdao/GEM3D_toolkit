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

def format_colname(df):
    if len(df.columns) == 4 :
        return ['geneID','x','y','MIDCounts']
    elif len(df.columns) == 5:
        if df.columns[4] in ('cell', 'label'):
            return  ['geneID','x','y','MIDCounts','cell']
        else:
            return ['geneID','x','y','MIDCounts','ExonCount']
    elif len(df.columns) == 6:
        return ['geneID','x','y','MIDCounts','ExonCount','cell']
    elif len(df.columns) == 7:
        return ['geneID','x','y','MIDCounts','spatial3d_x','spatial3d_y','spatial3d_z']
    elif len(df.columns) == 8:
        if df.columns[4] in ('cell','label'):
            return ['geneID','x','y','MIDCounts','cell','spatial3d_x','spatial3d_y','spatial3d_z']
        else:
            return ['geneID','x','y','MIDCounts','ExonCount','spatial3d_x','spatial3d_y','spatial3d_z']
    elif len(df.columns) == 9:
        return  ['geneID','x','y','MIDCounts','ExonCount','cell','spatial3d_x','spatial3d_y','spatial3d_z']
    else:
        print('Unknow GEM(C) header, please contact guolidong@genomics.cn',flush=True)
        sys.exit(1)

class slice_dataframe:
    """
    Brief   :
        class slice_dataframe to provide easy-access interfaces for visualization.

    Motivation  :
        most of the time we only want to see one aspect of the slice at one time.
    """

    def __init__(self): 
        self.m_dataframe = None
        self.m_xyz = None
        self.cellbin = False
        self.excon = False
        self.spatial3d = False

    def init_from_file(self,gem_file_name:str, min_x = None, min_y=None):
        df = pd.read_csv(gem_file_name, sep='\t', header=0, compression='infer', comment='#')
        self.init(df,min_x,min_y)

    def init(self, df,min_x=None, min_y=None):
        self.m_dataframe = df
        if len(self.m_dataframe.columns) == 4 :
            self.m_dataframe.columns = ['geneID','x','y','MIDCounts']
        elif len(self.m_dataframe.columns) == 5:
            if self.m_dataframe.columns[4] in ('cell', 'label'):
                self.m_dataframe.columns = ['geneID','x','y','MIDCounts','cell']
                self.cellbin=True
            else:
                self.m_dataframe.columns = ['geneID','x','y','MIDCounts','ExonCount']
                self.excon=True
        elif len(self.m_dataframe.columns) == 6:
            self.m_dataframe.columns = ['geneID','x','y','MIDCounts','ExonCount','cell']
            self.cellbin=True
            self.excon=True
        elif len(self.m_dataframe.columns) == 7:
            self.m_dataframe.columns = ['geneID','x','y','MIDCounts','spatial3d_x','spatial3d_y','spatial3d_z']
            self.spatial3d=True
        elif len(self.m_dataframe.columns) == 8:
            if self.m_dataframe.columns[4] in ('cell','label'):
                self.m_dataframe.columns = ['geneID','x','y','MIDCounts','cell','spatial3d_x','spatial3d_y','spatial3d_z']
                self.cellbin=True
                self.spatial3d=True
            else:
                self.m_dataframe.columns = ['geneID','x','y','MIDCounts','ExonCount','spatial3d_x','spatial3d_y','spatial3d_z']
                self.excon=True
                self.spatial3d=True
        elif len(self.m_dataframe.columns) == 9:
            self.m_dataframe.columns = ['geneID','x','y','MIDCounts','ExonCount','cell','spatial3d_x','spatial3d_y','spatial3d_z']
            self.cellbin=True
            self.excon=True
            self.spatial3d=True
        else:
            print('Unknow GEM(C) header, please contact guolidong@genomics.cn',flush=True)
            sys.exit(1)
        if min_x is None:
            self.min_x = np.min(self.m_dataframe.x)
        else: 
            self.min_x = min_x
        max_x=np.max(self.m_dataframe.x)
        if min_y is None:
            self.min_y=np.min(self.m_dataframe.y)
        else: 
            self.min_y = min_y
        print(f'final GEM xmin = {self.min_x},final GEM ymin={self.min_y}',flush=True)
        max_y=np.max(self.m_dataframe.y)
        self.m_xyz=slice_xyz(max_x-self.min_x+1,max_y-self.min_y+1, self.min_x,self.min_y)

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
        new_df.init(choped_df.copy())
        return new_df

    def printGEM(self,out_f):
        self.m_dataframe.to_csv(out_f,sep='\t',header=True,index=False)

    def mask(self,mask_array):
        mask_array = mask_array.astype(int)
        self.m_dataframe['valid'] = self.m_dataframe.apply(lambda row: mask_array[row['y'] - self.min_y,
                                                                                  row['x'] - self.min_x],
                                                           axis=1)
        self.m_dataframe = self.m_dataframe[ self.m_dataframe['valid'] != 0 ].copy()
        self.m_dataframe = self.m_dataframe.drop(columns=['valid'])

    def get_expression_count_vector(self,binsize=50) -> np.ndarray:
        """
        Return : rectangar matrix with UMI counts

        Notice : this function will modify the orignial GEM dataframe
        """
        xyz = self.m_xyz
        draw_width , draw_height  = xyz.get_bin_wh(binsize)
        coords=np.zeros((draw_height,draw_width))
        df = self.m_dataframe
        df['x'] = df['x'] - self.min_x
        df['y'] = df['y'] - self.min_y
        if binsize > 1 :
            df['x'] = (df['x'] / binsize).astype(int)
            df['y'] = (df['y'] / binsize).astype(int)
        df = df.groupby(['x', 'y']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()
        if df['x'].max() +1 != draw_width or df['y'].max() +1 != draw_height :
            print("ERROR : heatmap wh error ")
            exit(1001)
        coords[df['y'], df['x']] = df['UMI_sum']
        return coords

    def get_gene_ids(self):
        """
        Return : [genes...], dict {gene_name : gene_id, ...}
        """
        uniq_gene_names = self.m_dataframe['geneID'].unique()
        gene_ids = {}
        for index, name in enumerate(uniq_gene_names):
            gene_ids[name] = index
        return uniq_gene_names, gene_ids

    def get_cellbins(self):
        """
        Return : [cells...], dict {cell: cell_id, ...}
        """
        uniq_cells = self.m_dataframe['cell'].unique()
        cell_ids = {}
        for index, name in enumerate(uniq_cells):
            cell_ids[name] = index
        return uniq_cells, cell_ids

    def getxy_cellbins(self):
        return self.m_dataframe.groupby('cell')[['x','y']].mean()

    def getarea_cellbins(self):
        self.m_dataframe['x_y'] = self.m_dataframe.apply(lambda row : f'{row["x"]}_{row["y"]}', axis=1)
        counts = self.m_dataframe.groupby('cell')['x_y'].nunique().reset_index(name='nSpots').set_index('cell')
        self.m_dataframe.drop('x_y', axis=1)
        return counts
           
    def get3dxyz_cellbins(self):
        return self.m_dataframe.groupby('cell')[['spatial3d_x','spatial3d_y','spatial3d_z']].mean()

    def get_bins(self,binsize=50):
        """
        Return : [genes...], dict {gene_name : gene_id, ...}
        """
        self.m_dataframe['bin_x'] = self.m_dataframe['x'] // binsize
        self.m_dataframe['bin_y'] = self.m_dataframe['y'] // binsize
        self.m_dataframe['bin_name'] = self.m_dataframe.apply(lambda row: f'{row["bin_x"]}_{row["bin_y"]}',axis=1)
        uniq_cells = self.m_dataframe['bin_name'].unique()
        cell_ids = {}
        for index, name in enumerate(uniq_cells):
            cell_ids[name] = index
        return uniq_cells, cell_ids

    def getxy_bins(self):
        return self.m_dataframe.groupby('bin_name')[['x','y']].mean()
    def get3dxyz_bins(self):
        return self.m_dataframe.groupby('bin_name')[['spatial3d_x','spatial3d_y','spatial3d_z']].mean()
