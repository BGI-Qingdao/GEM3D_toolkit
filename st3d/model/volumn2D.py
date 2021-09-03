import numpy as np
import pandas as pd

def xyv_to_volumn2D( df : pd.DataFrame, xmin, xmax, ymin,ymax,downsize):
    df.column = ['x','y','v']
    df['x'] = df['x'] - xmin
    df['y'] = df['y'] - ymin
    df['x'] = (df['x'] / downsize).astype(int)
    df['y'] = (df['y'] / downsize).astype(int)

    draw_height = ( ymax - ymin )//downsize +1
    draw_width  = ( xmax - xmin )//downsize +1

    coords=np.zeros((draw_height,draw_width))
    coords[df['y'], df['x']] = df['v']
    return coords

