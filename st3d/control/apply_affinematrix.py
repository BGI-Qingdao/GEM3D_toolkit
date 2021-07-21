import time
from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_xyz import slice_xyz
from st3d.view.slice2d import print_affined_scatter_2d


def affine_one( data : [] ):
    bos_dataframe = data[0]
    affine_matrix = data[1]
    binsize = data[2]
    slice_index = data[3]
    prefix = data[4]
    slice_info = data[5]

    init_affine_slice(prefix,slice_index)
    xyz = slice_xyz(slice_info.slice_width,
                    slice_info.slice_height,
                    slice_info.slice_min_x,
                    slice_info.slice_min_y)

    xyz.set_alignment_info(slice_index,affine_matrix)

    spot_coords = bos_dataframe[['bin_x','bin_y']].to_numpy()
    xyz_coords = xyz.model3D_coordinates_from_spots(spot_coords,binsize)
    bos_dataframe['3d_x'] = xyz_coords[:,0]
    bos_dataframe['3d_y'] = xyz_coords[:,1]
    bos_dataframe['3d_z'] = xyz_coords[:,2]

    print_tp_after_affine(bos_dataframe,prefix,slice_index)
    print_affined_scatter_2d(bos_dataframe,prefix,slice_index)

def affine_one_by_one(affines:{},slice_info:{},boss:{},
        prefix:str,binsize:int,tasks:int):
    init_affine_folder(prefix)
    args=[]
    for slice_id in affines.keys():
        args.append([boss[slice_id],
            affines[slice_id],
            binsize,
            slice_id,
            prefix,
            slice_info[slice_id]
            ])
    with Pool(tasks) as p:
        p.map(affine_one, args)

    #print_affine_scatter_3d(bos_dataframe,prefix,slice_index)
    #print_affine_anim_2d(bos_dataframe,prefix,slice_index)
