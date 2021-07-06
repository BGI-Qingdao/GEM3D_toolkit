import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def heatmap2D_png(values,out_f,spot_width,spot_height,binsize):
    plt.figure(figsize=(spot_width/(binsize*100),spot_height/(binsize*100)))
    plt.imshow(values, cmap='hot')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig(out_f,dpi=100)

