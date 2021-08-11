import time
from multiprocessing import Pool

import numpy as np

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe

def gen_one_masked_bfm(args : []):
    mask_file = args[0]
    slice_index = args[1] 
    input_folder = args[2]
    prefix=args[3]
    downsize=args[4]

    init_gem2bfm_slice(prefix,slice_index)

    fromf="{}/slice_{}/slices.json".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/slices.json".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    fromf="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv.gz".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv.gz".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    fromf="{}/slice_{}/raw_feature_bc_matrix/features.tsv.gz".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/raw_feature_bc_matrix/features.tsv.gz".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    fromf="{}/slice_{}/spatial/tissue_positions_list.csv".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/spatial/tissue_positions_list.csv".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    masks = np.loadtxt(mask_file,dtype=int,delimiter='\t')
    slice_info = load_slice_info("{}/slice_{}/slices.json".format(prefix ,slice_index))
    

def mask_bfms(masks_map,input_folder,prefix,downsize,tasks):
    create_a_folder(prefix)
    args=[]
    for mask_file in masks_map:
        slice_index = masks_map[mask_file]
        args.append([mask_file,slice_index,input_folder,prefix,downsize])
    with Pool(tasks) as p:
        p.map(gen_one_masked_bfm, args)

