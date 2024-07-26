from scipy.io import loadmat
from scipy.special import erfcinv
import numpy as np
import pandas as pd
from scipy.stats import kruskal
from itertools import combinations
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches


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


# load variables (perc_all, perc_strong, DIV, Config, Matrix) from columns in .mat file
perc_all, perc_strong, DIV, Config, Matrix = ...

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
p_vals_strong_conf = []
p_vals_strong_div = []

for div in DIVUnique:
    metric_all = []
    metric_strong = []
    df_pval = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
    df_pval.index.name = div
    df_pval2 = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
    df_pval2.index.name = div

    for idx, conf in enumerate(ConfigUnique):
        mat_all = perc_all[np.logical_and(DIV == div, Config == conf)]
        mat_strong = perc_strong[np.logical_and(DIV == div, Config == conf)]
        metric_all.append(mat_all)
        metric_strong.append(mat_strong)
        mean_all = np.mean(mat_all)
        mean_strong = np.mean(mat_strong)

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric_all, 2), combinations(ConfigUnique, 2))):
        p_val = kruskal(group1, group2).pvalue
        df_pval[c2][c1] = round(p_val[0], 5)
        df_pval[c1][c2] = star(p_val)
    p_vals_all_conf.append(df_pval)

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric_strong, 2), combinations(ConfigUnique, 2))):
        p_val = kruskal(group1, group2).pvalue
        df_pval2[c2][c1] = round(p_val[0], 5)
        df_pval2[c1][c2] = star(p_val)
    p_vals_strong_conf.append(df_pval2)

for conf in ConfigUnique:
    metric_all = []
    metric_strong = []
    df_pval = pd.DataFrame('', index=DIVUnique, columns=DIVUnique)
    df_pval.index.name = conf
    df_pval2 = pd.DataFrame('', index=DIVUnique, columns=DIVUnique)
    df_pval2.index.name = conf

    for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric_all, 2), combinations(DIVUnique, 2))):
        p_val = kruskal(group1, group2).pvalue
        df_pval[c2][c1] = round(p_val[0], 5)
        df_pval[c1][c2] = star(p_val)
    p_vals_all_div.append(df_pval)

    for _, ((group1, group2), (c1, c2)) in enumerate(
            zip(combinations(metric_strong, 2), combinations(DIVUnique, 2))):
        p_val = kruskal(group1, group2).pvalue
        df_pval2[c2][c1] = round(p_val[0], 5)
        df_pval2[c1][c2] = star(p_val)
    p_vals_strong_div.append(df_pval2)

with pd.ExcelWriter('p_values_all_connections.xlsx', engine='openpyxl') as writer:

    for idx, df in enumerate(p_vals_all_conf):

        r = (idx // len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        c = (idx % len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        df.to_excel(writer, sheet_name='Configs', startrow=r, startcol=c)

    for idx, df in enumerate(p_vals_all_div):

        r = (idx // len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        c = (idx % len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        df.to_excel(writer, sheet_name='DIVs', startrow=r, startcol=c)

with pd.ExcelWriter('p_values_strong_connections.xlsx', engine='openpyxl') as writer:

    for idx, df in enumerate(p_vals_strong_conf):

        r = (idx // len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        c = (idx % len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        df.to_excel(writer, sheet_name='Configs', startrow=r, startcol=c)

    for idx, df in enumerate(p_vals_strong_div):

        r = (idx // len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        c = (idx % len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        df.to_excel(writer, sheet_name='DIVs', startrow=r, startcol=c)
