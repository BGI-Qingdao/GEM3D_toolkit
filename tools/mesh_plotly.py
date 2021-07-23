import pandas as pd
import plotly.graph_objects as go


xyz = pd.read_csv('xyz.csv',sep=" ",dtype=float)
ijk = pd.read_csv('ijk.csv',sep=" ",dtype=int)
fig = go.Figure(data=[go.Mesh3d(x=xyz.x, y=xyz.y, z=xyz.z, color='grey', opacity=0.50,i=ijk.i,j=ijk.j,k=ijk.k)])
fig.write_html('mesh.html')
