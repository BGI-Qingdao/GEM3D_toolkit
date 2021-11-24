import sys
import getopt
import numpy as np

# functions
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

def get_scale(chip , width_pixel, height_pixel):
    if chip == 'chip715' :
        width_scale = width_pixel / 0.715
        height_scale = height_pixel / 0.715
    else :
        width_scale = width_pixel / 0.5
        height_scale = height_pixel / 0.5
    return width_scale,height_scale

# usage
def handle_trackEM_matrix_usage():
    print("""
Usage : handle_trackEM_matrix.py -t <trackEM matrix> \\
        -c [chip500/chip715, default chip715] \\
        -w [um per pixel in width,  default 0.4803250]\\
        -h [um per pixel in height, default 0.4802272]\\

Example :
     handle_trackEM_matrix.py -t '-0.010963829,-0.999939895,0.999939895,-0.010963829,-129.2603788,1664.628308'
     """,flush=True)

def get_affine(chip , width_pixel, height_pixel,affine):
    width_scale , height_scale =  get_scale(chip , width_pixel, height_pixel)
    DAPI_to_smallDAPI_affine = np.matrix(np.array([
        [ width_scale, 0, 0 ],
        [ 0,  height_scale, 0 ],
        [ 0,  0,        1 ] ]))
    DAPI_to_bin1_affine = np.matmul(affine.I,DAPI_to_smallDAPI_affine)
    print("The final backward affine matrix :")
    print(DAPI_to_bin1_affine.I.tolist())
    print("The final forward affine matrix :")
    print(DAPI_to_bin1_affine.tolist())


def handle_trackEM_matrix_main(argv:[]) :
    chip = 'chip715'
    width_pixel = 0.4803250
    height_pixel = 0.4802272
    affine=np.eye(3)

    valid=False
    try:
        opts, args = getopt.getopt(argv,"w:h:c:t:",[ "width=",
                                                     "height=",
                                                     "chip=",
                                                     "trackem"])
    except getopt.GetoptError:
        handle_trackEM_matrix_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-w", "--width"):
            width_pixel = float(arg)
        elif opt in ("-h", "--height"):
            height_pixel = float(arg)
        elif opt in ('-t' , '--trackem'):
            affine = get_trackEM(arg)
            valid=True
        elif opt in ('-c' , '--chip'):
            chip = arg
    if not valid :
        handle_trackEM_matrix_usage()
        sys.exit(2)

handle_trackEM_matrix_main(sys.argv[1:])
