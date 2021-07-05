import os
import json
from json import JSONEncoder
import numpy as np
import pandas as pd

from st3d.model.rect_bin import *

class General_Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def init_outputs(prefix : str):
    if os.path.exists(prefix):
        print("output path {} exist ! exit ...".format(prefix))
        exit(101)
    os.mkdir(prefix)
    if not os.path.exists(prefix):
        print("create output path {}  failed! exit ...".format(prefix))
        exit(102)
    os.mkdir(os.path.join(prefix,"raw_feature_bc_matrix"))
    os.mkdir(os.path.join(prefix,"spatial"))
    os.mkdir(os.path.join(prefix,"heatmap"))

def save_3D_heatmap( data : np.ndarray , filename :str) :
    df = pd.DataFrame(data, columns = ['x','y','z','v'])
    df.to_csv(filename)


def save_new_gem(foldname:str):
    # 
    print("TODO")

def print_features_tsv(gene_names : [] , prefix:str):
    filename="{}/raw_feature_bc_matrix/features.tsv".format(prefix)
    sourceFile = open(filename, 'w')
    for items in gene_names:
        sourceFile.writelines(items+'\n')
    sourceFile.close()

def print_barcodes_tsv(bin_ids: bins_of_slices , prefix:str):
    filename="{}/raw_feature_bc_matrix/barcodes.tsv".format(prefix)
    sourceFile = open(filename, 'w')
    for key in bin_ids.slices.keys():
        bos = bin_ids.get_slice(key)
        for abin in bos.bins:
            sourceFile.writelines(abin.bin_name+'\n')
    sourceFile.close()

def print_matrix_mtx(mtx,prefix,gnum,bnum):
    filename="{}/raw_feature_bc_matrix/matrix.mtx".format(prefix)
    sourceFile = open(filename, 'w')
    sourceFile.writelines(
"""%%MatrixMarket matrix coordinate integer general
%metadata_json: {"software_version": "Cell Ranger 4", "format_version": 2}
""")
    sourceFile.writelines("{} {} {}\n".format(gnum,bnum,len(mtx)))
    for _, row in mtx.iterrows():
        sourceFile.writelines("{} {} {}\n".format(row['gid'],row['bid'],row['count']))
    sourceFile.close()

def print_tissue_positions_list(bin_ids : bins_of_slices , prefix:str):
    filename="{}/spatial/tissue_positions_list.csv".format(prefix)
    sourceFile = open(filename, 'w')
    for key in bin_ids.slices.keys():
        bos = bin_ids.get_slice(key)
        for abin in bos.bins:
            sourceFile.writelines("{},{},{},{},-1,-1,{},-1,-1,-1\n".format(abin.bin_name,
                                                                           int(abin.valid),
                                                                           int(abin.spot_x),
                                                                           int(abin.spot_y),
                                                                           abin.slice_id
                                                                           ))
    sourceFile.close()

def print_slices_json(slices_info : {} , prefix: str):
    filename="{}/spatial/slices.json".format(prefix)
    sourceFile = open(filename, 'w')
    sourceFile.writelines(json.dumps(slices_info, sort_keys=False, indent=4, separators=(',', ':'),cls=General_Encoder))
    sourceFile.close()

