# GEM3D_toolkit

## Overview

This toolkit "GEM3D_toolkit" is design to integrate several 2D slices into one scroll-like 2D slice.

The main targets are :

* align 2D slices into uniform 3D space ( the real 3D space of the raw organ )
* let the y axes in scroll-like 2D slice represent both y axes and z axes of 3D space by ```y_scroll=z_3D*max_y_3D_length + y_3D``` 

## Usage :

```
Usage : GEM3D_toolkit.py -c <config-file> -o <output-prefix> -b [bin-size (default 50)]
```

## Detail of conf.json:

### structure of each item in conf.json

* PF : path to this raw gene expression matrix ( GEM ) files
* ID : index of this GEM
* AM :affine matrix of this GEM

### structure of conf.json

[ [ PF1, ID1 ,AM1 ] , [PF2, ID2,AM2] ...[PFn, IDn,AMn] ]

### example of conf.json

```
[
    ["../all_slices/DP8400016191TL_D1.17.gem",
     17,
     [ [-0.264045081, 0.96451028, 0, 95.43265743],
       [-0.96451028, -0.264045081, 0, 495.4747745],
       [0, 0, 1, 0], 
       [0, 0, 0, 1]
     ]
    ],
    ["../all_slices/DP8400016191TL_D1.18.gem", 
     18,
     [ [-0.365460363, 0.930826742, 0, 130.761296],
       [-0.930826742, -0.365460363, 0, 498.7089905],
       [0, 0, 1, 0],
       [0, 0, 0, 1]
     ]
    ],
]
```

### Detail of output


