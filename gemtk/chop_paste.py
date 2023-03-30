import numpy as np
from skimage import io
import getopt
import sys

def chop_paste_usage():
    print("""
Usage : chop_paste.py -i [the img which you input, if you input one, default chop]
                      -m [paste/chop]
                      -f [the chop or paste model, x or y]
                      -n [the number of pieces do you want to chop,default 2]
                      -o <outputfile>

Sample : 
    """,flush=True)

def chop_paste_main(argv:[]):
    imgname=''
    mode=''
    function='x'
    num=2
    prefix=''

    try:
        opts , args =getopt.getopt(argv,"hi:m:f:n:o:",["help=",
                                                       "imgname=",
                                                       "model=",
                                                       "function=",
                                                       "number=",                                              "output="  ])
    except getopt.GetoptError:
        chop_paste_usage()
        sys.exit(2)

    for opt,arg in opts:
        if opt in ("-h","--help"):
            chop_paste_usage()
            sys.exit(0)
        elif opt in ("-i","--imagname"):
            imgname = arg
        elif opt in ("-m","--mode"):
            mode = arg
        elif opt in ("-f","--function"):
            function = arg 
        elif opt in ("-n","--number"):
            num = arg
        elif opt in ("-o","--output"):
            prefix = arg
    if imgname == '' or mode == '' or prefix == '' :
        chop_paste_usage()
        sys.exit(2)
    
    n = int(len(imgname))
    if (n == 1) & (mode == 'chop'):
        img = io.imread(imgname[0])
        if function == 'y':
            img1 = img[0:int(img.shape[0] / num), ]
            io.imsave(f"{prefix}.img1.png", img1)
            for i in range(1,num):
                img2 = img[int(img.shape[0] * i/ num):int(img.shape[0] * (i+1)/ num),]
                io.imsave(f"{prefix}.img{i+1}.png",img2)
        elif function == 'x':
            img1 = img[:, 0:int(img.shape[1] / num)]
            io.imsave(f"{prefix}.img1.png",img1)
            for i in range(1,num):
                img2 = img[:,int(img.shape[1] * i/ num):int(img.shape[1] * (i+1)/ num)]
                io.imsave(f"{prefix}.img{i+1}.png",img2)
    elif (n > 1)  & (mode == 'paste'):
        if function == 'y':
            img = io.imread(imgname[0])
            for i in range(1,n):
                img1 = io.imread(imgname[i])
                img = np.vstack((img,img1))
            io.imsave(f"{prefix}.after_paste.png", img)
        elif function == 'x':
            img = io.imread(imgname[0])
            for i in range(1,n):
                img1 = io.imread(imgname[i])
                img = np.hstack((img,img1))
            io.imsave(f"{prefix}.after_paste.png", img)
    elif (n == 1) & (mode == 'paste'):
        print("please input file quantity more than one")
    elif (n > 1) & (mode == 'chop'):
        print("please input only one file")
    else:
        print("chose the model paste or chop or input the file")
    
