#!/usr/bin/env python3

import sys
import getopt
import time

############################################################################
# Main gateway: 
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

    secondregistration      second round registration

 actions work on intergrated 3d model:

    model2mesh              generate mesh from (x,y,z) model
    model2slices            generate aligned 2D slices from model

 other tools :
    handlemasks             convert mask matrixs to (x,y) and binary graph
    mask_xy_affine          apply affine matrixs to masks and genrate xyz
    tightbfm                remove pure zero rows and columns.
    chopimages              chop region of interests from whole images.
    chopgems                chop region of interests from GEMs.
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
                                                   "chopgems",
                                                   "secondregistration",
                                                   "model3d") :
        main_usage()
        exit(1)
    elif sys.argv[1] == "gem2bfm" :
        from st3d.control.gem2bfm import gem2bfm_main
        gem2bfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "maskbfm" :
        from st3d.control.maskbfm import maskbfm_main
        maskbfm_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "maskheatmap" :
        from st3d.control.maskheatmap import maskheatmap_main
        maskheatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "heatmap" :
        from st3d.control.gem2heatmap import heatmap_main
        heatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_affinematrix" :
        from st3d.control.apply_affinematrix import affine_main
        affine_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "scatter3d":
        from st3d.control.build_scatter3d import scatter3d_main
        scatter3d_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "model3d":
        from st3d.control.model3d import model3d_main
        model3d_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "segmentbfm" :
        from st3d.control.segmentbfm import segmentbfm_main
        segmentbfm_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "segmentmodel3d" :
        from st3d.control.segmentmodel3d import segmentmodel3d_main
        segmentmodel3d_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "handlemasks" :
        from st3d.control.handlemasks import handlemasks_main
        handlemasks_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "model2mesh":
        from st3d.control.model2mesh import model2mesh_main
        model2mesh_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "mask_xy_affine" :
        from st3d.control.mask_xy_affine import mask_xy_affine_main
        mask_xy_affine_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "model2slices" :
        from st3d.control.model2slices import model2slices_main
        model2slices_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "chopimages" :
        from st3d.control.chopimages import chopimages_main
        chopimages_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "chopgems" :
        from st3d.control.chopgems import chopgems_main
        chopgems_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "secondregistration":
        from st3d.control.secondregistration import secondregistration_main
        secondregistration_main(sys.argv[2:])
        exit(0)
    else:
        main_usage()
        exit(1)
