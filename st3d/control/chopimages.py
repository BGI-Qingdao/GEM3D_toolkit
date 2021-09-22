from PIL import Image
from st3d.control.save_miscdf import create_a_folder

def chopimages(roi_json,prefix):
    Image.LOAD_TRUNCATED_IMAGES = True
    Image.MAX_IMAGE_PIXELS = None
    create_a_folder(prefix)
    for sinfo in roi_json:
        slice_name = sinfo[0]
        slice_tif = sinfo[1]
        img = Image.open(slice_tif)
        for roi in sinfo[2]:
            item_name = roi[0]
            BX=roi[1]
            BY=roi[2]
            Width=roi[3]
            Height=roi[4]
            cropped = img.crop((BX,BY,BX+Width+1,BY+Height+1))  
            cropped.save("{}/{}-{}.tif".format(prefix,item_name,slice_name))
        print("{} done".format(slice_name),flush=True)

