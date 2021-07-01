"""Draw function by plotly"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def mask3D_and_saveas_html( model : np.ndarray , borders : [] , fname : str):
    fig = go.Figure(data=[go.Scatter3d(x=model[:,0], y=model[:,1], z=model[:,2],
                                   mode='markers',marker_size=1, marker_color='black')])
    for bs in borders:
        fig.add_trace(go.Scatter3d(x=bs[:,0],y=bs[:,1], z=bs[:,2],mode='lines'))
    fig.write_html(fname)

def anim2D_and_saveas_html( model :  np.ndarray , fname : str):

    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    fig = px.scatter(df,x='x',y='y',animation_frame='z',color='v',color_continuous_scale='hot')
    fig.write_html(fname)

def heat3D_and_saveas_html( model : np.ndarray , borders : [] , fname : str):

    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    df.to_csv('file2.csv')
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='v',color_continuous_scale='hot')
    fig.update_scenes(aspectmode='data')

    #for bs in borders:
    #    fig.add_trace(go.Scatter3d(x=bs[:,0],
    #                               y=bs[:,1], 
    #                               z=bs[:,2],
    #                               mode='lines'))

    #fig.update_traces( marker_line_width=2, marker_size=1)
    fig.write_html(fname)

def tab2_and_saveas_html( model : np.ndarray ,fname : str):
    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    df.to_csv('file1.csv')
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='v',color_continuous_scale='hot')
    fig.update_scenes(aspectmode='data')
    # Add dropdown
    fig.update_layout(
        updatemenus=[
            dict(
                type = "buttons",
                direction = "left",
                buttons=list([
                    dict(
                        args=[{"type": "Scatter3d", 'z':df['z']}],
                        #       'scatter_3d.z':'z',
                        #       'scatter_3d.y':'y',
                        #       'scatter_3d.z':'z',
                        #       'scatter_3d.color_continuous_scale':'hot'}],
                        label="3D Scatter",
                        method="restyle"
                     ),
                    dict(
                        args=["type", "scatter"],
                        #       'scatter.animation_frame':'z',
                        #       'scatter.y':'y',
                        #       'scatter.z':'z',
                        #       'scatter.color_continuous_scale':'hot'}],
                        label="2D slice",
                        method="restyle"
                    )
                 ]),
                 pad={"r": 10, "t": 10},
                 showactive=True,
                 x=0.11,
                 xanchor="left",
                 y=1.1,
                 yanchor="top"
            ),
        ])
    fig.write_html(fname)
