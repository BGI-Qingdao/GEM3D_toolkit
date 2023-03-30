import sys
import time
import getopt
import anndata
from skimage import io as skio
from gemtk.h5ad_dataframe import h5ad_dataframe

# usage
def mask_h5ad_usage():
    print("""
Usage : GEM_toolkit.py maskh5ad -i <input.h5ad> \\
                               -m <mask.png>  \\
                               -o <output.h5ad> \\
                               -x [default None, xmin] \\
                               -y [default None, ymin]
""")

def mask_h5ad_main(argv:[]):
    prefix=''
    binsize=1
    imask=''
    ih5ad=''
    min_x=None
    min_y=None
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:x:y:",["help","input=","output="])
    except getopt.GetoptError:
        mask_h5ad_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            mask_h5ad_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            ih5ad = arg
        elif opt in ("-m"):
            imask = arg
        elif opt in ("-x"):
            xmin = int(arg)
        elif opt in ("-y"):
            ymin = int(arg)
    if  ih5ad == '' or imask == "" or prefix== "" :
        mask_h5ad_usage()
        sys.exit(3)
    
    print("h5ad file is {}".format(ih5ad))
    print("output prefix is {}".format(prefix))
    print(f"xmin={min_x }; ymin={min_x}")
    print('loading mask now...')
    dapi_data = skio.imread(imask)
    print('loading h5ad now...')
    h5ad=h5ad_dataframe()
    h5ad.h5ad_init(ih5ad,min_x,min_y)
    print('mask h5ad now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    h5ad.mask(dapi_data)
    print('save h5ad now...')
    h5ad.printH5ad(f'{prefix}.h5ad')
    print('all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
