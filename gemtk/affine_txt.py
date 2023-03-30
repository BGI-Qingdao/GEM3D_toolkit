import sys
import getopt
import json
import scipy.ndimage as nd
from skimage import io as skio
import numpy as np

# usage
def affine_txt_usage():
    print("""
Usage : affine_txt.py  -i <input.txt> 
                             -o <output> 
                             -r <ref image>
                             -f [fliph/flipv/noflip, default noflip] 
                             -B [backward (reverse) affine matrix] 
                             -F [forward affine matrix]

Example :
        affine_txt.py -i input.txt \\
                            -o out.txt \\
                            -r ref.png \\
                            -f fliph \\
                            -F '[[1,0,10],[0,1,0],[0.0, 0.0, 1.0]]'   
Notice: please provide one of [ -B , -F ], if both present, the later one will overwrite previous one.
""",flush=True)



def affine_txt_main(argv:[]) :
    inputf = ''
    prefix = ''
    affine=np.eye(3)
    flip = 'noflip'
    ref = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:f:B:F:",["help=" ,
                                                     "input=",
                                                     "output=",
                                                     "affine=",
                                                     "ref="])
    except getopt.GetoptError:
        affine_txt_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--inputf"):
            inputf = arg
        elif opt in ('-h','--help'):
            affine_txt_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ('-f' , '--flip'):
            flip = arg
        elif opt in ('-r' , '--ref'):
            ref = arg
        elif opt in ("-F",):
            affine = np.matrix(np.array(json.loads(arg))).I
        elif opt in ("-B",):
            affine = np.matrix(np.array(json.loads(arg)))

    if inputf == '' or prefix == '' or not flip in ('fliph','flipv','npflip') or ref == '':
        affine_txt_usage()
        sys.exit(2)
    refd = skio.imread(ref)
    w,h = refd.shape
    print(f'ref w={w}, h={h}')

    ind = np.loadtxt(inputf,delimiter=' ',dtype=int)
    if flip == 'fliph':
        ind = np.fliplr(ind)
    elif flip == 'flipv':
        ind = np.flipud(ind)
    outd = nd.affine_transform(ind.T,affine,output_shape=(h,w),order=0)
    outd = outd.T
    np.savetxt(prefix,outd,fmt="%d")
