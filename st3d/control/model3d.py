import pandas as pd
import numpy as np
from st3d.control.save_miscdf import print_model3d,init_model3d
from st3d.view.model3d import html_model3d
from st3d.model.slice_xyz import slice_xyz

def update_masks(bos : pd.DataFrame, masks : np.ndarray, downsize = 10) ->np.ndarray:
    # downsize mask from bin5 to bin50
    xyz = slice_xyz(mask.shape[0],mask.shape[1] ,0,0)
    new_shape_x,new_shape_y = xyz.get_bin_wh(downsize)
    small_mask = np.zeros((new_shape_x,new_shape_y))
    small_mask1 = np.zeros((new_shape_x,new_shape_y))
    for i in range( mask.shape[0]):
        for j in range(mask.shape[1]):
            small_mask[i//downsize][j//downsize] += mask[i][j]

    for i in range( new_shape_x):
        for j in range(new_shape_y):
            if small_mask[i][j] > downsize*downsize*0.5:
                small_mask1[i][j] = 1
    return small_mask1

def build_model3d(cluster_df : pd.DataFrame,boss:{},prefix:str,mask_matrixs:{},downsize):
    init_model3d(prefix)
    slice_ids = pd.unique(cluster_df['slice'])
    datas=[]
    for sid in slice_ids:
        bos_dataframe = boss[sid]
        cdata=cluster_df.loc[cluster_df['slice']==sid]
        if sid in mask_matrixs:
            small_mask=update_masks(bos_dataframe,mask_matrixs[sid],downsize)
            bos_dataframe['masked']=small_mask.reshape(-1)
        for _, row in cdata.iterrows():
            tp=bos_dataframe.loc[bos_dataframe['bin_name']==row['bin_name']]
            if tp['masked'].tolist()[0] == 1 :
                datas.append([row['bin_name'],
                          row['slice'],
                          tp['3d_x'].tolist()[0],
                          tp['3d_y'].tolist()[0],
                          tp['3d_z'].tolist()[0],
                          row['cluster_id'],
                          row['sct_ncount']])
    df = pd.DataFrame(datas, columns=['bin_name','slice','x','y','z','cluster','sct_ncount'])
    print_model3d(df,prefix)
    html_model3d(df,prefix)
