from st3d.control.load_miscdf import *
from st3d.control.save_miscdf import *
import pandas as pd

def build_scatter3d(slices:[],input_folder:str ,prefix:str):
    create_a_folder(prefix)
    all_xyz=[]
    for x in slices :
        sid = slices[x]
        file2="{}/slice_{}/tissue_positions_list.csv".format(input_folder,sid)
        tp = load_slice_tissues_positions(file2)
        points = tp[tp['masked']==1]['bin_name','3d_x','3d_y','3d_z']
        all_xyz.append(points)

    all_points = pd.concat(all_xyz)
    all_points.to_csv("{}/bin_xyz.csv",sep=',',header=True,index=False)
    scatter_3d_html(all_points, '{}/scatter_3d.html')



