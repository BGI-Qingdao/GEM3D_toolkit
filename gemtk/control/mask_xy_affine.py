import sys
import time
import getopt
import numpy as np
import pandas as pd
from gemtk.control.load_miscdf import *
from gemtk.control.save_miscdf import create_a_folder


def mask_xy_affine(affines,mask_xy_map,prefix):
    xyz = pd.DataFrame(columns=['x','y','z'])

    create_a_folder(prefix)
    for slice_id in affines:
        mask_xyz = mask_xy_map[slice_id]
        mask_xyz['a'] = np.ones(len(mask_xyz),dtype=int)
        this_xyz = mask_xyz[['x','y','z','a']].to_numpy()
        this_affine = affines[slice_id]
        new_xyz = np.matmul(this_affine.I ,this_xyz.T)
        new_xyz = new_xyz[0:3: ,:]
        xyz = xyz.append(pd.DataFrame(new_xyz, columns=xyz.columns), ignore_index=True)
    xyz['x'] = xyz['x'].astype(int)
    xyz['y'] = xyz['y'].astype(int)
    xyz['z'] = xyz['z'].astype(int)
    xyz.to_csv("{}/mask_xyz.csv".format(prefix),sep=',',header=True,index=False)

############################################################################
# section 12 : mask_xy_affine
#############################################################################
# usage
def mask_xy_affine_usage():
    print("""
Usage : GEM_toolkit.py mask_xy_affine -i <input_folder>  \\
                                      -d <downsize> \\
                                      -o <output-folder> \\
                                      -a <affine.json>
""")

def mask_xy_affine_main(argv:[]):
    prefix=''
    downsize=0
    input_folder=''
    affine_json=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:a:",["help","input=","output=","downsize=","affine="])
    except getopt.GetoptError:
        mask_xy_affine_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            mask_xy_affine_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-a", "--affine"):
            affine_json= arg

    if  input_folder == "" or prefix== "" or downsize < 1 or affine_json == '':
        mask_xy_affine_usage()
        sys.exit(3)

    print("affine_json is {}".format(affine_json))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format(downsize))
    print('load datas now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    affines=load_affines(affine_json)
    mask_xy_map=load_mask_xy_by_affines(input_folder,affines,downsize)
    print('mask xy affine now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mask_xy_affine(affines,mask_xy_map,prefix)
    print('mask xy affine done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
