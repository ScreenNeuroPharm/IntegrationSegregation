from scipy.io import loadmat
from scipy.special import erfcinv
import numpy as np
import pandas as pd
from scipy.stats import kstest, kruskal
from itertools import combinations
from matplotlib import pyplot as plt


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


# load variables (data, DIV, Config, Matrix) from columns in .mat file
data, DIV, Config, Matrix = ...

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
labels = ['MFR', 'MBR', 'SxB', 'BD', 'IBI', 'MFIB', 'RS', 'PFIB']

mask_mat = np.unique([4*(i // 4) for i, d in enumerate(data[:, 0]) if len(d) < 3])
mask = np.concatenate([np.linspace(m, m+3, 4, dtype=int) for m in mask_mat])
mask = np.asarray([False if np.any(i == mask) else True for i in range(len(data))])

data = data[mask, :]
DIV = DIV[mask]
Config = Config[mask]

Titles = []
p_vals = []
p_stars = []

for idxL in range(0,8,2):
    for idxD, div in enumerate(DIVUnique):

        metricA = []
        metricB = []
        df_pval = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
        df_star = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)

        for conf in ConfigUnique:
            all_compartment = [d.flatten() for d in data[np.logical_and(DIV == div, Config == conf), idxL]]
            conf_mean = []

            for comp in all_compartment:

                if len(comp) == 0:
                    continue
                tmp = np.mean(comp[isnotOutlier(comp)])

                conf_mean.append(tmp)

            metricA.append(conf_mean)

        for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metricA, 2), combinations(ConfigUnique, 2))):

            p_val = kruskal(group1, group2).pvalue
            df_pval[c1][c2] = p_val
            df_star[c1][c2] = star(p_val)

        for conf in ConfigUnique:
            all_compartment = [d.flatten() for d in data[np.logical_and(DIV == div, Config == conf), idxL+1]]
            conf_mean = []

            for comp in all_compartment:

                if len(comp) == 0:
                    continue
                tmp = np.mean(comp[isnotOutlier(comp)])

                conf_mean.append(tmp)

            metricB.append(conf_mean)

        Titles.append(div+'_'+labels[idxL]+'_'+labels[idxL+1])

        for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metricB, 2), combinations(ConfigUnique, 2))):

            p_val = kruskal(group1, group2).pvalue
            df_pval[c2][c1] = p_val
            df_star[c2][c1] = star(p_val)

        p_vals.append(df_pval)
        p_stars.append(df_star)

with pd.ExcelWriter('p_values_spiking_bursting.xlsx', engine='xlsxwriter') as writer:
    for df, tit in zip(p_vals, Titles):
        df.to_excel(writer, sheet_name=tit)

with pd.ExcelWriter('p_values_spiking_bursting_2.xlsx', engine='xlsxwriter') as writer:
    for df, tit in zip(p_stars, Titles):
        df.to_excel(writer, sheet_name=tit)
