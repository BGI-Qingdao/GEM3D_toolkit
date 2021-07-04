# GEM3D_toolkit

## Overview

"GEM_toolkit" is design to handle stereo-seq gene expression matrix ( GEM ).

It support below feathures:

* convert a single GEM file into 10X format barcode feature matix (BFM)  file.
* convert serveral GEM files into one 10X format BFM file.
    * all raw slices will be horizontal stacked to build one scroll-like slice.

## Dependencies

* pandas
* numpy
* matplotlib
* plotly

## Usage :

### Basic usage

```
Usage : GEM_toolkit.py action [options ]

Action:
        gem2bfm
        apply_affinematrix

```

### gem2bfm usage

```
Usage : GEM_toolkit.py gem2bcm -c <config.json> \
                               -o <output-prefix> \
                               -b [bin-size (default 50)]
```

#### Detail of gem2bcf.conf.json :

##### structure of each item in conf.json

* PF : path to this raw gene expression matrix ( GEM ) files
* ID : index of this GEM

##### structure of conf.json

[ [ PF1, ID1 ] , [PF2, ID2 ] ...,[PFn, IDn] ]

##### example of conf.json

example of 1 slice :

```
[
    ["../all_slices/DP8400016191TL_D1.17.gem", 17]
]
```

example of 3 slices :

```
[
    ["../all_slices/DP8400016191TL_D1.17.gem", 17],
    ["../all_slices/DP8400016191TL_D1.18.gem", 18],
    ["../all_slices/DP8400016191TL_D1.19.gem", 19]
]
```

### apply_affinematrix usage

```
Usage : GEM_toolkit.py apply_affinematrix -c <affinematix.conf.json> \
                                          -i <input-tissue_positions.csv> \
                                          -s <scroll.conf.csv>
                                          -o <output-tissue_positions.csv>

Notice: input-tissue_positions.csv and scroll.conf.csv are output files of gem2bfm command.

```
#### detail of affinematix.conf.json :

##### structure of each item in affinematix.conf.json

* ID : index of this GEM
* AM : affine matrix of this GEM

### structure of affinematix.conf.json

[ [ ID1 ,AM1 ] , [ ID2,AM2 ] ...[ IDn,AMn ] ]

### example of conf.json

```
[
    [17,
     [ [-0.264045081, 0.96451028, 0, 95.43265743],
       [-0.96451028, -0.264045081, 0, 495.4747745],
       [0, 0, 1, 0], 
       [0, 0, 0, 1]
     ]
    ],
    [18,
     [ [-0.365460363, 0.930826742, 0, 130.761296],
       [-0.930826742, -0.365460363, 0, 498.7089905],
       [0, 0, 1, 0],
       [0, 0, 0, 1]
     ]
    ],
]
```

## output of gem2bfm

#### file tree of output folder

```
  example
  ├── raw_feature_bc_matrix
  │   ├── barcodes.tsv.gz
  │   ├── features.tsv.gz
  │   └── matrix.mtx.gz
  ├── spatial
  │   ├── scroll.csv
  │   └── tissue_positions_list.csv
  └── heatmap
     ├── slice_01_heatmap.png
     ├── slice_02_heatmap.png
     ....
     ├── slice_n_heatmap.png
     └── bin_expression.csv
```

* raw_feature_bc_matrix folder contain everything we need to analysis stereo data by scRNA tools
* spatial folder contain coordinate data that used by apply_affinematrix and other ST tools
* heatmap folder contain gene expression heatmap picture for slice registration.

#### header of tissue_positions_list.csv

The first five columns are the same with 10X format, we append the last four columns.

```
bin_name    masked  bin_x   bin_y   png_x   png_y   slice_id    3d_x    3d_y    3d_z
```

* In the result of gem2bfm, the last 3 columns are all -1.
* The apply_affinematrix command will only change the last 3 columns.


