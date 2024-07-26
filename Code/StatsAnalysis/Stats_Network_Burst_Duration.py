from scipy.io import loadmat
from scipy.special import erfcinv
import numpy as np
import pandas as pd
from scipy.stats import kruskal
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


# load variables (NBD, DIV, Config, Matrix) from columns in .mat file
NBD, DIV, Config, Matrix = ...

NBD_no_out = np.asarray([a[isnotOutlier(a)] for a in NBD], dtype=object)

Config[Config == 'controllo'] = 'Controllo'
Config[Config == 'Controllo'] = 'CTRL'
Config[Config == 'RimozioneDIV5'] = 'RimozioneDIV05'
Config[Config == 'RimozioneDIV05'] = 'RD05'
Config[Config == 'RimozioneDIV10'] = 'RD10'
Config[Config == 'RimozioneDIV15'] = 'RD15'
DIV[DIV == 'DIV13'] = 'DIV14'
DIV[DIV == 'DIV19'] = 'DIV18'

ConfigUnique = np.unique(Config)
DIVUnique = np.unique(DIV)
p_vals = []
p_vals2 = []

for div in DIVUnique:
    metric = []
    df_pval = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
    df_pval.index.name = div
    for conf in ConfigUnique:
        all_mat = NBD_no_out[np.logical_and(DIV == div, Config == conf)]
        MEA = Matrix[np.logical_and(DIV == div, Config == conf)]
        mat_mean = []
        mat_no_out = []

        for (mat, mea) in zip(all_mat, MEA):
            if len(mat) < 3:
                continue
            m = np.mean(mat)
            mat_mean.append(m)
        mat_mean = np.asarray(mat_mean)
        metric.append(mat_mean[isnotOutlier(mat_mean)])

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric, 2), combinations(ConfigUnique, 2))):

        p_val = kruskal(group1, group2).pvalue
        df_pval[c2][c1] = p_val
        df_pval[c1][c2] = star(p_val)

    p_vals.append(df_pval)

for conf in ConfigUnique:
    metric = []
    df_pval = pd.DataFrame('', index=DIVUnique, columns=DIVUnique)
    df_pval.index.name = conf
    for div in DIVUnique:
        all_mat = NBD_no_out[np.logical_and(DIV == div, Config == conf)]
        MEA = Matrix[np.logical_and(DIV == div, Config == conf)]
        mat_mean = []
        mat_no_out = []

        for (mat, mea) in zip(all_mat, MEA):
            if len(mat) < 3:
                continue
            m = np.mean(mat)
            mat_mean.append(m)
        mat_mean = np.asarray(mat_mean)
        metric.append(mat_mean[isnotOutlier(mat_mean)])

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric, 2), combinations(DIVUnique, 2))):
        p_val = kruskal(group1, group2).pvalue
        df_pval[c2][c1] = p_val
        df_pval[c1][c2] = star(p_val)

    p_vals2.append(df_pval)

with pd.ExcelWriter('p_values_network_burst_duration.xlsx', engine='openpyxl') as writer:

    for idx, df in enumerate(p_vals):

        r = (idx // len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        c = (idx % len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        df.to_excel(writer, sheet_name='Configs', startrow=r, startcol=c)

    for idx, df in enumerate(p_vals2):

        r = (idx // len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        c = (idx % len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        df.to_excel(writer, sheet_name='DIVs', startrow=r, startcol=c)
