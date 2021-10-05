import sys
import time
import getopt
from st3d.control.load_miscdf import *
from PIL import Image
from st3d.control.save_miscdf import create_a_folder

def chopimages(roi_json,prefix):
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None
    create_a_folder(prefix)
    for sinfo in roi_json:
        slice_name = sinfo[0]
        slice_tif = sinfo[1]
        img = Image.open(slice_tif)
        for roi in sinfo[2]:
            item_name = roi[0]
            BX=roi[1]
            BY=roi[2]
            Width=roi[3]
            Height=roi[4]
            cropped = img.crop((BX,BY,BX+Width+1,BY+Height+1))  
            cropped.save("{}/{}-{}.tif".format(prefix,item_name,slice_name))
        print("{} done".format(slice_name),flush=True)

############################################################################
# section 14 : chopimages
#############################################################################
# usage
def chopimages_usage():
    print("""
Usage : GEM_toolkit.py chopimages   -i <roi.json>  \\
                                    -o <output-folder>
""")

def chopimages_main(argv:[]) :
    prefix=''
    ijson=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","input=","output="])
    except getopt.GetoptError:
        chopimages_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            chopimages_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            ijson = arg

    if  ijson == "" or prefix== "" :
        chopimages_usage()
        sys.exit(3)

    print("roi.json is {}".format(ijson))
    print("output prefix is {}".format( prefix))
    print('get roi.json now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    roi_json=load_json(ijson)
    print('chopimages now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    chopimages(roi_json,prefix)
    print('chopimages  all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
