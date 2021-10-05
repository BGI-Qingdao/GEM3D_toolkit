import sys
import time
import getopt
from st3d.control.load_miscdf import *

import pandas as pd
import numpy as np

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



############################################################################
# section 10 : handlemasks
#############################################################################
# usage
def handlemasks_usage():
    print("""
Usage : GEM_toolkit.py handlemasks     -i masks.json  \\
                                       -o <output-folder>
""")

def handlemasks_main(argv:[]) :
    prefix=''
    maskconf=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","input=","output="])
    except getopt.GetoptError:
        handlemasks_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            handlemasks_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            maskconf = arg

    if  maskconf == "" or prefix== "" :
        handlemasks_usage()
        sys.exit(3)

    print("mask conf is {}".format(maskconf))
    print("output prefix is {}".format( prefix))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    masks = load_slices(maskconf)
    print('handle masks ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    handlemasks(masks,prefix)
    print('handle masks all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
