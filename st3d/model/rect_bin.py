import numpy as np

class rect_bin:
    def __init__(self,bin_id:int , slice_id : int, spot_x: int ,spot_y:int):
        self.bin_name = "s{}b{}".format(slice_id,bin_id)
        self.bin_id   = bin_id
        self.slice_id = slice_id
        self.spot_x   = spot_x
        self.spot_y   = spot_y
        self.valid    = False
        #return self

    def set_valid(self):
        self.valid    = True

    def assign_graph_xy(self,graph_x,graph_y):
        self.graph_x  = graph_x
        self.graph_y  = graph_y

    def assign_3d_xyz(self,x,y,z):
        self.d3_x     = x
        self.d3_y     = y
        self.d3_z     = z

class bins_of_slice:
    def __init__(self,slice_id:int, bin_id_min:int):
        self.bins     = []
        self.slice_id = slice_id
        self.min_binid= bin_id_min
        #return self

    def init_bins(self,bin_coords: np.ndarray):
        for x in range(len(bin_coords)):
            one_bin = rect_bin(self.min_binid+x, self.slice_id, bin_coords[x][0], bin_coords[x][1])
            self.bins.append(one_bin)

    def assign_graph_xy_matrix(self,data:np.ndarray):
        for x in range(len(self.bins)):
            one_bin=self.bins[x]
            one_bin.assign_graph_xy(data[x][0],data[x][1])

    def get_bin(self,bin_index) ->rect_bin:
        return self.bins[bin_index]

    def bin_num(self):
        return len(self.bins)

    def valid_bin_num(self):
        ret=0
        for abin in self.bins:
            if abin.valid :
                ret =ret+1
        return ret

    def set_valid(self,index):
        self.bins[index].set_valid()
    #def get_valids(self) -> bins_of_slice :
    #    bos=bins_of_slice(self.slice_id ,self.min_binid)
    #    for abin in self.bins:
    #        if abin.valid :
    #            bos.bins.append(abin)
    #    return bos

class bins_of_slices:
    def __init__(self):
        self.slices={}
        self.bin_num=0
        #return self

    def add_slice(self,slice_id : int , bos : bins_of_slice):
        self.slices[slice_id] = bos
        self.bin_num += len(bos.bins)

    def get_slice(self,slice_id:int) -> bins_of_slice:
        return self.slices[slice_id]
