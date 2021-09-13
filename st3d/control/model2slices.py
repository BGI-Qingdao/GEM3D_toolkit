import numpy as np
import pandas as pd
from st3d.control.save_miscdf import create_a_folder
from st3d.view.slice2d import *
from st3d.model.volumn2D import *

def model2slices(xyz,prefix,downsize):
    xyz = xyz.astype(int)
    max_x = xyz['x'].max()
    min_x = xyz['x'].min()
    max_y = xyz['y'].max()
    min_y = xyz['y'].min()
    print("min_x :".format(min_x))
    print("min_y :".format(min_y))
    print("max_x :".format(max_x))
    print("max_y :".format(max_y))
    uniq_z = np.unique(xyz['z'])

    create_a_folder(prefix)
    for x in uniq_z :
        slice_id = x // downsize
        #if 'cluster' in xyz.columns:
        #    ddata=xyz[xyz['z']==x][['x','y','cluster']]
        #    ddata=ddata.copy()
        #else:
        ddata=xyz[xyz['z']==x][['x','y']]
        ddata=ddata.copy()
        ddata['v']=np.ones(len(ddata))

        slice_volumn2D = xyv_to_volumn2D(ddata,min_x,max_x,min_y,max_y,downsize )
        fname="{}/slice_{}.png".format(prefix,slice_id)
        draw_slice_cluster(fname,slice_volumn2D)
