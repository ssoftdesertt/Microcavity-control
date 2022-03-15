#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 14:47:43 2021

@author: softdesert
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import shutil

file_name = os.path.splitext(os.path.basename(__file__))[0]
print(file_name)
df = pd.read_csv(file_name+".csv", index_col=0)

# THESE MUST BE CHANGED FOR NEW ANALOG DISCOVERY SET UP
# dc# names correspond to connections made on each analog discovery but are sorted here under list transformation
steps = df.steps.to_list()
DC_1550 = df.dc1.to_list() 
DC_1310 = df.dc2.to_list()
AMPLITUDE = df.dc3.to_list()
PHASE = df.dc4.to_list()
AC_TO_DC_GAIN = (28000000/20000)**(-1)

peaks = spy.find_peaks_cwt(np.array(DC_1550),0.1)
avg = np.mean(np.diff(peaks))
steps_to_distance_ratio = (1550/2)/avg #nm per step
print('PEAKS: '+str(peaks))
print('AVERAGE SEPERATION: '+str(avg))
print('steps to distance ratio: '+str(steps_to_distance_ratio)+'nm/step')



SCALE_X_AXIS = [float(i*steps_to_distance_ratio) for i in df.steps.to_list()[:-1]]

# numerical approach to sensitivity calculation
# Derivative = []
# ABS_Derivative = []
# for i in range(200-1):
#    Derivative.append((DC_1550[i+1]-DC_1550[i])/steps_to_distance_ratio)
#    ABS_Derivative.append(abs((DC_1550[i+1]-DC_1550[i])/steps_to_distance_ratio))

# scaled_amplitude = []
# for num1, num2 in zip(Derivative, AMPLITUDE):
# 	scaled_amplitude.append(abs(num1)**(-1) * num2)

#PLOT SENSITIVITY NUMERICALLY
# plt.figure(1)
# plt.plot(SCALE_X_AXIS,Derivative)
# plt.ylabel('Sensitivity (V/nm)', size=16, name='FreeSans')
# plt.xlabel('Fiber Position (nm)', size=16, name = 'FreeSans')
# plt.title('Cantilever Sensitivity from 1550DC')
# plt.legend()


# See all data
fig, axs = plt.subplots(4)
fig.suptitle('Microcavity analysis')
axs[0].plot(steps, AMPLITUDE)
axs[1].plot(steps, PHASE)
axs[2].plot(steps, DC_1550)
axs[3].plot(steps, DC_1310)

# analytic approach to sensitivity calculation

# range in terms of steps
lower = 34
upper = 48

# visualize desired range
plt.figure(2)
plt.plot(steps[lower:upper],DC_1550[lower:upper], marker='.')
plt.ylabel('Amplitude (V)', size=16)
plt.xlabel('steps', size=16)
plt.title('1550DC Signal')

# fit data
coefficients = np.polyfit(steps[lower-1:upper+1],DC_1550[lower-1:upper+1], 6)
poly = np.poly1d(coefficients)
derivative = poly.deriv()

new_x = np.linspace(steps[lower],steps[upper],1000)
new_y = poly(new_x)
nnew_y = abs(derivative(new_x))*AC_TO_DC_GAIN/steps_to_distance_ratio


plt.figure(3)
plt.plot(steps[lower:upper],DC_1550[lower:upper],'.', new_x, new_y)
plt.ylabel('Amplitude (V)', size=16)
plt.xlabel('steps', size=16)
plt.title('1550DC Signal')

#plot sensitivity and add 1550DC values to each point
plt.figure(5)
plt.plot(new_x,nnew_y,".")
plt.ylabel('Sensitivity (V/nm)', size=16)
plt.xlabel('steps', size=16)
plt.title('Sensitivity')
for i, txt in enumerate(new_y[:-1]):
    plt.annotate(round(txt,4) , (new_x[i], nnew_y[i]),fontsize='xx-small')

plt.show()


