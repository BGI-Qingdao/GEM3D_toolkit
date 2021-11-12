import numpy as np
import pandas as pd
from vedo import *
import plotly.express as px
import plotly.graph_objects as go

#################################################
# load data
# 
data=np.loadtxt('mesh.txt',dtype=int,delimiter=' ')
print(data.shape)
pts0= Points(data)

#################################################
# recoSurface
#
pts0 = pts0.clone().smoothMLS2D(f=1.5)
reco = recoSurface(pts0,radius=30)

reco = reco.extractLargestRegion()
reco = reco.fillHoles()
#reco = reco.decimate(fraction=0.2)
reco = reco.smoothLaplacian()
reco = reco.smoothLaplacian()
reco = reco.smoothLaplacian()
#reco = reco.clone().smoothWSinc(niter=20, passBand=0.1, edgeAngle=15, featureAngle=60)
#reco = reco.clone().smoothWSinc(niter=20, passBand=0.1, edgeAngle=15, featureAngle=60)
#reco = reco.decimate(fraction=0.05)

#################################################
# save mesh
# 
io.write(reco,'reco.ply',binary=False)

#################################################
# display
# 
plt = Plotter(N=1, axes=0)
#plt.show(Points(reco.points()), at=0)
plt.show(reco, at=0, axes=7, interactive=1).close()

