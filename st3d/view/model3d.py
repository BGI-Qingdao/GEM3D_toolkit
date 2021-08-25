"""Draw function by plotly"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def html_model3d(df: pd.DataFrame,prefix:str):
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
    color18={ 'cluster_0':'#c51b7d',
           'cluster_1':'#de77ae',
           'cluster_2':'#f1b6da',
           'cluster_3':'#fde0ef',
           'cluster_4':'#f7f7f7',
           'cluster_5':'#e6f5d0',
           'cluster_6':'#b8e186',
           'cluster_7':'#7fbc41',
           'cluster_8':'#4d9221',
           'cluster_9':'#d53e4f',
           'cluster_10':'#f46d43',
           'cluster_11':'#fdae61',
           'cluster_12':'#fee08b',
           'cluster_13':'#ffffbf',
           'cluster_14':'#e6f598',
           'cluster_15':'#abdda4',
           'cluster_16':'#66c2a5',
           'others':'#3288bd'}
    color_discrete_map= {'cluster_0': px.colors.qualitative.Plotly[0],
                     'cluster_1': px.colors.qualitative.Plotly[1],
                     'cluster_2': px.colors.qualitative.Plotly[2],
                     'cluster_3': px.colors.qualitative.Plotly[3],
                     'cluster_4': px.colors.qualitative.Plotly[4],
                     'cluster_5': px.colors.qualitative.Plotly[5],
                     'cluster_6': px.colors.qualitative.Plotly[6],
                     'cluster_7': px.colors.qualitative.Plotly[7],
                     'cluster_8': px.colors.qualitative.Plotly[8],
                     'others':    px.colors.qualitative.Plotly[9]
                     }
    cluster_names = []
    for ids in df['cluster']:
        if ids < 24 :
            cluster_names.append("cluster_{}".format(ids))
        else :
            cluster_names.append("others")
    df['cluster_name']=cluster_names
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='cluster_name',color_discrete_map=color25)#color_discrete_map)
    for i in range(0,len(fig.data)):
        fig.data[i].update(marker_size=1)
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

