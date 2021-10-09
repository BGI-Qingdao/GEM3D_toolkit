import sys
import time
import getopt
from st3d.control.load_miscdf import *

from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe

############################################################################
# logic codes
#############################################################################
def gem2bfm_one_slice(data:[]):
    gem_file_name  = data[0]
    z_index     = data[1]
    #one_slice   = data[0]
    prefix      = data[2]
    binsize     = data[3]

    one_slice = slice_dataframe()
    one_slice.init_from_file(gem_file_name,z_index)
    slice_index = one_slice.slice_index
    init_gem2bfm_slice(prefix,slice_index)

    print("build gene maps for slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    gene_maps = one_slice.get_gene_ids()

    print("get bins of slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slices_info, bos = one_slice.get_bins_of_slice(binsize=binsize)

    print("get mtx of slice {}...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mtx = one_slice.get_mtx(gene_maps,bos)

    print('save slice {} data ...'.format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print_features_tsv(gene_maps.keys(),prefix,slice_index)
    print_barcodes_tsv(bos ,prefix,slice_index)
    print_tissue_positions_list(bos,prefix,slice_index)
    print_gem2bfm_slices_json(slices_info,prefix,slice_index)
    print_matrix_mtx(mtx,prefix,slice_index,len(gene_maps),bos.bin_num())
    print('gem2bfm done for {}'.format(slice_index))

# multi-processing run all slices
def gem2bfm_slices_one_by_one(slices,prefix,binsize=50,tasks=8):
    init_gem2bfm_output(prefix)
    args=[]
    #for slice_id in range(0,slices.slices_num):
    for slice_name in slices:
        z_index = slices[slice_name]
        #one_slice = slices.slices[slice_id]
        args.append([slice_name,z_index,prefix,binsize])
    with Pool(tasks) as p:
        p.map(gem2bfm_one_slice, args)


############################################################################
# section 1 : gem2bfm
#############################################################################

# usage of gem2bfm
def gem2bfm_usage():
    print("""
Usage : GEM_toolkit.py gem2bfm -c <config.json> \\
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

