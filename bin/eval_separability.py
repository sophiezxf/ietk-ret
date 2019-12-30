import numpy as np
import pandas as pd
import glob
import re
import seaborn as sns
from os.path import join
import os
from matplotlib import pyplot as plt
import seaborn as sns


from ietk.eval_consistency import PATTERN, get_data
from ietk.data import IDRiD


def ks_scores_from_hist(a, b):
    ca = (a/a.sum(1, keepdims=True)).cumsum(1)
    cb = (b/b.sum(1, keepdims=True)).cumsum(1)
    return np.abs(ca - cb).max(1, keepdims=True)


def _get_separability_scores(fp):
    meta = PATTERN.search(fp).groupdict()
    dat = get_data(fp)
    hists = [dat[x] for x in ['healthy', 'diseased']]
    ks_scores = ks_scores_from_hist(*hists)
    color = {0: 'red', 1: 'green', 2: 'blue'}
    meta.update({f'{color[ch]}': score for ch, score in enumerate(ks_scores.ravel())})
    return meta


def get_separability_scores(fps):
    return pd.DataFrame([_get_separability_scores(fp) for fp in fps])


if __name__ == "__main__":
    save_img_dir='./data/histograms_idrid_plots/'
    os.makedirs(save_img_dir, exist_ok=True)
    fps = glob.glob('./data/histograms_idrid_data/IDRiD*.npz')

    df = get_separability_scores(fps)

    print('separability plots')
    # KS score, per channel
    df2 = df.rename(columns={'lesion_name': 'Lesion', 'method_name': 'Method'})\
        .melt(['img_id', 'Lesion', 'Method'], ['red', 'green', 'blue'], 'Color Channel', 'Separability score (KS test)')\
        .sort_values(['Lesion', 'Method'])
    fig = sns.catplot(
        x='Lesion', y='Separability score (KS test)', hue='Method', col='Color Channel', data=df2, kind='bar'
    ).savefig(join(save_img_dir, 'separability_per_channel.png'))
    # KS score, max across channels
    fig = sns.catplot(
        x='Lesion', y='Separability score (KS test)', hue='Method',
        data=df2.loc[df2.groupby(['img_id', 'Lesion', 'Method'])['Separability score (KS test)'].idxmax()],
        kind='bar'
    ).savefig(join(save_img_dir, 'separability_max_of_channels.png'))
    #  ).set_titles(['Separability: KS score, max of color channels'])\

#  'ks_0': 'red', 'ks_1': 'green', 'ks_2': 'blue