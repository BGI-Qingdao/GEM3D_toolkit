"""Model for manipulate the coordinate of spots in one slice

One slice_xyz object corresponding to one gem file
"""
import numpy as np
from scipy.spatial.transform import Rotation as R

class slice_xyz:
    """
    Brief   :
        transform spot x,y in one slice into 3D x,y,z

    Step by Step:
        1. transform spot x,y into graph x,y
        2. transform graph x,y into 3D x,y,z
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
        self.affines = np.matrix(affines)

    ###########################################################################
    # coordinate operations
    ##########################################################################

    def slice_index_from_spot(self, spot_x : int , spot_y : int ) ->( int, int) :
        """
        Get the related slice spot index based on spot coordinate.
        index start from 0
        """
        return spot_x - self.spot_min_x ,spot_y - self.spot_min_y ;

    def slice_indexs_from_spots(self, spots : np.ndarray ) -> np.ndarray :
        """
        Get the related slice spot indexs based on spot coordinates.
        index start from 0
        """
        return spots - (self.spot_min_x,self.spot_min_y)

    def graph_pixel_from_spot(self, spot_x : int , spot_y : int ) ->( float , float) :
        """Get the pixel coordinate of dyeing graph based on spot coordinate"""
        # TODO :
        # currently use slice spot index to represent the graph pixel coordinate.
        return self.slice_index_from_spot(spot_x,spot_y)

    def graph_pixels_from_spots(self, spots: np.ndarray) -> np.ndarray :
        """Get the pixel coordinates of dyeing graph based on spot coordinates"""
        # TODO :
        # currently use slice spot index to represent the graph pixel coordinate.
        return self.slice_indexs_from_spots(spots)

    def model3D_coordinate_from_graph_pixel(self, graph_x , graph_y ) -> ( float , float, float ):
        """Get the 3D coordinate based on pixel coordinate and alignment info """
        z_coord = self.slice_z_index * 20
        #r = R.from_euler('z',self.slice_rotate, degrees=True)
        #rotate_xyz = r.apply(np.ndarray([graph_x,graph_y,z_coord]))
        #move_xyz = rotate_xyz + (self.slice_x_move, self.slice_y_move, 0)

        new_xyz1 = np.matmul(self.affines,np.ndarray([graph_x,graph_y,z_coord,1]))
        return new_xyz1[0:3]

    def model3D_coordinates_from_graph_pixels(self, spots: np.ndarray) -> np.ndarray :
        """Get the 3D coordinate based on pixel coordinate and alignment info """
        # move center to zero
        #spots -= np.mean(spots, axis=0)
        # prepare 3d coordinates
        spots = spots/5 # turn into bin5
        z_coords = np.zeros(spots.shape[0])
        f_ones = np.ones(spots.shape[0])
        z_coord = self.slice_z_index * 20 
        z_coord = z_coord / 5 ## turn into bin5
        z_coords = z_coords + z_coord
        #in_xyz = np.hstack( ( spots ,z_coords.reshape(-1,1))) 
        #return in_xyz
        in_xyz = np.hstack( ( spots ,z_coords.reshape(-1,1),f_ones.reshape(-1,1)) )
        print(self.slice_z_index)
        new_xyz1 =  np.matmul(self.affines.I, in_xyz.T)
        new_xyz = new_xyz1[0:3: ,:]
        return new_xyz.T

    def model3D_coordinate_from_spot(self, spot_x : int , spot_y : int ) -> ( float , float, float ):
        """Get the 3D coordinate based on spot coordinate"""
        graph_x , graph_y = self.graph_pixel_from_spot(spot_x,spot_y)
        return self.model3D_coordinate_from_graph_pixel(graph_x,graph_y)

    def model3D_coordinates_from_spots(self, spots: np.ndarray) -> np.ndarray :
        graph_coords = self.graph_pixels_from_spots(spots)
        return self.model3D_coordinates_from_graph_pixels(graph_coords)

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

    def model2D_coordinate_of_slice(self,binsize=50) ->np.ndarray :
        """
        Return the 2D spot index coordiante of all spot in this slice
        """
        coords= self.get_bins(binsize)
        return self.graph_pixels_from_spots(coords)

    def model3D_coordinate_of_slice(self,binsize=50) -> np.ndarray :
        """
        Return the 3D coordiante of all spot in this slice
        """
        coords = self.get_bins(binsize)
        return self.model3D_coordinates_from_spots(coords)

    def border3D_coordinate_of_slice(self) -> np.ndarray :
        """
        Return the 3D coordiante of 4 border spot in this slice
        """
        coords=np.zeros((5,2))
        coords[0][0],coords[0][1] = self.spot_min_x,self.spot_min_y
        coords[1][0],coords[1][1] = self.spot_min_x+self.spot_width-1,self.spot_min_y
        coords[2][0],coords[2][1] = self.spot_min_x+self.spot_width-1,self.spot_min_y+self.spot_height-1
        coords[3][0],coords[3][1] = self.spot_min_x,self.spot_min_y+self.spot_height-1
        coords[4][0],coords[4][1] = self.spot_min_x,self.spot_min_y
        return self.model3D_coordinates_from_spots(coords)
