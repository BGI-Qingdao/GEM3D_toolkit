import numpy as np
import pandas as pd

def xyv_to_volumn2D( df : pd.DataFrame, xmin, xmax, ymin,ymax,downsize):
    df.columns = ['x','y','v']
    df['x'] = df['x'] - xmin
    df['y'] = df['y'] - ymin
    if downsize >=2 :
        df_s = df.copy()
        df_s['x'] = df_s['x'] + int(downsize//2)
        df_s['y'] = df_s['y'] + int(downsize//2)
        df_s['x'] = (df_s['x'] / downsize).astype(int)
        df_s['y'] = (df_s['y'] / downsize).astype(int)

    df['x'] = (df['x'] / downsize).astype(int)
    df['y'] = (df['y'] / downsize).astype(int)

    df['v'] = (df['v'] +1).astype(int)
    draw_height = int(( ymax+downsize-1 - ymin )//downsize +1)
    draw_width  = int(( xmax+downsize-1 - xmin )//downsize +1)

    coords=np.zeros((draw_height,draw_width))
    coords[df['y'], df['x']] = df['v']
    if downsize >=2 :
        coords[df_s['y'], df_s['x']] = df_s['v']

    return coords

