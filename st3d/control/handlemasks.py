import numpy as np
import pandas as pd

from st3d.control.save_miscdf import create_a_folder
from st3d.view.slice2d import heatmap2D_png

def handle_one_mask(mask : np.ndarray, prefix :str, slice_index : int) :
    total = np.sum(mask)
    coords = np.zeros((total,2),dtype=int)

    height , width = mask.shape
    lid=0 
    for i in range(height):
        for j in range(width):
            if mask[i][j] == 1 :
                coords[lid][0] = j
                coords[lid][1] = i
                lid += 1
    df = pd.DataFrame(coords, columns = ['x','y'])
    df.to_csv("{}/slice_{}.csv".format(prefix,slice_index),sep=',',header=True,index=False)
    heatmap2D_png(mask,"{}/slice_{}.png".format(prefix,slice_index),width,height)

def handlemasks(masks : {} ,prefix : str) :
    create_a_folder(prefix)
    for mask_file in masks:
        slice_index = masks[mask_file]
        mask = np.loadtxt(mask_file,dtype=int,delimiter='\t')
        handle_one_mask(mask,prefix,slice_index)

