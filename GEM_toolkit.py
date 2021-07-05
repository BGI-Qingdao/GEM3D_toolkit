#!usr/bin/env python3

import sys
import getopt 
import json

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
                               -b [bin-size (default 50)]
""")

# main of gem2bfm
def gem2bfm_main(argv):
    config = ''
    prefix = ''
    binsize= 50
    draw_heatmap=True
    try:
        opts, args = getopt.getopt(argv,"hnc:o:b:",["help",'no_heatmap',"iconf=","ofile=","bin="])
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
        elif opt in ("-o", "--ofile"):
            prefix = arg

    if config == "" or prefix == "" or binsize<1:
        gem2bfm_usage()
        sys.exit(3)
    print("config file is {}".format(config))
    print("output prefix is {}".format( prefix))
    print("binsize is {}".format(binsize))

    init_outputs(prefix)
    slice_data = load_slices(json.load(open(config)))
    gene_names , gene_ids    = build_genes_ids(slice_data)
    slices_info , bin_ids    = slice_data.get_bins_of_slices(binsize=binsize)
    mtx , valid_bin_num      = slice_data.get_mtx(gene_ids,bin_ids)

    print_features_tsv(gene_names,prefix)
    print_barcodes_tsv(bin_ids,prefix)
    print_tissue_positions_list(bin_ids,prefix)
    print_matrix_mtx(mtx,prefix)
    print_slices_json(slices_info,prefix)

    if draw_heatmap :
        # build detailed heatmap by bin5
        bin_5_ids  = build_bins(slice_data,binsize=5)
        gen_heatmap(slice_data,bin_5_ids,prefix)

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
    elif len(sys.argv) < 2 :
        main_usage()
        exit(1)
    elif sys.argv[1] == "gem2bfm" :
        gem2bfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_affinematrix" :
        affine_main(sys.argv[2:])
        exit(0)
