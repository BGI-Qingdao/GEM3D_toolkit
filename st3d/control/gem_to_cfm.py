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
import skimage.morphology as sm
from skimage import filters

def gem_to_cfm_usage():
    print("""
Usage : GEM_toolkit.py gem_to_cfm               -s <ssdna tiff file> \\
                                                -g <gem file>  \\
                                                -b <cell segment outline file> \\
                                                -m <cell segment mask file>\\
                                                -M <mask file>
                                                -r <roi with affine file>\\
                                                -h [show this usage]\\
                                                -o <output prefix>
Notice:
total 5 model
    1. -s ssdna.tif -g gem.gem -b border.txt -m mask.txt -r roi_affine.json -o output  
    function: gem to cfm if you have successful cell segmentation and roi registration results 
    
    2. -s ssdna.tif -g gem.gem -b border.txt -m mask.txt -a affine_matrix.txt -o output 
    function: gem to cfm if you have successful cell segmentation and all registration results
    
    3. -s ssdna.tif -g gem.gem -a affine_matrix.txt -o output
    function: gem to mask gem if you only have all registration results
    
    4. -s ssdna.tif -o output
    function: ssdna to mask with specific manner
    
    5. -M mask.tif -g gem.gem -a affine_matrix.txt -o output
    function: gem to mask gem only with a mask which make by yourself
     
""",flush=True)

def get_ids(data_map, data):
    ids = np.zeros(len(data), dtype=int)
    for index, x in enumerate(data):
        ids[index] = data_map[x]
    return ids


def gemc_to_cfm_roi(gemc,prefix,item_names):

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

def gemc_to_cfm_all(gemc,prefix):

    gems = gemc
    #pd.read_csv(f'{prefix}.gemc', sep='\t',header=0, compression='infer', comment='#')
    gems.columns = ['geneID', 'x', 'y', 'MIDCounts', 'cell']

    agg_gems = gems.groupby(by=['cell', 'geneID']).agg(np.sum).reset_index()  # ??
    cells = np.unique(agg_gems['cell'])
    genes = np.unique(agg_gems['geneID'])

    os.mkdir(f'{prefix}_cfm')
    np.savetxt(f'{prefix}_cfm/barcodes.tsv', cells.T, fmt="%s")
    check_call(f'gzip {prefix}_cfm/barcodes.tsv', shell=True)
    np.savetxt(f'{prefix}_cfm/features.tsv', genes.T, fmt="%s")
    check_call(f'gzip {prefix}_cfm/features.tsv', shell=True)

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

    sourceFile = open(f'{prefix}_cfm/mtx.csv', 'w')
    sourceFile.writelines(
        """%%MatrixMarket matrix coordinate integer general                                   
        %metadata_json: {"software_version": "Cell Ranger 4", "format_version": 2}           
        """)
    sourceFile.writelines("{} {} {}\n".format(len(gene_map), len(cell_map), len(mtx)))
    for _, row in mtx.iterrows():
        sourceFile.writelines("{} {} {}\n".format(row['gid'], row['cid'], row['count']))
    sourceFile.close()
    check_call(f'gzip {prefix}_cfm/mtx.csv', shell=True)
    print(f'{prefix} cfm file is saved')

def get_heatmap(gem_data):
    gem_data.columns = ['geneID', 'x', 'y', 'MIDCounts']
    gem_data_x_min = gem_data['x'].min()
    gem_data_y_min = gem_data['y'].min()
    gem_data_x_max = gem_data['x'].max()
    gem_data_y_max = gem_data['y'].max()
    gem_data['x'] = gem_data['x'] - gem_data_x_min
    gem_data['y'] = gem_data['y'] - gem_data_y_min
    gem_data['x'] = gem_data['x'].astype(int)
    gem_data['y'] = gem_data['y'].astype(int)


    coords = np.zeros((gem_data_y_max-gem_data_y_min+1,gem_data_x_max-gem_data_x_min+1),dtype=int)
    gem_data = gem_data.groupby(['x', 'y']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()
    coords[gem_data['y'], gem_data['x']] = gem_data['UMI_sum']
    coords = coords.astype('uint8')

    return coords


def get_mask(ssdna_file,prefix):
    ssdna = skio.imread(ssdna_file)

    if len(ssdna.shape) == 3:  # RGB tiff to 8 bit gray tiff
        new_data = np.zeros((ssdna.shape[0], ssdna.shape[1]), dtype=int)
        new_data = new_data + ssdna[:, :, 0]
        new_data = new_data + ssdna[:, :, 1]
        new_data = new_data + ssdna[:, :, 2]
        ssdna = new_data.astype('uint8')

    # ssdna =sfr.enhance_contrast(ssdna, sm.disk(9))
    # ssdna =sfr.enhance_contrast(ssdna, sm.disk(3))

    #convert to mask
    thre = filters.threshold_otsu(ssdna)
    ssdna[ssdna >= thre] = 255
    ssdna[ssdna < thre] = 0

    #expand pixel
    ssdna_dilation = sm.dilation(ssdna, sm.disk(9))
    # ssdna_dilation=sm.dilation(ssdna_dilation,sm.square(5))
    # edges = edges.astype('uint8')
    # print(edges)
    # edges = edges.astype('uint8')'''

    skio.imsave(f'{prefix}.mask.tif', ssdna_dilation)
    return ssdna_dilation

def ssdna_cut_gem(prefix,ssdna_file,gem_file,affine):

    mask = get_mask(ssdna_file,prefix)
    gem = pd.read_csv(gem_file,sep='\t', header=0, compression='infer', comment='#')
    affineR = np.matrix(np.loadtxt(affine))

    heatmap_image = get_heatmap(gem)
    heatmap = heatmap_image.copy()

    affine_mask = nd.affine_transform(mask.T,affineR,output_shape=heatmap.T.shape,order=0)
    affine_mask = affine_mask.T
    heatmap[affine_mask == 0] = 0
    gem_cut = gem.copy()
    gem_cut['cell'] = heatmap[gem['y'],gem['x']]
    gem_cut = gem_cut[gem_cut['cell']!=0]
    gem_cut.drop(columns=['cell'], inplace=True)


    gem_cut.to_csv(f'{prefix}.after_cut.gem', sep='\t', header=True, index=False)
    skio.imsave(f'{prefix}.heatmap.tif',heatmap_image)
    skio.imsave(f'{prefix}.heatmap.mask.tif',heatmap)

def mask_cut_gem(prefix,mask_file,gem_file,affine):

    mask = skio.imread(mask_file)
    gem = pd.read_csv(gem_file,sep='\t', header=0, compression='infer', comment='#')
    affineR = np.matrix(np.loadtxt(affine))

    heatmap_image = get_heatmap(gem)
    heatmap = heatmap_image.copy()

    affine_mask = nd.affine_transform(mask.T,affineR,output_shape=heatmap.T.shape,order=0)
    affine_mask = affine_mask.T
    heatmap[affine_mask == 0] = 0
    gem_cut = gem.copy()
    gem_cut['cell'] = heatmap[gem['y'],gem['x']]
    gem_cut = gem_cut[gem_cut['cell']!=0]
    gem_cut.drop(columns=['cell'], inplace=True)


    gem_cut.to_csv(f'{prefix}.after_cut.gem', sep='\t', header=True, index=False)
    skio.imsave(f'{prefix}.heatmap.tif',heatmap_image)
    skio.imsave(f'{prefix}.heatmap.mask.tif',heatmap)

def gem_to_cfm_main(argv:[]):
    prefix = ''
    mask = ''
    border = ''
    gem = ''
    roi_affines = ''
    ssdna = ''
    affine = ''
    Mask = ''

    try:
        opts, args = getopt.getopt(argv,"hm:b:g:o:r:s:a:M:",["help","mask=","border=","gem=","output=","roi=","ssdna=","affine","Mask"])
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
        elif opt in ("-M", "--Mask"):
            Mask = arg
        elif opt in ("-b", "--border"):
            border = arg
        elif opt in ("-g", "--gem"):
            gem = arg
        elif opt in ("-r", "--roi"):
            roi_affines = arg
        elif opt in ("-a", "--affine"):
            affine = arg
        elif opt in ("-s", "--ssdna"):
            ssdna = arg



    if ssdna != "" and mask != "" and prefix != "" and border != "" and gem != "" and roi_affines != "" and affine == "" and Mask == "" :
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

            roi_mask = masks[yd:yd+hd,xd:xd+wd]
            roi_border = borders[yd:yd+hd,xd:xd+wd]
            roi_ssdna = dapi_data[yd:yd+hd,xd:xd+wd]

            affined_roi_mask = nd.affine_transform(roi_mask.T,affineR,output_shape=(wh,hh),order=0)
            affined_roi_mask = affined_roi_mask.T
            #affined_roi_mask = affined_roi_mask[300:-300, 300:-300]
            np.savetxt(f'{prefix}/{item_name}.cell_mask.txt',affined_roi_mask,fmt="%d")

            affined_roi_border = nd.affine_transform(roi_border.T,affineR,output_shape=(wh,hh),order=0)
            affined_roi_border = affined_roi_border.T
            #affined_roi_border = affined_roi_border[300:-300, 300:-300]
            np.savetxt(f'{prefix}/{item_name}.cell_border.txt',affined_roi_border,fmt="%d")


            affined_roi_ssdna = nd.affine_transform(roi_ssdna.T,affineR,output_shape=(wh,hh),order=0)
            affined_roi_ssdna = affined_roi_ssdna.T
            #affined_roi_ssdna = affined_roi_ssdna[300:-300, 300:-300]
            skio.imsave(f'{prefix}/{item_name}.ssDNA.tif',affined_roi_ssdna)
            #affined_roi_ssdna[affined_roi_border==1]=255
            skio.imsave(f'{prefix}/{item_name}.ssDNA.border_masked.tif',affined_roi_ssdna)
            print(f'{item_name} mask and border image is saved')

            #xh, yh, wh, hh = xh + 300, yh + 300, wh - 600, hh - 600
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
            choped_gem_tosave.to_csv(f'{prefix}/{item_name}.gemc', sep='\t', header=True, index=False)

            #delete cells outside mask
            cell_cems_tosave = choped_gem_tosave[choped_gem_tosave['cell']!=0]
            deleted_gems_tosave = choped_gem_tosave[choped_gem_tosave['cell']==0]
            cell_cems_tosave.to_csv(f'{prefix}/{item_name}.gemc_saved',sep='\t',header=True,index=False)
            deleted_gems_tosave.to_csv(f'{prefix}/{item_name}.gemc_deleted',sep='\t',header=True,index=False)


            print(f'{item_name} gemc file is saved')

            gemc_to_cfm_roi(cell_cems_tosave,prefix,item_name)

            heatmap_image = choped_gem.copy()
            coords_image = np.zeros((hh,wh),dtype=int)
            heatmap_image = heatmap_image.groupby(['x', 'y']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()
            coords_image[heatmap_image['y'], heatmap_image['x']] = heatmap_image['UMI_sum']
            coords_image = coords_image.astype('uint8')
            skio.imsave(f'{prefix}/{item_name}.heatmap.tif',coords_image)



            cell_cems = choped_gem[choped_gem['cell'] != 0]
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
            skio.imsave(f'{prefix}/{item_name}.heatmap.mask.tif',coords)
            coords[affined_roi_border==1]=0
            skio.imsave(f'{prefix}/{item_name}.heatmap.border_masked.tif',coords)

    elif ssdna != "" and mask != "" and prefix != "" and border != "" and gem != "" and roi_affines == "" and affine !="" and Mask =="":

        print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
        # load gems
        gem_data = pd.read_csv(gem, sep='\t', header=0, compression='infer', comment='#')
        heatmap = get_heatmap(gem_data)
        skio.imsave(f'{prefix}.heatmap.tif',heatmap)

        print(f'gem file is {gem}')
        gem_data.columns = ['geneID','x','y','MIDCounts']
        gem_data_x_min = gem_data['x'].min()
        gem_data_y_min = gem_data['y'].min()
        gem_data['x'] = gem_data['x'] - gem_data_x_min
        gem_data['y'] = gem_data['y'] - gem_data_y_min
        gem_data['x'] = gem_data['x'].astype(int)
        gem_data['y'] = gem_data['y'].astype(int)
        # load ssdna
        ssdna_data = skio.imread(ssdna)
        print(f'ssdna file is {ssdna}')
        if len(ssdna_data.shape) == 3 : # RGB tiff to 8 bit gray tiff
            new_data = np.zeros((ssdna_data.shape[0],ssdna_data.shape[1]),dtype=int)
            new_data = new_data + ssdna_data[:,:,0]
            new_data = new_data + ssdna_data[:,:,1]
            new_data = new_data + ssdna_data[:,:,2]
            new_data = (new_data+2) / 3
            ssdna_data = new_data
        ssdna_data = ssdna_data.astype('uint8')

        # load cell ids and borders
        masks = np.loadtxt(mask,dtype=int,delimiter=' ')
        borders =  np.loadtxt(border,dtype='uint8',delimiter=' ')
        print(f'mask file is {mask}')
        print(f'border file is {border}')


        affineR = np.loadtxt(affine)

        affined_mask = nd.affine_transform(masks.T, affineR, output_shape=heatmap.T.shape, order=0)
        affined_mask = affined_mask.T
        np.savetxt(f'{prefix}.cell_mask.txt', affined_mask, fmt="%d")

        affined_border = nd.affine_transform(borders.T, affineR, output_shape=heatmap.T.shape, order=0)
        affined_border = affined_border.T
        np.savetxt(f'{prefix}.cell_border.txt', affined_border, fmt="%d")

        affined_ssdna = nd.affine_transform(ssdna_data.T, affineR, output_shape=heatmap.T.shape, order=0)
        affined_ssdna = affined_ssdna.T
        skio.imsave(f'{prefix}.ssDNA.tif', affined_ssdna)
        affined_ssdna[affined_border == 1] = 255
        skio.imsave(f'{prefix}.ssDNA.border_masked.tif', affined_ssdna)
        print(f'{prefix} mask and border image is saved')


        choped_gem = gem_data.copy()

        choped_gem_x_min = choped_gem['x'].min()
        choped_gem_y_min = choped_gem['y'].min()
        choped_gem['x'] = choped_gem['x'] - choped_gem_x_min
        choped_gem['y'] = choped_gem['y'] - choped_gem_y_min
        choped_gem['cell'] = affined_mask[choped_gem['y'], choped_gem['x']]

        choped_gem_tosave = choped_gem.copy()

        choped_gem_tosave['x'] = choped_gem_tosave['x'] + gem_data_x_min + choped_gem_x_min
        choped_gem_tosave['y'] = choped_gem_tosave['y'] + gem_data_y_min + choped_gem_y_min
        choped_gem_tosave.to_csv(f'{prefix}.gemc', sep='\t', header=True, index=False)

        # delete cells outside mask
        cell_cems_tosave = choped_gem_tosave[choped_gem_tosave['cell'] != 0]
        deleted_gems_tosave = choped_gem_tosave[choped_gem_tosave['cell'] == 0]
        cell_cems_tosave.to_csv(f'{prefix}.gemc_saved', sep='\t', header=True, index=False)
        deleted_gems_tosave.to_csv(f'{prefix}.gemc_deleted', sep='\t', header=True, index=False)
        print(f'{prefix} gemc file is saved')

        gemc_to_cfm_all(cell_cems_tosave, prefix)

        cell_cems = choped_gem[choped_gem['cell'] != 0]
        cell_cems = cell_cems.copy()
        cell_cems.drop(columns=['cell'], inplace=True)
        coords = np.zeros((heatmap.shape), dtype=int)
        cell_cems = cell_cems.groupby(['x', 'y']).agg(UMI_sum=('MIDCounts', 'sum')).reset_index()
        coords[cell_cems['y'], cell_cems['x']] = cell_cems['UMI_sum']
        expression = coords
        ret = np.zeros(expression.shape, dtype=int)
        h, w = expression.shape
        for i in range(0, 6):
            for j in range(0, 6):
                newm = np.zeros(expression.shape)
                newm[i:, j:] = expression[:h - i, :w - j]
                ret = ret + newm
        ret[ret > 255] = 255
        ret = ret.astype('uint8')
        coords = ret
        skio.imsave(f'{prefix}.heatmap.mask.tif', coords)
        coords[affined_border == 1] = 0
        skio.imsave(f'{prefix}.heatmap.border_masked.tif', coords)

    elif ssdna != "" and mask == "" and prefix != "" and border == "" and gem != "" and roi_affines == "" and affine != "" and Mask == "":
        ssdna_cut_gem(prefix,ssdna,gem,affine)

    elif ssdna != "" and mask == "" and prefix != "" and border == "" and gem == "" and roi_affines == "" and affine == "" and Mask == "":
        get_mask(ssdna,prefix)

    elif ssdna == '' and mask == "" and prefix != "" and border == "" and gem != "" and roi_affines == "" and affine != "" and Mask !="":
        mask_cut_gem(prefix,Mask,gem,affine)

    else:
        gem_to_cfm_usage()
        sys.exit(3)



if __name__ == "__main__":
    gem_to_cfm_main(sys.argv[1:])
    print('all file has been saved')
    print(time.strftime("%Y-%m-%d %H:%M:%S"), file=sys.stderr, flush=True)
