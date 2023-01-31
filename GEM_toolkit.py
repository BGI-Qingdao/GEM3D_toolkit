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
Usage : GEM_toolkit.py action [options]

Actions:

---------------------------------------------------------------------

 Workflow for single slice to generate single-cell resolved data:
    prepare_registration_heatmap  generate 8bit bin1 heatmap with highlighted tracklines.
    prepare_registration_ssdna    generate 8bit bin1-scaled ssDNA graph with highlighted tracklines.
    second_registration           second round registration.
    gem_to_gemc                   convert GEM into GEMC based on cellbin result and registration results.

 Workflow for multiply slices (3D mode) to generate 3D resolved coordinates:
    prepare_alignment_image       generate 8bit bin1 binary/annatation image for 3D alignment.
    apply_alignment               set 3D coordinate for GEM(C)/h5ad/ssDNA/cell.mask.

 Format coverting tools:
    gem_to_h5ad                   convert GEM into h5ad by a certain binsize.
    gemc_to_h5ad                  convert GEMC into h5ad.
 
 Affine tools:
    affine_gem                    modify the 2D coordinate in GEM(C) by user-defined affine matrix.
    affine_h5ad                   modify the 2D coordinate in GEM(C) by user-defined affine matrix.
    affine_ssdna                  affine the ssdna image by user-defined affine matrix.

 Region of interest(ROI) tools: 
    chopimage                     chop region of interests from whole image.
    chopgem                       chop region of interests from GEM(C).

 Mask tools:
    mask_gem                      mask GEM(C) by mask image.
    mask_ssdna                    mask ssDNA image by mask image.
    mask_h5ad                     mask h5ad data by mask image.
  
 Visualization tools:
    heatmap                       draw heatmap of expression counts with/without cellbin and with/without ssDNA.
 
 Other tools:
    chop_paste                    chop or paste ssDNA image. This tools is useful for ultra-large ssDNA image.
    handle_trakEM2_matrix         covert trakEM2_matrix to standart affine matrix.

    -----------------------------------------------------------------
    -h/--help               show this short usage
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
                                                   "prepareregistrationheatmap",
                                                   "prepareregistrationssdna",
                                                   "prepareregistrationdapi",
                                                   "model3d",
                                                   "gem_to_cfm",
                                                   ) :
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
    elif sys.argv[1] == "prepareregistrationheatmap":
        from st3d.control.prepare_registration_heatmap import prepareregistrationheatmap_main 
        prepareregistrationheatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("prepareregistrationssdna" , "prepareregistrationdapi"):
        from st3d.control.prepare_registration_dapi import prepareregistrationdapi_main 
        prepareregistrationdapi_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "gem_to_cfm":
        from st3d.control.gem_to_cfm import gem_to_cfm_main
        gem_to_cfm_main(sys.argv[2:])
        exit(0)
    else:
        main_usage()
        exit(1)
