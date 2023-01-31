import sys
import time
import math
import getopt
from multiprocessing import Pool

import numpy as np

from gemtk.control.save_miscdf import *
from gemtk.control.load_miscdf import *
from gemtk.model.slice_dataframe import slice_dataframe
from gemtk.model.slice_xyz import slice_xyz
from gemtk.view.slice2d import *

def gen_one_masked_heatmap(args : []):
    mask_file = args[0]
    slice_index = args[1] 
    input_folder = args[2]
    prefix=args[3]

    # step0 : create folders
    init_heatmap_slice(prefix,slice_index)

    # step1 : cp unchanged files
    fromf="{}/slice_{}/slice.json".format(input_folder ,slice_index)
    to_f ="{}/slice_{}/slice.json".format(prefix ,slice_index)
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
        for j in range(masks.shape[1]):
            if masks[i][j] == 0 :
                heatmap[i][j]=0

    np.savetxt('{}/slice_{}/heatmatrix.txt'.format(prefix,slice_index)
             , heatmap, fmt='%d')
    heatmap2D_png(heatmap,
                  '{}/slice_{}/slice_{}.png'.format(prefix,slice_index,slice_index),
                  masks.shape[1],
                  masks.shape[0])

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

############################################################################
# section 6 : maskheatmap
#############################################################################

def maskheatmap_usage():
    print("""
Usage : GEM_toolkit.py maskheatmap  -i <input-folder>  \\
                                    -o <output-folder> \\
                                    -m <mask.json> \\
                                    -t <threads>

Notice:
        1. the input folder is output folder of heatmap action.
""")

def maskheatmap_main(argv:[]):
    input_folder = ''
    masks=''
    prefix=''
    threads=4
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:t:",["help","input=","output=","mask_cfg=","threads="])
    except getopt.GetoptError:
        maskheatmap_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            maskheatmap_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-m", "--mask_cfg"):
            masks= arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)

    if  input_folder == "" or prefix=="" or masks == "" or threads < 1 :
        maskheatmap_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("mask conf.json is {}".format(masks))
    print("working threads is {}".format(threads))

    print('loading masks...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    # masks_map
    masks_map  = load_slices(masks)
    print('gen masked heatmap (s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mask_heatmap(masks_map,input_folder,prefix,threads)
    print('gen masked heatmap (s) all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

