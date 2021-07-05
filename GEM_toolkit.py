#!usr/bin/env python3

import sys
import getopt 
import json
import time

from st3d.view.model3d import * 
from st3d.view.slice2d import *

from st3d.control.global_instances import *
from st3d.control.load_slices import *
from st3d.control.save_miscdf import *

############################################################################
# section 1 : gem2bfm
#############################################################################

# usage of gem2bfm
def gem2bfm_usage():
    print("""
Usage : GEM_toolkit.py gem2bcm -c <config.json> \\
                               -o <output-prefix>  \\
                               -b [bin-size (default 50)] \\
                               [-n/--no_heatmap]
""")

# main of gem2bfm
def gem2bfm_main(argv):
    config = ''
    prefix = ''
    binsize= 50
    threads=8
    draw_heatmap=True
    try:
        opts, args = getopt.getopt(argv,"hnc:o:b:t:",["help",'no_heatmap',"iconf=","ofile=","bin=","threads="])
    except getopt.GetoptError:
        gem2bfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem2bfm_usage()
            sys.exit(0)
        elif opt in ('-n', '--no_heatmap'):
            draw_heatmap=False
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

    init_outputs(prefix)
    print('start loading slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    slice_data = load_slices(json.load(open(config)))
    print('build_genes_ids ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    gene_names , gene_ids    = build_genes_ids(slice_data)
    print('get bins of slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    slices_info , bin_ids    = slice_data.get_bins_of_slices(binsize=binsize)
    print('get mtx of slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    mtx, valid_bin_num,_     = slice_data.get_mtx(gene_ids,bin_ids,threads)

    
    print('save data into disk ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    print_features_tsv(gene_names,prefix)
    print_barcodes_tsv(bin_ids,prefix)
    print_tissue_positions_list(bin_ids,prefix)
    print_matrix_mtx(mtx,prefix,len(gene_names),valid_bin_num)
    print_slices_json(slices_info,prefix)

    if draw_heatmap :
        print('draw heatmap(s) ...')
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        # build detailed heatmap by bin5
        bin_5_ids  = build_bins(slice_data,binsize=5)
        gen_heatmap(slice_data,bin_5_ids,prefix)

    print('all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
############################################################################
# section 2 : apply_affinematrix
#############################################################################
def affine_usage():
    print("""
Usage : GEM_toolkit.py apply_affinematrix -c <affinematix.conf.json> \\
                                          -i <input-tissue_positions.csv> \\
                                          -s <scroll.conf.csv> \\
                                          -o <output-tissue_positions.csv>

Notice: input-tissue_positions.csv and scroll.conf.csv are output files of gem2bfm command.
""")

def affine_main():
    affine_usage()
    #TODO

############################################################################
# section 3 : main
#############################################################################

# usage
def main_usage():
    print("""
Usage : GEM_toolkit.py action [options ]

Action:
    gem2bfm
    apply_affinematrix
""")

# logic codes
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ( "-h" , "--help" ):
        main_usage()
        exit(0)
    elif len(sys.argv) < 2 or not sys.argv[1] in ("gem2bfm", "apply_affinematrix"):
        main_usage()
        exit(1)
    elif sys.argv[1] == "gem2bfm" :
        gem2bfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_affinematrix" :
        affine_main(sys.argv[2:])
        exit(0)
