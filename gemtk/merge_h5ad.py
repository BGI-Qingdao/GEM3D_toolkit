import anndata
import os 
import sys
import getopt
import pandas as pd
#Usage
def merge_h5ad_usage():
    print("""
Usage : merge_h5ad.py    -i  <filepath>
                         -o  <output>
    """,flush=True)

def merge_h5ad_main(argv:[]):
    filepath=''
    prefix=''
    try:
        opts , args =getopt.getopt(argv,"hi:o:",["help=","input=","output="])
    except getopt.GetoptError:
        merge_h5ad_usage()
        sys.exit(2)
    for opt, arg in opts :
        if opt in ("-h","--help"):
            merge_h5ad_usage()
            sys.exit(0)
        elif opt in ("-i","--input"):
            filepath= arg 
        elif opt in ("-o","--output"):
            prefix = arg
    if filepath =="" or prefix =="":
        merge_h5ad_usage()
        sys.exit(0)
    files=[h5ad for h5ad in os.listdir(filepath) if '.h5ad' in h5ad]
    for i in range(len(files)):
        try:
            data=anndata.read(filepath+files[i])
        except:
            data=anndata.read(filepath+'/'+files[i])
        data.obs.index=pd.DataFrame(data.obs.index)[0].apply(lambda x : 'm'+str(i)+'_'+str(x))
        data.obs.index.name='m'+str(i)
        if i==0:
            h5admerge=data
        else:
            h5admerge=h5admerge.concatenate(data)
    h5admerge.write(f'{prefix}_merged.h5ad',compression='gzip')
