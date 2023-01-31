import sys
import time
import getopt
from multiprocessing import Pool

from gemtk.control.load_miscdf import *
from gemtk.control.save_miscdf import *

from gemtk.model.slice_xyz import slice_xyz
from gemtk.view.slice2d import print_affined_scatter_2d

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
    print_affine_slices_json(slice_info,prefix,slice_index)

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

############################################################################
# section 3 : apply_affinematrix
#############################################################################
def affine_usage():
    print("""
Usage : GEM_toolkit.py apply_affinematrix -c <affinematix.conf.json> \\
                                          -i <input-folder> \\
                                          -o <output-folder> \\
                                          -b [binsize(default 5)]> \\
                                          -t [threads(default 8)]
Notice:
        1. the input folder must be the output folder of gem2bfm or maskbfm action.
        2. the binsize must be the binsize used in heatmap action.
""")

def affine_main(argv:[]):
    config = ''
    input_folder = ''
    prefix=''
    binsize=5
    threads=8
    try:
        opts, args = getopt.getopt(argv,"hc:i:o:b:t:",["help","iconf=","input=","output=","bin=","threads="])
    except getopt.GetoptError:
        affine_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            affine_usage()
            sys.exit(0)
        elif opt in ("-b", "--bin"):
            binsize = int(arg)
        elif opt in ("-c", "--iconf"):
            config = arg
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)
        elif opt in ("-i", "--input"):
            input_folder = arg
    if config == "" or input_folder == "" or binsize<1 or threads <1:
        affine_usage()
        sys.exit(3)

    print("config file is {}".format(config))
    print("input prefix is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("binsize is {}".format(binsize))
    print("threads is {}".format(threads))

    print('loading datas...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    affines = load_affines(config)
    slice_info , boss = load_tissues_positions_byaffines(affines,input_folder)
    print('apply affine matrix(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    affine_one_by_one(affines,slice_info,boss,prefix,binsize,threads)
    print('apply affine matix, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

