import pandas as pd
import numpy as np
from st3d.control.save_miscdf import print_model3d,init_model3d
from st3d.model.volumn2D import xyv_to_volumn2D
from st3d.view.model3d import html_model3d
from st3d.model.slice_xyz import slice_xyz
from st3d.view.slice2d import *

def build_model3d(cluster_df : pd.DataFrame, boss:{},sinfos:{},prefix, downsize:int):
    init_model3d(prefix)
    slice_ids = pd.unique(cluster_df['slice'])
    datas=pd.DataFrame(columns=('bin_name','slice','x','y','z','cluster','sct_ncount','bx','by''gid','bid','count'))

    xmin=None
    xmax=None
    ymin=None
    ymax=None

    for x in boss :
        bos =  boss[x]
        df  = bos[bos['masked']==1]
        df_xmin = np.min(df['3d_x'])
        df_ymin = np.min(df['3d_y'])
        df_xmax = np.max(df['3d_x'])
        df_ymax = np.max(df['3d_y'])

        if xmin == None or df_xmin < xmin :
            xmin = df_xmin
        if ymin == None or df_ymin < ymin :
            ymin = df_ymin

        if xmax == None or df_xmax > xmax :
            xmax = df_xmax
        if ymax == None or df_ymax > ymax :
            ymax = df_ymax

    for sid in slice_ids :
        if sid in sinfos :
            bos_dataframe = boss[sid]
            cdata=cluster_df.loc[cluster_df['slice']==sid]
            sinfo=sinfos[sid]
            index=0
            valid_index=0
            mtx=pd.DataFrame(columns=('bin_name','slice','x','y','z','cluster','sct_ncount','bx','by'),index=range(0,len(cdata)))
            for _ , row in cdata.iterrows():
                bin_x = index % sinfo.binwidth
                bin_y = index // sinfo.binwidth
                index+=1
                tp=bos_dataframe.loc[bos_dataframe['bin_name']==row['bin_name']]
                if tp['masked'].tolist()[0] == 1 :
                    mtx.loc[valid_index]=[row['bin_name'],
                              row['slice'],
                              tp['3d_x'].tolist()[0],
                              tp['3d_y'].tolist()[0],
                              tp['3d_z'].tolist()[0],
                              row['cluster_id'],
                              row['sct_ncount'],
                              bin_x,
                              bin_y]
                valid_index+=1
            mtx.dropna(inplace=True)
            datas=pd.concat([datas, mtx], ignore_index=True)
            ddata=mtx[['x','y','cluster']]
            ddata=ddata.copy()
            slice_volumn2D = xyv_to_volumn2D(ddata,xmin,xmax,ymin,ymax,downsize )
            fname="{}/slice_{}.png".format(prefix,sid)
            draw_slice_cluster(fname,slice_volumn2D)

    print_model3d(datas,prefix)
    html_model3d(datas,prefix,downsize)
