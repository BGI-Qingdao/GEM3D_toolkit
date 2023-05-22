#!/usr/bin/env python3
import os
import sys
import time
import json
import getopt
import numpy as np
import pandas as pd
import scipy.ndimage as nd
from skimage import io as skio
from skimage import img_as_ubyte

def apply_registration_usage():
    print("""
Usage : GEM_toolkit.py apply_registration \\
             -o <output prefix>
             -s <ssdna tif/png file> \\
             -r [roi with affine file]\\
             -a [matrix file output from handle_trackEM_matrix]\\
             -A [affine matrix string]
             -g [gem file]  \\
             -b [cell segment outline file] \\
             -m [cell segment mask file]\\
             -x [xshift of gem to heatmap, default xmin] \\
             -y [yshift of gem to heatmap, default ymin] \\
             -W [width of heatmap] \\
             -H [height of heatmap] \\
             -h [show this usage]

Notice:
 1. one and only one of -r -a -A should be provided!
 2. -g is necessary only when -r is provided.
 3. -W and -H is necessary if -r is not provided.
""",flush=True)

def apply_registration_main(argv:[]):
    prefix = ''
    ssdna = ''

    roi_affines = ''
    affine = ''
    Affine = ''

    mask = ''
    border = ''
    gem = ''
    xmin=None
    ymin=None
    affine_count = 0
    W=None
    H=None
    if len(argv) < 1:
        apply_registration_usage()
        sys.exit(0)
    try:
        opts, args = getopt.getopt(argv,"ho:s:r:a:A:g:b:m:x:y:W:H:",["help"])
    except getopt.GetoptError:
        appl_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            apply_registration_usage()
            sys.exit(0)
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("-s"):
            ssdna = arg
        elif opt in ("-r"):
            roi_affines = arg
            affine_count = affine_count + 1
            # load roi and affined matrics
            roi_affines_data = json.load(open(roi_affines))
        elif opt in ("-a"):
            affine = arg
            affine_count = affine_count + 1
            affineR = np.loadtxt(affine)
        elif opt in ("-A"):
            Affine = arg
            affine_count = affine_count + 1
            affineR = np.matrix(np.array(json.loads(arg)))
        elif opt in ("-g"):
            gem = arg
        elif opt in ("-b"):
            border = arg
        elif opt in ("-m"):
            mask = arg
        elif opt in ("-x"):
            xmin = int(arg)
        elif opt in ("-y"):
            ymin = int(arg)
        elif opt in ("-H"):
            W = int(arg)
        elif opt in ("-W"):
            H= int(arg)

    if prefix == '' :
        print('Error: no -o exit ...')
        sys.exit(2)
    if affine_count != 1 :
        print('Error: one and only one of -r -a -A should be provided! exit ...')
        sys.exit(1)
    if ssdna == '' and mask == '' and border == '':
        print('Error: no -s,-m and -b. exit ...')
        sys.exit(2)
    if roi_affines != '' and gem == '':
        print('Error: no -g with -r. exit ...')
        sys.exit(3)
    if roi_affines == '' and ( W is None or H is None) :
        print('Error: no -H or -H in no -r mode. exit ...')
        sys.exit(4)

    if gem != '':
        # load gems
        gem_data = pd.read_csv(gem, sep='\t', header=0, compression='infer', comment='#')
        print(f'gem file is {gem}')
        if len(gem_data.columns) == 4 :
            gem_data.columns = ['geneID','x','y','MIDCounts']
        elif len(gem_data.columns) == 5 :
            gem_data.columns = ['geneID','x','y','MIDCounts','ExonCount']
        if xmin is None:
            gem_data_x_min = gem_data['x'].min()
        else:
            gem_data_x_min = xmin
        if ymin is None:
            gem_data_y_min = gem_data['y'].min()
        else:
            gem_data_y_min = ymin
        gem_data['x'] = gem_data['x'] - gem_data_x_min
        gem_data['y'] = gem_data['y'] - gem_data_y_min
        gem_data['x'] = gem_data['x'].astype(int)
        gem_data['y'] = gem_data['y'].astype(int)
    else:
        gem_data = None

    if ssdna != None:
        print(f'ssdna file is {ssdna}')
        dapi_data = skio.imread(ssdna)
        dapi_data = img_as_ubyte(dapi_data)
        if len(dapi_data.shape) == 3:  # RGB to 8 bit gray 
            if dapi_data.shape[2] == 3:
                new_data = np.zeros((dapi_data.shape[0], dapi_data.shape[1]), dtype=int)
                new_data = new_data + dapi_data[:, :, 0]
                new_data = new_data + dapi_data[:, :, 1]
                new_data = new_data + dapi_data[:, :, 2]
                new_data = new_data/3
                dapi_data = new_data
                dapi_data = dapi_data.astype('uint8')
            elif dapi_data.shape[2] == 2:
                new_data = np.zeros((dapi_data.shape[0], dapi_data.shape[1]), dtype=int)
                new_data = new_data + dapi_data[:, :, 0]
                new_data = new_data + dapi_data[:, :, 1]
                new_data = new_data/2
                dapi_data = new_data
                dapi_data = dapi_data.astype('uint8')
        dapi_data = dapi_data.astype('uint8')
    else:
        dapi_data = None

    if mask != '':
        print(f'mask file is {mask}')
        masks = np.loadtxt(mask,dtype=int,delimiter=' ')
    else:
        masks = None

    if border != '':
        borders =  np.loadtxt(border,dtype='uint8',delimiter=' ')
        print(f'border file is {border}')
    else:
        borders = None

    if roi_affines != '':
        print(f'roi file is {roi_affines}')
        print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
        os.mkdir(prefix)
        # get items one by one
        for item in roi_affines_data:
            # get info
            item_name = item[0]
            xh,yh,wh,hh = item[1]
            xd,yd,wd,hd = item[2]
            affineR = np.matrix(np.array(item[3]))
            # chop images 
            # save roi
            roi_list = pd.DataFrame(columns=['x', 'y', 'width', 'height'])
            roi_list.loc['heatmap'] = [xh, yh, wh, hh]
            roi_list.loc['ssdna'] = [xd, yd, wd, hd]
            roi_list.loc['gem'] = [xh+gem_data_x_min, yh+gem_data_y_min, wh, hh]
            roi_list.to_csv(f'{prefix}/{item_name}.roi.txt', sep='\t', header=True, index=True)
            # affine mask
            if masks is not None:
                roi_mask = masks[yd:yd+hd,xd:xd+wd]
                affined_roi_mask = nd.affine_transform(roi_mask.T,affineR,output_shape=(wh,hh),order=0)
                affined_roi_mask = affined_roi_mask.T
                np.savetxt(f'{prefix}/{item_name}.cell_mask.txt',affined_roi_mask,fmt="%d")
            # affine border 
            if borders is not None:
                roi_border = borders[yd:yd+hd,xd:xd+wd]
                affined_roi_border = nd.affine_transform(roi_border.T,affineR,output_shape=(wh,hh),order=0)
                affined_roi_border = affined_roi_border.T
                np.savetxt(f'{prefix}/{item_name}.cell_border.txt',affined_roi_border,fmt="%d")
            # affine ssdna
            if dapi_data is not None:
                roi_ssdna = dapi_data[yd:yd+hd,xd:xd+wd]
                affined_roi_ssdna = nd.affine_transform(roi_ssdna.T,affineR,output_shape=(wh,hh),order=0)
                affined_roi_ssdna = affined_roi_ssdna.T
                skio.imsave(f'{prefix}/{item_name}.ssDNA.png',affined_roi_ssdna)
                if borders is not None:
                    affined_roi_ssdna[affined_roi_border==1]=255
                    skio.imsave(f'{prefix}/{item_name}.ssDNA.border_masked.png',affined_roi_ssdna)
            if gem_data is not None:
                choped_gem = gem_data[ ( ( gem_data['x']>=xh ) & ( gem_data['x']<xh+wh ) & ( gem_data['y']>=yh ) &  ( gem_data['y']<yh+hh ) ) ]
                if masks is not None:
                    choped_gem = choped_gem.copy()
                    choped_gem['x'] = choped_gem['x'] - xh
                    choped_gem['y'] = choped_gem['y'] - yh
                    choped_gem['cell'] =  affined_roi_mask[choped_gem['y'],choped_gem['x']]
                    choped_gem_tosave = choped_gem.copy()
                    choped_gem_tosave['x'] = choped_gem_tosave['x'] + gem_data_x_min + xh
                    choped_gem_tosave['y'] = choped_gem_tosave['y'] + gem_data_y_min + yh
                    cell_cems_tosave = choped_gem_tosave[choped_gem_tosave['cell']!=0]
                    cell_cems_tosave.to_csv(f'{prefix}/{item_name}.gemc_saved',sep='\t',header=True,index=False)
                else:
                    choped_gem_tosave = choped_gem.copy()
                    choped_gem_tosave['x'] = choped_gem_tosave['x'] + gem_data_x_min
                    choped_gem_tosave['y'] = choped_gem_tosave['y'] + gem_data_y_min
                    choped_gem.to_csv(f'{prefix}/{item_name}.gem',sep='\t',header=True,index=False)
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
        # save roi
        roi_list = pd.DataFrame(columns=['x', 'y', 'width', 'height'])
        roi_list.loc['heatmap'] = [0, 0, -1, -1]
        roi_list.loc['ssdna'] = [0, 0, -1, -1]
        roi_list.loc['gem'] = [gem_data_x_min, gem_data_y_min, -1, -1]
        roi_list.to_csv(f'{prefix}.roi.txt', sep='\t', header=True, index=True)
        # affine mask
        if masks is not None:
            affined_roi_mask = nd.affine_transform(masks.T,affineR,output_shape=(W,H),order=0)
            affined_roi_mask = affined_roi_mask.T
            np.savetxt(f'{prefix}.cell_mask.txt',affined_roi_mask,fmt="%d")
        # affine border 
        if borders is not None:
            affined_roi_border = nd.affine_transform(borders.T,affineR,output_shape=(W,H),order=0)
            affined_roi_border = affined_roi_border.T
            np.savetxt(f'{prefix}.cell_border.txt',affined_roi_border,fmt="%d")
        # affine ssdna
        if dapi_data is not None:
            affined_roi_ssdna = nd.affine_transform(dapi_data.T,affineR,output_shape=(W,H),order=0)
            affined_roi_ssdna = affined_roi_ssdna.T
            skio.imsave(f'{prefix}.ssDNA.png',affined_roi_ssdna)
            if borders is not None:
                affined_roi_ssdna[affined_roi_border==1]=255
                skio.imsave(f'{prefix}.ssDNA.border_masked.png',affined_roi_ssdna)
        if gem_data is not None:
            if masks is not None:
                gem_data['cell'] = affined_roi_mask[gem_data['y'],gem_data['x']]
                gem_data['x'] = gem_data['x'] + gem_data_x_min
                gem_data['y'] = gem_data['y'] + gem_data_y_min
                gem_data = gem_data[gem_data['cell']!=0]
                gem_data.to_csv(f'{prefix}.gemc_saved',sep='\t',header=True,index=False)

if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
    apply_registration_main(sys.argv[1:])
    print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
