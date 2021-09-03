import pandas as pd
import numpy as np
from st3d.control.save_miscdf import print_model3d,init_model3d
from st3d.model.volumn2D import xyv_to_volumn2D
from st3d.view.model3d import html_model3d
from st3d.model.slice_xyz import slice_xyz

def build_model3d(cluster_df : pd.DataFrame, boss:{},sinfos:{},prefix, downsize:int):
    init_model3d(prefix)
    slice_ids = pd.unique(cluster_df['slice'])
    datas=pd.DataFrame(columns=('bin_name','slice','x','y','z','cluster','sct_ncount','bx','by''gid','bid','count'))

    xmin=none
    xmax=none
    ymin=none
    ymax=none

    for x in boss :
        df =  boss[sid]
        df_xmin = np.min(tp['3d_x'])
        df_ymin = np.min(tp['3d_y'])
        df_xmax = np.max(tp['3d_x'])
        df_ymax = np.max(tp['3d_y'])

        if xmin == none or df_xmin < xmin :
            xmin = df_xmin
        if ymin == none or df_ymin < ymin :
            ymin = df_ymin

        if xmax == none or df_xmax > xmax :
            xmax = df_xmax
        if ymax == none or df_ymax > ymax :
            ymax = df_ymax

    for sid in slice_ids :
        if sid in sinfos :
            bos_dataframe = boss[sid]
            cdata=cluster_df.loc[cluster_df['slice']==sid]
            sinfo=sinfos[sid]
            index=0
            valid_index=0
            mtx=pd.DataFrame(columns=('bin_name','slice','x','y','z','cluster','sct_ncount','bx','by''gid','bid','count'),index=range(0,len(cdata)))
            for _, row in cdata.iterrows():
                bin_x = index % sinfo.binwidth
                bin_y = index // sinfo.binwidth
                index+=1
                tp=bos_dataframe.loc[bos_dataframe['bin_name']==row['bin_name']]
                if tp['masked'].tolist()[0] == 1 :
                    mtx[valid_index]=[row['bin_name'],
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
            slice_volumn2D = xyv_to_volumn2D( mtx[['x','y','cluster_id']],xmin,xmax,ymin,ymax,downsize )
            fname="{}/slice_{}.png".format(sid)
            draw_slice_cluster(fname,slice_volumn2D)

    print_model3d(datas,prefix)
    html_model3d(datas,prefix,downsize)
