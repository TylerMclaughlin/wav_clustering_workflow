"""
Hierarchically clusters wav samples. Currently tested on drum samples. Saves copies that are renamed -- numbered and ordered by similarity.
"""

import os
import glob
import pandas as pd
from shutil import copy

from pyAudioAnalysis import ShortTermFeatures as aF
from pyAudioAnalysis import audioBasicIO as aIO 


from scipy.cluster.hierarchy import ward, dendrogram, leaves_list
from scipy.spatial.distance import pdist
from matplotlib import pyplot as plt

def get_short_term_features(wav_loc, win = 0.050, step = 0.050):
    """ 
    Extract short-term features using default 50msec non-overlapping windows
    """

    # get sampling frequency and signal.
    fs, s = aIO.read_audio_file(wav_loc)

    # print duration of wav in seconds:
    duration = len(s) / float(fs)
    print(f'{wav_loc} duration = {duration} seconds')
    
    # features, feature names.
    # feature names look like ['zcr', 'energy', 'energy_entropy', 'spectral_centroid', 'spectral_spread', 'spectral_entropy', 'spectral_flux', 'spectral_rolloff', 'mfcc_1', 'mfcc_2', 'mfcc_3', 'mfcc_4', 'mfcc_5', 'mfcc_6', 'mfcc_7', 'mfcc_8', 'mfcc_9', 'mfcc_10', 'mfcc_11', 'mfcc_12', 'mfcc_13', 'chroma_1', 'chroma_2', 'chroma_3', 'chroma_4', 'chroma_5', 'chroma_6', 'chroma_7', 'chroma_8', 'chroma_9', 'chroma_10', 'chroma_11', 'chroma_12', 'chroma_std', 'delta zcr', 'delta energy', 'delta energy_entropy', 'delta spectral_centroid', 'delta spectral_spread', 'delta spectral_entropy', 'delta spectral_flux', 'delta spectral_rolloff', 'delta mfcc_1', 'delta mfcc_2', 'delta mfcc_3', 'delta mfcc_4', 'delta mfcc_5', 'delta mfcc_6', 'delta mfcc_7', 'delta mfcc_8', 'delta mfcc_9', 'delta mfcc_10', 'delta mfcc_11', 'delta mfcc_12', 'delta mfcc_13', 'delta chroma_1', 'delta chroma_2', 'delta chroma_3', 'delta chroma_4', 'delta chroma_5', 'delta chroma_6', 'delta chroma_7', 'delta chroma_8', 'delta chroma_9', 'delta chroma_10', 'delta chroma_11', 'delta chroma_12', 'delta chroma_std']
    # features f look like numpy matrices
    try:
        [f, fn] = aF.feature_extraction(s, fs, int(fs * win), int(fs * step))
        print(f'{f.shape[1]} frames, {f.shape[0]} short-term features')

        return [f, fn]
    # sometimes the feature extraction yields a ValueError because the sample is too short.
    except ValueError:
        return None

def flatten_n_frames(f,n):
    m = f[:,:n]
    # use Fortran order so that [[1,2],[3,4],[5,6]] becomes [1,3,5,2,4,6] (i.e., adjacent frames first, then onto the next feature.)
    return m.flatten('F')

def get_features_frame(wav_locs, first_n_frames, include_parent_dir = False):
    """
    Iterates over the list of paths to each wav file of interest. Extracts feature matrix. Subsets the feature matrix to the first_n_frames.  

    include_parent_dir should be set to True if the parent directory of the sample contains meaningful information (like the drum machine, for instance).
    If this is the case, the new drum name will be like 'kicks/kd01.wav'.  I call this a 'dir_wav'.

    """
    feature_dict = {}
    for w in wav_locs:
        wav_basename = w.split('/')[-1]
        if include_parent_dir: # For plotting, make the name of the wav a 'dir_wav', e.g., 'dir_name/sample_name.wav'
            wav_dirname = w.split('/')[-2]
            wav_basename = wav_dirname + '/' + wav_basename
        try:
            f, fn = get_short_term_features(w)
            feature_dict[wav_basename] = flatten_n_frames(f, first_n_frames)
        except TypeError:
            print(f'{w} appears to be too short to extract features')
    features_wavs_df = pd.DataFrame.from_dict(feature_dict, orient='index').transpose()
    return features_wavs_df 


def save_ordered_wav_copies(parent_dir, list_of_dir_wavs, outdir):
    """ 
    list_of_dir_wavs is a list of wavs in their directories, like ['kicks/kd01.wav','kicks/kd02.wav','snare/sd01.wav','hh/hh01.wav'].
    Saves list of original filenames as a text file.
    Copies the files to a new, sorted location using the function copy() from shutil.  
    Symlinking would save space, but since it doesn't work for all applications, I went with copy().
   """
    # make the output directory if it doesn't exist.
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    # write the original filenames (and full path) to a text file, in  the same order as the output sorted and numbered wavs.   
    # Basically a reference table.
    # If sample library is organized, by drum machine for example, this text file is useful for looking up the instrument or drum name of samples.
    with open(os.path.join(outdir, "original_filenames.txt"), "w") as output:
        for orig_wav in list_of_dir_wavs:
            output.write(str(os.path.join(parent_dir, orig_wav)) +'\n')
    for i, source_wav in enumerate(list_of_dir_wavs):
        # add leading zeros to the output filename.  For simplicity, just use a number.  
        out_filename = str(i).zfill(5) + '.wav'
        copy(os.path.join(parent_dir, source_wav), os.path.join(outdir,out_filename))

# a few tests for the BPB Casette 909 data set.  
# a 'sanity check' or positive control.
# If the clustering is working, all snares should be clustered together, all cymbals should cluster together, etc.

def save_test_909_data():
    """
    Saves pandas df of features for all 909 samples
    """
    wav_pattern = "/Users/mclaurt/Music/dahnloads/BPB Cassette 909/clean/*.wav"
    bp909_wavs = glob.glob(wav_pattern)
    print(bp909_wavs)
    out_matrix = get_features_frame(bp909_wavs, 2)
    out_matrix.to_csv('data/drums_and_features.csv', index = None)
    print(out_matrix)


def cluster_test_909_data():
    """
    Extends the test above to perform hierarchical clustering.  Also saves renamed copies of the wav files and displays a plotted dendrogram. 

    Implementation details:
    Transposes the dataframe, makes it an n x m  numpy matrix, n features and m samples. 
    """
    wav_pattern = "/Users/mclaurt/Music/dahnloads/BPB Cassette 909/clean/*.wav"
    bp909_wavs = glob.glob(wav_pattern)
    df_matrix = get_features_frame(bp909_wavs, 2)
    df_matrix.fillna(0, inplace = True)
    feature_matrix = df_matrix.T.values # n dimensional, m observations.
    Z = ward(pdist(feature_matrix))
    ll = list(leaves_list(Z))
    drumnames = df_matrix.columns[ll]
    print(drumnames)
    list_of_909_dir_wavs = ['clean/' + x for x in df_matrix.columns]
    save_ordered_wav_copies("/Users/mclaurt/Music/dahnloads/BPB Cassette 909/", list_of_dir_wavs = list_of_909_dir_wavs, outdir = '909_test')
    # For labels, use the ordering of the dataframe columns, NOT the order in the leaves_list, ll.
    # left means the roots are on the left, rather than the top.
    dn = dendrogram(Z, labels = list_of_909_dir_wavs, orientation = 'left')
    plt.savefig('909_test/dendrogram.png')


def cluster_and_save_order(globbed_wav_list, n_frames, parent_dir, outdir):
    """
    This is the function for hierarchically clustering wav files and saving them with renamed files, sorted by similarity.
    taking a list of wavs, a number of time frames 
    """
    df_matrix = get_features_frame(globbed_wav_list, n_frames, include_parent_dir = True)
    # Replace missing data. 
    # This is necessary for files that aren't long enough to have features for all the time frames.
    # Fills NaNs with zero.  Zero is pretty arbitrary.  
    df_matrix.fillna(0, inplace = True)
    feature_matrix = df_matrix.T.values # n dimensional, m observations.
    Z = ward(pdist(feature_matrix))
    ll = list(leaves_list(Z))
    drumnames = df_matrix.columns[ll]
    print(f'wav names in clustered order:  {drumnames}')
    # saves renamed,  copies of the wav files, sorted by similarity.
    # also saves the original wav file names in the order.
    save_ordered_wav_copies(parent_dir, list_of_dir_wavs = drumnames, outdir = outdir)
    # For labels, use the ordering of the dataframe columns, NOT the order in the leaves_list, ll.
    # left means the roots are on the left, rather than the top.
    dn = dendrogram(Z, labels = df_matrix.columns, orientation = 'left')
    # save plot in the out dir.
    plt.savefig(os.path.join(outdir,'dendrogram.png'))

# the following functions compartmentalize some experiments.
# They focus on either a single drum machine (Korg Minipops), a single manufacturer (Korg / Elektron), the entire kb6 collection.

def get_minipops():
    parent_dir = '/Users/mclaurt/Music/dahnloads/kb6_drum_samples/ALL_EXTRACTED/'
    minipops_wavs = glob.glob(parent_dir + '[[]KB6[]]_Korg_Minipops/*.wav')
    cluster_and_save_order(minipops_wavs, 2, parent_dir = parent_dir, outdir = 'minipops_2frames')

def get_all_elektron():
    parent_dir = '/Users/mclaurt/Music/dahnloads/kb6_drum_samples/ALL_EXTRACTED/'
    elektron_wavs = glob.glob(parent_dir + '[[]KB6[]]_Electron*/*.wav')
    cluster_and_save_order(elektron_wavs, 2, parent_dir = parent_dir, outdir = 'elektron_2frames')

def get_all_korg():
    parent_dir = '/Users/mclaurt/Music/dahnloads/kb6_drum_samples/ALL_EXTRACTED/'
    wavs = glob.glob(parent_dir + '[[]KB6[]]_Korg*/*.wav')
    cluster_and_save_order(wavs, 2, parent_dir = parent_dir, outdir = 'korg_2frames')

def get_all_kb6():
    parent_dir = '/Users/mclaurt/Music/dahnloads/kb6_drum_samples/ALL_EXTRACTED/'
    wavs = glob.glob(parent_dir + '[[]KB6[]]_*/*.wav')
    cluster_and_save_order(wavs, 2, parent_dir = parent_dir, outdir = 'all_2frames')
