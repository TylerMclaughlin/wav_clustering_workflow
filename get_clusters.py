import os
import pickle
import numpy as np
from scipy.cluster.hierarchy import ward, leaves_list, fcluster

def load_linkage(data_dir):
    with open(os.path.join(data_dir, 'ward_linkage.pkl'), 'rb') as f:
        Z = pickle.load(f)
    return Z


def get_fclusters(Z, target_num_clusters, max_iterations = 100):
    """ 
    Specify a target number of clusters.  Depending on the tree, this target number may not be possible.
    Returns a vector of cluster membership for each sample.
    Implementation uses a max number of iterations to decide when to stop bisecting if exact match is not found. 
    Since the threshold is continuous, i'm not sure there is an optimal way to decide when to stop.
    """
    if target_num_clusters > Z.shape[0]:
        raise ValueError('You cannot have more clusters than datapoints. Reduce the "target_num_clusters" value.')
    # thresholds for bisection search
    left = 0
    right = Z[:,2].max() # maximum of distance column in linkage object 
    mid = (right - left)/2
    iteration = 0
    while iteration < max_iterations:
        f_mid = fcluster(Z, mid, criterion = 'distance')
        n_clusters = f_mid.max()
        if n_clusters > target_num_clusters: 
            left = mid 
            mid = (right + left)/2
        elif n_clusters < target_num_clusters:
            right = mid 
            mid = (right + left)/2
        # if you find an exact match:
        elif n_clusters == target_num_clusters:
            print('exact match found')
            return f_mid
        iteration += 1
    # if you run out of iterations before finding the exact number of target clusters, return the closest result
    print(f'no exact match found.  returning closest approximation: {n_clusters} clusters.')
    return f_mid
    
