import sys
import pandas as pd
import numpy as np
from skimage import io as skio
import getopt

#Usage
def prepare_alignment_image_usage():
    print(""""
Usage : prepare_alignment_image.py -m <mask.txt>
                                   -o <output.tif>
                                   -t <celltype.csv>
Sample : prepare_alignment_image.py -m mask.txt \\
                                    -o output.tif \\
                                    -t celltype.csv
    """,flush=True)

def prepare_alignment_image_main(argv : []):
    infile=''
    prefix=''
    cell_type=''
    try:
        opts , args = getopt.getopt(argv,"hm:o:t:",["help=","mask=","output=","celltype="])
    except getopt.GetoptError:
        prepare_alignment_image_usage()
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ("-h","--help"):
            prepare_alignment_image_usage()
            sys.exit(0)
        elif opt in ("-m","--mask"):
            infile = arg
        elif opt in ("-o","--output"):
            prefix = arg
        elif opt in ("-t","--celltype"):
            cell_type = arg

    if infile == "" or prefix == "" or cell_type == "":
        prepare_alignment_image_usage()
        sys.exit(2)
    cell_segment=np.loadtxt(infile,delimiter=' ')
    w,h=cell_segment.shape
    type=pd.read_csv(cell_type)

    y,x = np.nonzero(cell_segment)

    draw_data = pd.DataFrame()
    draw_data['y'] = y
    draw_data['x'] = x
    draw_data['cell_id'] = cell_segment[y,x]
    draw_data_type=pd.merge(draw_data, type, on=['cell_id'], how='inner')
    draw_data_no_type=pd.concat([draw_data, draw_data_type, draw_data_type]).drop_duplicates(subset=["y","x",'cell_id'],keep=False)
    canvas = np.zeros((w,h,3),dtype='uint8')
    draw_data_no_type["cell_type"]=np.array([int(125) for i in range(draw_data_no_type["x"].shape[0])])
    draw_data=draw_data_type.append(draw_data_no_type)
    y=np.array(draw_data["y"])
    x=np.array(draw_data["x"])
    
    colors = [ '#e6194b', '#3cb44b', '#ffe119', '#4363d8',
            '#f58231', '#911eb4', '#46f0f0', '#f032e6',
            '#bcf60c', '#fabebe', '#008080', '#e6beff',
            '#9a6324', '#fffac8', '#800000', '#aaffc3', 
            '#808000', '#ffd8b1', '#000075', '#808080', 
            '#ffffff', '#000000']

    colors = [
            [255,0,0],
            [0,255,0],
            [0,0,255],
            [255,255,0],
            [0,255,255],
            [255,0,255],
            [192,192,192],
            [128,128,128],
            [128,0,0],
            [0,0,128],
            [0,128,0],
            [128,0,128],
            [0,128,128],
            [128,128,128]
    ]

    #Red    #FF0000 (255,0,0)
    #Lime	#00FF00	(0,255,0)
    #Blue	#0000FF	(0,0,255)
    #Yellow	#FFFF00	(255,255,0)
    #Cyan 	#00FFFF	(0,255,255)
    #Magent #FF00FF	(255,0,255)
    #Silver	#C0C0C0	(192,192,192)
    #Gray	#808080	(128,128,128)
    #Maroon	#800000	(128,0,0)
    #Olive	#808000	(128,128,0)
    #Green	#008000	(0,128,0)
    #Purple	#800080	(128,0,128)
    #Teal	#008080	(0,128,128)
    #Navy	#000080	(0,0,128)
    colors = np.array(colors)
    draw_data['color_r'] = colors[(draw_data['cell_type']%14).astype(int).to_list(),0]
    draw_data['color_g'] = colors[(draw_data['cell_type']%14).astype(int).to_list(),1]
    draw_data['color_b'] = colors[(draw_data['cell_type']%14).astype(int).to_list(),2]

    canvas[y,x,0] = draw_data['color_r']
    canvas[y,x,1] = draw_data['color_g']
    canvas[y,x,2] = draw_data['color_b'] 
    skio.imsave(prefix,canvas)
