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
        json_list.append(patch_list)
    with open(f"{prefix}.json",'w') as f:
        json.dump(json_list,f)