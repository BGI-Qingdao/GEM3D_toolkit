import sys
import pandas as pd
import numpy as np
from skimage import io as skio
import getopt

#Usage
def prepare_alignment_image_usage():
    print(""""
Usage : prepare_alignment_image.py -m <mask.txt>
                                   -o <output.png>
                                   -t <celltype.csv>

Sample : prepare_alignment_image.py -m mask.txt \\
                                    -o output.png \\
                                    -t celltype.csv

Notice: celltype.csv should contain cell_id and cell_type columns with delimiter=",".
        cell_id should be the same integer in mask.txt;
        cell_type should be integers.

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
    type_info=pd.read_csv(cell_type)
    y,x = np.nonzero(cell_segment)
    max_celltype_id = type_info['cell_type'].max()
    draw_data = pd.DataFrame()
    draw_data['y'] = y
    draw_data['x'] = x
    draw_data['cell_id'] = cell_segment[y,x]
    draw_data_type=pd.merge(draw_data, type_info, on=['cell_id'], how='inner')
    draw_data_no_type=pd.concat([draw_data, draw_data_type, draw_data_type]).drop_duplicates(subset=["y","x",'cell_id'],keep=False)
    canvas = np.zeros((w,h,3),dtype='uint8')
    if max_celltype_id < 13 :
        draw_data_no_type["cell_type"]=np.array([int(13) for i in range(draw_data_no_type["x"].shape[0])])
    elif max_celltype_id < 84:
        draw_data_no_type["cell_type"]=np.array([int(83) for i in range(draw_data_no_type["x"].shape[0])])
    else:
        draw_data_no_type["cell_type"]=np.array([int(83) for i in range(draw_data_no_type["x"].shape[0])])
        print('Warning: there are too much celltypes (>84), some celltype may use the same color!',flush=True)

    draw_data=draw_data_type.append(draw_data_no_type)
    y=np.array(draw_data["y"])
    x=np.array(draw_data["x"])

    #Red    #FF0000 (255,0,0)
    #Lime	#00FF00	(0,255,0)
    #Blue	#0000FF	(0,0,255)
    #Yellow	#FFFF00	(255,255,0)
    #Cyan 	#00FFFF	(0,255,255)
    #Magent #FF00FF	(255,0,255)
    #Silver	#C0C0C0	(192,192,192)
    #Maroon	#800000	(128,0,0)
    #Navy	#000080	(0,0,128)
    #Green	#008000	(0,128,0)
    #Purple	#800080	(128,0,128)
    #Teal	#008080	(0,128,128)
    #Olive	#808000	(128,128,0)
    #Gray	#808080	(128,128,128)

    colors14 = [
            [255,0,0],
            [0,255,0],
            [0,0,255],
            [255,255,0],
            [0,255,255],
            [255,0,255],
            [192,192,192],
            [128,0,0],
            [0,0,128],
            [0,128,0],
            [128,0,128],
            [0,128,128],
            [128,128,0],
            [128,128,128]
    ]
    colors84 = [
            [96, 78, 151],
            [246, 166, 0],
            [179, 68, 108],
            [220, 211, 0],
            [136, 45, 23],
            [141, 182, 0],
            [101, 69, 34],
            [226, 88, 34],
            [43, 61, 38],
            [0, 0, 128],
            [100, 149, 237],
            [30, 144, 255],
            [0, 191, 255],
            [0, 255, 255],
            [255, 20, 147],
            [255, 0, 255],
            [160, 32, 240],
            [99, 184, 255],
            [0, 139, 139],
            [84, 255, 159],
            [0, 255, 0],
            [118, 238, 0],
            [255, 246, 143],
            [255, 255, 0],
            [255, 215, 0],
            [255, 185, 15],
            [255, 106, 106],
            [255, 255, 0],
            [28, 230, 255],
            [255, 52, 255],
            [255, 74, 70],
            [0, 137, 65],
            [0, 111, 166],
            [163, 0, 89],
            [255, 228, 225],
            [0, 0, 166],
            [99, 255, 172],
            [183, 151, 98],
            [0, 77, 67],
            [143, 176, 255],
            [153, 125, 135],
            [90, 0, 7],
            [128, 150, 147],
            [27, 68, 0],
            [79, 198, 1],
            [59, 93, 255],
            [255, 47, 128],
            [186, 9, 0],
            [107, 121, 0],
            [0, 194, 160],
            [255, 170, 146],
            [255, 144, 201],
            [185, 3, 170],
            [221, 239, 255],
            [123, 79, 75],
            [161, 194, 153],
            [10, 166, 216],
            [0, 160, 135],
            [77, 187, 213],
            [230, 75, 53],
            [60, 84, 136],
            [243, 132, 0],
            [161, 202, 241],
            [194, 178, 128],
            [132, 132, 130],
            [230, 143, 172],
            [0, 103, 165],
            [249, 147, 121],
            [255, 130, 71],
            [255, 165, 79],
            [255, 127, 36],
            [255, 48, 48],
            [255, 165, 0],
            [255, 127, 0],
            [255, 114, 86],
            [255, 99, 71],
            [255, 69, 0],
            [255, 20, 147],
            [255, 110, 180],
            [238, 48, 167],
            [139, 0, 139],
            [136, 136, 136],
            [25, 25, 112] ,
            [89,89,89],
        ]

    if max_celltype_id < 13:
        colors = np.array(colors14)
        draw_data['color_r'] = colors[(draw_data['cell_type']%14).astype(int).to_list(),0]
        draw_data['color_g'] = colors[(draw_data['cell_type']%14).astype(int).to_list(),1]
        draw_data['color_b'] = colors[(draw_data['cell_type']%14).astype(int).to_list(),2]
    else:
        colors = np.array(colors84)
        draw_data['color_r'] = colors[(draw_data['cell_type']%84).astype(int).to_list(),0]
        draw_data['color_g'] = colors[(draw_data['cell_type']%84).astype(int).to_list(),1]
        draw_data['color_b'] = colors[(draw_data['cell_type']%84).astype(int).to_list(),2]

    canvas[y,x,0] = draw_data['color_r']
    canvas[y,x,1] = draw_data['color_g']
    canvas[y,x,2] = draw_data['color_b'] 
    skio.imsave(prefix,canvas)
