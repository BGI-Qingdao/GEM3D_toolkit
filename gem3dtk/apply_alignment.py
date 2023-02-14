import sys
import pandas as pd
import numpy as np
import anndata
from skimage import io as skio
import getopt
import json
import scipy.ndimage as nd

#Usage 
def apply_alignment_usage():
    print("""
Usage : apply_alignment.py  -i <input.json>
                            -o [outputdir]

input.json  :
            {
                "N"    : {"num" : int  , "values" : int },
                "ssdnafile"   : "fliph/flipv/noflip",
                "data"  :  [
                             ["gemfile_1","h5adfile_1","ssdnafile_1","maskfile_1","[[1,0,10], [0,1,0],[0.0, 0.0, 1.0]]"],
                                    ....
                             ["gemfile_N","h5adfile_N","ssdnafile_N","maskfile_N","[[1,0,10], [0,1,0],[0.0, 0.0, 1.0]]"]
                                ]
            }

Sample : apply_alignment.py  -i input.json \\
                             -o prefix   \\
                             -F '[[1,0,10], [0,1,0],[0.0, 0.0, 1.0]]'    
Notice: please provide one of [ -B , -F ], if both present, the later one will overwrite previous one.                             
    """,flush=True)

def apply_alignment_main(argv:[]):
    jsonfile=''
    affine=''
    prefix=''
 
    try:
         opts ,args =getopt.getopt(argv,"hi:o:",["help=",
                                                     "input=",
                                                     "output=",])
    except getopt.GetoptError:
        apply_alignment_usage()
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ("-h","--help"):
            apply_alignment_usage()
            sys.exit(0)
        elif opt in ("-i","--input"):
            jsonfile = arg
        elif opt in ("-o","--output"):
            prefix = arg 
        
    if jsonfile == '' or prefix == '':
        apply_alignment_usage()
        sys.exit(0)

    json_data=open(jsonfile,'r')
    class_indict = json.load(json_data)
    N_dict=class_indict["N"]
    N=int(N_dict["num"])
    value=int(N_dict["values"])
    flip=class_indict["ssdnafile"]
    collections=class_indict["data"]
    for i in range(N):
        try:
            collection=collections[i]
            affine=np.matrix(np.array(json.loads(collection[4])))
        except:
            print("file of json is erro !!!")
            apply_alignment_usage()
            sys.exit(0)
        affine_gem(collection[0],prefix,affine,i+1,value)
        affine_h5ad(collection[1],prefix,affine,i+1,value)
        affine_ssdna(collection[2],prefix,affine,flip,i+1)
        affine_txt(collection[3],prefix,affine,flip,i+1)

def affine_gem(inputgem,prefix,affine,N,value):
    df = pd.read_csv(inputgem, sep='\t', comment='#')
    gemxy=np.array(df[["x",'y']])
    gemxy=np.insert(gemxy,2,values=np.ones((gemxy.shape[0],)),axis=1)
    affine_result=np.dot(affine,gemxy.T)[0:2,:]
    df["new_x"]=np.array(affine_result[0:1,:].T)
    df["new_y"]=np.array(affine_result[1:2,:].T)
    df["z"]=np.array([int(value) for _ in range(df["x"].shape[0])])
    df.to_csv(f"{prefix}_{N}.gem",index=None,sep='\t')

def affine_ssdna(inputssdna,prefix,affine,flip,N):
    affine=affine.I
    dapi_data = skio.imread(inputssdna)
    w,h= dapi_data.shape

    if len(dapi_data.shape) == 3 : # RGB tiff to 8 bit gray tiff
        new_data = np.zeros((dapi_data.shape[0],dapi_data.shape[1]),dtype=int)
        new_data = new_data + dapi_data[:,:,0]
        new_data = new_data + dapi_data[:,:,1]
        new_data = new_data + dapi_data[:,:,2]
        new_data = (new_data+2) / 3
        dapi_data = new_data
    dapi_data = dapi_data.astype('uint8')
    ind = dapi_data
    if flip == 'fliph':
        ind = np.fliplr(ind)
    elif flip == 'flipv':
        ind = np.flipud(ind)
    outd = nd.affine_transform(ind.T,affine,output_shape=(h,w),order=0)
    outd = outd.T
    outd = outd.astype('uint8')
    skio.imsave(f'{prefix}_{N}.tif',outd)

def affine_h5ad(inputh5ad,prefix,affine,N,value):
    h5ad=anndata.read(inputh5ad)
    h5adxy=np.array(h5ad.obs[["x",'y']])
    h5adxy=np.insert(h5adxy,2,values=np.ones((h5adxy.shape[0],)),axis=1)
    affine_result=np.dot(affine,h5adxy.T)[0:2,:]
    h5ad.obs['new_x']=np.array(affine_result[0:1,:].T)
    h5ad.obs['new_y']=np.array(affine_result[1:2,:].T)
    h5ad.obs['z']=np.array([int(value)for _ in range(h5ad.obs.x.shape[0])])
    h5ad.write(f'{prefix}_{N}.h5ad',compression='gzip')

def affine_txt(inputmask,prefix,affine,flip,N):
    ind = np.loadtxt(inputmask,delimiter=' ',dtype=int)
    w,h = ind.shape
    if flip == 'fliph':
        ind = np.fliplr(ind)
    elif flip == 'flipv':
        ind = np.flipud(ind)
    outd = nd.affine_transform(ind.T,affine,output_shape=(h,w),order=0)
    outd = outd.T
    np.savetxt(f'{prefix}_{N}.txt',outd,fmt="%d")
        
