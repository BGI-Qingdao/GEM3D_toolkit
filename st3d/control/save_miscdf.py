import numpy as np
import pandas as pd

def save_3D_heatmap( data : np.ndarray , filename :str) :
    df = pd.DataFrame(data, columns = ['x','y','z','v'])
    df.to_csv(filename)


def save_new_gem(foldname:str):
    # 
    print("TODO")
