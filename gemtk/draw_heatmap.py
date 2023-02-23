import numpy as np
import pandas as pd
import getopt
import sys 
from skimage import io as skio
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colors
from gemtk.slice_dataframe import format_colname
def heatmap_usage():
    print("""
Usage : heatmap.py -i <input gem>
                   -o <output.tif/output.png>
                   -l [gene.list, default all genes]
                   -c [cmap name, default RdBu_r]
                   -x [xmin, default gem.x.min()] 
                   -y [ymin. default gem.y.min()]
                   -W [width, defait gem.x.max()-x+1]
                   -H [height, defait gem.y.max()-y+1]
    """,flush=True)

def heatmap_main(argv:[]):
    infile=''
    prefix=''
    genelist=''
    X=''
    Y=''
    W=''
    H=''
    cmap_name = 'RdBu_r'
    try:
        opts,args=getopt.getopt(argv,"hi:o:l:x:y:c:W:H:",["help=","intput=","output=","list="])
    except getopt.GetoptError:
        heatmap_usage()
        sys.exit(2)
    
    for opt ,arg in opts:
        if opt in ("-h","--help"):
            heatmap_usage()
            sys.exit(0)
        elif opt in ('-i',"--help"):
            infile = arg
        elif opt in ("-o","--output"):
            prefix = arg
        elif opt in ("-l","--list"):
            genelist= arg
        elif opt == '-c':
            cmap_name = arg
        elif opt in ('-x'):
            # -x must be int 
            X = int(arg) 
        elif opt in ('-y'):
            # -x must be int 
            Y = int(arg)
        elif opt in ('-W'):
            W = int(arg)
        elif opt in ('-H'):
            H = int(arg)

    if infile == ''  or prefix =='':
        heatmap_usage()
        sys.exit(2)
    
    draw =pd.read_csv(infile,comment="#",sep='\t')
    draw.columns=format_colname(draw) #['geneID','x','y','MIDCounts','ExonCount']
    # calculate xmin ymin before subset them!!!
    draw["x"] = draw["x"].astype(int)
    draw["y"] = draw["y"].astype(int)
    if X=='': 
        X=np.min(draw["x"])
    if Y=='':
        Y=np.min(draw["y"])
    draw["y"] = draw["y"] - Y
    draw["x"] = draw["x"] - X    
    draw["x"] = draw["x"].astype(int)
    draw["y"] = draw["y"].astype(int)
    if W == '':
        W=np.max(draw["x"])+1
    if H == '':
        H=np.max(draw["y"])+1

    if genelist != '':
        # filter data by gene list
        gene_list=pd.read_csv(genelist,header=None)
        gene_list.columns=["geneid"]
        draw=draw[draw['geneID'].isin(gene_list['geneid'])].copy()
        
    # merge all valid genes here.
    draw.groupby(['x','y']).sum().reset_index()
    # normalise count range from 0 - 255
    countMin = draw["MIDCounts"].min()
    countMax = draw["MIDCounts"].max()
    print(f'gene exp range [{countMin}, {countMax}]',flush=True)
    draw["MIDCounts"] = (draw["MIDCounts"]*255)/countMax
    draw["MIDCounts"] = draw["MIDCounts"].astype(int)
    
    # create colorlist from cmap
    cmap = plt.get_cmap(cmap_name)
    color_list = np.zeros((266,3),dtype=int)
    for i in range(266):
        x = (np.array(cmap(i)) * 255).astype(int)
        color_list[i,:] = x[:3]
  
    draw['color_r'] = color_list[(draw['MIDCounts']).to_list(),0]
    draw['color_g'] = color_list[(draw['MIDCounts']).to_list(),1]
    draw['color_b'] = color_list[(draw['MIDCounts']).to_list(),2]

    canvas = np.zeros((H,W,3),dtype='uint8')
    canvas[draw['y'],draw['x'],0] = draw['color_r']
    canvas[draw['y'],draw['x'],1] = draw['color_g']
    canvas[draw['y'],draw['x'],2] = draw['color_b']
    skio.imsave(prefix,canvas)
