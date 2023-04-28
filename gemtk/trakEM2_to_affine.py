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
def trackEM2_to_affine_usage():
    print("""
Usage : trackEM2_to_affine.py -t <trakEM ssDNA matrix> \\
                                 -T <trakEM headmap matrix> \\
                                 -o <output prefix> \\
                                 -c [chip500/chip715, default chip500] \\
                                 -w [um per pixel in width,  default 0.5]\\
                                 -h [um per pixel in height, default 0.5]\\

Example :
     trackEM2_to_affine.py -t '-0.010963829,-0.999939895,0.999939895,-0.010963829,-129.2603788,1664.628308' \\ 
                              -T '1,0,0,0.1,-54,123' -o ttt
""",flush=True)


def trakEM2_to_affine_main(argv:[]) :
    chip = 'chip500'
    width_pixel = 0.5
    height_pixel = 0.5
    affine=np.eye(3)
    affine1=np.eye(3)
    prefix=""
    valid=False
    valid1=False
    try:
        opts, args = getopt.getopt(argv,"w:h:c:t:T:o:",[ "width=",
                                                     "height=",
                                                     "chip=",
                                                     "trackem=",
                                                     "heatmap=",
                                                     "prefix="])
    except getopt.GetoptError:
        trackEM2_to_affine_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-w", "--width"):
            width_pixel = float(arg)
        elif opt in ("-h", "--height"):
            height_pixel = float(arg)
        elif opt in ('-t' , '--trackem'):
            affine = get_trackEM(arg)
            valid=True
        elif opt in ('-T' , '--heatmap'):
            affine1 = get_trackEM(arg)
            valid1 =True
        elif opt in ('-c' , '--chip'):
            chip = arg
        elif opt in ('-o' , '--prefix'):
            prefix = arg

    if (not valid and not valid1) or prefix == "":
        trackEM2_to_affine_usage()
        sys.exit(2)

    width_scale , height_scale =  get_scale(chip , width_pixel, height_pixel)
    
    DAPI_to_smallDAPI_affine = np.matrix(np.array([                  
      [ width_scale, 0, 0 ],
      [ 0,  height_scale, 0 ],
      [ 0,  0,        1 ] ]))
                                                              
    DAPI_to_bin1_affine = np.matmul(affine.I,DAPI_to_smallDAPI_affine)
    DAPI_to_bin1_affine_base = np.matmul(affine1,DAPI_to_bin1_affine)
    np.savetxt(f"{prefix}.affine.txt",DAPI_to_bin1_affine_base.I)   
    print("The final backward affine matrix :")
    print(DAPI_to_bin1_affine_base.I.tolist())
    print("The final forward affine matrix :")
    print(DAPI_to_bin1_affine_base.tolist())
