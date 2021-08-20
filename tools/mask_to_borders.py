#!/usr/bin/env python3
import sys
import getopt
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import hdbscan
from sklearn.cluster import spectral_clustering
from sklearn import cluster
import alphashape
from descartes import PolygonPatch


def draw_mask(masks : np.ndarray , prefix:str):
    plt.figure(figsize=(masks.shape[1]/10,masks.shape[0]/10))
    plt.imshow(masks, cmap='binary')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig("{}_raw_mask.png".format(prefix),dpi=10)

def draw_labels(color_matrix :np.ndarray, prefix:str,label:str):
    plt.figure(figsize=(color_matrix.shape[1]/10,color_matrix.shape[0]/10))
    plt.imshow(color_matrix, cmap='Dark2')
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig("{}_{}.png".format(prefix,label),dpi=10)

def draw_borders(points:{} , borders : {}, prefix:str):
    # Initialize plot
    fig, ax = plt.subplots()
    for l in points:
        point = points[l]
        border= borders[l]
        if border.is_empty:
            continue
        # Plot input points
        X_mean=point.mean(axis=0)
        plt.scatter(x=point[:,0],y=point[:,1],c='blue',s=0.1)
        plt.text(X_mean[0],X_mean[1],"c%d"%l)
        print(X_mean)
        print(l)
        # Plot alpha shape
        ax.add_patch(PolygonPatch(border, alpha=0.5))
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1,hspace=0,wspace=0)
    plt.savefig("{}_borders.png".format(prefix))

def getPoints(masks :np.ndarray):
    valid_nums = np.sum(masks)
    points = np.zeros((valid_nums,2))
    points = points.astype(int)
    index = 0;
    for i in range(masks.shape[0]):
        for j in range(masks.shape[1]):
            if masks[i][j] == 1 :
                points[index][0] = i;
                points[index][1] = j;
                index +=1
    return valid_nums,points

def doHDBSCAN(masks:np.ndarray,points:np.ndarray, prefix : str) :
    clusterer = hdbscan.HDBSCAN(min_cluster_size=50)
    clusterer.fit(points)
    labels = clusterer.labels_
    color_matrix = np.zeros(masks.shape)
    for i in range(points.shape[0]):
        if labels[i] != -1 :
            label = labels[i]+1
            color_matrix[points[i][0] , points[i][1]]=label
    draw_labels(color_matrix, prefix,'hdbscan')
    return labels

def getBorder(points : np.ndarray):
    # Define alpha parameter
    alpha = 0.2
    # Generate the alpha shape
    alpha_shape = alphashape.alphashape(points, alpha)
    return alpha_shape

def doBorders(points:np.ndarray,labels, prefix : str):
    points_clusters={}
    valid_nums = points.shape[0]
    for i in range(valid_nums):
        if labels[i] != -1 :
            label = labels[i]+1
            if label in points_clusters:
                points_clusters[label].append((points[i][0] , points[i][1]))
            else:
                points_clusters[label]=[]
                points_clusters[label].append((points[i][0] , points[i][1]))
    ids = np.unique(labels)
    borders= {}
    for l in points_clusters :
        points_clusters[l] = np.array(points_clusters[l])
    for l in points_clusters :
        borders[l]=getBorder(points_clusters[l])
    draw_borders(points_clusters,borders,prefix)

def main_usage():
    print("""
Usage : mask_to_borders.py  -i mask.txt -o prefix
""")

def main(argv:[]):
    input_file= ''
    prefix=''
    try:
        opts, args = getopt.getopt(argv,"i:o:",["input=","output="])
    except getopt.GetoptError:
        main_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-o", "--output"):
            prefix = arg
        elif opt in ("-i", "--input_file"):
            input_file = arg
    # load masks
    masks = np.loadtxt(input_file,dtype=int,delimiter='\t')
    # draw masks
    draw_mask(masks,prefix)
    valid_nums, points = getPoints(masks)
    labels = doHDBSCAN(masks,points,prefix)
    doBorders(points,labels,prefix)

# logic codes
if __name__ == "__main__":
    if len(sys.argv) <= 2:
        main_usage()
    else :
        main(sys.argv[1:])


