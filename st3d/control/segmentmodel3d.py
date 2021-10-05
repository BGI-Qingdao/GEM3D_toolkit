import sys
import time
import getopt
import pandas as pd

from st3d.control.load_miscdf import *
from st3d.control.save_miscdf import print_model3d,init_model3d,create_a_folder
from st3d.view.model3d import html_model3d

def segmentmodel3d(  segmentations : pd.DataFrame, input_folder : str ,  prefix : str, downsize=4 ):
    model3d = pd.read_csv( '{}/model3d.csv'.format(input_folder), sep=',' )
    names = segmentations.columns
    names = names.tolist()
    create_a_folder(prefix)
    for name in names:
        model3d_new = model3d[
                (model3d['x']>segmentations.loc['min-x',name]) &  
                (model3d['x']<segmentations.loc['max-x',name]) &
                (model3d['y']>segmentations.loc['min-y',name]) &
                (model3d['y']<segmentations.loc['max-y',name]) ]
        model3d_new = model3d_new.copy()
        prefix_new = '{}/{}'.format(prefix,name)
        create_a_folder(prefix_new)
        print_model3d(model3d_new,prefix_new)
        html_model3d(model3d_new,prefix_new,downsize)

############################################################################
# section 9 : segmentmode3d
#############################################################################
# usage
def segmentmodel3d_usage():
    print("""
Usage : GEM_toolkit.py segmentmodel3d  -i <input-folder>  \\
                                       -s <segmentations.csv> \\
                                       -o <output-folder> \\
                                       -d <downsize>
""")

def segmentmodel3d_main(argv:[]) :
    input_folder = ''
    prefix=''
    segconf=''
    downsize=0
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:d:",["help","input=","output=","segs=","downsize="])
    except getopt.GetoptError:
        segmentmodel3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            segmentmodel3d_usage()
            sys.exit(0)
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-s", "--segs"):
            segconf = arg

    if  input_folder == "" or prefix== "" or segconf == "" or downsize <1 :
        segmentmodel3d_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("segmetation conf is {}".format( segconf))
    print("downsize is {}".format( downsize))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    segs = load_segmentations(segconf)
    print('segment model3d ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    segmentmodel3d(segs,input_folder,prefix,downsize)
    print('segment model3d all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

