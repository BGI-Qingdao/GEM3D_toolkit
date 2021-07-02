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
    try:
        opts, args = getopt.getopt(argv,"hc:o:b:",[["help","iconf=","ofile=","bin="])
    except getopt.GetoptError:
       gem2bfm_usage()
       sys.exit(2)
    for opt, arg in opts:
       if opt == ('-h' ,'--help)':
          gem2bfm_usage()
          sys.exit(0)
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

    load_slices(json.load(open(config)))
    gem_4c = get_expression_count3d(binsize=50)
    save_3D_heatmap(gem_4c,"{}.hot3d.csv".format(prefix))
    heat3D_and_saveas_html(gem_4c, "{}.scatter3d.html".format(prefix))

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
    if len(sys.argv) ==2 and sys.argv[1] in ( "-h" , "--help" ):
        main_usage()
        exit(0)
    elif len(sys.argv) < 2 or ! ( sys.argv[1] in ( "-h" , "--help" ) ) :
        main_usage()
        exit(1)
    elif sys.argv[1] == "gem2bfm" :
        gem2bfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_affinematrix" :
        affine_main(sys.argv[2:])
        exit(0)
