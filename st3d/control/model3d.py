import sys
import time
import getopt
from st3d.control.load_miscdf import *

import numpy as np
import pandas as pd
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

############################################################################
# section 4 : model3d
#############################################################################

def model3d_usage():
    print("""
Usage : GEM_toolkit.py model3d   -i <input-folder>  \\
                                 -r <cluster.txt> \\
                                 -o <output-folder> \\
                                 -d <downsize>

Notice:
        1. the input folder must be the output folder of apply_affinematrix action.
        2. the columns of cluster.txt should be \"bin_name,slice_id,cluster_id,sct_ncount\"
        3. downsize = bin size of cluster( bfm ) / bin size of heatmap
""")

def model3d_main(argv:[]):
    input_folder = ''
    c_result=''
    prefix=''
    downsize=0
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:d:",["help","input=","output=","cluster_result=","downsize="])
    except getopt.GetoptError:
        model3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            model3d_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-r", "--cluster_result"):
            c_result= arg
        elif opt in ("-d", "--downsize"):
            downsize=int(arg)
    if  input_folder == "" or prefix=="" or c_result =="" or downsize < 1:
        model3d_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("cluster result is {}".format(c_result))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format( downsize))
    print('loading datas...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    cluster_df = load_clusters(c_result)
    bin_xyz, sinfos = load_tissues_positions_bycluster(cluster_df,input_folder)
    print('gen model3d (s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    build_model3d(cluster_df,bin_xyz,sinfos,prefix,downsize)
    print('gen model3d, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

