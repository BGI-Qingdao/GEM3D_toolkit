import sys
import time
import getopt
import numpy as np
from multiprocessing import Pool

from gemtk.control.load_miscdf import *
from gemtk.control.save_miscdf import *

from gemtk.model.slice_dataframe import slice_dataframe
from gemtk.model.rect_bin import *
from gemtk.view.slice2d import *

def assign_graph_xy(bos : bins_of_slice,binwidth:int):
    ids = np.zeros((bos.bin_num(),2))
    for i in range(0,bos.bin_num()):
        ids[i,0]= i%binwidth
        ids[i,1]= i//binwidth
    bos.assign_graph_xy_matrix(ids)

def heatmap_slice_one(data:[]):
    gem_file_name  = data[0]
    print('---------------------')
    print(gem_file_name)
    print('---------------------')
    z_index     = data[1]
    prefix      = data[2]
    binsize     = data[3]
    one_slice = slice_dataframe()
    one_slice.init_from_file(gem_file_name,z_index)

    slice_index = one_slice.slice_index
    init_heatmap_slice(prefix,slice_index)

    print("get bins of slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slice_info, bos = one_slice.get_bins_of_slice(binsize=binsize)
    #print(len(bos.bins))
    print("get mtx of slice {}...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print_slices_heatmap_json(slice_info,prefix,slice_index)
    assign_graph_xy(bos,slice_info.binwidth)
    print_heatmap_tissue_positions_list(bos,prefix,slice_index)
    heatmap_matrix = one_slice.get_expression_count_vector(binsize)
    np.savetxt('{}/slice_{}/heatmatrix.txt'.format(prefix,slice_index)
             , heatmap_matrix, fmt='%d')
    heatmap2D_png(heatmap_matrix,
                  '{}/slice_{}/slice_{}.png'.format(prefix,slice_index,slice_index),
                  slice_info.binwidth,
                  slice_info.binheight)

# multi-processing run all slices
def heatmap_slices_one_by_one(slices,prefix,binsize,tasks) :
    init_heatmap_output(prefix)
    args=[]
    #for slice_id in range(0,slices.slices_num):
    for slice_name in slices:
        z_index = slices[slice_name]
        args.append([slice_name,z_index,prefix,binsize])
    with Pool(tasks) as p:
        print(p.map(heatmap_slice_one, args))

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
