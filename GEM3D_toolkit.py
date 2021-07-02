#!usr/bin/env python3

import sys
import getopt 
import json

from st3d.view.model3d import * 
from st3d.view.slice2d import *

from st3d.control.global_instances import *
from st3d.control.load_slices import *
from st3d.control.save_miscdf import *

def usage():
    print('Usage : GEM3D_toolkit.py -c <config-file> -o <output-prefix>')

def main(argv):
    config = ''
    prefix = ''
    try:
       opts, args = getopt.getopt(argv,"hsc:o:",["slices","iconf=","ofile="])
    except getopt.GetoptError:
       usage()
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          usage()
          sys.exit()
       elif opt in ("-c", "--iconf"):
          config = arg
       elif opt in ("-o", "--ofile"):
          prefix = arg
    print("config file is {}".format(config))
    print("output prefix is {}".format( prefix))
    if config == "" or prefix == "" :
        usage()
        sys.exit(3)

    load_slices(json.load(open(config)))
    gem_4c = get_expression_count3d(binsize=50)
    save_3D_heatmap(gem_4c,"{}.hot3d.csv".format(prefix))
    heat3D_and_saveas_html(gem_4c, "{}.scatter3d.html".format(prefix))

if __name__ == "__main__":
   main(sys.argv[1:])
