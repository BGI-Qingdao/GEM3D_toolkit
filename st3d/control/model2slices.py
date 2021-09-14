import numpy as np
import pandas as pd
from st3d.control.save_miscdf import create_a_folder
from st3d.view.slice2d import *
from st3d.model.volumn2D import *

def model2slices(xyz,prefix,downsize,max_x,min_x,max_y,min_y):
    xyz = xyz.astype(int)
    max_x =int(max_x) 
    min_x =int(min_x) 
    max_y =int(max_y) 
    min_y =int(min_y) 
    print("min_x :{}".format(min_x))
    print("min_y :{}".format(min_y))
    print("max_x :{}".format(max_x))
    print("max_y :{}".format(max_y))
    uniq_z = np.unique(xyz['z'])

    create_a_folder(prefix)
    for x in uniq_z :
        slice_id = x // downsize
        ddata=xyz[xyz['z']==x][['x','y']]
        ddata=ddata.copy()
        ddata['v']=np.ones(len(ddata))
        slice_volumn2D = xyv_to_volumn2D(ddata,min_x,max_x,min_y,max_y,downsize )
        fname="{}/slice_{}.png".format(prefix,slice_id)
        heatmap2D_png(slice_volumn2D,fname,slice_volumn2D.shape[1],slice_volumn2D.shape[0])
