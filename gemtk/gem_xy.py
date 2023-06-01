import sys
import time
import getopt
from gemtk.slice_dataframe import slice_dataframe

############################################################################
# section 15 : chopgems
#############################################################################
# usage
def gem_xy_usage():
    print("""
Usage : GEM_toolkit.py gemxy   -i <input.gem> 
""")

def gem_xy_main(argv:[]):
    igem =''
    try:
        opts, args = getopt.getopt(argv,"hi:",["help"])
    except getopt.GetoptError:
        gem_xy_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            gem_xy_usage()
            sys.exit(0)
        elif opt in ("-i", "--input"):
            igem = arg
    if  igem == '':
        gem_xy_usage()
        sys.exit(3)

    print('loading gem now...')
    gem = slice_dataframe()
    gem.init_from_file(igem)
    print('all done')
    print(time.strftime("%Y-%m-%d %H:%M:%S"),flush=True)
