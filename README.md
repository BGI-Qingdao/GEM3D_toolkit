# GEM3D_toolkit

## Overview

"GEM_toolkit" is design to handle stereo-seq gene expression matrix ( GEM ).

It support below feathures:

* convert a single GEM file into 10X format barcode feature matix (BFM)  file.
* generate expression counts heatmap from GEM file
* apply affine matrix to add 3d (x,y,z0 into tissue-position-list.csv
* visualize 3D expression count scatter 
* visualize 3D cluster results

## Dependencies

* pandas
* numpy
* matplotlib
* plotly

## example

```
cd example

# test gem2bfm
python3 ../GEM_toolkit.py  gem2bfm  -c test_gem2bfm.json -o test_g

# test heatmap
python3 ../GEM_toolkit.py  heatmap  -c test_gem2bfm.json -o test_h

# test apply_affinematrix
python3 ../GEM_toolkit.py  apply_affinematrix  -c test_affine.json -i example_bfm_5658 -o test_a
# test model3d
python3 ../GEM_toolkit.py model3d -i test_a -r cluster_56_58.txt -o test_m

```

## Usage :

### Basic usage

```

Usage : GEM_toolkit.py action [options ]

Action:

    -----------------------------------------------------------------

    gem2bfm                 convert GEM into BFM.
    heatmap                 heatmap of expression counts.
    apply_affinematrix      apply affinematrix to add 3D (x,y,z)
                            coordinates into tissue-position-list.csv
    model3d                 join cluster results with (x,y,z) coord
                            and visualize by interactive html.
    -----------------------------------------------------------------

    -h/--help               show this short usage
    -----------------------------------------------------------------

```

### gem2bfm usage

```

Usage : GEM_toolkit.py gem2bcm -c <config.json> \
                               -o <output-folder>  \
                               -b [bin-size (default 50)] \
                               -t [threads (default 8)]

Notice : Since one gem file will be handled only in one thread,
         there is no need to set -t greater than slice number.
```

#### Detail of gem2bfm.conf.json :

##### structure of each item in gem2bfm.conf.json

* PF : path to this raw gene expression matrix ( GEM ) files
* ID : index of this GEM

##### structure of gem2bfm.conf.json

[ [ PF1, ID1 ] , [PF2, ID2 ] ...,[PFn, IDn] ]

##### example of gem2bfm.conf.json

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

### heatmap usage

* heatmap generate gene expression heatmap picture for slice registration.

```

Usage : GEM_toolkit.py heatmap  -c <conf.json> \
                                -o <output-folder>  \
                                -b [binsize (default 5)] \
                                -t [threads (default 8)]

Notice : Since one gem file will be handled only in one thread,
         ther is no need to set -t greater than slice number.

```

The config file follow the same format of gem2bfm

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

### example of affinematix.conf.json

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

### model3d usage

```
Usage : GEM_toolkit.py model3d   -i <input-folder>  \
                                 -r <cluster.txt> \
                                 -o <output-folder>
Notice:
        1. the input folder must be the output folder of apply_affinematrix action.
        2. the columns of cluster.txt should be "bin_name,slice_id,cluster_id,sct_ncount"

```

## outputs

### file tree of gem2bfm's output folder

```
test_g
└── slice_88
    ├── raw_feature_bc_matrix
    │   ├── barcodes.tsv.gz
    │   ├── features.tsv.gz
    │   └── matrix.mtx.gz
    ├── slices.json
    └── spatial
        └── tissue_positions_list.csv

    ... other slices if have...
```

* raw_feature_bc_matrix folder contain everything we need to analysis stereo data by scRNA tools
* spatial folder contain coordinate data that used by apply_affinematrix and other ST tools

### file tree of heatmap's output folder

```
test_h
└── slice_88
    ├── heatmap.png
    ├── slice.json
    └── tissue_positions_list.csv

    ... other slices if have...
```

### file tree of apply_affinematrox output folder

```
test_a/
├── slice_56
│   ├── affined.scatter_xy.png
│   └── tissue_positions_list.csv
└── slice_58
    ├── affined.scatter_xy.png
    └── tissue_positions_list.csv
```

### file tree of model3d output folder

```
test_m/
├── model3d.csv
└── model3d.html
```

## header of tissue_positions_list.csv

The first five columns are the same with 10X format, we append the last four columns.

```
bin_name    masked  bin_x   bin_y   png_x   png_y   slice_id    3d_x    3d_y    3d_z
```

* In the result of gem2bfm, the last 3 columns, png_x and png_y are all -1 . 
* In the result of heatmap, only the last 3 columns are -1, png_x and png_y represent the pixel in heatmap.
* The apply_affinematrix command will only change the last 3 columns.

### head of  model3d.csv

```
bin_name,slice,x,y,z,cluster,sct_ncount
bin-17,56,107.67536063307665,315.74575386450175,224.0,32,32
bin-18,56,106.86436452193108,305.7786934730285,224.0,5,5
bin-19,56,106.05336841078548,295.81163308155527,224.0,26,26
bin-20,56,105.24237229963987,285.84457269008203,224.0,7,7
bin-21,56,104.43137618849428,275.8775122986088,224.0,2,2
bin-22,56,103.62038007734868,265.91045190713555,224.0,2,2
bin-23,56,102.80938396620309,255.9433915156623,224.0,2,2
bin-24,56,101.99838785505749,245.9763311241891,224.0,2,2
bin-25,56,101.18739174391187,236.0092707327158,224.0,2,2

```
