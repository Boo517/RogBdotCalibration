# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 13:51:09 2023

@author: P3 Lab Office
"""

#%%
"""
IMPORTS
"""
import scopePlottingLib as spl
import numpy as np

#%%
"""
data = loadData(filename)
The scope separates channels into separate files, so we need to get all the 
files/channels from 1 shot and combine them into a single data array.
We can get all files from a given shot using the name of a single file/channel
from that shot
format of 'data' is [time, c1, c2, c3, c4] = [t, pearson, rog1, rog2, bdot]
"""
def loadData(filename):
    folder = spl.filefolder(filename)
    # file format is [date]/s[shot#]/c[channel#]/b[bdot#]/_/[bdot orientation]
    # 'dateshot' holds date and shot, and 'bdot' holds bdot# and orientation
    name = filename.split('/')[-1].split('.')[0]    # filename without path
    (dateshot, bdot) = name.split('c')  # pieces either side of channel# 
    bdot = bdot[1:]     # get rid of channel# after 'c'
    
    # need to load first channel to get # of data rows to preallocate array
    data = np.genfromtxt(folder+dateshot+'c1'+bdot+'.csv', skip_header=6, 
                         delimiter=',', usecols=(3, 4))
    # expand data array so all channels can fit
    # though each file has its own time column, they're all the same in reality
    # so only need space for 3 remaining data columns
    data = np.pad(data, ((0,0),(0,3)), constant_values=np.nan)
    # first two columns are time and c1, already obtained from file1
    for channel in [2, 3, 4]:
        # scope output file has 6 lines of headers, and 5 columns,
        # of which the first 3 (0,1,2) are always empty in the actual data
        # and the 4th (3) is the time column already obtained 
        col = np.genfromtxt(folder+dateshot+'c'+str(channel)+bdot+'.csv', 
                            skip_header=6, delimiter=',', usecols=4)
        data[:, channel] = col
    return data

#%%
"""
FILE SELECT/LOAD
"""
# choose a file for 0 degree and 90 degree orientation
# both provide rogowski calibration vals
# 0 degree gives bdot values, and 90 degree gives an idea of error bounds
# as 90 degree bdot should have no signal
file_0 = spl.getfile("0 degree")
data_0 = loadData(file_0)
file_90 = spl.getfile("90 degree")
data_90 = loadData(file_90)
folder = spl.filefolder(file_0)

    
        