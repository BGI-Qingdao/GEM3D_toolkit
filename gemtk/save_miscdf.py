import os
import json
import numpy as np
import pandas as pd
from json import JSONEncoder
from subprocess import check_call

###########################################################
# section1 : common functions
###########################################################
class General_Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def create_a_folder(prefix):
    if os.path.exists(prefix):
        print("output path {} exist ! exit ...".format(prefix))
        exit(101)
    os.mkdir(prefix)
    if not os.path.exists(prefix):
        print("create output path {}  failed! exit ...".format(prefix))
        exit(102)


def cp_file( fromf :str , tof :str ) :
    check_call('cp {} {}'.format(fromf,tof),shell=True)
