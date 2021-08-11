import time
from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe

def gem2bfm_one_slice(data:[]):
    gem_file_name  = data[0]
    z_index     = data[1]
    #one_slice   = data[0]
    prefix      = data[2]
    binsize     = data[3]

    one_slice = slice_dataframe(gem_file_name,z_index)
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
    mtx = one_slice.get_mtx(gene_maps,bos)

    print('save slice {} data ...'.format(slice_index))
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    print_features_tsv(gene_maps.keys(),prefix,slice_index)
    print_barcodes_tsv(bos ,prefix,slice_index)
    print_tissue_positions_list(bos,prefix,slice_index)
    print_gem2bfm_slices_json(slices_info,prefix,slice_index)
    print_matrix_mtx(mtx,prefix,slice_index,len(gene_maps),bos.bin_num())

# multi-processing run all slices
def gem2bfm_slices_one_by_one(slices,prefix,binsize=50,tasks=8):
    init_gem2bfm_output(prefix)
    args=[]
    #for slice_id in range(0,slices.slices_num):
    for slice_name in slices:
        z_index = slices[slice_name]
        #one_slice = slices.slices[slice_id]
        args.append([slice_name,z_index,prefix,binsize])
    with Pool(tasks) as p:
        p.map(gem2bfm_one_slice, args)

