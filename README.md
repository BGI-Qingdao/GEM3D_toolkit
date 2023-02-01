# GEM3D_toolkit

NOTICE: this dev branch is still under developing, you can find previous codes in the main branch.

Specially designed for Stereo-seq platform, GEM_toolkit is a collection of scrips that cooperates with ImageJ/TrakEM2 and CellProfiler to semi-automatic generate single-cell and 3D spatial resolved transtriptomics data from gene expression matrix (GEM) and ssDNA image.

GEM_toolkit also provide severial handly tools for file convert, image or data subset/mask/ROI/affine coordinate/visualize. Enjoy with GEM_toolkit.

Overview of this workflow :

![image](https://user-images.githubusercontent.com/8720584/215430450-8a238a31-4f88-4726-8d22-dd33b51bf8a3.png)

## Dependencies

* pandas
* numpy
* skimage
* scipy
* json

## Quick start

```
./GEM_toolkit.py -h

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
```

## Frequent Q & A

### Why some valid actions not exist in usage?

We rename some action name in this new version and keep the old action name valid for barkwark compatible:

```
prepareregistrationheatmap ==  prepare_registration_heatmap
prepareregistrationssdna == prepare_registration_ssdna
secondregistration == second_registration
gem_to_cfm == gem_to_gemc
```

## Cite us

Please cite our GitHub url: http://github.com/BGI-Qingdao/GEM3D_toolkit directly.

The registration scripts have no update between dev branch and the old main branch, however, if you really need specify the software version, please cite the zendo doi [![DOI](https://zenodo.org/badge/373742809.svg)](https://zenodo.org/badge/latestdoi/373742809) that we special released for the previous stable codes.

## References

The Stereo-seq platform: [Chen, et al., Cell, 2022 Spatiotemporal transcriptomic atlas of mouse organogenesis using DNA nanoball-patterned arrays](https://doi.org/10.1016/j.cell.2022.04.003)

ImageJ/TrakEM2: [Cardona1, et al., PLOS ONE, 2012 TrakEM2 Software for Neural Circuit Reconstruction](https://doi.org/10.1371/journal.pone.0038011)

CellProfiler: [DR, et al., BMC Bioinformatics, 2021 CellProfiler 4: improvements in speed, utility and usability](https://doi.org/10.1186/s12859-021-04344-9)

