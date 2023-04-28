from xml.dom.minidom import parse
import xml.dom.minidom
import numpy as np
import sys
import getopt
import json
#Usage
def get_xml_matrix_usage():
    print("""
Usage : get_xml_matrix.py -i <file.xml>
                          -o  <output>
    """,flush=True)

def get_trackEM_forward(param :str) -> np.matrix:
    """
    handle '-0.010963829,-0.999939895,0.999939895,-0.010963829,-129.2603788,1664.628308'
    @return reverse affine matrix.
    """
    affine = np.zeros((3,3))
    in_data = np.array(param.split(',')).astype(float).reshape((3,2))
    affine[0:2,:]=in_data.T
    affine[2] = [0,0,1]
    return np.matrix(affine)


def get_xml_matrix_main(argv:[]):
    file=''
    prefix=''
    try:
        opts , args =getopt.getopt(argv,"hi:o:",["help=","input=","output="])
    except getopt.GetoptError:
        get_xml_matrix_usage()
        sys.exit(2)
    for opt, arg in opts :
        if opt in ("-h","--help"):
            get_xml_matrix_usage()
            sys.exit(0)
        elif opt in ("-i","--input"):
            file = arg 
        elif opt in ("-o","--output"):
            prefix = arg
    if file =="" or prefix =="":
        get_xml_matrix_usage()
        sys.exit(0)
    DOMTree = xml.dom.minidom.parse(file)
    collection = DOMTree.documentElement
    patchs = collection.getElementsByTagName("t2_patch")

    json_list = []
    for patch in patchs:

        patch_list = []
        if patch.hasAttribute("title"):
            tit = patch.getAttribute("title")
            patch_list.append(tit)
        if patch.hasAttribute("transform"):
            transform = patch.getAttribute("transform")
            transform = transform[7:-1]
            patch_list.append(transform)
            forward = get_trackEM_forward(transform)
            backward = forward.I
            patch_list.append('Forward affine matrix: ')
            patch_list.append(json.dumps(forward.tolist()))
            patch_list.append('Backward affine matrix: ')
            patch_list.append(json.dumps(backward.tolist()))
            json_list.append(patch_list)
    with open(f"{prefix}.json",'w') as f:
        json.dump(json_list,f,indent='\t')
