import sys
import time
import getopt

from gemtk.slice_dataframe import slice_dataframe
from gemtk.save_miscdf import *

def chopgems(roi_json,prefix,binsize):
    create_a_folder(prefix)
    sinfo = roi_json
    slice_gem  = sinfo[0]
    sdf = slice_dataframe()
    sdf.init_from_file(slice_gem)
    for roi in sinfo[1]:
        item_name = roi[0]
        BX=roi[1]
        BY=roi[2]
        Width=roi[3]
        Height=roi[4]
        cropped = sdf.chop(BX,BY,Width,Height,binsize)
        cropped.printGEM("{}/{}.gem".format(prefix,item_name))

############################################################################
# section 15 : chopgems
#############################################################################
# usage
def chopgems_usage():
    print("""
Usage : GEM_toolkit.py chop_gem     -i <roi.json>  \\
                                    -o <output-folder> \\
                                    -b [ binsize for new heatmap, default 1 ] \\
example of roi.json:
[
    "input.gem",
     [
         [sample1, 0,0,100,200],
         [sample2, 300,400,200,300],
         ...
         [samplen, x,y,w,h]
     ]
]
""")

def chopgems_main(argv:[]):
    prefix=''
    binsize=1
    ijson=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:b:",["help","input=","output=","binsize="])
    except getopt.GetoptError:
        chopgems_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            chopgems_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-b", "--binsize"):
            binsize = int(arg)
        elif opt in ("-i", "--input"):
            ijson = arg

    if  ijson == "" or prefix== "" or binsize <1:
        chopgems_usage()
        sys.exit(3)

    print("roi.json is {}".format(ijson))
    print("output prefix is {}".format( prefix))
    print('get roi.json now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    roi_json=json.load(open(ijson))
    print('chopgems now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    chopgems(roi_json,prefix,binsize)
    print('chopgems  all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

