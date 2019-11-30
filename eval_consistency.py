import numpy as np
import pandas as pd
import glob
import re
import seaborn as sns
from matplotlib import pyplot as plt



PATTERN = re.compile('(?P<img_id>IDRiD_\d{2})-(?P<lesion_name>..)-(?P<method_name>.*?).npz$')


def get_data(fp):
    #  dat = np.load(fp)
    #  healthy = dat['healthy']
    #  diseased = dat['diseased']
    #  return healthy, diseased
    return dict(np.load(fp))


def main():
    fps = glob.glob('./data/histograms_idrid_data/*.npz')
    print(fps[0])
    metadatas = [PATTERN.search(fp).groupdict() for fp in fps]

    meta = pd.DataFrame(metadatas)


    # testing:  got the histograms for each lesion, method, channel, and
    # averaged over whole dataset.
    hists = get_hists(fps, meta)
    for lesion in ['MA', 'HE', 'EX', 'SE']:
        fig = sns.catplot(x='bin', y='hist', hue='method_name', col='channel', data=hists.query(f'lesion_name=="{lesion}"').query('bin > 0'))
        fig.set_titles("%s {col_name} {col_var}" % lesion)

    df = get_consistency_scores(fps, meta).xs('diseased')
    df['std_as_pct'] = df.groupby(['channel', 'lesion_name'])['std'].transform(lambda x: x/x.max())
    fig = sns.catplot(x='lesion_name', y='std', hue='method_name', col='channel', data=df.reset_index(), kind='bar')
    globals().update(locals())  # TODO: remove after testing done


def get_hists(fps, meta):
    return pd.concat(list(_get_hists(fps, meta)))


def _get_hists(fps, meta):
    for grp_id, grp in meta.groupby(['lesion_name', 'method_name']):
        data = [ get_data(fps[i]) for i in grp.index ]
        #  healthy = np.stack([x['healthy'] for x in data])
        diseased = np.stack([x['diseased'] for x in data])
        # axis shape:  (images, channels, histogram)
        assert diseased.shape[1] == 3, 'bug'
        df = pd.DataFrame(diseased.mean(axis=0), index=['red', 'green', 'blue'], columns=range(256))
        df.columns.name = 'bin'
        df.index.name = 'channel'
        df2 = df.stack()
        df2.name = 'hist'
        df2 = df2.reset_index()
        df2['lesion_name'] = grp_id[0]
        df2['method_name'] = grp_id[1]
        yield df2


def get_consistency_scores(fps, meta):
    return pd.concat(list(_get_consistency_scores(fps, meta)))


def _get_consistency_scores(fps, meta):
    for grp_id, grp in meta.groupby(['lesion_name', 'method_name']):
        data = [ get_data(fps[i]) for i in grp.index ]
        healthy = np.stack([x['healthy'] for x in data])
        diseased = np.stack([x['diseased'] for x in data])
        # axis shape:  (images, channels, histogram)
        assert healthy.shape[1] == 3, 'bug'
        assert diseased.shape[1] == 3, 'bug'

        # evaluate the standard deviation across images
        #  std
          #  - per channel, per lesion, per method
          #  - over all imgs
        df = pd.DataFrame.from_dict(
            {'healthy': healthy.std(axis=(0, 2)),
             'diseased': diseased.std(axis=(0, 2))},
            orient='index', columns=['red', 'green', 'blue'])
        df2 = df.stack().rename('std').to_frame()
        df2.index.set_names(['healthy_or_diseased', 'channel'], inplace=True)
        df2['lesion_name'] = grp_id[0]
        df2['method_name'] = grp_id[1]
        yield df2

        # 1. histogram fix in gen_histograms
        # 2. redo the gen_histograms.
        # 3. consistency
        # 4. bug with the types

    #  for metadata, fp in zip(metadatas, fps):


if __name__ == "__main__":
    main()

