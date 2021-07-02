import os
import numpy as np
import pandas as pd

def init_outputs(prefix : str):
    if os.path.exists(prefix):
        print("output path {} exist ! exit ...".format(prefix))
        exit(101)
    os.mkdir(prefix)
    if not os.path.exists(prefix):
        print("create output path {}  failed! exit ...".format(prefix))
        exit(102)
    os.mkdir(os.path.join(prefix,"raw_feature_bc_matrix"))
    os.mkdir(os.path.join(prefix,"spatial"))
    os.mkdir(os.path.join(prefix,"heatmap"))

def save_3D_heatmap( data : np.ndarray , filename :str) :
    df = pd.DataFrame(data, columns = ['x','y','z','v'])
    df.to_csv(filename)


def save_new_gem(foldname:str):
    # 
    print("TODO")
