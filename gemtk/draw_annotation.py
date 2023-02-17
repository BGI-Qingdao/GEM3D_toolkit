from skimage import io as skio
import sys
import getopt
from PIL import ImageFile
from PIL import Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

def draw_annotation_usage():
    print("""
Usage : draw_annotation.py -i <input.tif>
                            -s <ssdna.tif>
                            -b <border.tif>
                            -o <output.tif>
""",flush=True)

def draw_annotation_main(argv:[]):
    infile = ''
    ssdna = ''
    border = ''
    prefix = ''
    try:
        opts , args =getopt.getopt(argv,"hi:s:b:o:",["help=","input=","ssdna=","border=","output="])
    except getopt.GetoptError:
        draw_annotation_usage()
        sys.exit(2)

    for opt,arg in opts:
        if opt in ("-h","--help"):
            draw_annotation_usage()
            sys.exit(0)
        elif opt in ("-i","--input"):
            infile = arg
        elif opt in ("-s","--ssdna"):
            ssdna = arg
        elif opt in ("-b","--border"):
            border = arg
        elif opt in ("-o","--output"):
            prefix = arg
    

    if infile == '' or ssdna == '' or prefix == '':
        draw_annotation_usage()
        sys.exit(2)

    img1=Image.open(infile).convert('RGB')
    img2=Image.open(ssdna).convert('RGB')
    img=Image.blend(img1,img2,0.3)
    if border != '':
        img3=Image.open(border).convert('RGB')
        img=Image.blend(img,img3,0.5)
    img.save(prefix)
