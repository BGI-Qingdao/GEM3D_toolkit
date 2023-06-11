import sys
import time
import getopt
from skimage import io as skio
from gemtk.slice_dataframe import slice_dataframe
from gemtk.save_miscdf import *

from PIL import ImageFile
from PIL import Image

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

############################################################################
# section 15 : chopgems
#############################################################################
# usage
def mask_gem_usage():
    print("""
Usage : GEM_toolkit.py maskgem -i <input.gem> \\
                               -m <mask.png>  \\
                               -o <output-folder> \\
                               -x [default None, xmin] \\
                               -y [default None, ymin]
""")

def mask_gem_main(argv:[]):
    prefix=''
    binsize=1
    imask=''
    igem=''
    xmin=None
    ymin=None
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:x:y:",["help","input=","output="])
    except getopt.GetoptError:
        mask_gem_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            mask_gem_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            igem = arg
        elif opt in ("-m"):
            imask = arg
        elif opt in ("-x"):
            xmin = int(arg)
        elif opt in ("-y"):
            ymin = int(arg)
    if  igem == '' or imask == "" or prefix== "" :
        mask_gem_usage()
        sys.exit(3)

    print("mask file is {}".format(imask))
    print("output prefix is {}".format(prefix))
    print(f"xmin={xmin}; ymin={ymin}")
    print('loading mask now...')
    dapi_data = skio.imread(imask)
    print('loading gem now...')
    gem = slice_dataframe()
    gem.init_from_file(igem,xmin,ymin)
    print('mask gem now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    gem.mask(dapi_data)
    print('save gem now...')
    gem.printGEM(f'{prefix}.gem')
    print('all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
