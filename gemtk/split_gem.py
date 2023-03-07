import pandas as pd
import numpy as np
import getopt
import sys

def split_gem_Usage():
    print("""
Usage : split_gem.py -i <input.gem>
                     -o <output.gem>
                     -x <X of split>
                     -y <Y of split>
Notice: There's only  -x or  -y
""",flush=True)

def split_gem_main(argv:[]):
    ingem=''
    prefix=''
    X=''
    Y=''
    try:
        opts,args=getopt.getopt(argv,"hi:o:x:y:",["help=","input=","output="])
    except getopt.GetoptError:
        split_gem_Usage()
        sys.exit(2)
    
    for opt,arg in opts:
        if opt in ('-h','--help'):
            split_gem_Usage()
            sys.exit(0)
        if opt in ('-i','--input'):
            ingem = arg
        if opt in ('-o','--output'):
            prefix = arg
        if opt in ('-x'):
            X = int(arg)
        if opt in ('-y'):
            Y = int(arg)

    if ingem == '' or prefix == '' or (X == '' and Y == ''):
        split_gem_Usage()
        sys.exit(0)
    
    df = pd.read_csv(ingem, sep='\t', comment='#')
    if X!='':
        df_1=df[df["x"]<=X]
        df_2=df[df["x"]>X]
    if Y!='':
        df_1=df[df["y"]<=Y]
        df_2=df[df["y"]>Y]
    df_1.to_csv(f'{prefix}_1.gem',index=None,sep='\t')
    df_2.to_csv(f'{prefix}_2.gem',index=None,sep='\t')
