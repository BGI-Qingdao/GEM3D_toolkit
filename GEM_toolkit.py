#!/usr/bin/env python3

import sys
import getopt
import time

from st3d.control.load_slices import *
from st3d.control.gem2bfm import gem2bfm_slices_one_by_one
from st3d.control.gem2heatmap import heatmap_slices_one_by_one
from st3d.control.apply_affinematrix import affine_one_by_one
from st3d.control.model3d import build_model3d
############################################################################
# section 1 : gem2bfm
#############################################################################

# usage of gem2bfm
def gem2bfm_usage():
    print("""
Usage : GEM_toolkit.py gem2bcm -c <config.json> \\
                               -o <output-folder>  \\
                               -b [bin-size (default 50)] \\
                               -t [threads (default 8)]

Notice : Since one gem file will be handled only in one thread,
         there is no need to set -t greater than slice number.
""")

# main of gem2bfm
def gem2bfm_main(argv):
    config = ''
    prefix = ''
    binsize= 50
    threads=8
    try:
        opts, args = getopt.getopt(argv,"hc:o:b:t:",["help","iconf=","ofile=","bin=","threads="])
    except getopt.GetoptError:
        gem2bfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem2bfm_usage()
            sys.exit(0)
        elif opt in ("-b", "--bin"):
            binsize = int(arg)
        elif opt in ("-c", "--iconf"):
            config = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)
        elif opt in ("-o", "--ofile"):
            prefix = arg

    if config == "" or prefix == "" or binsize<1 or threads <1:
        gem2bfm_usage()
        sys.exit(3)

    print("config file is {}".format(config))
    print("output prefix is {}".format( prefix))
    print("binsize is {}".format(binsize))
    print("threads is {}".format(threads))

    print('start loading slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slice_data = load_slices(config)
    print('handle slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    gem2bfm_slices_one_by_one(slice_data,prefix,binsize,threads)
    print('gem2bfm, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 2 : heatmap
#############################################################################
def heatmap_usage():
    print("""
Usage : GEM_toolkit.py heatmap  -c <conf.json> \\
                                -o <output-folder>  \\
                                -b [binsize (default 5)] \\
                                -t [threads (default 8)]

Notice : Since one gem file will be handled only in one thread,
         ther is no need to set -t greater than slice number.
""")

def heatmap_main(argv:[]):
    config = ''
    prefix = ''
    binsize= 5
    threads=8
    try:
        opts, args = getopt.getopt(argv,"hc:o:b:t:",["help","iconf=","ofile=","bin=","threads="])
    except getopt.GetoptError:
        heatmap_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            heatmap_usage()
            sys.exit(0)
        elif opt in ("-b", "--bin"):
            binsize = int(arg)
        elif opt in ("-c", "--iconf"):
            config = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)
        elif opt in ("-o", "--ofile"):
            prefix = arg
    if config == "" or prefix == "" or binsize<1 or threads <1:
        heatmap_usage()
        sys.exit(3)

    print('start loading slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    slice_data = load_slices(config)
    print('handle slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    heatmap_slices_one_by_one(slice_data,prefix,binsize,threads)
    print('heatmap, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))

############################################################################
# section 3 : apply_affinematrix
#############################################################################
def affine_usage():
    print("""
Usage : GEM_toolkit.py apply_affinematrix -c <affinematix.conf.json> \\
                                          -i <input-folder> \\
                                          -o <output-folder> \\
                                          -b [binsize(default 5)]> \\
                                          -t [threads(default 8)]
Notice:
        1. the input folder must be the output folder of gem2bfm action.
        2. the binsize must be the binsize used in heatmap action.
""")

def affine_main(argv:[]):
    config = ''
    input_folder = ''
    prefix=''
    binsize=5
    threads=8
    try:
        opts, args = getopt.getopt(argv,"hc:i:o:b:t:",["help","iconf=","input=","output=","bin=","threads="])
    except getopt.GetoptError:
        affine_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            affine_usage()
            sys.exit(0)
        elif opt in ("-b", "--bin"):
            binsize = int(arg)
        elif opt in ("-c", "--iconf"):
            config = arg
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)
        elif opt in ("-i", "--input"):
            input_folder = arg
    if config == "" or input_folder == "" or binsize<1 or threads <1:
        affine_usage()
        sys.exit(3)

    print("config file is {}".format(config))
    print("input prefix is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("binsize is {}".format(binsize))
    print("threads is {}".format(threads))

    print('loading datas...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    affines = load_affines(config)
    slice_info , boss = load_tissues_positions(affines,input_folder)
    print('apply affine matrix(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    affine_one_by_one(affines,slice_info,boss,prefix,binsize,threads)
    print('apply affine matix, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 4 : model3d
#############################################################################

def model3d_usage():
    print("""
Usage : GEM_toolkit.py model3d   -i <input-folder>  \\
                                 -r <cluster.txt> \\
                                 -o <output-folder> \\
                                 -m [mask-folder] \\
                                 -d [downsize]

Notice:
        1. the input folder must be the output folder of apply_affinematrix action.
        2. the columns of cluster.txt should be \"bin_name,slice_id,cluster_id,sct_ncount\"
        3. downsize = bin size of cluster / bin size of mask
""")

def model3d_main(argv:[]):
    input_folder = ''
    c_result=''
    masks=''
    prefix=''
    downsize=0
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:m:d:",["help","input=","output=","cluster_result=","masks=","downsize="])
    except getopt.GetoptError:
        model3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            model3d_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-m", "--masks"):
            masks= arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-r", "--cluster_result"):
            c_result= arg
        elif opt in ("-d", "--downsize"):
            downsize=int(arg)
    if  input_folder == "" or prefix=="" or c_result =="":
        model3d_usage()
        sys.exit(3)
    if masks != "" and downsize == 0 :
        print(" please set -d with -m ! exit ...")
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("cluster result is {}".format(c_result))
    print("output prefix is {}".format( prefix))
    if masks != '' :
        print("mask folder is {}".format(masks))
        print("downsize is {}".format(downsize))


    print('loading datas...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    cluster_df = load_clusters(c_result)
    mask_matrixs={}
    if masks != '' :
        load_masks(masks,cluster_df,mask_matrixs)
    bin_xyz = load_tissues_positions_bycluster(cluster_df,input_folder)
    print('apply affine matrix(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    build_model3d(cluster_df,bin_xyz,prefix,mask_matrixs,downsize)
    print('apply affine matix, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 5 : main
#############################################################################

# usage
def main_usage():
    print("""
Usage : GEM_toolkit.py action [options ]

Action:

    -----------------------------------------------------------------

    gem2bfm                 convert GEM into BFM.
    heatmap                 heatmap of expression counts.
    apply_affinematrix      apply affinematrix to add 3D (x,y,z)
                            coordinates into tissue-position-list.csv.
    model3d                 join cluster results with (x,y,z) coord
                            and visualize by interactive html.
    -----------------------------------------------------------------

    -h/--help               show this short usage
    -----------------------------------------------------------------
""")

# logic codes
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ( "-h" , "--help" ):
        main_usage()
        exit(0)
    elif len(sys.argv) < 2 or not sys.argv[1] in ("gem2bfm","heatmap","apply_affinematrix","model3d"):
        main_usage()
        exit(1)
    elif sys.argv[1] == "gem2bfm" :
        gem2bfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "heatmap" :
        heatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_affinematrix" :
        affine_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "model3d":
        model3d_main(sys.argv[2:])
        exit(0)
    else:
        main_usage()
        exit(1)
