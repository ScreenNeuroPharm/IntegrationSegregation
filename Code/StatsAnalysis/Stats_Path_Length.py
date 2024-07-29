from scipy.io import loadmat
from scipy.special import erfcinv
import numpy as np
import pandas as pd
from scipy.stats import kruskal
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


# load variables (PL, DIV, Config, Matrix) from columns in .mat file
PL, DIV, Config, Matrix = ...

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

p_vals_all_conf = []
p_vals_all_div = []

for div in DIVUnique:
    metric = []
    metric_no_out = []
    df_pval = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
    df_pval.index.name = div
    for conf in ConfigUnique:
        all_mat = PL[np.logical_and(DIV == div, Config == conf)]
        mean_mat = np.asarray([np.mean(mat) for mat in all_mat])
        mean_mat = mean_mat[np.isfinite(mean_mat)]
        mean_no_out = mean_mat[isnotOutlier(mean_mat)]

        metric.append(mean_mat)
        metric_no_out.append(mean_no_out)

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric_no_out, 2), combinations(ConfigUnique, 2))):

        p_val = kruskal(group1, group2).pvalue
        df_pval[c2][c1] = p_val
        df_pval[c1][c2] = star(p_val)

    p_vals_all_conf.append(df_pval)

for conf in ConfigUnique:
    metric = []
    metric_no_out = []
    df_pval = pd.DataFrame('', index=DIVUnique, columns=DIVUnique)
    df_pval.index.name = conf
    for div in DIVUnique:
        all_mat = PL[np.logical_and(DIV == div, Config == conf)]
        mean_mat = np.asarray([np.mean(mat) for mat in all_mat])
        mean_mat = mean_mat[np.isfinite(mean_mat)]
        mean_no_out = mean_mat[isnotOutlier(mean_mat)]

        metric.append(mean_mat)
        metric_no_out.append(mean_no_out)

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric_no_out, 2), combinations(DIVUnique, 2))):

        p_val = kruskal(group1, group2).pvalue
        df_pval[c2][c1] = p_val
        df_pval[c1][c2] = star(p_val)

    p_vals_all_conf.append(df_pval)
