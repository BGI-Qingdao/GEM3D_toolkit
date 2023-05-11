import sys
import time
import getopt
import json
import numpy as np
import scipy.ndimage as nd
from skimage import io as skio

from multiprocessing import Pool

from PIL import ImageFile
from PIL import Image

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

def get_fujiyama(param : str) -> np.matrix:
    """
        handle  '0.9789672225355872 -0.014001262294250694 0 0.014001262294229377 0.9789672225355872 0 0 0 0.9790673409653101 -49.386112981985995 -98.51787299912003 0'

        @return reverse affine matrix.
    """
    affine = np.zeros((3,3))
    in_data = np.array(param.split(' ')).astype(float).reshape((4,3))
    affine[0]=in_data[0]
    affine[1]=in_data[1]
    affine[:,2]=in_data[3].T
    affine[2] = [0,0,1]
    return np.matrix(affine)

def get_trackEM(param :str) -> np.matrix:
    """
        handle '-0.010963829,-0.999939895,0.999939895,-0.010963829,-129.2603788,1664.628308'

        @return reverse affine matrix.
    """
    affine = np.zeros((3,3))
    in_data = np.array(param.split(',')).astype(float).reshape((3,2))
    affine[0:2,:]=in_data.T
    affine[2] = [0,0,1]
    return np.matrix(affine).I


def get_affine(param : str) -> np.matrix:
    """
        handle '[[0.033629421,0.983042659,-133.4590388],[-0.983042659,0.033629421,2262.081494],[0,0,1]]'

        @return reverse affine matrix.
    """
    return np.matrix(np.array(json.loads(param)))

def match_score(mask_rna, mask_dapi ,affineR):
    affinem = nd.affine_transform(mask_dapi.T,affineR,output_shape=mask_rna.T.shape,order=0)
    affinem = affinem.T
    return np.sum(mask_rna[affinem==1])

def draw_masks(mask_rna,mask_dapi,best_affineR,prefix,rid):
    draw=np.zeros((mask_rna.shape[0], mask_rna.shape[1],3),dtype='uint8')
    affinem = nd.affine_transform(mask_dapi.T,best_affineR,output_shape=mask_rna.T.shape,order=0)
    affinem = affinem.T
    draw[affinem==1,0]=255
    draw[mask_rna==1,1]=255
    skio.imsave(f'{prefix}.aligned.r{rid}.png',draw)

def find_best_affine_roi(args:[]):
    heatmap_file = args[0]
    dapi_file = args[1]
    width_scale = args[2]
    height_scale = args[3]
    affine_list = args[4]
    prefix = args[5]
    s = args[6]
    r = args[7]
    shifts=args[8]
    xh,yh,wh,hh,xd,yd,wd,hd,fake = args[9:]

    # load data of whole image
    mask_rna = skio.imread(heatmap_file)
    # chop roi
    mask_rna = mask_rna[yh:yh+hh,xh:xh+wh]
    # format mask
    mask_rna[mask_rna==255] = 1
    # load data of whole image
    mask_dapi = skio.imread(dapi_file)
    # chop roi
    mask_dapi = mask_dapi[yd:yd+hd,xd:xd+wd]
    # format mask
    mask_dapi[mask_dapi==255] = 1

    affine = np.matrix(np.array(affine_list))

    ########################################################
    # construct the #1 affine matrix
    #

    # step1 : shift by roi
    DAPI_shift =  np.matrix(np.array([
              [ 1, 0 , xd ],
              [ 0, 1 , yd ],
              [ 0,  0, 1  ]]))

    shifted_DAPI_to_smallDAPI_affine = np.matrix(np.array([
              [ width_scale, 0, 0 ],
              [ 0,  height_scale, 0 ],
              [ 0,  0,        1 ] ]))

    smallDAPI_to_heatmap = affine.I

    heatmap_to_shiftedheatmap = np.matrix(np.array([
              [ 1, 0 , -xh ],
              [ 0, 1 , -yh ],
              [ 0,  0, 1   ]]))



    DAPI_to_heatmap = np.matmul(shifted_DAPI_to_smallDAPI_affine, DAPI_shift)
    DAPI_to_heatmap = np.matmul(smallDAPI_to_heatmap, DAPI_to_heatmap)
    DAPI_to_heatmap = np.matmul(heatmap_to_shiftedheatmap, DAPI_to_heatmap)

    if s == 1 and r == 0 :
        ## step-02 affine
        first_affineR = DAPI_to_heatmap.I
        print('match score of #1 :{}'.format(match_score(mask_rna,mask_dapi,first_affineR)),file=sys.stderr,flush=True)
        print(first_affineR.tolist(),file=sys.stderr,flush=True)
        draw_masks(mask_rna,mask_dapi,first_affineR,prefix,1)
    if fake == True:
        return 1000,[1,0,0,0]
    ########################################################
    # #2 round registration
    #
    scale_matrix =  np.matrix(np.array([[s,0,0],[0,s,0],[0,0,1]]))
    scaled = np.matmul(scale_matrix,DAPI_to_heatmap)
    rs = np.sin(r*np.pi/180)
    rc = np.cos(r*np.pi/180)
    rotate_matrix = np.matrix(np.array([[rc,rs,0],[-rs,rc,0,],[0,0,1]]))
    rotated = np.matmul(rotate_matrix,scaled)

    scores = []
    ls = []
    t = 0
    for l in shifts:
        shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
        shifted = np.matmul(shift,rotated)
        scores.append(match_score(mask_rna,mask_dapi,shifted.I))
        ls.append(l)

    maxhit=max(scores)
    l = ls[scores.index(maxhit)]

    fscores=[]
    fparams=[]
    for t in shifts:
        shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
        shifted = np.matmul(shift,rotated)
        fscores.append(match_score(mask_rna,mask_dapi,shifted.I))
        fparams.append([s,r,l,t])
    maxhit=max(fscores)
    param = fparams[fscores.index(maxhit)]
    return maxhit, param


def correct_roi(heatmap_file,dapi_file,width_scale,height_scale,affine,prefix,tasks,scales,rotates,shifts,
                xh,yh,wh,hh,xd,yd,wd,hd,
                region_name,fake=False):
    ########################################################
    # find best affine
    #
    print(f'iterate for {region_name} now ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    args = []
    for s in scales:
        for r in rotates:
            args.append([heatmap_file,
                             dapi_file,
                             width_scale,
                             height_scale,
                             affine.tolist(),
                             f"{prefix}_{region_name}",
                             s,
                             r,
                             shifts,
                             xh,yh,wh,hh,xd,yd,wd,hd,fake])
    fscores=[]
    fparams=[]
    with Pool(tasks) as p:
        for maxhit,param in  p.map(find_best_affine_roi,args):
            fscores.append(maxhit)
            fparams.append(param)
    print(f'iterate for {region_name} end...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    maxhit=max(fscores)
    param = fparams[fscores.index(maxhit)]
    print(f'match score of #2 :{maxhit}',file=sys.stderr,flush=True)
    print(f'#2 modify : {param}',file=sys.stderr,flush=True)
    s,r,l,t = param

    ########################################################
    # loading datas
    #

    # load data of whole image
    mask_rna = skio.imread(heatmap_file)
    # chop roi
    mask_rna = mask_rna[yh:yh+hh,xh:xh+wh]
    # format mask
    mask_rna[mask_rna==255] = 1
    # load data of whole image
    mask_dapi = skio.imread(dapi_file)
    # chop roi
    mask_dapi = mask_dapi[yd:yd+hd,xd:xd+wd]
    # format mask
    mask_dapi[mask_dapi==255] = 1

    ########################################################
    # construct the #1 affine matrix
    #

    # step1 : shift by roi
    DAPI_shift =  np.matrix(np.array([
              [ 1, 0 , xd ],
              [ 0, 1 , yd ],
              [ 0,  0, 1  ]]))

    shifted_DAPI_to_smallDAPI_affine = np.matrix(np.array([
              [ width_scale, 0, 0 ],
              [ 0,  height_scale, 0 ],
              [ 0,  0,        1 ] ]))

    smallDAPI_to_heatmap = affine.I

    heatmap_to_shiftedheatmap = np.matrix(np.array([
              [ 1, 0 , -xh ],
              [ 0, 1 , -yh ],
              [ 0,  0, 1   ]]))

    DAPI_to_heatmap = np.matmul(shifted_DAPI_to_smallDAPI_affine, DAPI_shift)
    DAPI_to_heatmap = np.matmul(smallDAPI_to_heatmap, DAPI_to_heatmap)
    DAPI_to_heatmap = np.matmul(heatmap_to_shiftedheatmap, DAPI_to_heatmap)

    scale_matrix =  np.matrix(np.array([[s,0,0],[0,s,0],[0,0,1]]))
    scaled = np.matmul(scale_matrix,DAPI_to_heatmap)
    rs = np.sin(r*np.pi/180)
    rc = np.cos(r*np.pi/180)
    rotate_matrix = np.matrix(np.array([[rc,rs,0],[-rs,rc,0,],[0,0,1]]))
    rotated = np.matmul(rotate_matrix,scaled)
    shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
    shifted = np.matmul(shift,rotated)
    best_affineR = shifted.I
    print(best_affineR.tolist(),file=sys.stderr)
    np.savetxt(f'{prefix}_{region_name}.best_affineR.txt',best_affineR)
    ########################################################
    # draw the #2 results
    #
    draw_masks(mask_rna,mask_dapi,best_affineR,f"{prefix}_{region_name}",2)

def find_best_affine(args:[]):
    heatmap_file = args[0]
    dapi_file = args[1]
    width_scale = args[2]
    height_scale = args[3]
    affine_list = args[4]
    prefix = args[5]
    s = args[6]
    r = args[7]
    shifts=args[8]
    fake = args[9]

    mask_rna = skio.imread(heatmap_file)
    mask_rna[mask_rna==255] = 1
    mask_dapi = skio.imread(dapi_file)
    mask_dapi[mask_dapi==255] = 1
    #mask_rna = np.loadtxt(heatmap_file,delimiter=' ',dtype='uint8')
    #mask_dapi = np.loadtxt(dapi_file,delimiter=' ',dtype='uint8')
    affine = np.matrix(np.array(affine_list))

    ########################################################
    # construct the #1 affine matrix
    #
    DAPI_to_smallDAPI_affine = np.matrix(np.array([
              [ width_scale, 0, 0 ],
              [ 0,  height_scale, 0 ],
              [ 0,  0,        1 ] ]))
    DAPI_to_bin1_affine = np.matmul(affine.I,DAPI_to_smallDAPI_affine)
    if s == 1 and r == 0 :
        ## step-02 affine
        first_affineR = DAPI_to_bin1_affine.I
        print('match score of #1 :{}'.format(match_score(mask_rna,mask_dapi,first_affineR)),file=sys.stderr,flush=True)
        print(first_affineR.tolist(),file=sys.stderr,flush=True)
        draw_masks(mask_rna,mask_dapi,first_affineR,prefix,1)

    if fake == True:
        return 1000,[1,0,0,0]
    ########################################################
    # #2 round registration
    #
    scale_matrix =  np.matrix(np.array([[s,0,0],[0,s,0],[0,0,1]]))
    scaled = np.matmul(scale_matrix,DAPI_to_bin1_affine)
    rs = np.sin(r*np.pi/180)
    rc = np.cos(r*np.pi/180)
    rotate_matrix = np.matrix(np.array([[rc,rs,0],[-rs,rc,0,],[0,0,1]]))
    rotated = np.matmul(rotate_matrix,scaled)

    scores = []
    ls = []
    t = 0
    for l in shifts:
        shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
        shifted = np.matmul(shift,rotated)
        scores.append(match_score(mask_rna,mask_dapi,shifted.I))
        ls.append(l)

    maxhit=max(scores)
    l = ls[scores.index(maxhit)]

    fscores=[]
    fparams=[]
    for t in shifts:
        shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
        shifted = np.matmul(shift,rotated)
        fscores.append(match_score(mask_rna,mask_dapi,shifted.I))
        fparams.append([s,r,l,t])
    maxhit=max(fscores)
    param = fparams[fscores.index(maxhit)]
    return maxhit, param

def correct_all(heatmap_file,dapi_file,width_scale,height_scale,affine,prefix,tasks,scales,rotates,shifts,fake=False):
    print('iterate now ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    args = []
    for s in scales:
        for r in rotates:
            args.append([heatmap_file,
                             dapi_file,
                             width_scale,
                             height_scale,
                             affine.tolist(),
                             prefix,
                             s,
                             r,
                             shifts,
                             fake])
    fscores=[]
    fparams=[]
    with Pool(tasks) as p:
        for maxhit,param in  p.map(find_best_affine,args):
            fscores.append(maxhit)
            fparams.append(param)
    print('iterate end...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    maxhit=max(fscores)
    param = fparams[fscores.index(maxhit)]
    print(f'match score of #2 :{maxhit}',file=sys.stderr,flush=True)
    print(f'#2 modify : {param}',file=sys.stderr,flush=True)
    s,r,l,t=param
    ##################################################
    # reconstruct the best affine matrix
    DAPI_to_smallDAPI_affine = np.matrix(np.array([
              [ width_scale, 0, 0 ],
              [ 0,  height_scale, 0 ],
              [ 0,  0,        1 ] ]))
    DAPI_to_bin1_affine = np.matmul(affine.I,DAPI_to_smallDAPI_affine)
    scale_matrix =  np.matrix(np.array([[s,0,0],[0,s,0],[0,0,1]]))
    scaled = np.matmul(scale_matrix,DAPI_to_bin1_affine)
    rs = np.sin(r*np.pi/180)
    rc = np.cos(r*np.pi/180)
    rotate_matrix = np.matrix(np.array([[rc,rs,0],[-rs,rc,0,],[0,0,1]]))
    rotated = np.matmul(rotate_matrix,scaled)
    shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
    shifted = np.matmul(shift,rotated)
    best_affineR = shifted.I
    print(best_affineR.tolist(),file=sys.stderr)
    np.savetxt(f'{prefix}.best_affineR.txt',best_affineR)
    mask_rna = skio.imread(heatmap_file)
    mask_rna[mask_rna==255] = 1
    mask_dapi = skio.imread(dapi_file)
    mask_dapi[mask_dapi==255] = 1
    draw_masks(mask_rna,mask_dapi,best_affineR,prefix,2)

############################################################################
# main logic of second registration
#############################################################################
# usage
def secondregistration_usage():
    print("""
Usage : GEM_toolkit.py second_registration \\
                 -H <heatmap.trackline.tif/png>  \\
                 -d <ssDNA.trackline.tif/png> \\
                 -o <output prefix> \\
                 -f [Fujiyama output matrix, default None] \\
                 -t [TrackEM output matrix, default None]\\
                 -a [3*3 backward affine matrix, default none] \\
                 -c [chip715/chip500, default chip500] \\
                 -w [um per pixel in width,  default 0.5]\\
                 -h [um per pixel in height, default 0.5]\\
                 -l [S/M/L search area. default S] \\
                 -s [thread number, default 8] \\
                 -r [roi json file, default none ] \\
                 -F [yes/no, default no. fake round2] \\

Notice :
     please only use one of ( -f , -a , -t ) .

Example of matrix:

  A 3*3 backward affine matrix
    -f '[[0.033629421,0.983042659,-133.4590388],[-0.983042659,0.033629421,2262.081494],[0,0,1]]'

  or a 3*4 Fujiyama output matrix
    -a '0.9789672225355872 -0.014001262294250694 0 0.014001262294229377 0.9789672225355872 0 0 0 0.9790673409653101 -49.386112981985995 -98.51787299912003 0'

  or a 2*3 TrackEM output matrix
    -t '-0.010963829,-0.999939895,0.999939895,-0.010963829,-129.2603788,1664.628308'
""")

def secondregistration_main(argv:[]) :
    heatmap_file = ''
    dapi_file = ''
    prefix = ''
    affine = np.zeros((3,3))
    chip = 'chip500'
    width_pixel = 0.5
    height_pixel = 0.5
    level='S'
    tasks=8
    roi = ''
    fake = False
    try:
        opts, args = getopt.getopt(argv,"H:d:o:f:a:t:c:w:h:l:s:r:F:",["heatmap=",
                                                         "dapi=",
                                                         "output=",
                                                         "fujiyama=",
                                                         "affine=",
                                                         "trackem=",
                                                         "chip=",
                                                         "width=",
                                                         "height=",
                                                         "level=",
                                                         'thread=',
                                                         'roi='
                                                         ])
    except getopt.GetoptError:
        secondregistration_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-H", "--heatmap_file"):
            heatmap_file = arg
        elif opt in ("-d", "--dapi"):
            dapi_file = arg
        elif opt in ("-f", "--fujiyama"):
            affine = get_fujiyama(arg)
        elif opt in ("-a", "--affine"):
            affine = get_affine(arg)
        elif opt in ('-o' , '--output'):
            prefix = arg
        elif opt in ('-t' , '--trackem'):
            affine = get_trackEM(arg)
        elif opt in ('-c' , '--chip'):
            chip = arg
        elif opt in ("-w", "--width"):
            width_pixel = float(arg)
        elif opt in ("-h", "--height"):
            height_pixel = float(arg)
        elif opt in ("-l", "--level"):
            level = arg
        elif opt in ("-s", "--thread"):
            tasks = int(arg)
        elif opt in ("-r", "--roi"):
            roi = arg
        elif opt in ("-F"):
            if arg == 'yes':
                fake = True

    if  ( heatmap_file == "" or
          dapi_file == "" or
          prefix == "" or
          np.sum(affine) == 0 or 
          not chip in ('chip715','chip500') or 
          not level in ('S','L','M')  or 
          tasks < 1 ):
        secondregistration_usage()
        sys.exit(3)

    #######################################################
    #
    # print logs
    #
    #######################################################
    print(f"heatmap file is {heatmap_file}",file=sys.stderr)
    print(f"dapi file is {dapi_file}",file=sys.stderr)
    print(f'prefix is {prefix}',file=sys.stderr)
    print(f'affine is {affine}',file=sys.stderr)
    print(f'um per pixel in width is {width_pixel}',file=sys.stderr)
    print(f'um per pixel in height is {height_pixel}',file=sys.stderr)
    print(f"chip is {chip}",file=sys.stderr)
    print(f"level is {level}",file=sys.stderr)
    print(f"thread number is {tasks}",file=sys.stderr,flush=True)

    ## step-01 zoom
    if chip == 'chip715' :
        width_scale = width_pixel / 0.715
        height_scale = height_pixel / 0.715
    else :
        width_scale = width_pixel / 0.5
        height_scale = height_pixel / 0.5

    if level == 'S':
        scales = [1,0.999,0.998,0.997,0.996,1.001,1.002,1.003,1.004]
        #rotates = [399.6,399.7,399.8,399.9,0,0.1,0.2,0.3,0.4]
        rotates = [359.8,359.85,359,359.95,0,0.05,0.1,0.15,0.2]
        shifts = range(-15, 16, 1)
    elif level == 'M' :
        scales = [1,0.999,0.998,0.997,0.996,0.995,0.994,0.993,1.001,1.002,1.003,1.004,1.005,1.006,1.007]
        rotates = [359.5,359.4,359.3,359.6,359.7,359.8,359.9,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]
        shifts = range(-20, 22, 1)
    elif level == 'L' :
        scales = [1,0.999,0.998,0.997,0.996,0.995,0.994,0.993,0.992,0.991,0.99,1.001,1.002,1.003,1.004,1.005,1.006,1.007,1.008,1.009,1.01]
        rotates = [359.5,359.4,359.3,359.2,359.1,359,359.6,359.7,359.8,359.9,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
        shifts = range(-30, 32, 1)

    #scales = [1,0.999,0.998]
    #rotates = [399.5,399.4,1]
    #shifts = [1,2,3]
    #######################################################
    # find best affine
    #######################################################

    if roi == '' :
        correct_all(heatmap_file,dapi_file,width_scale,height_scale,affine,prefix,tasks,scales,rotates,shifts,fake)
    else :
        roi_pairs = json.load(open(roi))
        for a_roi_pair in roi_pairs:
            region_name = a_roi_pair[0]
            xh,yh,wh,hh = a_roi_pair[1]
            xd,yd,wd,hd = a_roi_pair[2]
            correct_roi(heatmap_file,dapi_file,width_scale,
                    height_scale,affine,prefix,tasks,scales,rotates,shifts,
                    xh,yh,wh,hh,xd,yd,wd,hd,region_name,fake)

