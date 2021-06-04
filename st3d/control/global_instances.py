"""Datahub for all global variables and easy-access interfaces

"""

from st3d.model.slices_manager import slices_manager
#from st3d.model.slice_dataframe import slice_dataframe
#from st3d.model.slice_xyz import slice_xyz

class gv:
    the_model = slices_manager()

def get_masks3d(binsize=50):
    return gv.the_model.get_masks3d(binsize)

def get_borders3d():
    return gv.the_model.get_borders3d()

def load_slice(gem_file_name:str,move_x=0,move_y=0,rotate=0):
    gv.the_model.add_slice(gem_file_name,move_x,move_y,rotate)

def get_expression_count3d(binsize=50):
    return gv.the_model.get_expression_count3d(binsize)

def get_expression_count2d(slice_id=0,binsize=50):
    return gv.the_model.get_expression_count2d(slice_id,binsize)
