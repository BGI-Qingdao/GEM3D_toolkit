import sys
import time
import getopt
import json
import numpy as np
import scipy.ndimage as nd
from skimage import io as skio
from st3d.model.slice_dataframe import slice_dataframe


###############################################################################
#
# basic chip settings
#
###############################################################################
### T1   500
grid_x = [112, 144, 208, 224, 224, 208, 144, 112, 160]
grid_y = [112, 144, 208, 224, 224, 208, 144, 112, 160]

## T10  715  2940
#grid_x = [ 240, 300, 330, 390, 390, 330, 300, 240, 420]
#grid_y = [ 240, 300, 330, 390, 390, 330, 300, 240, 420]

############################################################################
# main logic of second registration
#############################################################################

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

def get_affine(param : str) -> np.matrix:
    """
        handle '[[0.033629421,0.983042659,-133.4590388],[-0.983042659,0.033629421,2262.081494],[0,0,1]]'

        @return reverse affine matrix.
    """
    return np.matrix(np.array(json.loads(param)))

def find_minPatten(sums,pattern):
    """
    find the minimum pattern

    @args :
        sums     : one-dimension array of all data
        pattern  : one-dimension array of pattern
    @return :
        index of pattern
        the minimum value
    """
    patterns = np.hstack((pattern,pattern))
    for min_len in range(9, 2, -1):
        targets = []
        target_sps = []
        for start_pos in range(0,9):
            pattern_slice = patterns[start_pos:start_pos+min_len]
            tmp_positions = np.cumsum(pattern_slice)
            positions = np.zeros(len(tmp_positions)+1,dtype=int)
            positions[1:len(tmp_positions)+1]=tmp_positions
            results = []
            for pos in  range(len(sums) - np.max(positions) - 1):
                results.append(np.sum(sums[positions+pos]))
            if len(results) == 0 :
                continue
            elif min(results) == 0 :
                targets.append(results.index(0))
                target_sps.append(start_pos)
        if len(targets) == 0 :
            continue
        else:
            min_pos = min(targets)
            min_id = target_sps[targets.index(min_pos)]
            return min_len, min_id , min_pos
    print('FATAL : non pattern found !',file=sys.stderr,flush=True)
    exit(1)

def trackline_mask(expression_matrix : np.ndarray, prefix:str) -> np.ndarray :
    '''
    @param :
       expression_matrix rna expression matrix in ndarray.
    @return :
       mask of rna trackline. 1 represent trackline and 0 represent others.
    '''

    height , width  = expression_matrix.shape
    # -------------------------------------------------------------------------
    # find the first (left-top) point of trackline a 10*10 pattern
    x_sum = np.sum(expression_matrix, 0)  ## horizontal
    y_sum = np.sum(expression_matrix, 1)  ## vertical
    _, x_index , x_pos = find_minPatten(x_sum,grid_x)
    _, y_index , y_pos = find_minPatten(y_sum,grid_y)

    # -------------------------------------------------------------------------
    # find all point of trackline a 10*10 pattern
    mask = np.zeros(expression_matrix.shape, dtype='uint8')

    while x_pos < width :
        if x_pos + 2 < width :
            mask[:,x_pos:x_pos + 3] = 1
        else :
            mask[:,x_pos:width] =1 
        x_pos += grid_x[x_index]
        x_index = x_index + 1
        x_index = x_index % 9

    while y_pos < height:
        if y_pos + 2 < height :
            mask[y_pos:y_pos + 3,:] = 1
        else :
            mask[y_pos:width,:] = 1
        y_pos += grid_y[y_index]
        y_index = y_index + 1
        y_index = y_index % 9

    return mask

def get_mask_rna(gem_file : str , prefix : str) -> np.ndarray :
    print('loading gem ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    gem = slice_dataframe()
    gem.init_from_file(gem_file,1)
    expression = gem.get_expression_count_vector(binsize=1)
    # this may drop some high expression but it's ok for bin1
    # not ok for bin5 !
    expression = expression.astype('uint8')
    skio.imsave(f'{prefix}.heatmap.8bit.tiff',expression)
    print('gen mask_rna ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    mask=trackline_mask(expression,prefix)
    mask[mask==1] = 255
    skio.imsave(f'{prefix}.heatmap.trackline.png',mask)
    mask[mask==255] = 1
    np.savetxt(f'{prefix}.heatmap.trackline.txt',mask,fmt="%d")
    print('gen mask_rna end...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    return mask

def get_mask_dapi(dapi_file:str, min_brightness : int , prefix:str ) ->  np.ndarray: 
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

    print('gen mask_dapi ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    dapi_data[dapi_data>min_brightness]=255
    dapi_data[dapi_data<min_brightness]=0
    dapi_data = 255 - dapi_data
    skio.imsave(f'{prefix}.dapi.trackline.png',dapi_data)
    dapi_data[dapi_data==255] =1
    np.savetxt(f'{prefix}.dapi.trackline.txt',dapi_data,fmt="%d")
    print('gen mask_dapi end ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    return dapi_data

def match_score(mask_rna, mask_dapi ,affineR):
    affinem = nd.affine_transform(mask_dapi.T,affineR,output_shape=mask_rna.T.shape,order=0)
    affinem = affinem.T
    return np.sum(mask_rna[affinem==1])


def find_best_affine( mask_rna, mask_dapi , binsize, scale, fijiyama_reverse_affine):
    ########################################################
    # construct the #1 affine matrix
    #

    ## step-01 zoom
    DAPI_to_smallDAPI_affine = np.matrix(np.array([
              [ scale, 0, 0 ],
              [ 0,  scale, 0 ],
              [ 0,  0,        1 ] ]))

    ## step-02 fijiyama affine
    DAPI_to_bin5_affine = np.matmul(fijiyama_reverse_affine.I,DAPI_to_smallDAPI_affine)

    ## binsize
    bin5_to_bin1_affine =  np.matrix(np.array([
              [ binsize , 0, 0 ],
              [ 0 , binsize, 0 ],
              [ 0 , 0, 1 ] ]))
    ## step-03 bin5-to-bin1
    DAPI_to_bin1_affine = np.matmul(bin5_to_bin1_affine , DAPI_to_bin5_affine)
    print('match score of #1 :{}'.format(match_score(mask_rna,mask_dapi,DAPI_to_bin1_affine.I)),file=sys.stderr,flush=True)

    ########################################################
    # #2 round registration
    #
    print('iterate now ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    fscores=[]
    fparams=[]
    for s in [1,0.98,0.99,1.01,1.02]:
        scale_matrix =  np.matrix(np.array([[s,0,0],[0,s,0],[0,0,1]]))
        scaled = np.matmul(scale_matrix,DAPI_to_bin1_affine)
        for r in [0.0 ,359.0 ,358.0 ,1.0, 2.0]:
            rs = np.sin(r*np.pi/180)
            rc = np.cos(r*np.pi/180)
            rotate_matrix = np.matrix(np.array([[rc,rs,0],[-rs,rc,0,],[0,0,1]]))
            rotated = np.matmul(rotate_matrix,scaled)
            t = 0
            scores = []
            ls = []
            for l in range(-20, 22, 2):
                shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
                shifted = np.matmul(shift,rotated)
                scores.append(match_score(mask_rna,mask_dapi,shifted.I))
                ls.append(l)

            maxhit=max(scores)
            l = ls[scores.index(maxhit)]
            for t in range (-20, 22, 2):
                shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
                shifted = np.matmul(shift,rotated)
                fscores.append(match_score(mask_rna,mask_dapi,shifted.I))
                fparams.append([s,r,l,t])
    print('iterate end...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)

    maxhit=max(fscores)
    param = fparams[fscores.index(maxhit)]
    print(f'match score of #2 :{maxhit}',file=sys.stderr,flush=True)
    print(f'#2 modify : {param}',file=sys.stderr,flush=True)

    ##################################################
    # reconstruct the best affine matrix
    s,r,l,t = param
    scale_matrix =  np.matrix(np.array([[s,0,0],[0,s,0],[0,0,1]]))
    scaled = np.matmul(scale_matrix,DAPI_to_bin1_affine)
    rs = np.sin(r*np.pi/180)
    rc = np.cos(r*np.pi/180)
    rotate_matrix = np.matrix(np.array([[rc,rs,0],[-rs,rc,0,],[0,0,1]]))
    rotated = np.matmul(rotate_matrix,scaled)
    shift = np.matrix(np.array([[1,0,l],[0,1,t],[0,0,1]]))
    shifted = np.matmul(shift,rotated)
    ##################################################
    # return affineR
    return shifted.I

def draw_masks(mask_rna,mask_dapi,affine,best_affineR,prefix):
    affinem = nd.affine_transform(mask_dapi.T,best_affineR,output_shape=mask_rna.T.shape,order=0)
    affinem = affinem.T
    mask_rna[affinem==1]=1
    mask_rna[mask_rna==1]=255
    skio.imsave(f'{prefix}.aligned.png',mask_rna)


############################################################################
# main logic of second registration
#############################################################################
# usage
def secondregistration_usage():
    print("""
Usage : GEM_toolkit.py secondregistration  -g <gem file>  \\
                                           -b <binsize of heatmap used in first round registration> \\
                                           -d <dapi tiff file> \\
                                           -s <scale factor of dapi used in first round registration> \\
                                           -m [minimum brightness threashold of trackline, default 0] \\
                                           -f [fujiyama output matrx, default None] \\
                                           -a [3*3 backward affine matrix, default none] \\
                                           -o <output prefix>

Notice :
     please do not use -f and -a at the same time.

Example of matrix:

  a 3*3 backward affine matrix
    -f '[[0.033629421,0.983042659,-133.4590388],[-0.983042659,0.033629421,2262.081494],[0,0,1]]'
  or a 3*4 fujiyama output matrix
    -a '0.9789672225355872 -0.014001262294250694 0 0.014001262294229377 0.9789672225355872 0 0 0 0.9790673409653101 -49.386112981985995 -98.51787299912003 0'
""")

def secondregistration_main(argv:[]) :
    gem_file = ''
    binsize = ''
    dapi_file = ''
    scale = 1.0
    min_brightness = 0
    fijiyama = ''
    affine = np.zeros((3,3))
    prefix=''

    try:
        opts, args = getopt.getopt(argv,"hg:b:d:s:m:f:a:o:",["help",
                                                         "gem=",
                                                         "binsize=",
                                                         "dapi=",
                                                         "scale=",
                                                         "minbright=",
                                                         "fujiyama=",
                                                         "affine=",
                                                         "output="])
    except getopt.GetoptError:
        secondregistration_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            secondregistration_usage()
            sys.exit(0)
        elif opt in ("-g", "--gem"):
            gem_file = arg
        elif opt in ("-b", "--binsize"):
            binsize = int(arg)
        elif opt in ("-d", "--dapi"):
            dapi_file = arg
        elif opt in ("-s", "--scale"):
            scale = float(arg)
        elif opt in ("-m", "--minbright"):
            min_brightness = int(arg)
        elif opt in ("-f", "--fujiyama"):
            affine = get_fujiyama(arg)
        elif opt in ("-a", "--affine"):
            affine = get_affine(arg)
        elif opt in ('-o' , '--output'):
            prefix = arg

    if  ( gem_file == "" or
          dapi_file == "" or
          prefix == "" or
          binsize < 1 or 
          scale >1 or
          scale <= 0 or 
          min_brightness <0 or
          min_brightness > 255 or
          np.sum(affine) == 0 ):
        secondregistration_usage()
        sys.exit(3)

    #######################################################
    #
    # print logs
    #
    #######################################################
    print(f"gem file is {gem_file}",file=sys.stderr)
    print(f"dapi file is {dapi_file}",file=sys.stderr)
    print(f'prefix is {prefix}',file=sys.stderr)
    print(f'binsize is {binsize}',file=sys.stderr)
    print(f'scale is {scale}',file=sys.stderr)
    print(f'min_brightness is {min_brightness}',file=sys.stderr)
    print(f'affine is {affine}',file=sys.stderr)

    #######################################################
    # loading gem and generate mask_rna
    #######################################################
    mask_rna = get_mask_rna(gem_file,prefix)

    #######################################################
    # loading dapi and generate mask_dapi
    #######################################################
    mask_dapi= get_mask_dapi(dapi_file,min_brightness,prefix)

    #######################################################
    # find best affine
    #######################################################
    best_affineR = find_best_affine( mask_rna, mask_dapi , binsize, scale, affine )

    #######################################################
    # save result
    #######################################################
    print(best_affineR,file=sys.stderr)
    draw_masks(mask_rna,mask_dapi,affine,best_affineR,prefix)
