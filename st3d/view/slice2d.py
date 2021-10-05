import matplotlib as mpl
import numpy as np
mpl.use('Agg')
import matplotlib.pyplot as plt

def heatmap2D_png(values,out_f,spot_width,spot_height):
    plt.figure(figsize=(spot_width/20,spot_height/20))
    plt.imshow(values, cmap='gray')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig(out_f,dpi=20)
    plt.close()
    # also draw a colorful one
    plt.figure(figsize=(spot_width/20,spot_height/20))
    plt.imshow(values, cmap='Spectral_r')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig("{}_color.png".format(out_f),dpi=20)
    plt.close()


def print_affined_scatter_2d(bos_dataframe,prefix,slice_index):
    plt.figure(figsize=(6,6))
    plt.scatter(bos_dataframe['3d_x'],bos_dataframe['3d_y'],c=bos_dataframe['masked'])
    plt.savefig("{}/slice_{}/affined.scatter_xy.png".format(prefix,slice_index),dpi=100)
    plt.close()

def draw_slice_cluster(filename,d2d:np.ndarray):
    height , width = d2d.shape
    plt.figure(figsize=(width/20,height/20))
    plt.imshow(d2d, cmap='tab20',vmin=0.9,vmax=20.1)
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig(filename,dpi=20)
    plt.close()


