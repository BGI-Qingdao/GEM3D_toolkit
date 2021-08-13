"""Interfaces for loading slices"""
import os.path
from pathlib import Path

import numpy as np
import pandas as pd
import json

from st3d.model.slice_dataframe import slice_meta_data
from st3d.model.rect_bin import bins_of_slice
###########################################################
# common
###########################################################

def load_slice_info( filename : str ) -> slice_meta_data :
    slice_info_json = json.load(open(filename))
    slice_info = slice_meta_data(slice_info_json['slice_id'],
                                 slice_info_json['slice_min_x'],
                                 slice_info_json['slice_min_y'],
                                 slice_info_json['slice_width'],
                                 slice_info_json['slice_height'])
    slice_info.assign_bininfo(slice_info_json['binsize'],
                              slice_info_json['binwidth'],
                              slice_info_json['binheight'])
    return slice_info

def load_slice_tissues_positions(filename : str) -> pd.DataFrame :
    header=['bin_name','masked','bin_x','bin_y','png_x','png_y','slice_id','3d_x','3d_y','3d_z']
    bos_dataframe = pd.read_csv(filename,sep=',',header=None)
    bos_dataframe.columns=header
    return bos_dataframe


###########################################################
# gem2bfm
###########################################################
def load_slices(config :str) ->{}:
    files=json.load(open(config))
    slices = {}
    for one_file in files:
        slices[one_file[0]]=one_file[1]
    return slices

###########################################################
# affine matrix
###########################################################
def load_slice_tp(input_folder:str, slice_index:int) -> (slice_meta_data,pd.DataFrame):
    file1="{}/slice_{}/slices.json".format(input_folder,slice_index)
    slice_info = load_slice_info(file1)

    file2="{}/slice_{}/spatial/tissue_positions_list.csv".format(input_folder,slice_index)
    bos_dataframe = load_slice_tissues_positions(file2)
    return  slice_info , bos_dataframe
    #for _ ,row in bos_dataframe.iterrows():

def load_affines(config:str):
    affine_json=json.load(open(config))
    affine_datas={}
    for x in affine_json:
        affine_datas[x[0]] = np.matrix(np.array(x[1]))
    return affine_datas

def load_tissues_positions_byaffines(affine_datas:{}, input_folder:str):
    slices_infos={}
    boss = {}
    for slice_index in affine_datas.keys():
        slice_info , bos = load_slice_tp(input_folder,slice_index)
        slices_infos[slice_index] = slice_info
        boss[slice_index] = bos
    return slices_infos,boss

###########################################################
# model3d
###########################################################
def load_clusters(filename:str)->pd.DataFrame:
    cluster_df = pd.read_csv(filename,sep=',')
    return cluster_df

def load_tissues_positions_bycluster(cluster_df:pd.DataFrame, input_folder:str):
    slice_ids = pd.unique(cluster_df['slice'])
    pds = {}
    sinfos={}
    for sid in slice_ids:
        cdata=cluster_df.loc[cluster_df['slice']==sid]
        file1="{}/slice_{}/slices.json".format(input_folder,sid)
        slice_info = load_slice_info(file1)
        sinfos[sid]=slice_info
        file2="{}/slice_{}/tissue_positions_list.csv".format(input_folder,sid)
        bos_dataframe = load_slice_tissues_positions(file2)
        pds[sid]=bos_dataframe
    return pds,sinfos

def load_masks_byclusters(folder:str ,cluster_df:pd.DataFrame, cache : {}):
    slice_ids = pd.unique(cluster_df['slice'])
    for sid in slice_ids:
        filename="{}/slice_{}.txt".format(folder,sid)
        my_file = Path(filename)
        if my_file.is_file() and my_file.exists() :
            cache[sid] = np.loadtxt(filename,dtype=int,delimiter='\t')

###########################################################
# maskbfm
###########################################################

def load_sparse_matrix(filename:str) ->pd.DataFrame :
    df =  pd.read_csv(filename, compression='gzip', header=2, sep=' ',  error_bad_lines=False)
    return df