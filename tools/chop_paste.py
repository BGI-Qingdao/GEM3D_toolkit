#!/usr/bin/env python3
import numpy as np
from skimage import io
import numpy
import argparse


def main(args):
    n = int(len(args.imgname))
    num = args.number
    if (n == 1) & (args.mode == 'chop'):
        img = io.imread(args.imgname[0])
        if args.function == 'y':
            img1 = img[0:int(img.shape[0] / num), ]
            io.imsave(f"{args.output}.img1.tif", img1)
            for i in range(1,num):
                img2 = img[int(img.shape[0] * i/ num):int(img.shape[0] * (i+1)/ num),]
                io.imsave(f"{args.output}.img{i+1}.tif",img2)
        elif args.function == 'x':
            img1 = img[:, 0:int(img.shape[1] / num)]
            io.imsave(f"{args.output}.img1.tif",img1)
            for i in range(1,num):
                img2 = img[:,int(img.shape[1] * i/ num):int(img.shape[1] * (i+1)/ num)]
                io.imsave(f"{args.output}.img{i+1}.tif",img2)
    elif (n > 1)  & (args.mode == 'paste'):
        if args.function == 'y':
            img = io.imread(args.imgname[0])
            for i in range(1,n):
                img1 = io.imread(args.imgname[i])
                img = np.vstack((img,img1))
            io.imsave(f"{args.output}.after_paste.tif", img)
        elif args.function == 'x':
            img = io.imread(args.imgname[0])
            for i in range(1,n):
                img1 = io.imread(args.imgname[i])
                img = np.hstack((img,img1))
            io.imsave(f"{args.output}.after_paste.tif", img)
    elif (n == 1) & (args.mode == 'paste'):
        print("please input file quantity more than one")
    elif (n > 1) & (args.mode == 'chop'):
        print("please input only one file")
    else:
        print("chose the model paste or chop or input the file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="either 'paste' or 'chop' ", type=str, default="chop")
    parser.add_argument("-i","--imgname", help="the img which you input, if you input one, default chop",type=str, default=[], nargs='+')
    parser.add_argument("-f", "--function", help="the chop or paste model, x or y", type=str, default="x")
    parser.add_argument("-n", "--number", help="the number of pieces do you want to chop,default 2", type=int, default=2)
    parser.add_argument("-o", "--output", help="directory to save files", type=str,default='output')
    args = parser.parse_args()
    main(args)
