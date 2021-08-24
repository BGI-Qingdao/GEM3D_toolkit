import pandas as pd

from st3d.control.save_miscdf import print_model3d,init_model3d
from st3d.view.model3d import html_model3d

def segmentbfm(  segmentations : pd.DataFrame, input_folder : str ,  prefix : str ):
    model3d = pd.read_csv( '{}/model3d.csv'.format(input_folder), sep=',' )
    names = segmentations.columns
    names = names.tolist()
    for name in names:
        model3d_new = model3d[
                (model3d['x']>segmentations.loc['min-x',name]) &  
                (model3d['x']<segmentations.loc['max-x',name]) &
                (model3d['y']>segmentations.loc['min-y',name]) &
                (model3d['y']<segmentations.loc['max-y',name]) ]
        prefix_new = '{}/{}'.format(prefix,name)
        print_model3d(model3d_new,prefix_new)
        html_model3d(model3d_new,prefix_new)
        

