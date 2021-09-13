import matplotlib as mpl
import numpy as np
mpl.use('Agg')
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def heatmap2D_png(values,out_f,spot_width,spot_height):
    plt.figure(figsize=(spot_width/10,spot_height/10))
    plt.imshow(values, cmap='gray')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig(out_f,dpi=10)
    plt.close()


def print_affined_scatter_2d(bos_dataframe,prefix,slice_index):
    plt.figure(figsize=(6,6))
    plt.scatter(bos_dataframe['3d_x'],bos_dataframe['3d_y'],c=bos_dataframe['masked'])
    plt.savefig("{}/slice_{}/affined.scatter_xy.png".format(prefix,slice_index),dpi=100)
    plt.close()

def draw_slice_cluster(filename,d2d:np.ndarray):
    height , width = d2d.shape
    plt.figure(figsize=(width/10,height/10))
    plt.imshow(d2d, interpolation='nearest', cmap='gray',vmin=1,vmax=2)
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig(filename,dpi=10)
    plt.close()


def anim2D_and_saveas_html( df , fname : str ):
    xmin = df['x'].min() // 100 * 100
    xmax = df['x'].max() // 100 * 100 + 100
    ymin = df['y'].min() // 100 * 100
    ymax = df['y'].max() // 100 * 100 + 100
    fig = px.scatter(df,x='x',y='y',animation_frame='z',range_x=(xmin,xmax),range_y=(ymin,ymax))
    fig.write_html(fname)


