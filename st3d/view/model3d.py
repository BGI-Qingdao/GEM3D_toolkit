"""Draw function by plotly"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def html_model3d(df: pd.DataFrame,prefix:str, downsize=4):
    # discrete color map
    color25={
        'cluster_0' : '#1C86EE' ,
        'cluster_1' : '#E31A1C' ,
        'cluster_2' : '#008B00' ,
        'cluster_3' : '#6A3D9A' ,
        'cluster_4' : '#FF7F00' ,
        'cluster_5' : '#000000' ,
        'cluster_6' : '#FFD700' ,
        'cluster_7' : '#7EC0EE' ,
        'cluster_8' : '#FB9A99' ,
        'cluster_9' : '#90EE90' ,
        'cluster_10' : '#CAB2D6',
        'cluster_11' : '#FDBF6F',
        'cluster_12' : '#B3B3B3',
        'cluster_13' : '#EEE685',
        'cluster_14' : '#B03060',
        'cluster_15' : '#FF83FA',
        'cluster_16' : '#FF1493',
        'cluster_17' : '#0000FF',
        'cluster_18' : '#36648B',
        'cluster_19' : '#00CED1',
        'cluster_20' : '#00FF00',
        'cluster_21' : '#8B8B00',
        'cluster_22' : '#CDCD00',
        'cluster_23' : '#8B4500',
        'others' : '#A52A2A'
    }
    # create labels
    cluster_names = []
    for ids in df['cluster']:
        if ids < 24 :
            cluster_names.append("cluster_{}".format(ids))
        else :
            cluster_names.append("others")
    df['cluster_name']=cluster_names

    # draw cells as scatters in 3D space
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='cluster_name',color_discrete_map=color25)
    marker_size=int(downsize/2)
    if marker_size < 1 :
        marker_size = 1
    for i in range(0,len(fig.data)):
        fig.data[i].update(marker_size=marker_size)


    # prepare volumn
    x1 = np.linspace( int(df['x'].min()),
                      int(df['x'].max()),
                     (int(df['x'].max())-int(df['x'].min()))//downsize+1)
    y1 = np.linspace( int(df['y'].min()),
                      int(df['y'].max()),
                     (int(df['y'].max())-int(df['y'].min()))//downsize+1)
    z1 = np.linspace( int(df['z'].min()),
                      int(df['z'].max()),
                     (int(df['z'].max())-int(df['z'].min()))//downsize+1)
    X, Y, Z = np.meshgrid(x1, y1, z1)
    # mask valid points
    values= np.zeros(X.shape)
    print(values.shape)
    for _ , row in df.iterrows():
        values[int(row['y']//downsize),int(row['x']//downsize),int(row['z']//downsize)] = 0.5

    # draw a surface
    fig.add_trace(go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=values.flatten(),
        opacity=0.1,
        colorscale='Greys',
        isomin=0.45,
        isomax=0.55,
        surface_count=3,
        showscale=False, # remove colorbar
    ))

    fig.update_scenes(aspectmode='data')
    fig.write_html("{}/model3d.html".format(prefix))

def anim2D_and_saveas_html( model :  np.ndarray , fname : str):
    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    fig = px.scatter(df,x='x',y='y',animation_frame='z',color='v',color_continuous_scale='hot')
    fig.write_html(fname)

def heat3D_and_saveas_html( model : np.ndarray , fname : str):
    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='v',color_continuous_scale='hot')
    fig.update_scenes(aspectmode='data')
    fig.write_html(fname)

def scatter_3d_html(all_points: pd.DataFrame, fname :str):
    if len(all_points) > 10000:
        frac=10000/len(all_points)
        all_points=all_points.sample(frac=frac, replace=True, random_state=1)
    fig = px.scatter_3d(all_points,x='3d_x',y='3d_y',z='3d_z')
    fig.data[0].update(marker_size=1)
    fig.update_scenes(aspectmode='data')
    fig.write_html(fname)

