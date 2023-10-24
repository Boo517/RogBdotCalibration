# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 13:52:15 2023

@author: P3 Lab Office
"""

#%%
"""
IMPORTS
"""
import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
import numpy as np

#%%
"""
filepath = getfile()
this function opens a file select dialog through Tkinter and returns 
the path to the selected file
"""
def getfile():
    root = Tkinter.Tk()
    root.after(100, root.focus_force)
    root.after(200,root.withdraw)    
    filepath = tkFileDialog.askopenfilename(parent=root,title='Pick a file')    
    return filepath 

#%%
"""
folder = filefolder(filepath)
returns parent folder of a file, including an extra '/' so it's easier to 
add new files to the folder
ex: 
    In:     filefolder("C:/test/test.txt")
    Out:    "C:/test/"
"""
def filefolder(filepath):
    folder = '/'.join(filepath.split('/')[:-1]) + '/'
    return folder

#%%
"""
get actual voltage, accounting for attenuation
using the formula 'attenuation[dB] = 20*log(V_in/V_out)'
-> V_in = V_out*10^(dB/20)
"""
def deAttenV(attenuated, attenuation):
    return attenuated*10**(attenuation/20)

#%%
"""
similar to the matlab function of the same name,
this function returns a vector the same shape as y(t) containing the 
cumulative trapezoidal integration of y(t) over the time vector t
with initial value 0 
"""
def cumtrapz(t, y):
    dt = np.diff(t)     #timesteps
    integration = np.cumsum(dt*(y[0:-1]+y[1:])/2)
    return np.concatenate(([0.0], integration))