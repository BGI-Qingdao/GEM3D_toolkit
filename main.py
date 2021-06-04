#!usr/bin/env python3

from st3d.view.model3d import * 
from st3d.view.slice2d import *

from st3d.control.global_instances import *
from st3d.control.load_slices import *

#def main( argv : [] ) :

if __name__ == '__main__':
    load_slices([['../3d_test/DP8400016191TL_E4.83.gem'],
                 ['../3d_test/DP8400016191TL_E4.84.gem',1000,1000,90],
                 ['../3d_test/DP8400016191TL_E4.85.gem',-1000,-1000,180] ]);

    #scatter2D_and_saveas_html(get_expression_count2d(binsize=20), fname="test_heart02.html")
    heat3D_and_saveas_html(get_expression_count3d(binsize=50), get_borders3d(), "test_heart01.html")

