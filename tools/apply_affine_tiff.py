#!/usr/bin/env python3
import sys
import getopt
import json
import scipy.ndimage as nd
from skimage import io as skio
import numpy as np

# usage
def apply_affine_tiff_usage():
    print("""
Usage : apply_affine_tiff.py  -i <input.tif> \\
                             -o <output prefix> \\
                             -a <reverse affine matrix> \\
                             -r <ref image> \\
                             -f [fliph/flipv/noflip, default noflip] \\
                             -O [draw overlaped graph, no arg, default no set]

Example :
        apply_affine_tiff.py -i input.tif \\
                            -o prefix \\
                            -r ref.tif \\
                            -a '[[0.023890163936836614, 1.1533635423882767, 3673.0911462805616], [-1.1509242533824746, 0.022522101202567, 22343.59128420033], [0.0, 0.0, 1.0]]' \\
                            -f h
""",flush=True)


def apply_affine_tiff_main(argv:[]) :
    inputf = ''
    prefix = ''
    affine=np.eye(3)
    flip = 'noflip'
    ref = ''
    overlap = False
    try:
        opts, args = getopt.getopt(argv,"hi:o:a:f:r:O",["help=" ,
                                                     "input=",
                                                     "output=",
                                                     "affine=",
                                                     "flip=",
                                                     "ref=",
                                                     "overlap"])
    except getopt.GetoptError:
        apply_affine_tiff_usage()
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
        elif opt in ('-O' , '--overlap'):


    if inputf == '' or prefix == '' or not flip in ('fliph','flipv','noflip') or ref == '':
        apply_affine_tiff_usage()
        sys.exit(2)
    refd = skio.imread(ref)
    w,h = refd.shape
    print(f'ref w={w}, h={h}')

    ind = skio.imread(inputf)
    if flip == 'fliph':
        ind = np.fliplr(ind)
    elif flip == 'flipv':
        ind = np.flipud(ind)
    outd = nd.affine_transform(ind.T,affine,output_shape=(h,w),order=0)
    outd = outd.T
    skio.imsave(f'{prefix}.affined.tiff',outd)
    if overlap:
        draw=np.zeros((refd.shape[0], refd.shape[1],3),dtype='uint8')
        draw[:,0]=refd
        draw[:,1]=outd
        skio.imsave(f'{prefix}.overlap.tiff',draw)

if __name__ == "__main__":
    apply_affine_tiff_main(sys.argv[1:])
