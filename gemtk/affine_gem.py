import sys
import getopt
import json
import pandas as pd 
import numpy as np
def affine_gem_usage():
    print("""
Usage : affine_gem.py  -i <input.gem> \\
                            -o <output> \\
                            -B [backward (reverse) affine matrix] 
                            -F [forward affine matrix]
Example:
        affine_gem.py  -i input.gem \\
                            -o output.gem \\
                            -F '[[1,0,10], [0,1,0] [0.0, 0.0, 1.0]]'    
Notice: please provide one of [ -B , -F ], if both present, the later one will overwrite previous one.                             
    """,flush=True) 

def affine_gem_main(argv:[]):
    inputgem=''
    prefix=''
    affine=''
    try:
        opts,args = getopt.getopt(argv,"hi:o:F:B:",["help=",
                                                  "input=",
                                                  "output="])
    except getopt.GetoptError:
        affine_gem_usage()
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ("-i", "--input"):
            inputgem=arg
        elif opt in ("-o", "--output"):
            prefix= arg
        elif opt in ("-F",):
            affine = np.matrix(np.array(json.loads(arg)))
        elif opt in ("-B",):
            affine = np.matrix(np.array(json.loads(arg))).I
        elif opt in ("-h","--help"):
            affine_gem_usage()
            sys.exit(0)
    if inputgem == "" or prefix == "" :
        affine_gem_usage()
        sys.exit(2)
    
    df = pd.read_csv(inputgem, sep='\t', comment='#')
    gemxy=np.array(df[["x",'y']])
    gemxy=np.insert(gemxy,2,values=np.ones((gemxy.shape[0],)),axis=1)
    affine_result=np.dot(affine,gemxy.T)[0:2,:]
    df["new_x"]=np.array(affine_result[0:1,:].T)
    df["new_y"]=np.array(affine_result[1:2,:].T)
    df.to_csv(prefix,index=None,sep='\t')

