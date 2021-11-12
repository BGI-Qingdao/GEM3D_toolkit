#!/usr/bin/env python3
import os
import sys
import time
import json
import getopt
import numpy as np
import pandas as pd
import scipy.ndimage as nd
from subprocess import check_call
from skimage import io as skio

def gem_to_cfm_usage():
    print("""
Usage : GEM_toolkit.py prepareregistrationssdna -s <ssdna tiff file> \\
                                                -g <gem file>  \\
                                                -b <cell segment outline file> \\
                                                -m <cell segment mask file>\\
                                                -r <roi file>\\
                                                -h [show this usage]\\
                                                -o <output prefix>
Notice:
    all the file (-s -g -b -m -r) must be prepared
""",flush=True)

def get_ids(data_map, data):
    ids = np.zeros(len(data), dtype=int)
    for index, x in enumerate(data):
        ids[index] = data_map[x]
    return ids


def gemc_to_cfm(gemc,prefix,item_names):

    gems = gemc
    #pd.read_csv(f'{prefix}.gemc', sep='\t',header=0, compression='infer', comment='#')
    gems.columns = ['geneID', 'x', 'y', 'MIDCounts', 'cell']

    agg_gems = gems.groupby(by=['cell', 'geneID']).agg(np.sum).reset_index()  # ??
    cells = np.unique(agg_gems['cell'])
    genes = np.unique(agg_gems['geneID'])

    os.mkdir(f'{prefix}/{item_names}_cfm')
    np.savetxt(f'{prefix}/{item_names}_cfm/barcodes.tsv', cells.T, fmt="%s")
    check_call(f'gzip {prefix}/{item_names}_cfm/barcodes.tsv', shell=True)
    np.savetxt(f'{prefix}/{item_names}_cfm/features.tsv', genes.T, fmt="%s")
    check_call(f'gzip {prefix}/{item_names}_cfm/features.tsv', shell=True)

    cell_map = {}
    gene_map = {}
    for index, gene in enumerate(genes):
        gene_map[gene] = index + 1
    for index, cell in enumerate(cells):
        cell_map[cell] = index + 1


    #
    mtx = pd.DataFrame(columns=('cid', 'gid', 'count'), index=range(len(agg_gems)))
    mtx['cid'] = get_ids(cell_map, agg_gems['cell'])
    mtx['gid'] = get_ids(gene_map, agg_gems['geneID'])
    mtx['count'] = agg_gems['MIDCounts']

    sourceFile = open(f'{prefix}/{item_names}_cfm/mtx.csv', 'w')
    sourceFile.writelines(
        """%%MatrixMarket matrix coordinate integer general                                   
        %metadata_json: {"software_version": "Cell Ranger 4", "format_version": 2}           
        """)
    sourceFile.writelines("{} {} {}\n".format(len(gene_map), len(cell_map), len(mtx)))
    for _, row in mtx.iterrows():
        sourceFile.writelines("{} {} {}\n".format(row['gid'], row['cid'], row['count']))
    sourceFile.close()
    check_call(f'gzip {prefix}/{item_names}_cfm/mtx.csv', shell=True)
    print(f'{prefix}/{item_names} cfm file is saved')



def gem_to_cfm_main(argv:[]):
    prefix = ''
    mask = ''
    border = ''
    gem = ''
    roi_affines = ''
    ssdna = ''

    try:
        opts, args = getopt.getopt(argv,"hm:b:g:o:r:s:",["help","mask=","border=","gem=","output=","roi=","ssdna="])
    except getopt.GetoptError:
        gem_to_cfm_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem_to_cfm_usage()
            sys.exit(0)
        elif opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-m", "--mask"):
            mask = arg
        elif opt in ("-b", "--border"):
            border = arg
        elif opt in ("-g", "--gem"):
            gem = arg
        elif opt in ("-r", "--roi"):
            roi_affines = arg
        elif opt in ("-s", "--ssdna"):
            ssdna = arg

    if  ssdna == '' or mask == "" or prefix=="" or border =="" or gem == "" or roi_affines == "":
        gem_to_cfm_usage()
        sys.exit(3)

    # load roi and affined matrics
    roi_affines_data = json.load(open(roi_affines))
    print(f'roi file is {roi_affines}')
    print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
    # load gems
    gem_data = pd.read_csv(gem, sep='\t', header=0, compression='infer', comment='#')
    print(f'gem file is {gem}')
    gem_data.columns = ['geneID','x','y','MIDCounts']
    gem_data_x_min = gem_data['x'].min()
    gem_data_y_min = gem_data['y'].min()
    gem_data['x'] = gem_data['x'] - gem_data_x_min
    gem_data['y'] = gem_data['y'] - gem_data_y_min
    gem_data['x'] = gem_data['x'].astype(int)
    gem_data['y'] = gem_data['y'].astype(int)
    # load ssdna
    dapi_data = skio.imread(ssdna)
    print(f'ssdna file is {ssdna}')
    if len(dapi_data.shape) == 3 : # RGB tiff to 8 bit gray tiff
        new_data = np.zeros((dapi_data.shape[0],dapi_data.shape[1]),dtype=int)
        new_data = new_data + dapi_data[:,:,0]
        new_data = new_data + dapi_data[:,:,1]
        new_data = new_data + dapi_data[:,:,2]
        new_data = (new_data+2) / 3
        dapi_data = new_data
    dapi_data = dapi_data.astype('uint8')

    # load cell ids and borders
    masks = np.loadtxt(mask,dtype=int,delimiter=' ')
    borders =  np.loadtxt(border,dtype='uint8',delimiter=' ')
    print(f'mask file is {mask}')
    print(f'border file is {border}')

    os.mkdir(prefix)
    # get items one by one
    for item in roi_affines_data:
        item_name = item[0]
        xh,yh,wh,hh = item[1]
        xd,yd,wd,hd = item[2]
        affineR = np.matrix(np.array(item[3]))

        roi_mask = masks[yd-1:yd+hd,xd-1:xd+wd]
        roi_border = borders[yd-1:yd+hd,xd-1:xd+wd]
        roi_ssdna = dapi_data[yd-1:yd+hd,xd-1:xd+wd]

        affined_roi_mask = nd.affine_transform(roi_mask.T,affineR,output_shape=(wh,hh),order=0)
        affined_roi_mask = affined_roi_mask.T
        affined_roi_mask = affined_roi_mask[300:-300,300:-300]
        np.savetxt(f'{prefix}/{item_name}.cell_mask.txt',affined_roi_mask,fmt="%d")

        affined_roi_border = nd.affine_transform(roi_border.T,affineR,output_shape=(wh,hh),order=0)
        affined_roi_border = affined_roi_border.T
        affined_roi_border = affined_roi_border[300:-300,300:-300]
        np.savetxt(f'{prefix}/{item_name}.cell_border.txt',affined_roi_border,fmt="%d")


        affined_roi_ssdna = nd.affine_transform(roi_ssdna.T,affineR,output_shape=(wh,hh),order=0)
        affined_roi_ssdna = affined_roi_ssdna.T
        affined_roi_ssdna = affined_roi_ssdna[300:-300,300:-300]
        skio.imsave(f'{prefix}/{item_name}.ssDNA.tif',affined_roi_ssdna)
        affined_roi_ssdna[affined_roi_border==1]=255
        skio.imsave(f'{prefix}/{item_name}.ssDNA.border_masked.tif',affined_roi_ssdna)
        print(f'{item_name}mask and border image is saved')

        xh,yh,wh,hh = xh+300,yh+300,wh-600, hh-600
        choped_gem = gem_data[ ( ( gem_data['x']>=xh ) & ( gem_data['x']<xh+wh ) & ( gem_data['y']>=yh ) &  ( gem_data['y']<yh+hh ) ) ]
        choped_gem = choped_gem.copy()


        choped_gem_x_min = choped_gem['x'].min()
        choped_gem_y_min = choped_gem['y'].min()
        choped_gem['x'] = choped_gem['x'] - choped_gem_x_min
        choped_gem['y'] = choped_gem['y'] - choped_gem_y_min
        choped_gem['cell'] =  affined_roi_mask[choped_gem['y'],choped_gem['x']]

        choped_gem_tosave = choped_gem.copy()


        choped_gem_tosave['x'] = choped_gem_tosave['x'] + gem_data_x_min + choped_gem_x_min
        choped_gem_tosave['y'] = choped_gem_tosave['y'] + gem_data_y_min + choped_gem_y_min
        choped_gem_tosave.to_csv(f'{prefix}/{item_name}.gem', sep='\t', header=True, index=False)

        #delete cells outside mask
        cell_cems_tosave = choped_gem_tosave[choped_gem_tosave['cell']>0]
        deleted_gems_tosave = choped_gem_tosave[choped_gem_tosave['cell']==0]
        cell_cems_tosave.to_csv(f'{prefix}/{item_name}.gemc',sep='\t',header=True,index=False)
        deleted_gems_tosave.to_csv(f'{prefix}/{item_name}.gem_deleted',sep='\t',header=True,index=False)
        print(f'{item_name} gemc file is saved')

        gemc_to_cfm(cell_cems_tosave,prefix,item_name)

        cell_cems = choped_gem[choped_gem['cell'] > 0]
        cell_cems = cell_cems.copy()
        coords = np.zeros((hh,wh),dtype=int)
        cell_cems = cell_cems.groupby(['x', 'y']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()
        coords[cell_cems['y'], cell_cems['x']] = cell_cems['UMI_sum']
        coords = coords.astype('uint8')
        expression = coords
        ret = np.zeros(expression.shape,dtype=int)
        h,w = expression.shape
        for i in range(0,6):
            for j in range(0,6):
                newm = np.zeros(expression.shape)
                newm[i:,j:] = expression[:h-i,:w-j]
                ret = ret + newm
        ret[ret>255]=255
        ret = ret.astype('uint8')
        coords = ret
        skio.imsave(f'{prefix}/{item_name}.heatmap.tif',coords)
        coords[affined_roi_border==1]=0
        skio.imsave(f'{prefix}/{item_name}.heatmap.border_masked.tif',coords)

if __name__ == "__main__":
	gem_to_cfm_main(sys.argv[1:])
	print('all file has been saved')
	print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
