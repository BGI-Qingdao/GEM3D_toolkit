import sys
import time
import getopt
from gemtk.control.load_miscdf import *

from gemtk.model.slice_dataframe import slice_dataframe
#from gemtk.view.slice2d import *
from gemtk.control.save_miscdf import *

def chopgems(roi_json,prefix,binsize):
    create_a_folder(prefix)
    for sinfo in roi_json:
        slice_id = int(sinfo[0])
        slice_gem  = sinfo[1]
        sdf = slice_dataframe()
        sdf.init_from_file(slice_gem,slice_id)
        for roi in sinfo[2]:
            item_name = roi[0]
            BX=roi[1]
            BY=roi[2]
            Width=roi[3]
            Height=roi[4]
            cropped = sdf.chop(BX,BY,Width,Height,binsize)
            cropped.printGEM("{}/{}-slice{}.gem".format(prefix,item_name,slice_id))
            #gec = cropped.get_expression_count_vector(1)
            #heatmap2D_png(gec,
            #              "{}/{}-slice{}.heatmap.png".format(prefix,item_name,slice_id),
            #              gec.shape[1],gec.shape[0] )
        print("slice {} is done".format(slice_id),flush=True)
    print("{} done".format(slice_id),flush=True)

############################################################################
# section 15 : chopgems
#############################################################################
# usage
def chopgems_usage():
    print("""
Usage : GEM_toolkit.py chopgems     -i <roi.json>  \\
                                    -o <output-folder> \\
                                    -b [ binsize for new heatmap, default 1 ] \\
                                    -k [ yes/no keep original coordinate,default no ]
""")

def chopgems_main(argv:[]):
    prefix=''
    binsize=1
    ijson=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:b:k:",["help","input=","output=","binsize=","keep="])
    except getopt.GetoptError:
        chopimages_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            chopimages_usage()
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
    roi_json=load_json(ijson)
    print('chopgems now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    chopgems(roi_json,prefix,binsize)
    print('chopgems  all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

