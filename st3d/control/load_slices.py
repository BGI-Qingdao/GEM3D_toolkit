"""Interfaces for loading slices"""

from st3d.control.global_instances import load_slice
import numpy as np

def load_slices(files : [] ):
    for one_file in files:
        load_slice(one_file[0],one_file[1],np.array(one_file[2]))

