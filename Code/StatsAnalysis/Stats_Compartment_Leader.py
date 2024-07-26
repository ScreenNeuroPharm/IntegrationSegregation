from scipy.io import loadmat
from scipy.special import erfcinv
import numpy as np
import pandas as pd
from scipy.stats import kstest, chi2_contingency
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


# load variables (comp_leader, DIV, Config, Matrix) from columns in .mat file
comp_leader, DIV, Config, Matrix = ...
comp_leader = -np.sort(-comp_leader)

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

p_vals_conf = []
p_vals_div = []
p_vals_exp = []

for div in DIVUnique:

    metric = []
    df = pd.DataFrame('', index=ConfigUnique, columns=ConfigUnique)
    df.index.name = div

    for conf in ConfigUnique:
        all_mat = comp_leader[np.logical_and(DIV == div, Config == conf), :]
        all_mat = all_mat[np.sum(all_mat, axis=1) != 0]
        median_all_mat = np.median(all_mat, axis=0)
        metric.append(median_all_mat)

    for ((group1, group2), (c1, c2)) in zip(combinations(metric, 2), combinations(ConfigUnique, 2)):

        pval = kstest(group1, group2).pvalue
        df[c2][c1] = pval
        df[c1][c2] = star(pval)

    p_vals_conf.append(df)

for conf in ConfigUnique:

    metric = []
    df = pd.DataFrame('', index=DIVUnique, columns=DIVUnique)
    df.index.name = conf

    for div in DIVUnique:
        all_mat = comp_leader[np.logical_and(DIV == div, Config == conf), :]
        all_mat = all_mat[np.sum(all_mat, axis=1) != 0]
        median_all_mat = np.median(all_mat, axis=0)
        metric.append(median_all_mat)

    for ((group1, group2), (c1, c2)) in zip(combinations(metric, 2), combinations(DIVUnique, 2)):

        pval = kstest(group1, group2).pvalue
        df[c2][c1] = pval
        df[c1][c2] = star(pval)
    p_vals_div.append(df)

''' Expected (25% uniform) '''

df1 = pd.DataFrame('', index=DIVUnique, columns=ConfigUnique)
df1.index.name = 'Expected'
df2 = pd.DataFrame('', index=DIVUnique, columns=ConfigUnique)
df2.index.name = 'Expected'

for div in DIVUnique:
    for conf in ConfigUnique:

        all_mat = comp_leader[np.logical_and(DIV == div, Config == conf), :]
        all_mat = all_mat[np.sum(all_mat, axis=1) != 0]
        group1 = np.median(all_mat, axis=0)
        group2 = np.asarray([25, 25, 25, 25])
        pval = chi2_contingency([group1, group2]).pvalue

        df1[conf][div] = pval
        df2[conf][div] = star(pval)


with pd.ExcelWriter('p_values_compartment_leader.xlsx', engine='openpyxl') as writer:

    for idx, df in enumerate(p_vals_conf):

        r = (idx // len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        c = (idx % len(DIVUnique)) * (len(ConfigUnique) + 2) + 1
        df.to_excel(writer, sheet_name='Configs', startrow=r, startcol=c)

    for idx, df in enumerate(p_vals_div):

        r = (idx // len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        c = (idx % len(ConfigUnique)) * (len(DIVUnique) + 2) + 1
        df.to_excel(writer, sheet_name='DIVs', startrow=r, startcol=c)

    df1.to_excel(writer, sheet_name='Expected', startrow=1, startcol=1)
    df2.to_excel(writer, sheet_name='Expected', startrow=1, startcol=7)
