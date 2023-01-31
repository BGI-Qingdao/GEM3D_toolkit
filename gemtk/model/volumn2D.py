import numpy as np
import pandas as pd

def xyv_to_volumn2D( df : pd.DataFrame, xmin, xmax, ymin,ymax,downsize):
    df.columns = ['x','y','v']
    df['x'] = df['x'] - xmin
    df['y'] = df['y'] - ymin
    df['v'] = (df['v'] +1).astype(int)
    draw_height = int(( ymax+downsize-1 - ymin )//downsize +1)
    draw_width  = int(( xmax+downsize-1 - xmin )//downsize +1)
    coords=np.zeros((draw_height,draw_width))
    for i in range(0,downsize):
        for j in range(0,downsize):
            df_s = df.copy()
            df_s['x'] = df_s['x'] + i
            df_s['y'] = df_s['y'] + j
            df_s['x'] = (df_s['x'] / downsize).astype(int)
            df_s['y'] = (df_s['y'] / downsize).astype(int)
            coords[df_s['y'], df_s['x']] = df_s['v']

    return coords

