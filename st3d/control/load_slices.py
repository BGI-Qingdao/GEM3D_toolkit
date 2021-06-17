"""Interfaces for loading slices"""

from st3d.control.global_instances import load_slice

def load_slices(files : [] ):
    for one_file in files:
        load_slice(one_file[0],one_file[1],one_file[2])

