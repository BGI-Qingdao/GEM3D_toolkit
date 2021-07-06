"""Draw function by plotly"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def anim2D_and_saveas_html( model :  np.ndarray , fname : str):
    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    fig = px.scatter(df,x='x',y='y',animation_frame='z',color='v',color_continuous_scale='hot')
    fig.write_html(fname)

def heat3D_and_saveas_html( model : np.ndarray , fname : str):
    df = pd.DataFrame(model , columns = ['x','y','z','v'])
    fig = px.scatter_3d(df,x='x',y='y',z='z',color='v',color_continuous_scale='hot')
    fig.update_scenes(aspectmode='data')
    fig.write_html(fname)
