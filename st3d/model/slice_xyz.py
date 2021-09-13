"""Model for manipulate the coordinate of spots in one slice

One slice_xyz object corresponding to one gem file
"""
import numpy as np

class slice_xyz:
    """
    Brief   :
        transform spot x,y in one slice into 3D x,y,z

    Step by Step:
        1. transform spot x,y into graph x,y
        2. transform graph x,y into 3D x,y,z

    Define:
        c1: raw gem coordinate : ( spot_x , spot_y ), step 1, start from chip (0,0)
        c2: spot_index         : step1 spots , start from (0,0)
        c3: bin     coordinate : ( bin_x  , bin_y  ), step binsize, start from (0,0)
        c4: 3D  coordinate     : use registrationed pixel as x,y, use slice_index/4 as z
    """

    ###########################################################################
    # Init and configuare functions 
    ##########################################################################

    def __init__(self, width : int , height : int, min_x: int , min_y : int):
        """Init the rectangle area of the slice"""
        self.spot_width = width
        self.spot_height= height
        self.spot_min_x = min_x
        self.spot_min_y = min_y

    def set_alignment_info(self, z_index :float , affines : np.ndarray):
        self.slice_z_index = z_index
        self.affines = affines

    ###########################################################################
    # coordinate operations
    ##########################################################################

    #c1 ->c2
    def slice_index_from_spot(self, spot_x : int , spot_y : int ) ->( int, int) :
        """
        Get the related slice spot index based on spot coordinate.
        index start from 0
        """
        return spot_x - self.spot_min_x ,spot_y - self.spot_min_y ;

    #c1 ->c2
    def slice_indexs_from_spots(self, spots : np.ndarray ) -> np.ndarray :
        """
        Get the related slice spot indexs based on spot coordinates.
        index start from 0
        """
        return spots - (self.spot_min_x,self.spot_min_y)

    #c1 ->c3
    def bin_coord_from_spot(self, spot_x:int, spot_y:int, binsize:int) -> (int,int):
        """
        @input  : spot_x,y ; binsize ; bin_width of this slice
        @return : bin_x if all bins in rectangle matrix
                  bin_y if all bins in rectangle matrix
        """
        slice_index_x , slice_index_y = self.slice_index_from_spot(spot_x,spot_y)
        bin_x_index = slice_index_x//binsize
        bin_y_index = slice_index_y//binsize
        return bin_x_index ,bin_y_index

    #c1 ->c3
    def bin_coords_from_spots(self, spot_coords: np.ndarray , binsize:int) ->np.ndarray:
        slice_indexs = self.slice_indexs_from_spots(spot_coords)
        return slice_indexs/binsize
        #TODO

    #c1 ->c4
    def model3D_coordinate_from_spot(self, graph_x , graph_y ) -> ( float , float, float ):
        """Get the 3D coordinate based on pixel coordinate and alignment info """
        z_coord = self.slice_z_index * 20
        new_xyz1 = np.matmul(self.affines,np.ndarray([graph_x,graph_y,z_coord,1]))
        return new_xyz1[0:3]

    #c1 ->c4
    def model3D_coordinates_from_spots(self, spots: np.ndarray, reg_binsize:int) -> np.ndarray :
        """Get the 3D coordinate based on pixel coordinate and alignment info """
        spot_indexs=self.slice_indexs_from_spots(spots)
        reg_pixels= spot_indexs/reg_binsize
        z_coords = np.zeros(reg_pixels.shape[0])
        f_ones = np.ones(reg_pixels.shape[0])
        z_coord = self.slice_z_index * 20 # 10 um per size and 500nm per spot
        z_coord = z_coord / reg_binsize
        z_coords = z_coords + z_coord
        in_xyz = np.hstack( ( reg_pixels ,z_coords.reshape(-1,1),f_ones.reshape(-1,1)) )
        #print(self.slice_z_index)
        new_xyz1 =  np.matmul(self.affines.I, in_xyz.T)
        new_xyz = new_xyz1[0:3: ,:]
        new_xyzT = new_xyz.T
        if new_xyzT[0,2] < 0:
            new_xyzT[:,2] = new_xyzT[:,2] * -1 ;
        return new_xyzT


    ###########################################################################
    # overall interfaces
    ##########################################################################

    def get_bin_wh(self, binsize=50) -> (int ,int):
        draw_width = self.spot_width//binsize
        draw_height = self.spot_height//binsize
        if self.spot_width % binsize > 0:
            draw_width = draw_width + 1
        if self.spot_height % binsize > 0:
            draw_height = draw_height + 1
        return draw_width ,draw_height

    def get_bins(self,binsize=50) ->np.ndarray :
        draw_width ,draw_height = self.get_bin_wh(binsize)
        coords=np.zeros((draw_width*draw_height,2))
        for y in range(draw_height):
            for x in range(draw_width):
                index=y*draw_width+x
                bin_mid_x = x*binsize + self.spot_min_x 
                bin_mid_y = y*binsize + self.spot_min_y
                coords[index][0],coords[index][1]= bin_mid_x , bin_mid_y
        return coords

