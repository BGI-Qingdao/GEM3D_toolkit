import time
from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe
from st3d.model.rect_bin import *
from st3d.view.slice2d import *

def assign_graph_xy(bos : bins_of_slice,binwidth:int):
    ids = np.zeros((bos.bin_num(),2))
    for i in range(0,bos.bin_num()):
        ids[i,0]= i%binwidth
        ids[i,1]= i//binwidth
    bos.assign_graph_xy_matrix(ids)


def heatmap_slice_one(data:[]):
    one_slice = data[0]
    prefix    = data[1]
    binsize   = data[2]

    slice_index = one_slice.slice_index
    init_heatmap_slice(prefix,slice_index)

    print("get bins of slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slice_info, bos = one_slice.get_bins_of_slice(binsize=binsize)
    #print(len(bos.bins))
    print("get mtx of slice {}...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    heatmap_matrix = one_slice.get_expression_count(binsize)
    print_slices_heatmap_json(slice_info,prefix,slice_index)
    assign_graph_xy(bos,slice_info.binwidth)
    print_heatmap_tissue_positions_list(bos,prefix,slice_index)
    np.savetxt('{}/slice_{}/heatmatrix.txt'.format(prefix,slice_index)
             , heatmap_matrix, fmt='%d')
    heatmap2D_png(heatmap_matrix,
                  '{}/slice_{}/heatmap.png'.format(prefix,slice_index),
                  slice_info.binwidth,
                  slice_info.binheight)

# multi-processing run all slices
def heatmap_slices_one_by_one(slices,prefix,binsize,tasks) :
    init_heatmap_output(prefix)
    args=[]
    for slice_id in range(0,slices.slices_num):
        one_slice = slices.slices[slice_id]
        args.append([one_slice,prefix,binsize])
    with Pool(tasks) as p:
        print(p.map(heatmap_slice_one, args))

