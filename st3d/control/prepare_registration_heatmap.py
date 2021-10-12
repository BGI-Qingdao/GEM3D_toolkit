import sys
import time
import getopt
import json
import numpy as np
import scipy.ndimage as nd
from skimage import io as skio
from skimage import exposure
from st3d.model.slice_dataframe import slice_dataframe

###############################################################################
#
# basic chip settings
#
###############################################################################
### T1  715  2940 
grid_x_715 = [112, 144, 208, 224, 224, 208, 144, 112, 160]
grid_y_715 = [112, 144, 208, 224, 224, 208, 144, 112, 160]

## T10  500
grid_x_500 = [ 240, 300, 330, 390, 390, 330, 300, 240, 420]
grid_y_500 = [ 240, 300, 330, 390, 390, 330, 300, 240, 420]

############################################################################
# main logic of second registration
#############################################################################

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

def trackline_mask(expression_matrix : np.ndarray, chip:str, prefix:str) -> np.ndarray :
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
    if chip == 'chip715':
        grid_x = grid_x_715
        grid_y = grid_y_715
    else :
        grid_x = grid_x_500
        grid_y = grid_y_500
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

def get_mask_rna(gem_file : str , chip:str ,prefix : str) -> np.ndarray :
    print('loading gem ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    gem = slice_dataframe()
    gem.init_from_file(gem_file,1)
    expression = gem.get_expression_count_vector(binsize=1)
    # this may drop some high expression but it's ok for bin1
    # not ok for bin5 !
    expression = expression.astype('uint8')
    skio.imsave(f'{prefix}.heatmap.tiff',expression)
    print('gen mask_rna ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    mask=trackline_mask(expression,chip,prefix)
    mask[mask==1] = 255
    skio.imsave(f'{prefix}.heatmap.trackline.tiff',mask)
    expression[mask==255]=255
    expression = exposure.equalize_adapthist(expression)
    expression = expression*255
    expression = expression.astype('uint8')
    skio.imsave(f'{prefix}.heatmap.marked.tiff',expression)
    mask[mask==255] = 1
    np.savetxt(f'{prefix}.heatmap.trackline.txt',mask,fmt="%d")
    print('gen mask_rna end...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)

############################################################################
# main logic of second registration
#############################################################################
# usage
def prepareregistrationheatmap_usage():
    print("""
Usage : GEM_toolkit.py secondregistration  -g <gem file>  \\
                                           -o <output prefix> \\
                                           -c [chip715/chip500, default chip715]
""")

def prepareregistrationheatmap_main(argv:[]) :
    gem_file = ''
    prefix=''
    chip='chip715'
    try:
        opts, args = getopt.getopt(argv,"hg:c:o:",["help",
                                                  "gem=",
                                                  "chip=",
                                                  "output="])
    except getopt.GetoptError:
        prepareregistrationheatmap_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            prepareregistrationheatmap_usage()
            sys.exit(0)
        elif opt in ("-g", "--gem"):
            gem_file = arg
        elif opt in ("-c", "--chip"):
            chip = arg
        elif opt in ('-o' , '--output'):
            prefix = arg

    if  ( gem_file == "" or
          prefix == "" or
          not chip in ( 'chip715','chip500' ) ):
        prepareregistrationheatmap_usage()
        sys.exit(3)

    #######################################################
    #
    # print logs
    #
    #######################################################
    print(f"gem file is {gem_file}",file=sys.stderr)
    print(f'prefix is {prefix}',file=sys.stderr)
    print(f'chip is {chip}',file=sys.stderr)

    #######################################################
    # loading gem and generate mask_rna
    #######################################################
    get_mask_rna(gem_file,chip,prefix)

