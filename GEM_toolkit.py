#!/usr/bin/env python3

import sys
import getopt
import time

from st3d.control.load_miscdf import *
from st3d.control.gem2bfm import gem2bfm_slices_one_by_one
from st3d.control.gem2heatmap import heatmap_slices_one_by_one
from st3d.control.apply_affinematrix import affine_one_by_one
from st3d.control.model3d import build_model3d
from st3d.control.maskbfm import mask_bfms
from st3d.control.maskheatmap import mask_heatmap
from st3d.control.build_scatter3d import build_scatter3d
from st3d.control.segmentbfm import segmentbfm
from st3d.control.segmentmodel3d import segmentmodel3d
from st3d.control.handlemasks import handlemasks
from st3d.control.model2mesh import model2mesh
from st3d.control.mask_xy_affine import mask_xy_affine
from st3d.control.model2slices import model2slices
from st3d.control.chopimages import chopimages
############################################################################
# section 1 : gem2bfm
#############################################################################

# usage of gem2bfm
def gem2bfm_usage():
    print("""
Usage : GEM_toolkit.py gem2bfm -c <config.json> \\
                               -o <output-folder>  \\
                               -b [bin-size (default 50)] \\
                               -t [threads (default 8)]

Notice : Since one gem file will be handled only in one thread,
         there is no need to set -t greater than slice number.
""")

# main of gem2bfm
def gem2bfm_main(argv):
    config = ''
    prefix = ''
    binsize= 50
    threads=8
    try:
        opts, args = getopt.getopt(argv,"hc:o:b:t:",["help","iconf=","ofile=","bin=","threads="])
    except getopt.GetoptError:
        gem2bfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem2bfm_usage()
            sys.exit(0)
        elif opt in ("-b", "--bin"):
            binsize = int(arg)
        elif opt in ("-c", "--iconf"):
            config = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)
        elif opt in ("-o", "--ofile"):
            prefix = arg

    if config == "" or prefix == "" or binsize<1 or threads <1:
        gem2bfm_usage()
        sys.exit(3)

    print("config file is {}".format(config))
    print("output prefix is {}".format( prefix))
    print("binsize is {}".format(binsize))
    print("threads is {}".format(threads))

    print('start loading slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slice_data = load_slices(config)
    print('handle slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    gem2bfm_slices_one_by_one(slice_data,prefix,binsize,threads)
    print('gem2bfm, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 2 : heatmap
#############################################################################
def heatmap_usage():
    print("""
Usage : GEM_toolkit.py heatmap  -c <conf.json> \\
                                -o <output-folder>  \\
                                -b [binsize (default 5)] \\
                                -t [threads (default 8)]

Notice : Since one gem file will be handled only in one thread,
         ther is no need to set -t greater than slice number.
""")

def heatmap_main(argv:[]):
    config = ''
    prefix = ''
    binsize= 5
    threads=8
    try:
        opts, args = getopt.getopt(argv,"hc:o:b:t:",["help","iconf=","ofile=","bin=","threads="])
    except getopt.GetoptError:
        heatmap_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            heatmap_usage()
            sys.exit(0)
        elif opt in ("-b", "--bin"):
            binsize = int(arg)
        elif opt in ("-c", "--iconf"):
            config = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)
        elif opt in ("-o", "--ofile"):
            prefix = arg
    if config == "" or prefix == "" or binsize<1 or threads <1:
        heatmap_usage()
        sys.exit(3)

    print('start loading slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    slice_data = load_slices(config)
    print('handle slice(s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    heatmap_slices_one_by_one(slice_data,prefix,binsize,threads)
    print('heatmap, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))

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

############################################################################
# section 4 : model3d
#############################################################################

def model3d_usage():
    print("""
Usage : GEM_toolkit.py model3d   -i <input-folder>  \\
                                 -r <cluster.txt> \\
                                 -o <output-folder> \\
                                 -d <downsize>

Notice:
        1. the input folder must be the output folder of apply_affinematrix action.
        2. the columns of cluster.txt should be \"bin_name,slice_id,cluster_id,sct_ncount\"
        3. downsize = bin size of cluster( bfm ) / bin size of heatmap
""")

def model3d_main(argv:[]):
    input_folder = ''
    c_result=''
    prefix=''
    downsize=0
    try:
        opts, args = getopt.getopt(argv,"hi:o:r:d:",["help","input=","output=","cluster_result=","downsize="])
    except getopt.GetoptError:
        model3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            model3d_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-r", "--cluster_result"):
            c_result= arg
        elif opt in ("-d", "--downsize"):
            downsize=int(arg)
    if  input_folder == "" or prefix=="" or c_result =="" or downsize < 1:
        model3d_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("cluster result is {}".format(c_result))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format( downsize))
    print('loading datas...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    cluster_df = load_clusters(c_result)
    bin_xyz, sinfos = load_tissues_positions_bycluster(cluster_df,input_folder)
    print('gen model3d (s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    build_model3d(cluster_df,bin_xyz,sinfos,prefix,downsize)
    print('gen model3d, all done ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 5 : maskbfm
#############################################################################

def maskbfm_usage():
    print("""
Usage : GEM_toolkit.py maskbfm   -i <input-folder>  \\
                                 -o <output-folder> \\
                                 -m <mask.json> \\
                                 -d <downsize> \\
                                 -t <threads>

Notice:
        1. the input folder is output folder of gem2bfm action.
        2. downsize = bin size of cluster / bin size of mask
""")

def maskbfm_main(argv:[]):
    input_folder = ''
    masks=''
    prefix=''
    downsize=0
    threads=4
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:d:t:",["help","input=","output=","mask_cfg=","downsize=","threads="])
    except getopt.GetoptError:
        maskbfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            maskbfm_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-m", "--mask_cfg"):
            masks= arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-d", "--downsize"):
            downsize=int(arg)
        elif opt in ("-t", "--threads"):
            threads= int(arg)

    if  input_folder == "" or prefix=="" or downsize < 1 or masks == "" or threads < 1 :
        maskbfm_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("mask conf.json is {}".format(masks))
    print("downsize is {}".format(downsize))
    print("working threads is {}".format(threads))

    print('loading masks...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    # masks_map
    masks_map  = load_slices(masks)
    print('gen masked bfm (s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mask_bfms(masks_map,input_folder,prefix,downsize,threads)
    print('gen masked bfm (s) all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 6 : maskheatmap
#############################################################################

def maskheatmap_usage():
    print("""
Usage : GEM_toolkit.py maskheatmap  -i <input-folder>  \\
                                    -o <output-folder> \\
                                    -m <mask.json> \\
                                    -t <threads>

Notice:
        1. the input folder is output folder of heatmap action.
""")

def maskheatmap_main(argv:[]):
    input_folder = ''
    masks=''
    prefix=''
    threads=4
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:t:",["help","input=","output=","mask_cfg=","threads="])
    except getopt.GetoptError:
        maskheatmap_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            maskheatmap_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-m", "--mask_cfg"):
            masks= arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-t", "--threads"):
            threads= int(arg)

    if  input_folder == "" or prefix=="" or masks == "" or threads < 1 :
        maskheatmap_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("mask conf.json is {}".format(masks))
    print("working threads is {}".format(threads))

    print('loading masks...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    # masks_map
    masks_map  = load_slices(masks)
    print('gen masked heatmap (s)...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mask_heatmap(masks_map,input_folder,prefix,threads)
    print('gen masked heatmap (s) all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 7 :
#############################################################################

def scatter3d_usage():
    print("""
Usage : GEM_toolkit.py scatter3d    -i <input-folder>  \\
                                    -o <output-folder> \\
                                    -c <conf.json>

Notice:
        1. the input folder is output folder of apply_affinematrix action.
""")

def scatter3d_main(argv:[]):
    input_folder = ''
    prefix=''
    conf=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:c:",["help","input=","output=","conf="])
    except getopt.GetoptError:
        scatter3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            scatter3d_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-c", "--conf"):
            conf = arg

    if  input_folder == "" or prefix=="" or conf == "" :
        scatter3d_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("conf file is {}".format(conf))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slices = load_slices(conf)
    print('build scatter3d...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    build_scatter3d(slices,input_folder,prefix)
    print('build_scatter3d all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 8 : segmentbfm
#############################################################################
# usage
def segmentbfm_usage():
    print("""
Usage : GEM_toolkit.py segmentbfm   -i <bfm-folder>  \\
                                    -a <affine-folder> \\
                                    -c <conf.json> \\
                                    -s <segmentations.csv> \\
                                    -o <output-folder> \\
                                    -t <threads>
""")

def segmentbfm_main(argv:[]) :
    bfm_folder = ''
    affine_folder = ''
    prefix=''
    conf=''
    segconf=''
    threads=0
    try:
        opts, args = getopt.getopt(argv,"hi:a:o:c:s:t:",["help",
                                                         "bfm=",
                                                         "affine=",
                                                         "output=",
                                                         "conf=",
                                                         "tasks=",
                                                         "segs="])
    except getopt.GetoptError:
        segmentbfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            segmentbfm_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-a", "--affine"):
            affine_folder = arg
        elif opt in ("-i", "--bfm"):
            bfm_folder = arg
        elif opt in ("-c", "--conf"):
            conf = arg
        elif opt in ("-s", "--segs"):
            segconf = arg
        elif opt in ("-t", "--tasks"):
            threads = int(arg)

    if  (affine_folder == "" or
        bfm_folder == "" or 
        prefix=="" or
        conf == "" or
        threads < 1 or
        segconf == "" ):

        segmentbfm_usage()
        sys.exit(3)

    print("bfm folder is {}".format( bfm_folder))
    print("affine folder is {}".format( affine_folder))
    print("output prefix is {}".format( prefix))
    print("conf file is {}".format(conf))
    print("threads is {}".format(threads))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    slices = load_slices(conf)
    segs = load_segmentations(segconf)
    print('segment bfm...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    segmentbfm(slices,segs,bfm_folder,affine_folder,prefix,threads)
    print('segment bfm all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 9 : segmentmode3d
#############################################################################
# usage
def segmentmodel3d_usage():
    print("""
Usage : GEM_toolkit.py segmentmodel3d  -i <input-folder>  \\
                                       -s <segmentations.csv> \\
                                       -o <output-folder> \\
                                       -d <downsize>
""")

def segmentmodel3d_main(argv:[]) :
    input_folder = ''
    prefix=''
    segconf=''
    downsize=0
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:d:",["help","input=","output=","segs=","downsize="])
    except getopt.GetoptError:
        segmentmodel3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            segmentmodel3d_usage()
            sys.exit(0)
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-s", "--segs"):
            segconf = arg

    if  input_folder == "" or prefix== "" or segconf == "" or downsize <1 :
        segmentmodel3d_usage()
        sys.exit(3)

    print("input folder is {}".format( input_folder))
    print("output prefix is {}".format( prefix))
    print("segmetation conf is {}".format( segconf))
    print("downsize is {}".format( downsize))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    segs = load_segmentations(segconf)
    print('segment model3d ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    segmentmodel3d(segs,input_folder,prefix,downsize)
    print('segment model3d all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)


############################################################################
# section 10 : handlemasks
#############################################################################
# usage
def handlemasks_usage():
    print("""
Usage : GEM_toolkit.py handlemasks     -i masks.json  \\
                                       -o <output-folder>
""")

def handlemasks_main(argv:[]) :
    prefix=''
    maskconf=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","input=","output="])
    except getopt.GetoptError:
        handlemasks_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            handlemasks_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            maskconf = arg

    if  maskconf == "" or prefix== "" :
        handlemasks_usage()
        sys.exit(3)

    print("mask conf is {}".format(maskconf))
    print("output prefix is {}".format( prefix))
    print('loading confs...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    masks = load_slices(maskconf)
    print('handle masks ...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    handlemasks(masks,prefix)
    print('handle masks all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 11 : model2mesh
#############################################################################
# usage
def model2mesh_usage():
    print("""
Usage : GEM_toolkit.py model2mesh   -i <model3d.csv>  \\
                                    -d <downsize> \\
                                    -o <output-folder> \\
                                    -r [radius (default 35)] \\
                                    -c [cluster_id (default -1 for all)] \\
                                    -s [sample factor(default 0.1)] \\
                                    -v (show mesh by GUI (default not set))
                                    -m (smooth (default not set))

Notice : model3d.csv must contain x,y,z columns
""")

def model2mesh_main(argv:[]) :
    prefix=''
    model3d=''
    downsize=0
    cluster=-1
    radius=35
    sample_fac=0.1
    visual=False
    smooth=False
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:r:c:s:vm",["help","model=","output=","downsize=","radius=","cluster=","sample_fac=","visual","smooth"])
    except getopt.GetoptError:
        model2mesh_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            model2mesh_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--model"):
            model3d = arg
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-r", "--radius"):
            radius = int(arg)
        elif opt in ("-c", "--cluster"):
            cluster = int(arg)
        elif opt in ("-s", "--sample_fac"):
            sample_fac = float(arg)
        elif opt in ("-v", "--visual"):
            visual = True
        elif opt in ("-m", "--smooth"):
            smooth= True

    if  model3d == "" or prefix== "" or downsize < 1 :
        model2mesh_usage()
        sys.exit(3)

    print("model3d is {}".format(model3d))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format(downsize))
    print('get xyz now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    xyz,_,_,_,_=get_xyz(model3d,cluster)
    print('model2mesh now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    model2mesh(xyz,prefix,downsize,radius,visual,sample_fac,smooth)
    print('handle model2mesh all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 12 : mask_xy_affine
#############################################################################
# usage
def mask_xy_affine_usage():
    print("""
Usage : GEM_toolkit.py mask_xy_affine -i <input_folder>  \\
                                      -d <downsize> \\
                                      -o <output-folder> \\
                                      -a <affine.json>
""")

def mask_xy_affine_main(argv:[]):
    prefix=''
    downsize=0
    input_folder=''
    affine_json=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:a:",["help","input=","output=","downsize=","affine="])
    except getopt.GetoptError:
        mask_xy_affine_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            mask_xy_affine_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            input_folder = arg
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-a", "--affine"):
            affine_json= arg

    if  input_folder == "" or prefix== "" or downsize < 1 or affine_json == '':
        mask_xy_affine_usage()
        sys.exit(3)

    print("affine_json is {}".format(affine_json))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format(downsize))
    print('load datas now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    affines=load_affines(affine_json)
    mask_xy_map=load_mask_xy_by_affines(input_folder,affines,downsize)
    print('mask xy affine now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    mask_xy_affine(affines,mask_xy_map,prefix)
    print('mask xy affine done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 13 : model2slices
#############################################################################
# usage
def model2slices_usage():
    print("""
Usage : GEM_toolkit.py model2slices -i <model3d.csv>  \\
                                    -d <downsize> \\
                                    -o <output-folder> \\
                                    -c [cluster_id (default -1 for all)]

Notice : model3d.csv must contain x,y,z columns, need cluster column if -c is not -1.
""")

def model2slices_main(argv:[]) :
    prefix=''
    model3d=''
    downsize=0
    cluster=-1
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:c:",["help","model=","output=","downsize=","cluster="])
    except getopt.GetoptError:
        model2slices_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            model2slices_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--model"):
            model3d = arg
        elif opt in ("-d", "--downsize"):
            downsize = int(arg)
        elif opt in ("-c", "--cluster"):
            cluster = int(arg)

    if  model3d == "" or prefix== "" or downsize < 1 :
        model2slices_usage()
        sys.exit(3)

    print("model3d is {}".format(model3d))
    print("output prefix is {}".format( prefix))
    print("downsize is {}".format(downsize))
    print('get xyz now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    xyz,xmax,xmin,ymax,ymin=get_xyz(model3d,cluster)
    print('model2slices now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    model2slices(xyz,prefix,downsize,xmax,xmin,ymax,ymin)
    print('handle model2slices all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 14 : chopimages
#############################################################################
# usage
def chopimages_usage():
    print("""
Usage : GEM_toolkit.py chopimages   -i <roi.json>  \\
                                    -o <output-folder>
""")

def chopimages_main(argv:[]) :
    prefix=''
    ijson=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","input=","output="])
    except getopt.GetoptError:
        chopimages_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            chopimages_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input"):
            ijson = arg

    if  ijson == "" or prefix== "" :
        chopimages_usage()
        sys.exit(3)

    print("roi.json is {}".format(ijson))
    print("output prefix is {}".format( prefix))
    print('get roi.json now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    roi_json=load_json(ijson)
    print('chopimages now...')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
    chopimages(roi_json,prefix)
    print('chopimage  all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)

############################################################################
# section 15 : 
#############################################################################
# usage
def main_usage():
    print("""
Usage : GEM_toolkit.py action [options ]

Action:

    -----------------------------------------------------------------

 actions work on GEM :

    gem2bfm                 convert GEM into BFM.
    heatmap                 heatmap of expression counts.

 actions work on bin5 coordinate space :

    maskbfm                 mask bins by mask matrixs.
    maskheatmap             mask heatmaps by mask matrixs.
    apply_affinematrix      apply affinematrix to add 3D (x,y,z).
                            coordinates into tissue-position-list.csv.

 actions work on affined slices :

    scatter3d               intergrate affined slices into 3d.
    model3d                 join cluster results with (x,y,z) coord.
                            and visualize by interactive html.

    segmentmodel3d          segment model3d into multiply samples.
    segmentbfm              segment slice(s) into multiply samples.

 actions work on intergrated 3d model:

    model2mesh              generate mesh from (x,y,z) model
    model2slices            generate aligned 2D slices from model

 other tools :
    handlemasks             convert mask matrixs to (x,y) and binary graph
    mask_xy_affine          apply affine matrixs to masks and genrate xyz
    tightbfm                remove pure zero rows and columns.
    chopimages              chop region of interests from whole images.
    -h/--help               show this short usage
    -----------------------------------------------------------------
""")

# logic codes
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ( "-h" , "--help" ):
        main_usage()
        exit(0)
    elif len(sys.argv) < 2 or not sys.argv[1] in ("gem2bfm",
                                                   "maskbfm",
                                                   "heatmap",
                                                   "maskheatmap",
                                                   "apply_affinematrix",
                                                   "scatter3d",
                                                   "segmentbfm",
                                                   "segmentmodel3d",
                                                   "handlemasks",
                                                   "model2mesh",
                                                   "model2slices",
                                                   "mask_xy_affine",
                                                   "chopimages",
                                                   "model3d") :
        main_usage()
        exit(1)
    elif sys.argv[1] == "gem2bfm" :
        gem2bfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "maskbfm" :
        maskbfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "maskheatmap" :
        maskheatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "heatmap" :
        heatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_affinematrix" :
        affine_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "scatter3d":
        scatter3d_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "model3d":
        model3d_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "segmentbfm" :
        segmentbfm_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "segmentmodel3d" :
        segmentmodel3d_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "handlemasks" :
        handlemasks_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "model2mesh":
        model2mesh_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "mask_xy_affine" :
        mask_xy_affine_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "model2slices" :
        model2slices_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "chopimages" :
        chopimages_main(sys.argv[2:])
        exit(0)
    else:
        main_usage()
        exit(1)
