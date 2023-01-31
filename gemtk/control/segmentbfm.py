import sys
import time
import math
import getopt
from multiprocessing import Pool

import numpy as np
import pandas as pd

from  gemtk.control.save_miscdf import *
from  gemtk.control.load_miscdf import *

def segment_one_bfm(argv :[]):
    segmentations = argv[0]
    bfm_folder = argv[1]
    affine_folder = argv[2]
    prefix = argv[3]
    slice_index = argv[4]
    names = segmentations.columns
    names = names.tolist()

    sparse_matrix = load_sparse_matrix("{}/slice_{}/raw_feature_bc_matrix/matrix.mtx.gz".format(bfm_folder,slice_index))
    g_num = sparse_matrix.columns[0]
    b_num = sparse_matrix.columns[1]
    sparse_matrix.columns = ['gid','bid','count']
    tpfile='{}/slice_{}/tissue_positions_list.csv'.format(affine_folder,slice_index)
    tpm = load_slice_tissues_positions(tpfile)

    for name in names:
        prefix_n  = '{}/{}'.format(prefix,name)
        init_gem2bfm_slice(prefix_n,slice_index)
        # step1 : cp unchanged files
        fromf="{}/slice_{}/slices.json".format(bfm_folder,slice_index)
        to_f ="{}/slice_{}/slices.json".format(prefix_n,slice_index)
        cp_file(fromf,to_f)

        fromf="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv.gz".format(bfm_folder,slice_index)
        to_f ="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv.gz".format(prefix_n,slice_index)
        cp_file(fromf,to_f)

        fromf="{}/slice_{}/raw_feature_bc_matrix/features.tsv.gz".format(bfm_folder ,slice_index)
        to_f ="{}/slice_{}/raw_feature_bc_matrix/features.tsv.gz".format(prefix_n,slice_index)
        cp_file(fromf,to_f)

        # step2 : update masks
        tpm1 = tpm.copy()
        tpm1.loc[(tpm['3d_x']<=segmentations.loc['min-x',name]), 'masked'] = 0
        tpm1.loc[(tpm['3d_x']>=segmentations.loc['max-x',name]), 'masked'] = 0
        tpm1.loc[(tpm['3d_y']<=segmentations.loc['min-y',name]), 'masked'] = 0
        tpm1.loc[(tpm['3d_y']>=segmentations.loc['max-y',name]), 'masked'] = 0
        print_maskbfm_tissue_positions_list(tpm1,prefix_n,slice_index)

        # step3 : filter bfm
        tpm1['binid']=np.arange(1,int(b_num)+1)
        valid_bids=tpm1[tpm1['masked']==1]['binid']
        new_matrix = sparse_matrix[sparse_matrix['bid'].isin(valid_bids)]
        new_matrix.index = range(len(new_matrix.index))
        print_matrix_mtx(new_matrix,prefix_n,slice_index,g_num,b_num)

    print("end segment bfm for slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

def segmentbfm( slices : {} , 
                segmentations : pd.DataFrame,
                bfm_folder : str ,
                affine_folder: str ,
                prefix : str ,
                tasks : int):
    names = segmentations.columns
    names = names.tolist()

    create_a_folder(prefix)
    for name in names:
        create_a_folder('{}/{}'.format(prefix,name))
    args=[]
    for slice_name in slices:
        slice_index = slices[slice_name]
        args.append([segmentations,bfm_folder,affine_folder,prefix,slice_index])
    with Pool(tasks) as p:
        p.map(segment_one_bfm, args)


############################################################################
# section 8 : segmentbfm
#############################################################################
# usage
def segmentbfm_usage():
    print("""
Usage : GEM_toolkit.py segmentbfm   -i <bfm-folder>  \\
                                    -a <affine-folder> \\
                                    -c <conf.json> \\
                                    -s <segmentations.csv> \\
                                    -o <output-folder> \\
                                    -t <threads>
""")

def segmentbfm_main(argv:[]) :
    bfm_folder = ''
    affine_folder = ''
    prefix=''
    conf=''
    segconf=''
    threads=0
    try:
        opts, args = getopt.getopt(argv,"hi:a:o:c:s:t:",["help",
                                                         "bfm=",
                                                         "affine=",
                                                         "output=",
                                                         "conf=",
                                                         "tasks=",
                                                         "segs="])
    except getopt.GetoptError:
        segmentbfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            segmentbfm_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-a", "--affine"):
            affine_folder = arg
        elif opt in ("-i", "--bfm"):
            bfm_folder = arg
        elif opt in ("-c", "--conf"):
            conf = arg
        elif opt in ("-s", "--segs"):
            segconf = arg
        elif opt in ("-t", "--tasks"):
            threads = int(arg)

    if  (affine_folder == "" or
        bfm_folder == "" or 
        prefix=="" or
        conf == "" or
        threads < 1 or
        segconf == "" ):

        segmentbfm_usage()
        sys.exit(3)

    print("bfm folder is {}".format( bfm_folder))
    print("affine folder is {}".format( affine_folder))
    print("output prefix is {}".format( prefix))
    print("conf file is {}".format(conf))
    print("threads is {}".format(threads))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slices = load_slices(conf)
    segs = load_segmentations(segconf)
    print('segment bfm...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    segmentbfm(slices,segs,bfm_folder,affine_folder,prefix,threads)
    print('segment bfm all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
