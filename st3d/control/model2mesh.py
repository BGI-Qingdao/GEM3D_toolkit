import pandas as pd
import numpy as np

from st3d.view.slice2d import *
from st3d.control.save_miscdf import create_a_folder
from vedo import *

def waterflow_from( y_index , x_index , markers, xmax , ymax):
    if markers[y_index,x_index] != 0 :
        return
    next_list = [[y_index,x_index]]
    markers[y_index,x_index]=2
    while len(next_list) > 0 :
        new_next_list = []
        for x in next_list:
            y_id , x_id = x
            if x_id > 0 and  markers[y_id,x_id-1] == 0 :
                new_next_list.append([y_id,x_id-1])
                markers[y_id,x_id-1]=2
            if x_id < xmax-1 and markers[y_id,x_id+1] == 0 : 
                new_next_list.append([y_id,x_id+1])
                markers[y_id,x_id+1]=2
            if y_id > 0 and  markers[y_id-1,x_id] == 0 :
                new_next_list.append([y_id-1,x_id])
                markers[y_id-1,x_id]=2
            if y_id < ymax-1 and markers[y_id+1,x_id] == 0 : 
                new_next_list.append([y_id+1,x_id])
                markers[y_id+1,x_id]=2
        next_list = new_next_list
    return

class tight_xyz:
    def __init__(self, df:pd.DataFrame,downsize:int):
        df = df.copy()
        self.x_min = int(df['x'].min()) -downsize
        self.x_max = int(df['x'].max()) +downsize
        self.y_min = int(df['y'].min()) -downsize 
        self.y_max = int(df['y'].max()) +downsize
        self.downsize = downsize
        df['x'] = df['x'] - self.x_min
        df['x'] = df['x'] //downsize
        df['y'] = df['y'] - self.y_min
        df['y'] = df['y'] //downsize
        self.df = df
        self.slice_width  = int((self.x_max-self.x_min+1)//self.downsize)
        self.slice_height = int((self.y_max-self.y_min+1)//self.downsize)

    def tight_masks(self,slice_z : int) ->pd.DataFrame:
        markers = np.zeros((self.slice_height,self.slice_width))
        df = self.df[self.df['z']==slice_z]
        markers[df['y'],df['x']]=1
        return markers

    def get_marker_border(self,markers :np.ndarray) :
        # scan by x axes
        for j in range(1,self.slice_height-1):
            for i in range(1,self.slice_width-1):
                if markers[j][i] == 1 and markers[j][i-1]==2 :
                    markers[j][i] =3
                elif markers[j][i] == 1 and markers[j][i+1]==2 :
                    markers[j][i] =3
                elif markers[j][i] == 1 and markers[j-1][i]==2 :
                    markers[j][i] =3
                elif markers[j][i] == 1 and markers[j+1][i]==2 :
                    markers[j][i] =3
        return np.where(markers == 3)

    def reset_xyz(self, x_ids, y_ids,slice_z) ->pd.DataFrame:
        df = pd.DataFrame()
        df['x']=x_ids
        df['y']=y_ids
        df['z']=np.ones(len(df),dtype=int)*slice_z
        df['x']=df['x']*self.downsize
        df['x']+=self.x_min - self.downsize
        df['y']=df['y']*self.downsize
        df['y']+=self.y_min - self.downsize
        return df


    def get_border(self,slice_z : int,prefix:str) ->pd.DataFrame:
        markers = self.tight_masks(slice_z)
        for x in range(0,self.slice_width):
            waterflow_from(0,x,markers,self.slice_width,self.slice_height)
            waterflow_from(self.slice_height-1,x,markers,self.slice_width,self.slice_height)
        for y in range(0,self.slice_height):
            waterflow_from(y,0,markers,self.slice_width,self.slice_height)
            waterflow_from(y,self.slice_width-1,markers,self.slice_width,self.slice_height)
        #draw_slice_cluster("{}/slice_{}.png".format(prefix,slice_z),markers)
        y_ids ,x_ids = self.get_marker_border(markers)
        return self.reset_xyz(x_ids,y_ids,slice_z)

### get all borders
def get_borders(model :pd.DataFrame,downsize:int,prefix)-> pd.DataFrame :
    tightxyz = tight_xyz(model,downsize)
    slice_ids = np.unique(model['z'])
    borders=pd.DataFrame(columns=model.columns)
    min_z = np.min(slice_ids)
    max_z = np.max(slice_ids)
    for x in slice_ids :
        one_slice = model[model['z'] == x]
        if x == min_z or x == max_z :
            borders=borders.append(one_slice,ignore_index=True)
        else :
            borders=borders.append(tightxyz.get_border(x,prefix),ignore_index=True)
    return borders

def model2mesh(xyz : pd.DataFrame , prefix :str , downsize :int, radius=35 , visual = False , factor='0.1',smooth=False):
    xyz['x'] = xyz['x'].astype(int)
    xyz['y'] = xyz['y'].astype(int)
    xyz['z'] = xyz['z'].astype(int)
    create_a_folder(prefix)
    borders = get_borders(xyz,downsize,prefix)
    borders.to_csv('{}/borders.xyz'.format(prefix),index=False)
    anim2D_and_saveas_html(borders,'{}/borders.html'.format(prefix))

    pts0= Points(borders.to_numpy())
    if smooth:
        pts0 = pts0.clone().smoothMLS2D(f=1.5)
    reco = recoSurface(pts0,radius=radius)
    reco = reco.extractLargestRegion()
    reco = reco.clone().decimate(fraction=factor)
    if smooth:
        reco = reco.clone().fillHoles()
        reco = reco.clone().smoothLaplacian()
        reco = reco.clone().smoothLaplacian()
        reco = reco.clone().smoothLaplacian()
    io.write(reco,'{}/surface.ply'.format(prefix),binary=False)
    if  visual:
        plt = Plotter(N=1, axes=0)
        plt.show(reco, at=0, axes=7, interactive=1).close()
