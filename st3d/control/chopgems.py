from st3d.model.slice_dataframe import slice_dataframe
from st3d.view.slice2d import *
from st3d.control.save_miscdf import *

def chopgems(roi_json,prefix):
    create_a_folder(prefix)
    for sinfo in roi_json:
        slice_id = int(sinfo[0])
        slice_gem  = sinfo[1]
        slice_dataframe()
        sdf = slice_dataframe()
        sdf.init_from_file(slice_gem,slice_id)
        for roi in sinfo[2]:
            item_name = roi[0]
            BX=roi[1]
            BY=roi[2]
            Width=roi[3]
            Height=roi[4]
            cropped = sdf.chop(BX,BY,Width,Height)
            cropped.printGEM("{}/{}-slice{}.gem".format(prefix,item_name,slice_id))
            gec = cropped.get_expression_count_vector(5)
            heatmap2D_png(gec,
                          "{}/{}-slice{}.heatmap.png".format(prefix,item_name,slice_id),
                          gec.shape[1],gec.shape[0] )
        print("slice {} is done".format(slice_id),flush=True)
    print("{} done".format(slice_id),flush=True)

