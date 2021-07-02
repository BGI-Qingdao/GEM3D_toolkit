"""Interfaces for loading slices"""

#from st3d.control.global_instances import load_slice
from st3d.model.slices_manager import slices_manager
import numpy as np

def load_slices(files : [] ):
    slices = slices_manager()
    for one_file in files:
        slices.add_slice(one_file[0],one_file[1])
    return slices

def build_genes_ids( data : slices_manager):
    uniq_gene_ids = slices_manager.get_uniq_genes()
    gene_ids={}
    for index, name in enumerate(uniq_gene_ids):
        gene_ids[name]=index
    return gene_ids
