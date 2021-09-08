import numpy as np
import pandas as pd
from st3d.control.save_miscdf import create_a_folder


def mask_xy_affine(affines,mask_xy_map,prefix):
    xyz = pd.DataFrame(columns=['x','y','z'])

    create_a_folder(prefix)
    for slice_id in affines:
        mask_xyz = mask_xy_map[slice_id]
        mask_xyz['a'] = np.ones(len(mask_xyz),dtype=int)
        this_xyz = mask_xyz[['x','y','z','a']].to_numpy()
        this_affine = affines[slice_id]
        new_xyz = np.matmul(this_affine.I ,this_xyz.T)
        new_xyz = new_xyz[0:3: ,:]
        xyz = xyz.append(pd.DataFrame(new_xyz, columns=xyz.columns), ignore_index=True)
    xyz['x'] = xyz['x'].astype(int)
    xyz['y'] = xyz['y'].astype(int)
    xyz['z'] = xyz['z'].astype(int)
    xyz.to_csv("{}/mask_xyz.csv".format(prefix),sep=',',header=True,index=False)

