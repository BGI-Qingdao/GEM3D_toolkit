import pandas as pd
import numpy as np

from st3d.view.slice2d import *
from st3d.control.save_miscdf import create_a_folder
from vedo import *

### get border of one slice
def get_border(one_slice : pd.DataFrame )->pd.DataFrame :
    x_min = one_slice['x'].min()
    x_max = one_slice['x'].max()
    y_min = one_slice['y'].min()
    y_max = one_slice['y'].max()
    slice_width=x_max+1
    slice_height = y_max+1
    markers = np.zeros((slice_height+5,slice_width+5))
    status  = np.zeros((slice_height+5,slice_width+5))
    for _ , row in one_slice.iterrows():
        markers[row['y']][row['x']] = 1
    # scan by x axes
    for j in range(slice_height):
        curr=0
        for i in range(slice_width):
            if curr ==0 :
                if markers[j][i] == 1 and markers[j][i+1]==1 and markers[j][i+2]==1 and markers[j][i+3]==1  :
                    status[j][i] =1
                    curr =1
            else :
                if markers[j][i] == 1 and markers[j][i+1]==0 and markers[j][i+2]==0 and markers[j][i+3]==0 :
                    status[j][i] =1
                    curr = 0

    # scan by y axes
    for i in range(slice_width):
        curr=0
        for j in range(slice_height):
            if curr ==0 :
                if markers[j][i] == 1 and markers[j+1][i]==1 and  markers[j+2][i]==1 and  markers[j+3][i]==1 :
                    status[j][i] +=1 
                    curr =1
            else :
                if markers[j][i] == 1 and markers[j+1][i]==0 and markers[j+2][i]==0 and markers[j+3][i]==0  :
                    status[j][i] +=1
                    curr = 0

    # return border points
    borders=pd.DataFrame(columns=one_slice.columns)
    for _, row in one_slice.iterrows():
        if status[row['y']][row['x']] > 0 :
            #print(row)
            borders=borders.append(row, ignore_index=True)
    return borders

def prepare_xyz(df:pd.DataFrame,downsize:int) -> pd.DataFrame :
    df['x'] = df['x'] //downsize
    df['x'] = df['x'].astype(int)
    df['y'] = df['y'] //downsize
    df['y'] = df['y'].astype(int)
    df['z'] = df['z'].astype(int)
    return df

### get all borders
def get_borders(model :pd.DataFrame,downsize:int)-> pd.DataFrame :
    model=prepare_xyz(model,downsize)
    slice_ids = np.unique(model['z'])
    borders=pd.DataFrame(columns=model.columns)
    min_z = np.min(slice_ids)
    max_z = np.max(slice_ids)
    for x in slice_ids :
        one_slice = model[model['z'] == x]
        if x == min_z or x == max_z :
            borders=borders.append(one_slice,ignore_index=True)
        else :
            borders=borders.append(get_border(one_slice),ignore_index=True)
    borders['x'] = borders['x']*downsize
    borders['y'] = borders['y']*downsize
    return borders


def model2mesh(xyz : pd.DataFrame , prefix :str , downsize :int, radius=35 , visual = False , factor='0.1'):
    create_a_folder(prefix)
    borders = get_borders(xyz,downsize)
    borders.to_csv('{}/borders.xyz'.format(prefix),index=False)
    anim2D_and_saveas_html(borders,'{}/borders.html'.format(prefix))

    pts0= Points(borders.to_numpy())
    pts0 = pts0.clone().smoothMLS2D(f=1.5)
    reco = recoSurface(pts0,radius=radius)
    reco = reco.extractLargestRegion()
    reco = reco.clone().fillHoles()
    reco = reco.clone().smoothLaplacian()
    reco = reco.clone().smoothLaplacian()
    reco = reco.clone().smoothLaplacian()
    reco = reco.clone().decimate(fraction=factor)
    io.write(reco,'{}/surface.ply'.format(prefix),binary=False)
    if  visual == True :
        plt = Plotter(N=1, axes=0)
        plt.show(reco, at=0, axes=7, interactive=1).close()

