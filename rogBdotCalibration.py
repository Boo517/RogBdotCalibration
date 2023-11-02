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
import matplotlib.pyplot as plt
import numpy as np

#%%
"""
EXPERIMENTAL VALUES
"""
# attenuator on pearson coil
pearson_dB = 19.82
pearson = 100  # [A/V] from 0.01 V/A as labelled
# attenuators on rogowskis, from Ann's code (and scopePlotting)
rog1_dB = 19.82
rog2_dB = 19.49
attenuation = [0, pearson_dB, rog1_dB, rog2_dB, 0]    

# TODO: get dimensions of coil for magnetic field + make sure eqn works
# for our setup (magnetostatics holds?Not a full loop? long?)

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
    # e.g 102323s5c2b5_90 for rog1 data (c2) on 10-23-23's shot 5 (s5) w/ 
    # bdot 5 (b5) rotated 90 degrees (_90)
    # 'dateshot' holds date and shot, and 'bdot' holds bdot# and orientation
    name = filename.split('/')[-1].split('.')[0]    # filename without path
    (dateshot, bdot) = name.split('c')  # pieces either side of channel# 
    bdot = bdot[1:]     # get rid of channel# after 'c'
    
    # need to load first channel to get # of data rows to preallocate array
    data = np.genfromtxt(folder+dateshot+'c1'+bdot+'.csv', skip_header=6, 
                         delimiter=',', usecols=(3, 4))
    # expand data array so all channels can fit
    # though each file has its own time column, they're all the same 
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
raw_0 = loadData(file_0)

file_90 = spl.getfile("90 degree")
raw_90 = loadData(file_90)
folder = spl.filefolder(file_0)

#%%
"""
PLOTTING AND SCHEMING AND CALCULATING
"""

def plotBoth(data_0, data_90, labels, title):
    fig, (ax1, ax2) = plt.subplots(2,1)
    fig.suptitle(title)
    ax1.set_title("bdot 0 degrees")
    ax2.set_title("bdot 90 degrees")
    for channel in range(1, 5):
        ax1.plot(data_0[:,0], data_0[:,channel], label=labels[channel])
        ax2.plot(data_90[:,0], data_90[:,channel], label=labels[channel])
    ax1.set_xlabel(labels[0])
    ax2.set_xlabel(labels[0])
    ax1.legend()
    ax2.legend()

#%%
"""
RAW SIGNALS
"""
# raw values
raw_labels = ["times [s]", "pearson [raw]", 
          "rog1 [raw]", "rog2 [raw]", "bdot [raw]"]
plotBoth(raw_0, raw_90, raw_labels, "Raw Plots")

# de-attenuate signals
deatten_0 = raw_0[:,:]
deatten_90 = raw_90[:,:]
for channel in range(1,4):
    deatten_0[:, channel] = spl.deAttenV(deatten_0[:, channel], 
                                         attenuation[channel])
    deatten_90[:, channel] = spl.deAttenV(deatten_90[:, channel], 
                                         attenuation[channel])
deatten_labels = ["times [s]", "pearson [V]", 
          "rog1 [V]", "rog2 [V]", "bdot [V]"]
plotBoth(deatten_0, deatten_90, deatten_labels, "De-attenuated Signals")

#%%
"""
INTEGRATION
"""
# integrate d/dts 
integrated_0 = deatten_0[:,:]
integrated_90 = deatten_90[:,:]
for channel in range(2,5):
    integrated_0[:, channel] = spl.cumtrapz(integrated_0[:, 0], 
                                            integrated_0[:, channel])
    # TODO: should bdot integration be skipped for 90?
    integrated_90[:, channel] = spl.cumtrapz(integrated_90[:, 0], 
                                            integrated_90[:, channel])
integrated_labels = ["times [s]", "pearson [V]", 
          "rog1 [V*s]", "rog2 [V*s]", "bdot [V*s]"]
plotBoth(integrated_0, integrated_90, integrated_labels, "Integrated Voltages")
# NOTE: integrated signals have a VERY small amplitude, as the time we're
# integrating over is very short
#%%
"""
OBTAINING CONSTANTS
"""
scaled_0 = integrated_0[:,:]
scaled_90 = integrated_90[:,:]
# multiply pearson by its constant to get current from voltage
scaled_0[:,1] = scaled_0[:,1]*pearson
scaled_90[:,1] = scaled_90[:,1]*pearson

nchannels = integrated_0.shape[1]   # #of channels = #of columns
# first rows are constants, second rows are stdev for an extra check
constants_0 = np.ones((2, nchannels))    
constants_90 = constants_0[:,:]

# integrated signal needs to be multiplied by a constant to match real current
# so, obtain this constant by dividing the current by the integrated signal
# integrated [V*s] * C [A/(V*s)] = current [A] -> C = current/integrated
# this breaks down for current == 0, so create a mask to skip these
# and in fact, small number/small number gives numerical error, so 
# only pick places where the signal is > 25% of max
time = scaled_0[:,0]
pearson_0 = scaled_0[:,1]
pearson_90 = scaled_90[:,1]
signal_mask_0 = abs(pearson_0) >= .25*max(pearson_0)
for channel in range(2, 4):
    scale = pearson_0[signal_mask_0]/(scaled_0[:, channel][signal_mask_0]) 
    constants_0[0, channel] = np.mean(scale[np.logical_not(np.isnan(scale))])
    print("constant {}: {}, stdev={}".format(
        channel, constants_0[0,channel], np.std(scale)))
    
scaled_labels = ["times [s]", "pearson [V]", 
          "rog1 [V]", "rog2 [V]", "bdot [V]"]
plotBoth(integrated_0, integrated_0*constants_0[0,:], scaled_labels, "gwagwa")
    
        