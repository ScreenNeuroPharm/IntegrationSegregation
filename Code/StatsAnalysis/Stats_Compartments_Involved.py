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


# load variables (comp_involved, DIV, Config, Matrix) from columns in .mat file
comp_involved, DIV, Config, Matrix = ...

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

for comp in range(4):
    for div in DIVUnique:

        metric = []
        df_pval = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
        df_pval.index.name = div

        for conf in ConfigUnique:
            all_mat = comp_involved[np.logical_and(DIV == div, Config == conf), :]
            all_mat = all_mat[np.sum(all_mat, axis=1) != 0]

            if div == 'DIV11' and conf == 'RD15':
                all_mat = all_mat[2:]

            metric.append(all_mat[:, comp])

        for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric, 2), combinations(ConfigUnique, 2))):

            try:
                p_val = kruskal(group1, group2).pvalue
            except ValueError:
                p_val = 1

            df_pval[c2][c1] = p_val
            df_pval[c1][c2] = star(p_val)

        p_vals.append(df_pval)

p_vals2 = []

for comp in range(4):

    for conf in ConfigUnique:

        metric = []
        df_pval = pd.DataFrame('', index=DIVUnique, columns=DIVUnique)
        df_pval.index.name = conf

        for div in DIVUnique:
            all_mat = comp_involved[np.logical_and(DIV == div, Config == conf), :]
            all_mat = all_mat[np.sum(all_mat, axis=1) != 0]

            if div == 'DIV11' and conf == 'RD15':
                all_mat = all_mat[2:]

            metric.append(all_mat[:, comp])

        for _, ((group1, group2), (c1, c2)) in enumerate(zip(combinations(metric, 2), combinations(DIVUnique, 2))):

            try:
                p_val = kruskal(group1, group2).pvalue
            except ValueError:
                p_val = 1

            df_pval[c2][c1] = p_val
            df_pval[c1][c2] = star(p_val)

        p_vals2.append(df_pval)

with pd.ExcelWriter('p_values_compartments_involved.xlsx', engine='openpyxl') as writer:

    for idx, df in enumerate(p_vals):

        r = (idx // len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        c = (idx % len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        df.to_excel(writer, sheet_name='Configs', startrow=r, startcol=c)

    for idx, df in enumerate(p_vals2):

        r = (idx // len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        c = (idx % len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        df.to_excel(writer, sheet_name='DIVs', startrow=r, startcol=c)
