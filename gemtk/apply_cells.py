#!/usr/bin/env python3
import os
import sys
import time
import getopt
import numpy as np
import pandas as pd

def apply_cells_usage():
    print("""
Usage : GEM_toolkit.py apply_cells \\
             -g <gem file>  \\
             -m <cell segment mask file> \\
             -o <output prefix> \\
             -x [xshift of gem to heatmap, default xmin] \\
             -y [yshift of gem to heatmap, default ymin] \\
             -h [show this usage]

""",flush=True)

def apply_cells_main(argv:[]):
    prefix = ''
    mask = ''
    gem = ''
    xmin=None
    ymin=None
    if len(argv) < 1:
        apply_cells_usage()
        sys.exit(0)
    try:
        opts, args = getopt.getopt(argv,"hg:o:m:x:y:",["help"])
    except getopt.GetoptError:
        apply_cells_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            apply_cells_usage()
            sys.exit(0)
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("-g"):
            gem = arg
        elif opt in ("-m"):
            mask = arg
        elif opt in ("-x"):
            xmin = int(arg)
        elif opt in ("-y"):
            ymin = int(arg)

    if prefix == '' or gem == '' or mask == '' :
        apply_cells_usage()
        sys.exit(2)

    # load gems
    gem_data = pd.read_csv(gem, sep='\t', header=0, compression='infer', comment='#')
    print(f'gem file is {gem}')
    if len(gem_data.columns) == 4 :
        gem_data.columns = ['geneID','x','y','MIDCounts']
    elif len(gem_data.columns) == 5 :
        gem_data.columns = ['geneID','x','y','MIDCounts','ExonCount']
    if xmin is None:
        gem_data_x_min = gem_data['x'].min()
    else:
        gem_data_x_min = xmin
    if ymin is None:
        gem_data_y_min = gem_data['y'].min()
    else:
        gem_data_y_min = ymin
    gem_data['x'] = gem_data['x'] - gem_data_x_min
    gem_data['y'] = gem_data['y'] - gem_data_y_min
    gem_data['x'] = gem_data['x'].astype(int)
    gem_data['y'] = gem_data['y'].astype(int)
    # load mask 
    print(f'mask file is {mask}')
    masks = np.loadtxt(mask,dtype=int,delimiter=' ')
    # add cell
    gem_data['cell'] = masks[gem_data['y'],gem_data['x']]
    gem_data['x'] = gem_data['x'] + gem_data_x_min
    gem_data['y'] = gem_data['y'] + gem_data_y_min
    gem_data = gem_data[gem_data['cell']!=0]
    gem_data.to_csv(f'{prefix}.gemc_saved',sep='\t',header=True,index=False)
