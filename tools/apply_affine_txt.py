#!/usr/bin/env python3
import sys
import getopt
import json
import scipy.ndimage as nd
from skimage import io as skio
import numpy as np

# usage
def apply_affine_txt_usage():
    print("""
Usage : apply_affine_txt.py  -i <input.txt> \\
                             -o <output> \\
                             -a <reverse affine matrix> \\
                             -r <ref image> \\
                             -f [fliph/flipv/noflip, default noflip] 

Example :
        apply_affine_txt.py -i input.txt \\
                            -o out.txt \\
                            -r ref.tif \\
                            -a '[[0.023890163936836614, 1.1533635423882767, 3673.0911462805616], [-1.1509242533824746, 0.022522101202567, 22343.59128420033], [0.0, 0.0, 1.0]]' \\
                            -f fliph
""",flush=True)


def apply_affine_txt_main(argv:[]) :
    inputf = ''
    prefix = ''
    affine=np.eye(3)
    flip = 'noflip'
    ref = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:a:f:r:",["help=" ,
                                                     "input=",
                                                     "output=",
                                                     "affine=",
                                                     "flip=",
                                                     "ref="])
    except getopt.GetoptError:
        apply_affine_txt_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--inputf"):
            inputf = arg
        elif opt in ('-h','--help'):
            handle_trackEM_matrix_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ('-a' , '--affine'):
            affine = np.matrix(np.array(json.loads(arg)))
        elif opt in ('-f' , '--flip'):
            flip = arg
        elif opt in ('-r' , '--ref'):
            ref = arg


    if inputf == '' or prefix == '' or not flip in ('fliph','flipv','npflip') or ref == '':
        apply_affine_txt_usage()
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

apply_affine_txt_main(sys.argv[1:])
