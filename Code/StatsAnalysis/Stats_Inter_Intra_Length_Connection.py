from scipy.io import loadmat
from scipy.special import erfcinv
import numpy as np
import pandas as pd
from itertools import combinations

def star(p_val):

    assert 0 <= p_val <= 1

    if p_val >= 0.05:
        return 'ns'

    if p_val >= 0.01:
        return '*'

    if p_val >= 0.001:
        return '**'

    if p_val >= 0.0001:
        return '***'

    return '****'


def isnotOutlier(data):

    c = -1/(np.sqrt(2)*erfcinv(3/2))
    mad = c*np.median(np.abs(data-np.median(data)))

    return np.abs(data-np.median(data)) <= 3*mad


# load variables (LC, LC_inter, DIV, Config, Matrix) from columns in .mat file
LC, LC_inter, DIV, Config, Matrix = ...

metric_max = 3.2
bins_edges = np.arange(0.2, np.ceil(metric_max / 0.2) * 0.2, 0.2)
bins = (bins_edges[1:]+bins_edges[:-1])/2

Config[Config == 'controllo'] = 'Controllo'
Config[Config == 'Controllo'] = 'CTRL'
Config[Config == 'RimozioneDIV5'] = 'RimozioneDIV05'
Config[Config == 'RimozioneDIV05'] = 'RD05'
Config[Config == 'RimozioneDIV10'] = 'RD10'
Config[Config == 'RimozioneDIV15'] = 'RD15'
DIV[DIV == 'DIV13'] = 'DIV14'
DIV[DIV == 'DIV19'] = 'DIV18'

MFR = np.asarray([len(m) for m in loadmat('data.mat')['data'][:, 3]])
MFR_cond = np.asarray([True if all(x >= 3 for x in MFR[i:i+4]) else False for i in range(0, len(MFR), 4)])
NBD = np.asarray([len(row[0].flatten()) for row in loadmat('NBD.mat')['NBD']], dtype=object)
NBD_cond = NBD >= 3
cond = np.logical_and(MFR_cond, NBD_cond)

LC = LC[cond]
LC_inter = LC_inter[cond]
DIV = DIV[cond]
Config = Config[cond]
Matrix = Matrix[cond]

ConfigUnique = np.unique(Config)
DIVUnique = np.unique(DIV)

df = pd.DataFrame('', index=DIVUnique, columns=ConfigUnique)

for conf in ConfigUnique:
    for div in DIVUnique:
        all_mat_all = LC[np.logical_and(DIV == div, Config == conf)]
        all_mat_inter = LC_inter[np.logical_and(DIV == div, Config == conf)]

        all_LC = np.hstack(all_mat_all.tolist())
        inter_LC = np.hstack(all_mat_inter.tolist())

        hist_all = np.histogram(np.hstack(all_mat_all.tolist()), bins=bins_edges)[0]
        hist_inter = np.histogram(np.hstack(all_mat_inter.tolist()), bins=bins_edges)[0]

        ''' Bhattacharyya distance '''
        pval = -np.log(np.sum(np.sqrt(hist_all/np.sum(hist_all)*hist_inter/np.sum(hist_inter))))

        df[conf][div] = pval
