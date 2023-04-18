import sys
import time
import getopt
import numpy as np
import scipy.ndimage as nd
import scipy.signal as sg
from skimage import io as skio
from skimage import img_as_ubyte
def get_mask_dapi(dapi_file,min_brightness,width_pixel,height_pixel,chip,prefix,need_filter,mask_mode):
    print('loading ssDNA ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    dapi_data = skio.imread(dapi_file)
    dapi_data = img_as_ubyte(dapi_data)
    if len(dapi_data.shape) == 3:  # RGB to 8 bit gray
        if dapi_data.shape[2] == 3:
            new_data = np.zeros((dapi_data.shape[0], dapi_data.shape[1]), dtype=int)
            new_data = new_data + dapi_data[:, :, 0]
            new_data = new_data + dapi_data[:, :, 1]
            new_data = new_data + dapi_data[:, :, 2]
            new_data = new_data/3
            dapi_data = new_data
            dapi_data = dapi_data.astype('uint8')
        elif dapi_data.shape[2] == 2:
            new_data = np.zeros((dapi_data.shape[0], dapi_data.shape[1]), dtype=int)
            new_data = new_data + dapi_data[:, :, 0]
            new_data = new_data + dapi_data[:, :, 1]
            new_data = new_data/2
            dapi_data = new_data
            dapi_data = dapi_data.astype('uint8')
    dapi_data = dapi_data.astype('uint8')
    raw_dapi = dapi_data.copy()

    print('gen mask_ssDNA...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    
    if mask_mode :
        dapi_data[ dapi_data > min_brightness ] = 255
        dapi_data[ dapi_data <= min_brightness ] = 0
        dapi_data = 255 - dapi_data
        if need_filter:
            filtered_data = sg.medfilt(dapi_data,kernel_size=(5,5))
            dapi_data = np.uint8(filtered_data)
        skio.imsave(f'{prefix}.ssdna.trackline.png',dapi_data)
        raw_dapi[ dapi_data == 255 ] = 255
    else:
        dapi_data[ dapi_data <= min_brightness ] = 255 - dapi_data[ dapi_data <= min_brightness ]
        dapi_data[ raw_dapi > min_brightness ] = 0
        dapi_data[ dapi_data > 0 ] = 256 - dapi_data[ dapi_data > 0 ]
        dapi_data[ dapi_data > 0 ] = (255-((100//(min_brightness+1)) * dapi_data[ dapi_data > 0 ]))
        raw_dapi[ dapi_data >0 ] = dapi_data[dapi_data>0]

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
    skio.imsave(f'{prefix}.ssdna.masked.small.png',small_dapi)

    print('gen mask_ssdna end ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)

############################################################################
# main logic of second registration
#############################################################################
# usage
def prepareregistrationdapi_usage():
    print("""
Usage : GEM_toolkit.py prepare_registration_ssdna \\
             -d <ssdna tif/png file> \\
             -o <output prefix>  \\
             -c [chip500/chip715, default chip715] \\
             -w [um per pixel in width,  default 0.4803250]\\
             -h [um per pixel in height, default 0.4802272]\\
             -f [midfilt or not. default not set] \\
             -m [min_brightness, default 1]
             -M [generate mask, default not set] \\
Notice:
      If the tracklines in result are too dark to find, please try -m 2.
      If the tracklines in result are too bright to find, please try -m 0 or set -f.

      If the quality of ssDNA graph are too bad, try to update it by ImageJ :
         1. convert it int 8bit; 
         2. run enhance contrast;
         3. find the trackline brightness by eye;
         4. use the new ssDNA as input and assign the trackline brightness by -m.
""")

def prepareregistrationdapi_main(argv:[]) :
    dapi_file = ''
    min_brightness = 1
    prefix = ''
    chip = 'chip715'
    width_pixel = 0.4803250
    height_pixel = 0.4802272
    need_filter=False
    mask_mode = False
    try:
        opts, args = getopt.getopt(argv,"d:m:o:w:h:c:fM",[   "dapi=",
                                                         "minbright=",
                                                         "output=",
                                                         "width=",
                                                         "height=",
                                                         "chip=","filter","Mask"])
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
        elif opt in ('-f' , '--filter'):
            need_filter = True
        elif opt in ('-M' , '--Mask'):
            mask_mode = True

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
    print(f"ssdna file is {dapi_file}",file=sys.stderr)
    print(f"chip is {chip}",file=sys.stderr)
    print(f'prefix is {prefix}',file=sys.stderr)
    print(f'min_brightness is {min_brightness}',file=sys.stderr)
    print(f'um per pixel in width is {width_pixel}',file=sys.stderr)
    print(f'um per pixel in height is {height_pixel}',file=sys.stderr)


    #######################################################
    # loading dapi and generate mask_dapi
    #######################################################
    get_mask_dapi(dapi_file,min_brightness,width_pixel,height_pixel,chip,prefix,need_filter,mask_mode)

