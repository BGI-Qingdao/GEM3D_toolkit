import sys
import time
import getopt
import numpy as np
import scipy.ndimage as nd
from skimage import io as skio

def get_mask_dapi(dapi_file,min_brightness,width_pixel,height_pixel,chip,prefix):
    print('loading dapi ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    dapi_data = skio.imread(dapi_file)
    if len(dapi_data.shape) == 3 : # RGB tiff to 8 bit gray tiff
        new_data = np.zeros((dapi_data.shape[0],dapi_data.shape[1]),dtype=int)
        new_data = new_data + dapi_data[:,:,0]
        new_data = new_data + dapi_data[:,:,1]
        new_data = new_data + dapi_data[:,:,2]
        new_data = new_data / 3
        dapi_data = new_data
    dapi_data = dapi_data.astype('uint8')
    raw_dapi = dapi_data.copy()

    print('gen mask_dapi ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    dapi_data[ dapi_data > min_brightness ] = 255
    dapi_data[ dapi_data <= min_brightness ] = 0
    dapi_data = 255 - dapi_data
    raw_dapi[ dapi_data == 255 ] = 255
    dapi_data[dapi_data==255] =1
    np.savetxt(f'{prefix}.dapi.trackline.txt',dapi_data,fmt="%d")

    if chip == 'chip715' :
        width_scale = width_pixel / 0.715
        height_scale = height_pixel / 0.715
    else :
        width_scale = width_pixel / 0.5
        height_scale = height_pixel / 0.5
    small=np.matrix(np.array([[width_scale,0,1],[0,height_scale,1],[0,0,1]]))
    new_w = int(raw_dapi.shape[1]*width_scale)
    new_h = int(raw_dapi.shape[0]*height_scale)
    small_dapi = nd.affine_transform(raw_dapi.T, small.I ,output_shape=(new_w,new_h),order=0)
    small_dapi = small_dapi.T
    skio.imsave(f'{prefix}.dapi.masked.small.tiff',small_dapi)

    print('gen mask_dapi end ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)

############################################################################
# main logic of second registration
#############################################################################
# usage
def prepareregistrationdapi_usage():
    print("""
Usage : GEM_toolkit.py secondregistration  -d <dapi tiff file> \\
                                           -o <output prefix>  \\
                                           -c [chip500/chip715, default chip715] \\
                                           -w [um per pixel in width,  default 0.4803250]\\
                                           -h [um per pixel in height, default 0.4802272]\\
                                           -m [min_brightness, default 1]
Notice:
      If the tracklines in result are too dark to find, please try -m 2.
      If the tracklines in result are too bright to find, please try -m 0.
""")

def prepareregistrationdapi_main(argv:[]) :
    dapi_file = ''
    min_brightness = 1
    prefix = ''
    chip = 'chip715'
    width_pixel = 0.4803250
    height_pixel = 0.4802272

    try:
        opts, args = getopt.getopt(argv,"d:m:o:w:h:c:",[   "dapi=",
                                                         "minbright=",
                                                         "output=",
                                                         "width=",
                                                         "height=",
                                                         "chip="])
    except getopt.GetoptError:
        prepareregistrationdapi_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d", "--dapi"):
            dapi_file = arg
        elif opt in ("-w", "--width"):
            width_pixel = float(arg)
        elif opt in ("-h", "--height"):
            height_pixel = float(arg)
        elif opt in ("-m", "--minbright"):
            min_brightness = int(arg)
        elif opt in ('-o' , '--output'):
            prefix = arg
        elif opt in ('-c' , '--chip'):
            chip = arg

    if  ( dapi_file == "" or
          prefix == "" or
          min_brightness <0 or
          min_brightness > 255 or
          not chip in ('chip715' ,'chip500') ):
        prepareregistrationdapi_usage()
        sys.exit(3)

    #######################################################
    #
    # print logs
    #
    #######################################################
    print(f"dapi file is {dapi_file}",file=sys.stderr)
    print(f"chip is {chip}",file=sys.stderr)
    print(f'prefix is {prefix}',file=sys.stderr)
    print(f'min_brightness is {min_brightness}',file=sys.stderr)
    print(f'um per pixel in width is {width_pixel}',file=sys.stderr)
    print(f'um per pixel in height is {height_pixel}',file=sys.stderr)


    #######################################################
    # loading dapi and generate mask_dapi
    #######################################################
    get_mask_dapi(dapi_file,min_brightness,width_pixel,height_pixel,chip,prefix)

