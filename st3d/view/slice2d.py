import plotly.express as px
import numpy as np
import pandas as pd


def heatmap2D_and_saveas_html( model : np.ndarray , fname : str):
    fig = px.imshow(model)
    fig.write_html(fname)

def scatter2D_and_saveas_html( model : np.ndarray , fname : str):
    df = pd.DataFrame(model , columns = ['x','y','v'])
    fig = px.scatter(df,x='x',y='y',color='v',color_continuous_scale='Inferno')
    fig.write_html(fname)
