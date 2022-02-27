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
  
def save_clusters_into_dirs(data_dir, Z, cluster_membership):
    ll = leaves_list(Z)
    all_output_wavs = sorted(glob.glob(data_dir + '/*.wav') + glob.glob(data_dir + '/*.aif'))
    new_clusters = cluster_membership[ll]
    # make dictionary between original number and output wavs.
    for i, c in enumerate(new_clusters):
        cluster_dir = os.path.join(data_dir, 'clusters', 'cluster_' + str(c).zfill(4))
        if not os.path.exists(cluster_dir):
            os.makedirs(cluster_dir)
        copy(all_output_wavs[i], cluster_dir)
            
def save_cluster_folders(data_dir, n_clusters):
    # to do:  implement prompt if folder/file exists
    Z = load_linkage(data_dir)
    cm = fcluster(Z, n_clusters, criterion = 'maxclust')
    save_clusters_into_dirs(data_dir, Z, cm)

def test_korg():
    save_cluster_folders('korg_2frames', 5)
