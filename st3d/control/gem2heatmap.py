import time
from multiprocessing import Pool

from st3d.control.save_miscdf import *
from st3d.model.slice_dataframe import slice_dataframe


def heatmap_slice_one(data:[]):
    one_slice = data[0]
    prefix    = data[1]
    binsize   = data[2]

def heatmap_slices_one_by_one(slice_data,prefix,binsize,thread_num) :
    heatmaps = slice_data.get_expression2d()
