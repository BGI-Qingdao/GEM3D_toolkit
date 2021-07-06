import time
from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe

def handle_one_slice(data:[]):
    one_slice   = data[0]
    prefix      = data[1]
    binsize     = data[2]

    slice_index = one_slice.slice_index
    init_gem2bfm_slice(prefix,slice_index)

    print("build gene maps for slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    gene_maps = one_slice.get_gene_ids()

    print("get bins of slice {} ...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slices_info, bos = one_slice.get_bins_of_slice(binsize=binsize)

    print("get mtx of slice {}...".format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mtx, valid_bin_num = one_slice.get_mtx(gene_maps,bos)

    print('save slice {} data ...'.format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print_features_tsv(gene_maps.keys(),prefix,slice_index)
    print_barcodes_tsv(bos ,prefix,slice_index)
    print_tissue_positions_list(bos,prefix,slice_index)
    print_gem2bfm_slices_json(slices_info,prefix,slice_index)
    print_matrix_mtx(mtx,prefix,slice_index,len(gene_maps),valid_bin_num)

# multi-processing run all slices
def handle_slice_one_by_one(slices,prefix,binsize=50,tasks=8):
    init_gem2bfm_output(prefix)
    args=[]
    for slice_id in range(0,slices.slices_num):
        one_slice = slices.slices[slice_id]
        args.append([one_slice,prefix,binsize])
    with Pool(tasks) as p:
        print(p.map(handle_one_slice, args))

