import time
import math
from multiprocessing import Pool

import numpy as np

from st3d.control.save_miscdf import *
from st3d.control.load_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe
from st3d.model.slice_xyz import slice_xyz

def update_masks( mask : np.ndarray, downsize = 10) ->np.ndarray:
    # downsize mask from bin5 to bin50
    xyz = slice_xyz(mask.shape[0],mask.shape[1] ,0,0)
    new_shape_x,new_shape_y = xyz.get_bin_wh(downsize)
    small_mask = np.zeros((new_shape_x,new_shape_y))
    small_mask1 = np.zeros((new_shape_x,new_shape_y))
    for i in range( mask.shape[0]):
        for j in range(mask.shape[1]):
            small_mask[i//downsize][j//downsize] += mask[i][j]

    for i in range( new_shape_x):
        for j in range(new_shape_y):
            if small_mask[i][j] >= downsize*downsize*0.5:
                small_mask1[i][j] = 1
    return small_mask1

def gen_one_masked_bfm(args : []):
    mask_file = args[0]
    slice_index = args[1] 
    input_folder = args[2]
    prefix=args[3]
    downsize=args[4]

    # step0 : create folders
    init_gem2bfm_slice(prefix,slice_index)

    # step1 : cp unchanged files
    fromf="{}/slice_{}/slices.json".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/slices.json".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    fromf="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv.gz".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv.gz".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    fromf="{}/slice_{}/raw_feature_bc_matrix/features.tsv.gz".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/raw_feature_bc_matrix/features.tsv.gz".format(prefix ,slice_index)
    cp_file(fromf,to_f)

    # step2 : load datas
    masks = np.loadtxt(mask_file,dtype=int,delimiter='\t')
    new_masks = update_masks(masks,downsize)
    slice_info = load_slice_info("{}/slice_{}/slices.json".format(input_folder,slice_index))
    tp_data = load_slice_tissues_positions("{}/slice_{}/spatial/tissue_positions_list.csv".format(input_folder ,slice_index))
    sparse_matrix = load_sparse_matrix("{}/slice_{}/raw_feature_bc_matrix/matrix.mtx.gz".format(input_folder ,slice_index))

    # step3 : sanity check
    if slice_info.binwidth != new_masks.shape[1] or slice_info.binheight != new_masks.shape[0] :
        print("Error : mask != bin_rect for slice {}".format(slice_index))
        return

    # step4 : modify masks in tissue_possitions
    tp_data['masked']=new_masks.reshape(-1)
    print_maskbfm_tissue_positions_list(tp_data,prefix,slice_index)

    # step5 : filter sparse matrix
    g_num = sparse_matrix.columns[0]
    b_num = sparse_matrix.columns[1]
    sparse_matrix.columns = ['gid','bid','count']

    new_matrix = pd.DataFrame(columns = sparse_matrix.columns)
    index = 0
    for _ , row in sparse_matrix.iterrows() :
        tp_index = row['bid']
        if math.isnan(tp_index) :
            break
        tp_index = int(tp_index -1)
        if tp_data.loc[tp_index,'masked'] == 1 :
            new_matrix.loc[index]=[ row['gid'],row['bid'],row['count'] ]
            index+=1
    print_matrix_mtx(new_matrix,prefix,slice_index,g_num,b_num)

    # all done


def mask_bfms(masks_map,input_folder,prefix,downsize,tasks):
    create_a_folder(prefix)
    args=[]
    for mask_file in masks_map:
        slice_index = masks_map[mask_file]
        args.append([mask_file,slice_index,input_folder,prefix,downsize])
    with Pool(tasks) as p:
        p.map(gen_one_masked_bfm, args)

