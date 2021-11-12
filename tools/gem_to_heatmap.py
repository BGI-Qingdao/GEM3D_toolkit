#!/usr/bin/env python3

import sys
import getopt
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def main(argv :[]):
    # init
    in_f=""
    out_f=""
    binsize=50
    # parse parameters
    try:
        opts,args = getopt.getopt(argv,"i:o:b:h",["input=","output=","binsize=","help"])
    except getopt.GetoptError:
        print('gem_to_heatmap.py -i <input.gem> -o <output.png> -b [binsize=50]')
        sys.exit(1)
    for opt, arg in opts:
        if opt in ('-h' , "--help") :
            print('gem_to_heatmap.py -i <input.gem> -o <output.png> -b [binsize=50]')
            sys.exit()
        elif opt in ('-i' , "--input") :
            in_f = arg
        elif opt in ("-o" , "--output"):
            out_f = arg
        elif opt in ("-b" , "--binsize"):
            binsize= int(arg)
    #sanity check
    if in_f == "" or out_f == "" : 
        print('gem_to_heatmap.py -i <input.gem> -o <output.png> -b [binsize=50]')
        sys.exit(2)

    # load data
    m_dataframe=pd.read_csv(in_f,sep='\t')
    # prepare bin coordinates
    min_x=np.min(m_dataframe.x)
    max_x=np.max(m_dataframe.x)
    min_y=np.min(m_dataframe.y)
    max_y=np.max(m_dataframe.y)
    spot_width=max_x-min_x+1
    spot_height=max_y-min_y+1

    draw_width  = spot_width//binsize
    draw_height = spot_height//binsize
    if spot_width % binsize > 0:
        draw_width = draw_width + 1
    if spot_height % binsize > 0:
        draw_height = draw_height + 1

    #coords=np.zeros((draw_width*draw_height,2))
    #for y in range(draw_height):
    #    for x in range(draw_width):
    #        index=y*draw_width+x
    #        bin_mid_x = x*binsize
    #        bin_mid_y = y*binsize
    #        coords[index][0],coords[index][1]= bin_mid_x , bin_mid_y
    # prepare UMI count matrix of each bin
    values=np.zeros((draw_height,draw_width))
    for _,row in m_dataframe.iterrows():
        x , y = row['x']-min_x,row['y']-min_y
        bin_x = x // binsize
        bin_y = y // binsize
        values[bin_y,bin_x]+= row['MIDCounts']
    # draw
    plt.figure(figsize=(spot_width/500,spot_height/500))
    plt.imshow(values, cmap='hot')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0.1,wspace=0.1)
    plt.savefig(out_f,dpi=100)

    print("INFO: {} {} {}".format(out_f,spot_width,spot_height))

if __name__ == "__main__":
   main(sys.argv[1:])
