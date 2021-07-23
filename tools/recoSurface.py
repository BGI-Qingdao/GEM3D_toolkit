import numpy as np
import pandas as pd
from vedo import *
import plotly.express as px
import plotly.graph_objects as go

#################################################
# load data
# 
data=np.loadtxt('mesh.txt',dtype=int)
print(data.shape)
pts0= Points(data)

#################################################
# recoSurface
# 
reco = recoSurface(pts0,radius=35).legend("surf. reco")
reco = reco.extractLargestRegion()
reco = reco.clone().smoothWSinc(niter=20, passBand=0.1, edgeAngle=15, featureAngle=60)
reco = reco.decimate(fraction=0.01)

#################################################
# save mesh
# 
io.write(reco,'reco.ply',binary=False)

#################################################
# display
# 
plt = Plotter(N=2, axes=0)
plt.show(Points(reco.points()), at=0)
plt.show(reco, at=1, axes=7, interactive=1).close()

