import time
import math
from multiprocessing import Pool

import numpy as np

from st3d.control.save_miscdf import *
from st3d.control.load_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe
from st3d.model.slice_xyz import slice_xyz

def gen_one_masked_heatmap(args : []):
    mask_file = args[0]
    slice_index = args[1] 
    input_folder = args[2]
    prefix=args[3]

    # step0 : create folders
    init_heatmap_slice(prefix,slice_index)

    # step1 : cp unchanged files
    fromf="{}/slice_{}/slices.json".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/slices.json".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    # step2 : load datas
    masks = np.loadtxt(mask_file,dtype=int,delimiter='\t')
    heatmap = np.loadtxt("{}/slice_{}/heatmatrix.txt".format(input_folder ,slice_index),delimiter=' ')
    tp_data = load_slice_tissues_positions("{}/slice_{}/tissue_positions_list.csv".format(input_folder ,slice_index))

    # step3 : sanity check
    if  heatmap.shape[0] != masks.shape[0] or heatmap.shape[1] !=  masks.shape[1]:
        print("Error : mask != heatmap for slice {}".format(slice_index))
        return

    # step4 : modify masks in tissue_possitions
    tp_data['masked']=masks.reshape(-1)
    print_tp_after_affine(tp_data,prefix,slice_index)
    # step5 : filter heatmap
    for i in range(masks.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i][j] == 0 :
                heatmap[i][j]=0

    np.savetxt('{}/slice_{}/heatmatrix.txt'.format(prefix,slice_index)
             , heatmap, fmt='%d')
    heatmap2D_png(heatmap,
                  '{}/slice_{}/heatmap.png'.format(prefix,slice_index),
                  masks.shape[0],
                  masks.shape[1])

    print("mask heatmap done for slice {}...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    # all done


def mask_heatmap(masks_map,input_folder,prefix,tasks):
    create_a_folder(prefix)
    args=[]
    for mask_file in masks_map:
        slice_index = masks_map[mask_file]
        args.append([mask_file,slice_index,input_folder,prefix])
    with Pool(tasks) as p:
        p.map(gen_one_masked_heatmap, args)

