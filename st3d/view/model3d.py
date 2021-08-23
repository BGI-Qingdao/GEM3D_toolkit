"""Draw function by plotly"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def html_model3d(df: pd.DataFrame,prefix:str):
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
        if ids < 9 :
            cluster_names.append("cluster_{}".format(ids))
        else :
            cluster_names.append("others")
    df['cluster_name']=cluster_names
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='cluster_name',color_discrete_map=color_discrete_map)
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

