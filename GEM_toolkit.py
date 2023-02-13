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
    prepare_registration_heatmap  generate 8bit spot-level heatmap with highlighted tracklines.
    prepare_registration_ssdna    generate 8bit close-spot-level ssDNA iamge with highlighted tracklines.
    second_registration           second round registration.
    gem_to_gemc                   convert GEM into GEMC based on cellbin result and registration results.

 Workflow for multiply slices (3D mode) to generate 3D resolved coordinates:
    prepare_alignment_image       generate 8bit spot-level binary/annatation image for 3D alignment.
    apply_alignment               set 3D coordinate for GEM(C)/h5ad/ssDNA/cell.mask.

 Format coverting tools:
    gem_to_h5ad                   convert GEM into h5ad by a certain binsize.
    gemc_to_h5ad                  convert GEMC into h5ad.
 
 Affine tools:
    affine_gem                    modify the 2D coordinate in GEM(C) by user-defined affine matrix.
    affine_h5ad                   modify the 2D coordinate in GEM(C) by user-defined affine matrix.
    affine_ssdna                  affine the ssdna image by user-defined affine matrix.
    affine_txt                    affine txt like cell.mask by user-defined affine matrix.

 Region of interest(ROI) tools: 
    chop_image                    chop region of interests from whole image.
    chop_gem                      chop region of interests from GEM(C).

 Mask tools:
    mask_gem                      mask GEM(C) by mask image.
    mask_h5ad                     mask h5ad data by mask image.
  
 Visualization tools:
    heatmap                       draw heatmap of expression counts in bin1 resolution with/without cellbin and with/without ssDNA.
    draw_annotation               draw annotation result in bin1 resolution with/without cellbin and with/without ssDNA.
 
 Other tools:
    chop_paste                    chop or paste ssDNA image. This tools is useful for ultra-large ssDNA image.
    trakEM2_to_affine             covert trakEM2_matrix to standart affine matrix.

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
                                                   "gemc_to_h5ad",
                                                   "gem_to_h5ad",
                                                   "chop_image",
                                                   "chop_gem",
                                                   "mask_gem",
                                                   "affine_gem",
                                                   "affine_ssdna",
                                                   "affine_txt",
                                                   "affine_h5ad",
                                                   "mask_h5ad",
                                                   "prepare_alignment_image",
                                                   "apply_alignment",
                                                   "trakEM2_to_affine",
                                                   "chop_paste"

                                                   ) :
        main_usage()
        exit(1)
    elif sys.argv[1] in ( "secondregistration" , "second_registration"):
        from gemtk.second_registration import secondregistration_main
        secondregistration_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("prepareregistrationheatmap","prepare_registration_heatmap"):
        from gemtk.prepare_registration_heatmap import prepareregistrationheatmap_main 
        prepareregistrationheatmap_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("prepareregistrationssdna" , "prepareregistrationdapi","prepare_registration_ssdna"):
        from gemtk.prepare_registration_ssdna import prepareregistrationdapi_main 
        prepareregistrationdapi_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] in ("gem_to_cfm", "gem_to_gemc"):
        from gemtk.gem_to_gemc import gem_to_cfm_main
        gem_to_cfm_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "chop_image" :
        from gemtk.chop_image import chopimages_main
        chopimages_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "chop_gem" :
        from gemtk.chop_gem import chopgems_main
        chopgems_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "mask_gem" :
        from gemtk.mask_gem import mask_gem_main 
        mask_gem_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "gem_to_h5ad" :
        from gemtk.gem_to_h5ad import gem_to_h5ad_main 
        gem_to_h5ad_main(sys.argv[2:])
        exit(0)
    elif  sys.argv[1] == "gemc_to_h5ad" :
        from gemtk.gemc_to_h5ad import gemc_to_h5ad_main 
        gemc_to_h5ad_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "affine_ssdna" :
        from gemtk.affine_ssdna import affine_ssdna_main
        affine_ssdna_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "affine_gem" :
        from gemtk.affine_gem import affine_gem_main
        affine_gem_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "affine_txt" :
        from gemtk.affine_txt import affine_txt_main
        affine_txt_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "affine_h5ad" :
        from gemtk.affine_h5ad import affine_h5ad_main
        affine_h5ad_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "mask_h5ad" :
        from gemtk.mask_h5ad import mask_h5ad_main
        mask_h5ad_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "prepare_alignment_image" :
        from gem3dtk.prepare_alignment_image import prepare_alignment_image_main
        prepare_alignment_image_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "apply_alignment" :
        from gem3dtk.apply_alignment import apply_alignment_main
        apply_alignment_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "chop_paste" :
        from gemtk.chop_paste import chop_paste_main
        chop_paste_main(sys.argv[2:])
        exit(0)
    elif sys.argv[1] == "trakEM2_to_affine" :
        from gemtk.trakEM2_to_affine import trakEM2_to_affine_main
        trakEM2_to_affine_main(sys.argv[2:])
        exit(0)
    else:
        main_usage()
        exit(1)
