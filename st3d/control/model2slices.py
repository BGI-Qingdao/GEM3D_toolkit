import sys
import time
import getopt

import numpy as np
import pandas as pd
from st3d.control.save_miscdf import create_a_folder
from st3d.control.load_miscdf import *
from st3d.view.slice2d import *
from st3d.model.volumn2D import *
import nibabel as nib

def model2slices(xyz,prefix,downsize,max_x,min_x,max_y,min_y):
    xyz = xyz.astype(int)
    max_x =int(max_x) 
    min_x =int(min_x) 
    max_y =int(max_y) 
    min_y =int(min_y) 
    print("min_x :{}".format(min_x))
    print("min_y :{}".format(min_y))
    print("max_x :{}".format(max_x))
    print("max_y :{}".format(max_y))
    uniq_z = np.unique(xyz['z'])
    create_a_folder(prefix)
    final_volumn=None
    index=0
    for x in uniq_z :
        slice_id = x // downsize
        ddata=xyz[xyz['z']==x][['x','y']]
        ddata=ddata.copy()
        ddata['v']=np.ones(len(ddata))
        slice_volumn2D = xyv_to_volumn2D(ddata,min_x,max_x,min_y,max_y,downsize )
        if final_volumn is None :
            final_volumn=np.zeros((len(uniq_z),slice_volumn2D.shape[0],slice_volumn2D.shape[1]),dtype=int)
        final_volumn[index,:,:]=slice_volumn2D
        index=index+1
        fname="{}/slice_{}.png".format(prefix,slice_id)
        heatmap2D_png(slice_volumn2D,fname,slice_volumn2D.shape[1],slice_volumn2D.shape[0])

    affine = np.diag([1, 1, 1, 1])
    array_img = nib.Nifti1Image(final_volumn, affine)
    array_img.to_filename('{}/{}.nii'.format(prefix,prefix))

############################################################################
# section 13 : model2slices
#############################################################################
# usage
def model2slices_usage():
    print("""
Usage : GEM_toolkit.py model2slices -i <model3d.csv>  \\
                                    -d <downsize> \\
                                    -o <output-folder> \\
                                    -c [cluster_id (default -1 for all)]

Notice : model3d.csv must contain x,y,z columns, need cluster column if -c is not -1.
""")

def model2slices_main(argv:[]) :
    prefix=''
    model3d=''
    downsize=0
    cluster=-1
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:c:",["help","model=","output=","downsize=","cluster="])
    except getopt.GetoptError:
        model2slices_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            model2slices_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--model"):
            model3d = arg
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-c", "--cluster"):
            cluster = int(arg)

    if  model3d == "" or prefix== "" or downsize < 1 :
        model2slices_usage()
        sys.exit(3)

    print("model3d is {}".format(model3d))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format(downsize))
    print('get xyz now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    xyz,xmax,xmin,ymax,ymin=get_xyz(model3d,cluster)
    print('model2slices now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    model2slices(xyz,prefix,downsize,xmax,xmin,ymax,ymin)
    print('handle model2slices all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

