from skimage import io as skio
import cv2
import sys
import getopt

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

    img1=cv2.imread(infile)
    img2=cv2.imread(ssdna)
    img=cv2.add(img1,img2)
    if border != '':
        img3=cv2.imread(border)
        img=cv2.add(img,img3)
    skio.imsave(prefix,img)
