#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

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

### get all borders
def get_borders(model :pd.DataFrame)-> pd.DataFrame :
    slice_ids = np.unique(model['slice'])
    borders=pd.DataFrame(columns=model.columns)
    for x in slice_ids :
        one_slice = model[model['slice'] == x]
        borders=borders.append(get_border(one_slice),ignore_index=True)
    return borders

### load model3d
def load_model3d(filename : str) -> pd.DataFrame :
    df = pd.read_csv(filename,sep=",")
    df['x'] = df['x'].astype(int)
    df['x'] = df['x'] //10 
    df['y'] = df['y'].astype(int)
    df['y'] = df['y'] //10
    df['slice']=df['slice'].astype(int)
    return df

def anim2D_and_saveas_html( df , fname : str):
    fig = px.scatter(df,x='x',y='y',animation_frame='slice',range_x=(0,100),range_y=(0,100))
    fig.write_html(fname)

def heat3D_and_saveas_html(df  , fname : str):
    fig = px.scatter_3d(df,x='x',y='y',z='z')
    fig.update_scenes(aspectmode='data')
    fig.write_html(fname)
def mesh(df, fname):
    fig = go.Figure(data=[go.Mesh3d(x=df['x'], y=df['y'], z=df['z'])])
    fig.write_html(fname)

### main
def main(argv:[]):
    df = load_model3d(argv[0])
    borders = get_borders(df)
    print(borders.head())
    borders.to_csv('mesh.csv',index=False)
    anim2D_and_saveas_html(borders,'test01.html')
    heat3D_and_saveas_html(borders,'test02.html')
    mesh(borders,'mesh.html')

if __name__ == "__main__":
    main(sys.argv[1:])
