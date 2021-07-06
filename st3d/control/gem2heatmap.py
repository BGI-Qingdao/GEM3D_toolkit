import time
from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe
from st3d.view.slice2d import *

def heatmap_slice_one(data:[]):
    one_slice = data[0]
    prefix    = data[1]
    binsize   = data[2]

    slice_index = one_slice.slice_index
    #init_heatmap_slice(prefix,slice_index)

    print("get bins of slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slice_info, bos = one_slice.get_bins_of_slice(binsize=binsize)

    print("get mtx of slice {}...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    heatmap_matrix = one_slice.get_expression_count(binsize)
    print_slices_heatmap_json(slice_info,prefix,slice_index)
    heatmap2D_png(heatmap_matrix,
                  '{}/slice_{}.png'.format(prefix,slice_index),
                  slice_info.slice_width,
                  slice_info.slice_height,
                  binsize)

# multi-processing run all slices
def heatmap_slices_one_by_one(slices,prefix,binsize,tasks) :
    init_heatmap_output(prefix)
    args=[]
    for slice_id in range(0,slices.slices_num):
        one_slice = slices.slices[slice_id]
        args.append([one_slice,prefix,binsize])
    with Pool(tasks) as p:
        print(p.map(heatmap_slice_one, args))

