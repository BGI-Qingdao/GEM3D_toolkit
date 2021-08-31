import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def heatmap2D_png(values,out_f,spot_width,spot_height):
    plt.figure(figsize=(spot_width/10,spot_height/10))
    plt.imshow(values, cmap='gray')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig(out_f,dpi=10)


def print_affined_scatter_2d(bos_dataframe,prefix,slice_index):
    plt.figure(figsize=(6,6))
    plt.scatter(bos_dataframe['3d_x'],bos_dataframe['3d_y'],c=bos_dataframe['masked'])
    plt.savefig("{}/slice_{}/affined.scatter_xy.png".format(prefix,slice_index),dpi=100)

