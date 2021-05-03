import os
import glob
import pickle
import numpy as np
from shutil import copy
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
            print(f'exact match found for {target_num_clusters} clusters.')
            return f_mid
        iteration += 1
    # if you run out of iterations before finding the exact number of target clusters, return the closest result
    print(f'no exact match found.  returning closest approximation: {n_clusters} clusters.')
    return f_mid
  
def save_clusters_into_dirs(data_dir, Z, cluster_membership):
    ll = leaves_list(Z)
    # maps from original order to leaf list order
    forward = {i : v for i, v in enumerate(ll)}
    # this reverse map works because leaf_list is one-to-one.
    reverse = {v : k for k, v in forward.items()}
    all_output_wavs = sorted(glob.glob(data_dir + '/*.wav'))
    print(all_output_wavs)
    # make dictionary between original number and output wavs.
    wav_dict = {reverse[i] : f for i, f in enumerate(all_output_wavs)}
    print(f'n leaf-ordered wavs found in directory:  {len(all_output_wavs)}')
    for cluster_i in range(cluster_membership.max()):
        cluster_dir = os.path.join(data_dir, 'clusters', 'cluster_' + str(cluster_i + 1).zfill(4))
        if not os.path.exists(cluster_dir):
            os.makedirs(cluster_dir)
        indices = np.where(cluster_membership == (cluster_i + 1))
        for i in list(indices[0]):
            copy(wav_dict[i], cluster_dir)
            
def save_cluster_folders(data_dir, n_clusters):
    # to do:  implement prompt if folder/file exists
    Z = load_linkage(data_dir)
    cm = get_fclusters(Z, target_num_clusters = n_clusters)
    save_clusters_into_dirs(data_dir, Z, cm)

def test_korg():
    # to do: figure out why 0136, 0137, 0138 aren't clustering together.
    # they cluster with 3, but not 20.  is there randomness in the arrangement of the leaves?
    save_cluster_folders('korg_2frames', 20)

