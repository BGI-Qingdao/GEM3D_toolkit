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
    elif len(sys.argv) < 2 or not sys.argv[1] in ( "second_registration",
                                                   "secondregistration",
                                                   "prepareregistrationheatmap",
                                                   "prepare_registration_heatmap",
                                                   "prepare_registration_ssdna",
                                                   "prepareregistrationssdna",
                                                   "prepareregistrationdapi",
                                                   "gem_to_cfm",
                                                   "gem_to_gemc",
                                                   ) :
        main_usage()
        exit(1)
    elif sys.argv[1] in ( "secondregistration" , "second_registration"):
        from st3d.control.secondregistration import secondregistration_main
        secondregistration_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("prepareregistrationheatmap" or "prepare_registration_heatmap"):
        from st3d.control.prepare_registration_heatmap import prepareregistrationheatmap_main 
        prepareregistrationheatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("prepareregistrationssdna" , "prepareregistrationdapi","prepare_registration_ssdna"):
        from st3d.control.prepare_registration_dapi import prepareregistrationdapi_main 
        prepareregistrationdapi_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("gem_to_cfm", "gem_to_gemc"):
        from st3d.control.gem_to_cfm import gem_to_cfm_main
        gem_to_cfm_main(sys.argv[2:])
        exit(0)
    else:
        main_usage()
        exit(1)
