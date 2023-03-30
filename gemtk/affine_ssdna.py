import sys
import getopt
import json
import scipy.ndimage as nd
from skimage import io as skio
import numpy as np

from PIL import ImageFile
from PIL import Image

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None
# usage
def affine_ssdna_usage():
    print("""
Usage : affine_ssdna.py  -i <input.tif/png> \\
                             -o <output> \\
                             -B <backword (reverse) affine matrix> \\
                             -F <forword affine matrix> \\
                             -r <ref image> \\
                             -f [fliph/flipv/noflip, default noflip] 

Example :
        affine_ssdna.py -i input.png \\
                            -o out.png \\
                            -r ref.png \\
                            -f fliph  \\
                            -F '[[1,0,10],[0,1,0],[0.0, 0.0, 1.0]]'   
Notice: please provide one of [ -B , -F ], if both present, the later one will overwrite previous one.
""",flush=True)


def affine_ssdna_main(argv:[]) :
    inputf = ''
    prefix = ''
    affine=np.eye(3)
    flip = 'noflip'
    ref = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:F:B:f:r:",["help=" ,
                                                     "input=",
                                                     "output=",
                                                     "ref=",
                                                     "flip="
                                                     ])
    except getopt.GetoptError:
        affine_ssdna_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--inputf"):
            inputf = arg
        elif opt in ('-h','--help'):
            affine_ssdna_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ('-F'):
            affine_r = np.matrix(np.array(json.loads(arg))).I
        elif opt in ('-B'):
            affine_r = np.matrix(np.array(json.loads(arg)))
        elif opt in ('-f' , '--flip'):
            flip = arg
        elif opt in ('-r' , '--ref'):
            ref = arg

    if inputf == '' or prefix == '' or not flip in ('fliph','flipv','noflip') or ref == '':
        affine_ssdna_usage()
        sys.exit(2)
    refd = skio.imread(ref)
    if len(refd.shape)==3:
         w,h,_= refd.shape
    else:
        w,h=refd.shape
    print(f'ref w={w}, h={h}')

    dapi_data  = skio.imread(inputf)
    if len(dapi_data.shape) == 3 : # RGB to 8 bit gray
        new_data = np.zeros((dapi_data.shape[0],dapi_data.shape[1]),dtype=int)
        new_data = new_data + dapi_data[:,:,0]
        new_data = new_data + dapi_data[:,:,1]
        new_data = new_data + dapi_data[:,:,2]
        new_data = (new_data+2) / 3
        dapi_data = new_data
    dapi_data = dapi_data.astype('uint8')
    ind = dapi_data
    if flip == 'fliph':
        ind = np.fliplr(ind)
    elif flip == 'flipv':
        ind = np.flipud(ind)
    outd = nd.affine_transform(ind.T,affine_r,output_shape=(h,w),order=0)
    outd = outd.T
    outd = outd.astype('uint8')
    print(outd.shape)
    skio.imsave(prefix,outd)
