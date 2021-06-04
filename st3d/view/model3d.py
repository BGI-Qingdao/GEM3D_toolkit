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


def heat3D_and_saveas_html( model : np.ndarray , borders : [] , fname : str):

    df = pd.DataFrame(model , columns = ['x','y','z','v'])

    fig = px.scatter_3d(df,x='x',y='y',z='z',color='v',color_continuous_scale='Inferno')

    for bs in borders:
        fig.add_trace(go.Scatter3d(x=bs[:,0],
                                   y=bs[:,1], 
                                   z=bs[:,2],
                                   mode='lines'))

    #fig.update_traces( marker_line_width=2, marker_size=1)
    fig.write_html(fname)
