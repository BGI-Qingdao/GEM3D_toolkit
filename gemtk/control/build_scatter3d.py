import sys
import time
import getopt

from gemtk.control.load_miscdf import *
from gemtk.control.save_miscdf import *
import pandas as pd

def build_scatter3d(slices:[],input_folder:str ,prefix:str):
    create_a_folder(prefix)
    all_xyz=[]
    for x in slices :
        sid = slices[x]
        file2="{}/slice_{}/tissue_positions_list.csv".format(input_folder,sid)
        tp = load_slice_tissues_positions(file2)
        points = tp[tp['masked']==1]
        all_xyz.append(points)

    all_points = pd.concat(all_xyz)
    all_points.to_csv("{}/bin_xyz.csv".format(prefix),sep=',',header=True,index=False)
    scatter_3d_html(all_points, '{}/scatter_3d.html'.format(prefix))

############################################################################
# section 7 :
#############################################################################

def scatter3d_usage():
    print("""
Usage : GEM_toolkit.py scatter3d    -i <input-folder>  \\
                                    -o <output-folder> \\
                                    -c <conf.json>

Notice:
        1. the input folder is output folder of apply_affinematrix action.
""")

def scatter3d_main(argv:[]):
    input_folder = ''
    prefix=''
    conf=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:c:",["help","input=","output=","conf="])
    except getopt.GetoptError:
        scatter3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            scatter3d_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-c", "--conf"):
            conf = arg

    if  input_folder == "" or prefix=="" or conf == "" :
        scatter3d_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("conf file is {}".format(conf))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slices = load_slices(conf)
    print('build scatter3d...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    build_scatter3d(slices,input_folder,prefix)
    print('build_scatter3d all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
