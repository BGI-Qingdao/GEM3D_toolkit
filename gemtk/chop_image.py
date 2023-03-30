import sys
import time
import json
import getopt
from PIL import Image
from gemtk.save_miscdf import create_a_folder

def chopimages(roi_json,prefix):
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None
    create_a_folder(prefix)
    sinfo = roi_json
    slice_tif = sinfo[0]
    img = Image.open(slice_tif)
    for roi in sinfo[1]:
        item_name = roi[0]
        BX=roi[1]
        BY=roi[2]
        Width=roi[3]
        Height=roi[4]
        cropped = img.crop((BX,BY,BX+Width,BY+Height))
        cropped.save("{}/{}.png".format(prefix,item_name))
    print("{} done".format(slice_name),flush=True)

############################################################################
# section 14 : chopimages
#############################################################################
# usage
def chopimages_usage():
    print("""
Usage : GEM_toolkit.py chop_image   -i <roi.json>  \\
                                    -o <output-folder>
example of roi.json:
[
    "input.tif",
     [
         [sample1, 0,0,100,200],
         [sample2, 300,400,200,300],
         ...
         [samplen, x,y,w,h]
     ]
]
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
    roi_json=json.load(open(ijson))
    print('chopimages now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    chopimages(roi_json,prefix)
    print('chopimages  all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
