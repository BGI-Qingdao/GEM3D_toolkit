import sys
import time
import getopt
import numpy as np
import scipy.ndimage as nd
from skimage import io as skio
from skimage import exposure
from gemtk.slice_dataframe import slice_dataframe

###############################################################################
# basic chip settings
###############################################################################

### chip715
grid_x_715 = [112, 144, 208, 224, 224, 208, 144, 112, 160]
grid_y_715 = [112, 144, 208, 224, 224, 208, 144, 112, 160]

##  chip500
grid_x_500 = [ 240, 300, 330, 390, 390, 330, 300, 240, 420]
grid_y_500 = [ 240, 300, 330, 390, 390, 330, 300, 240, 420]

############################################################################
# main logic of second registration
#############################################################################

def find_pattern(sums,pattern):
    """
    find the tracklines 

    @args :
        sums     : one-dimension array of all data
        pattern  : one-dimension array of pattern
    @return :
        start of all tracklines
    """
    pattern_len = np.sum(pattern)
    max_pattern_num = int(int((len(sums)+pattern_len-1)//pattern_len)+1)
    patterns = pattern * max_pattern_num
    patternarr = np.array(patterns)
    tmp_positions = np.cumsum(patternarr)
    positions = np.zeros(len(tmp_positions)+1,dtype=int)
    positions[1:len(tmp_positions)+1]=tmp_positions
    for shift_x in range(0,pattern_len,1):
        tmp_indexs = positions - shift_x
        tmp_indexs = tmp_indexs[tmp_indexs>=0]
        tmp_indexs = tmp_indexs[tmp_indexs<len(sums)-2]
        if len(tmp_indexs)<2:
            continue
        if np.sum(sums[tmp_indexs])+ np.sum(sums[tmp_indexs+1])+np.sum(sums[tmp_indexs+2]) == 0 :
             return tmp_indexs
 
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
    x_sum = np.sum(expression_matrix, 0)  ## horizontal
    y_sum = np.sum(expression_matrix, 1)  ## vertical
    if chip == 'chip715':
        grid_x = grid_x_715
        grid_y = grid_y_715
    else :
        grid_x = grid_x_500
        grid_y = grid_y_500
    x_indexes = find_pattern(x_sum,grid_x)
    y_indexes = find_pattern(y_sum,grid_y)
    mask = np.zeros(expression_matrix.shape, dtype='uint8')
    mask[:,x_indexes]=1
    mask[:,x_indexes+1]=1
    mask[:,x_indexes+2]=1
    mask[y_indexes,:] = 1
    mask[y_indexes+1,:] = 1
    mask[y_indexes+2,:] = 1
    return mask

def enhance_bin5(expression):
    ret = np.zeros(expression.shape,dtype=int)
    h,w=expression.shape
    for i in range(0,6):
        for j in range(0,6):
            newm = np.zeros(expression.shape)
            newm[i:,j:] = expression[:h-i,:w-j]
            ret = ret + newm
    ret[ret>255]=255
    ret = ret.astype('uint8')
    return ret


def get_mask_rna(gem_file : str , chip:str ,prefix : str, eb5:str,draw_trackline,xmin,ymin) -> np.ndarray :
    print('loading gem ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    gem = slice_dataframe()
    gem.init_from_file(gem_file,xmin,ymin)
    expression = gem.get_expression_count_vector(binsize=1)
    # this may drop some high expression but it's ok for bin1
    # not ok for bin5 !
    expression = expression.astype('uint8')
    print('gen mask_rna ...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)
    mask=trackline_mask(expression,chip,prefix)
    mask[mask==1] = 255
    skio.imsave(f'{prefix}.heatmap.trackline.png',mask)
    if eb5 == 'yes':
        expression=enhance_bin5(expression)
    if draw_trackline == True:
        expression[mask==255]=255
    expression = exposure.equalize_adapthist(expression)
    expression = expression*255
    expression = expression.astype('uint8')
    skio.imsave(f'{prefix}.heatmap.marked.png',expression)
    print('gen mask_rna end...',file=sys.stderr)
    print(time.strftime("%Y-%m-%d %H:%M:%S"),file=sys.stderr,flush=True)

############################################################################
# main logic of second registration
#############################################################################
# usage
def prepareregistrationheatmap_usage():
    print("""
Usage : GEM_toolkit.py prepare_registration_heatmap \\
             -g <gem file>  \\
             -o <output prefix> \\
             -c [chip715/chip500, default chip715] \\
             -e [enhance by bin5, default not set] \\
             -n [yes/no draw trackline, default yes] \\
             -x [xmin, default None and caculate real xmin]
             -y [ymin, default None and caculate real ymin]
""")

def prepareregistrationheatmap_main(argv:[]) :
    gem_file = ''
    prefix = ''
    chip = 'chip715'
    eb5 = 'no'
    draw_trackline=True
    xmin=None
    ymin=None
    try:
        opts, args = getopt.getopt(argv,"hg:c:o:n:x:y:e",["help",
                                                  "gem=",
                                                  "chip=",
                                                  "output=",
                                                  "eb5"])
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
        elif opt == "-x":
            xmin = int(arg)
        elif opt == "-y":
            ymin = int(arg)
        elif opt in ('-n' ):
            if arg == 'no' :
                draw_trackline=False
        elif opt in ('-o' , '--output'):
            prefix = arg
        elif opt in ('-e' , '--eb5'):
            eb5 = 'yes'

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
    get_mask_rna(gem_file,chip,prefix,eb5,draw_trackline,xmin,ymin)
