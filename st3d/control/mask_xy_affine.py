import numpy as np
import pandas as pd

def mask_xy_affine(affines,mask_xy_map,prefix):
    xyz = pd.DataFrame(columns=['x','y','z'])

    for slice_id in affines:
        mask_xyz = mask_xy_map[slice_id]
        mask_xyz['a'] = np.ones(len(mask_xyz),dtype=int)
        this_xyz = np.mask_xyz[['x','y','z','a']].to_numpy()
        this_affine = affines[slice_id]
        new_xyz = np.matmul(this_affine.I ,this_xyz.T)
        new_xyz = new_xyz1[0:3: ,:]
        xyz = df.append(pd.DataFrame(new_xyz, columns=xyz.columns), ignore_index=True)
    xyz.to_csv("{}/mask_xyz.csv".format(prefix),sep=',',header=True,index=False)

