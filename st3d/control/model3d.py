import pandas as pd
import numpy as np
from st3d.control.save_miscdf import print_model3d,init_model3d
from st3d.view.model3d import html_model3d

def build_model3d(cluster_df : pd.DataFrame,boss:{},prefix:str):
    init_model3d(prefix)
    slice_ids = pd.unique(cluster_df['slice'])
    datas=[]
    for sid in slice_ids:
        bos_dataframe = boss[sid]
        cdata=cluster_df.loc[cluster_df['slice']==sid]
        for _, row in cdata.iterrows():
            tp=bos_dataframe.loc[bos_dataframe['bin_name']==row['bin_name']]
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
