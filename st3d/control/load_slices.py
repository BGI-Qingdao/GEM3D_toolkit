"""Interfaces for loading slices"""

from st3d.model.slices_manager import slices_manager
import numpy as np
import json

def load_slices(config :str ):
    files=json.load(open(config))
    slices = slices_manager()
    for one_file in files:
        slices.add_slice(one_file[0],one_file[1])
    return slices



