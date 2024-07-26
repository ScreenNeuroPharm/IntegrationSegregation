# Integration
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ScreenNeuroPharm/Integration/blob/master/LICENSE)

> The repository contains the data and the functions need to reproduce the analysis reported in the article "Cortical, striatal, and thalamic populations self-organize into a functionally connected circuit with long-term memory properties".

## Details
All uploaded scripts work with a .mat format. 
To reproduce our analysis is necessary to convert the ```.txt``` format file in ```.mat``` format file using the function ```TxT2Mat.m``` in the folder Conversion. 
All electrophysiological recordings are sampled at 10 KHz. 
```TxT2Mat.m``` function allows obtaining for each electrode (60) the peak train .mat file. 
Peak_train file is a sparse vector that reports the spike occur, saving the spike amplitudute.

### Code folder architecture:
- StatsAnalysis folder (python 3.8 scripts):
    * Stats_Spiking_Bursting.py: functions to compute p values with kruskal-wallis (MFR, MBR, MFIB, RS)
    * Stats_Network_Burst_Duration.py: functions to compute p values with kruskal-wallis
    * Stats_Compartments_Involved.py: functions to compute p values with kruskal-wallis
    * Stats_Compartment_Leader.py: functions to compute p values with kolmogorov-smirnov
    * Stats_All_Strong_Connections.py: functions to compute p values with kruskal-wallis
    * Stats_Inter_Intra_Length_Connections.py: functions to compute Bhattacharya Distance
    * Stats_Path_Length.py: functions to compute p values with kruskal-wallis
    * Stats_Clustering_Coefficient.py: functions to compute p values with kruskal-wallis
    * requirements.txt: version of python packages and libraries used in scripts

