import os
import json
from json import JSONEncoder
import numpy as np
import pandas as pd
from subprocess import check_call

from st3d.model.rect_bin import bins_of_slice, bins_of_slices
from st3d.model.slices_manager import slices_manager
from st3d.model.slice_dataframe import slice_dataframe

###########################################################
# section1 : common functions
###########################################################
class General_Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def create_a_folder(prefix):
    if os.path.exists(prefix):
        print("output path {} exist ! exit ...".format(prefix))
        exit(101)
    os.mkdir(prefix)
    if not os.path.exists(prefix):
        print("create output path {}  failed! exit ...".format(prefix))
        exit(102)

def print_tp_bins_of_slice(bos: bins_of_slice ,file_hander):
    #print(len(bos.bins))
    for abin in bos.bins:
        if not hasattr(abin,'graph_x') and not hasattr(abin,'d3_x') :
            file_hander.writelines("{},{},{},{},-1,-1,{},-1,-1,-1\n".format(
                        abin.bin_name,
                        int(abin.valid),
                        int(abin.spot_x),
                        int(abin.spot_y),
                        abin.slice_id
                        ))
        elif hasattr(abin,'graph_x') and not hasattr(abin,'d3_x') :
            file_hander.writelines("{},{},{},{},{},{},{},-1,-1,-1\n".format(
                        abin.bin_name,
                        int(abin.valid),
                        int(abin.spot_x),
                        int(abin.spot_y),
                        int(abin.graph_x),
                        int(abin.graph_y),
                        abin.slice_id
                        ))
        elif not hasattr(abin,'graph_x') and hasattr(abin,'d3_x') :
            file_hander.writelines("{},{},{},{},-1,-1,{},{},{},{}\n".format(
                        abin.bin_name,
                        int(abin.valid),
                        int(abin.spot_x),
                        int(abin.spot_y),
                        abin.slice_id,
                        abin.d3_x,
                        abin.d3_y,
                        abin.d3_z
                        ))
        else :
            file_hander.writelines("{},{},{},{},{},{},{},{},{},{}\n".format(
                        abin.bin_name,
                        int(abin.valid),
                        int(abin.spot_x),
                        int(abin.spot_y),
                        int(abin.graph_x),
                        int(abin.graph_y),
                        abin.slice_id,
                        abin.d3_x,
                        abin.d3_y,
                        abin.d3_z
                        ))

###########################################################
# section2 : gem2bfm
###########################################################

def init_gem2bfm_output(prefix : str):
    create_a_folder(prefix)

def init_gem2bfm_slice(prefix:str,slice_id):
    create_a_folder("{}/slice_{}".format(prefix,slice_id))
    create_a_folder("{}/slice_{}/raw_feature_bc_matrix".format(prefix,slice_id))
    create_a_folder("{}/slice_{}/spatial".format(prefix,slice_id))

def print_features_tsv(gene_names : [] , prefix:str,slice_id):
    filename="{}/slice_{}/raw_feature_bc_matrix/features.tsv".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    for items in gene_names:
        sourceFile.writelines(items.replace('_','-')+'\n')
    sourceFile.close()
    check_call('gzip {}'.format(filename),shell=True)

def print_barcodes_tsv(bos: bins_of_slices , prefix:str,slice_id):
    filename="{}/slice_{}/raw_feature_bc_matrix/barcodes.tsv".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    for abin in bos.bins:
        sourceFile.writelines(abin.bin_name+'\n')
    sourceFile.close()
    check_call('gzip {}'.format(filename),shell=True)

def print_tissue_positions_list(bos: bins_of_slice , prefix:str,slice_id):
    filename="{}/slice_{}/spatial/tissue_positions_list.csv".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    print_tp_bins_of_slice(bos,sourceFile)
    sourceFile.close()

def print_gem2bfm_slices_json(slices_info : {} , prefix: str,slice_id):
    filename="{}/slice_{}/slices.json".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    sourceFile.writelines(json.dumps(slices_info, sort_keys=False, indent=4, separators=(',', ':'),cls=General_Encoder))
    sourceFile.close()

def print_matrix_mtx(mtx,prefix,slice_id,gnum,bnum):
    filename="{}/slice_{}/raw_feature_bc_matrix/matrix.mtx".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    sourceFile.writelines(
"""%%MatrixMarket matrix coordinate integer general
%metadata_json: {"software_version": "Cell Ranger 4", "format_version": 2}
""")
    sourceFile.writelines("{} {} {}\n".format(gnum,bnum,len(mtx)))
    for _, row in mtx.iterrows():
        sourceFile.writelines("{} {} {}\n".format(row['gid'],row['bid'],row['count']))
    sourceFile.close()
    check_call('gzip {}'.format(filename),shell=True)

###########################################################
# section3 : heatmap
###########################################################

def init_heatmap_output(prefix:str):
    create_a_folder(prefix)

def init_heatmap_slice(prefix:str , slice_id :int):
    create_a_folder('{}/slice_{}'.format(prefix,slice_id))

def print_slices_heatmap_json(slices_info : {} , prefix: str,slice_id:int):
    filename="{}/slice_{}/slice.json".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    sourceFile.writelines(json.dumps(slices_info, sort_keys=False, indent=4, separators=(',', ':'),cls=General_Encoder))
    sourceFile.close()

def print_heatmap_tissue_positions_list(bos: bins_of_slice , prefix:str,slice_id):
    filename="{}/slice_{}/tissue_positions_list.csv".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    print_tp_bins_of_slice(bos,sourceFile)
    sourceFile.close()


###########################################################
# section4 :affine matrix 
###########################################################

def init_affine_folder(prefix:str):
    create_a_folder(prefix)

def init_affine_slice(prefix:str , slice_id :int):
    create_a_folder('{}/slice_{}'.format(prefix,slice_id))

def print_tp_after_affine(df :pd.DataFrame, prefix:{},slice_index:int):
    df.to_csv("{}/slice_{}/tissue_positions_list.csv".format(prefix,slice_index),
                     sep=',',
                     header=False,index=False)

def print_affine_slices_json(slices_info : {} , prefix: str,slice_id):
    filename="{}/slice_{}/slices.json".format(prefix,slice_id)
    sourceFile = open(filename, 'w')
    sourceFile.writelines(json.dumps(slices_info, sort_keys=False, indent=4, separators=(',', ':'),cls=General_Encoder))
    sourceFile.close()

###########################################################
# section5 : model3d
###########################################################
def init_model3d(prefix:str):
    create_a_folder(prefix)

def print_model3d(df :pd.DataFrame, prefix:str):
    df.to_csv("{}/model3d.csv".format(prefix),sep=',',header=True,index=False)


