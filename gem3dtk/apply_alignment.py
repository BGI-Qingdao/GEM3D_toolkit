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
                            -a [F/B , default F]
                            -t [True/False,default Flase]
                            -m [merge files of h5ad,default False]


input.json  :
            {       
                "data"  :  [
                             ['S1',"gemfile_1","h5adfile_1","ssdnafile_1","maskfile_1","[[1,0,10], [0,1,0],[0.0, 0.0, 1.0]]","z_value","[[1,0,0], [0,1,0],[0.0, 0.0, 1]]"],
                                    ....
                             ['Sn',"gemfile_N","h5adfile_N","ssdnafile_N","maskfile_N","[[1,0,10], [0,1,0],[0.0, 0.0, 1.0]]","z_value","[[1,0,0], [0,1,0],[0.0, 0.0, 1]]"]
                                ]            
                ]
            }

Sample : apply_alignment.py  -i input.json \\
                             -o prefix   \\
                             -a F
                             -t True
                             -m True
    """,flush=True)

def apply_alignment_main(argv:[]):
    jsonfile=''
    affine=''
    prefix=''
    a="F"
    hflag=False
    h5admerge=''
    tflag=False
    try:
         opts ,args =getopt.getopt(argv,"hi:o:a:m:t:",["help=",
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
        elif opt in ("-a"):
            a = arg
        elif opt in ('-m'):
            hflag = arg 
        elif opt in ('-m'):
            hflag = arg 
        elif opt in ('-t'):
            tflag = arg
        
    if jsonfile == '' or prefix == '':
        apply_alignment_usage()
        sys.exit(0)
    json_data=open(jsonfile,'r')
    class_indict = json.load(json_data)
    N_num=class_indict["data"]
    N=len(N_num)
    collections=class_indict["data"]
    for i in range(N):
        try:
            collection=collections[i]
            if a == 'F':
                affine=np.matrix(np.array(json.loads(collection[5])))
            elif a == "B":
                affine=np.matrix(np.array(json.loads(collection[5]))).I
        except:
            print("file of json is erro !!!")
            apply_alignment_usage()
            sys.exit(0)
        if collection[1]!='':
            if tflag == False:
                affine_gem(collection[1],prefix,affine,i+1,collection[6])
            else:
                transform=np.matmul(np.matrix(np.array(json.loads(collection[7]))),affine)
                affine_gem(collection[1],prefix,transform,i+1,collection[6])
        if collection[2]!='':
            if tflag == False:
                h5ad=affine_h5ad(collection[2],affine,collection[6],collection[0])
            else:
                transform=np.matmul(np.matrix(np.array(json.loads(collection[7]))),affine)
                h5ad=affine_h5ad(collection[2],transform,collection[6],collection[0])
            if hflag==False:
                h5ad.write(f'{prefix}_{i+1}.h5ad',compression='gzip')
            else:
                if i==0:
                    h5admerge=h5ad
                else:
                    h5admerge=h5admerge.concatenate(h5ad)
                if int(i+1)==int(N):
                    h5admerge.write(f'{prefix}_merged.h5ad',compression='gzip')
        if collection[3]!='':
            affine_ssdna(collection[3],prefix,affine,i+1)
        if collection[4]!='':
            affine_txt(collection[4],prefix,affine,i+1)

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
    if dapi_data.shape == 3:
        w,h,_=dapi_data.shape
    else:
        w,h= dapi_data.shape
    if len(dapi_data.shape) == 3 : # RGB to 8 bit gray 
        new_data = np.zeros((dapi_data.shape[0],dapi_data.shape[1]),dtype=int)
        new_data = new_data + dapi_data[
            :,:,0]
        new_data = new_data + dapi_data[:,:,1]
        new_data = new_data + dapi_data[:,:,2]
        new_data = (new_data+2) / 3
        dapi_data = new_data
    dapi_data = dapi_data.astype('uint8')
    ind = dapi_data
    outd = nd.affine_transform(ind.T,affine,output_shape=(h,w),order=0)
    outd = outd.T
    outd = outd.astype('uint8')
    skio.imsave(f'{prefix}_{N}.png',outd)

def affine_h5ad(inputh5ad,affine,value,S):
    h5ad=anndata.read(inputh5ad)
    h5adxy=np.array(h5ad.obs[["x",'y']])
    h5adxy=np.insert(h5adxy,2,values=np.ones((h5adxy.shape[0],)),axis=1)
    affine_result=np.dot(affine,h5adxy.T)[0:2,:]
    h5ad.obs['new_x']=np.array(affine_result[0:1,:].T)
    h5ad.obs['new_y']=np.array(affine_result[1:2,:].T)
    h5ad.obs['z']=np.array([int(value) for _ in range(h5ad.obs.x.shape[0])])
    if S!='':
        h5ad.obs.index.name=S
    return h5ad

def affine_txt(inputmask,prefix,affine,flip,N):
    ind = np.loadtxt(inputmask,delimiter=' ',dtype=int)
    w,h = ind.shape
    outd = nd.affine_transform(ind.T,affine,output_shape=(h,w),order=0)
    outd = outd.T
    np.savetxt(f'{prefix}_{N}.txt',outd,fmt="%d")
