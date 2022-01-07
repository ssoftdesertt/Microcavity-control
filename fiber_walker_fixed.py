#!/usr/bin/env python2

'''
09 May 2019
TODO: make simple web app gui for controlling sweeping and fiber walker.
'''
from ctypes import *
from dwfconstants import *
import time
import math
import sys
import os
import os.path
import pandas as pd
import fire
from scipy import signal
import numpy as np

import os
import shutil

import matplotlib.pyplot as plt
from subprocess import call


def walk(amp, pulses, save_data):
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary(
            "/Library/Frameworks/dwf.framework/dwf"
        )
    else:
        dwf = cdll.LoadLibrary("libdwf.so")
    sts = c_byte()
    cSamples = 4096
    # declare ctype variables
    IsInUse = c_bool()
    hdwf = c_int()
    rghdwf = []
    cChannel = c_int()
    cDevices = c_int()
    voltage = c_double()
    sts = c_byte()

    # declare string variables
    devicename = create_string_buffer(64)
    serialnum = create_string_buffer(16)

    # declare ctype variables
    rgdSamples1 = (c_double * cSamples)()
    rgdSamples2 = (c_double * cSamples)()
    rgdSamples3 = (c_double * cSamples)()
    rgdSamples4 = (c_double * cSamples)()

    channel1 = c_int(0)
    channel2 = c_int(1)

    # print DWF version
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print(("DWF Version: " + str(version.value)).encode())

    # enumerate connected devices
    dwf.FDwfEnum(c_int(0), byref(cDevices))
    if cDevices.value == 0:
        print("No device found")
        dwf.FDwfDeviceCloseAll()
        sys.exit(0)
    # open device
    "Opening first device..."
    for iDevice in range(0, cDevices.value):
        dwf.FDwfEnumDeviceName(c_int(iDevice), devicename)
        dwf.FDwfEnumSN(c_int(iDevice), serialnum)
        print("------------------------------")
        
        print(("Device " + str(iDevice + 1) 
        + " : \t" + devicename.value.decode() + "\t" + serialnum.value.decode()))
        
        
        
        dwf.FDwfDeviceOpen(c_int(iDevice), byref(hdwf))
        
        if hdwf.value == 0:
            szerr = create_string_buffer(512)
            dwf.FDwfGetLastErrorMsg(szerr)
            print(szerr.value)
            dwf.FDwfDeviceCloseAll()
            sys.exit(0)
        rghdwf.append(hdwf.value)
    if hdwf.value == hdwfNone.value:
        print("failed to open device")
        quit()
    timestr = time.strftime(
        "%m%d%Y-%H%M%S"
    )  # time of operation
    hzFreq = 2e3  # Wave frequency

    if amp < 0:
        print('you have selected a negative value, quitting')
        dwf.FDwfDeviceCloseAll()
        quit()
    if amp == 0:
        print('you have selected a zero value, quitting')
        dwf.FDwfDeviceCloseAll()
        quit()
    if 0 < amp < 5:
        print('amplitude = ' + str(amp))
        amp = amp
    if 5 <= amp < 10:
        check = eval(input(
            'you have selected a large amplitude, are you sure? (1/0): '
        ))
        if check == 1:
            amp = amp
            print('amplitude = ' + str(amp))
        else:
            dwf.FDwfDeviceCloseAll()
            quit()
    # pulses = input('input integer no. pulses: ')
    if pulses < 0:
        pulses = abs(int(round(pulses)))
        direc = -1.0
        print('leaving sample; ' + str(pulses) + ' steps')
    elif pulses > 0:
        pulses = int(round(pulses))
        direc = 1.0
        print('approaching sample; ' + str(
            pulses
        ) + ' steps')
    else:
        print('you have selected incorrect value, quitting')
        dwf.FDwfDeviceCloseAll()
        quit()
    # samples between -1 and +1
    for i in np.arange(0, len(rgdSamples1)):
        # rgdSamples[i] = 1.0*i/cSamples;
        
        
        rgdSamples1[i] = direc*signal.sawtooth(2*np.pi*i/len(rgdSamples1) + np.pi)
        rgdSamples2[i] = direc*signal.sawtooth(2*np.pi*i/len(rgdSamples1) + np.pi)
        rgdSamples3[i] = direc*signal.sawtooth(2*np.pi*i/len(rgdSamples1) + np.pi)
        rgdSamples4[i] = direc*signal.sawtooth(2*np.pi*i/len(rgdSamples1) + np.pi)

    
    
    time.sleep(1)
    # __________________________________________________

    if save_data == 'n':
        path = './data/temp'
    else:
        path = (
            './data/'
            + timestr
        )
    print(path)
    if not os.path.isdir(path):
        os.makedirs(path)
    # logging information into .txt file
    logpath = path + '/' + timestr + '_log.txt'
    ff = open(logpath, 'w+')
    ff.write(
        '%s \n %s \n %s \n %s \n'
        % (
            'date: ' + timestr,
            'Amplitude = ' + str(amp) + 'V',
            'Steps: ' + str(pulses),
            'Direction: ' + str(direc),
        )
    )
    ff.write(logpath)
    ff.close
    print(('data log saved to :' + path))
    # __________________________________________________

    print("Generating custom waveform...")

    # Setting up the parameters for waveform
    hdwf.value = rghdwf[0]

    dwf.FDwfAnalogOutNodeEnableSet(
        hdwf, channel1, AnalogOutNodeCarrier, c_bool(True)
    )
    dwf.FDwfAnalogOutNodeFunctionSet(
        hdwf, channel1, AnalogOutNodeCarrier, funcCustom
    )  # Define custom waveform; funcCustom
    dwf.FDwfAnalogOutNodeDataSet(
        hdwf,
        channel1,
        AnalogOutNodeCarrier,
        rgdSamples1,
        c_int(cSamples),
    )
    dwf.FDwfAnalogOutNodeFrequencySet(
        hdwf,
        channel1,
        AnalogOutNodeCarrier,
        c_double(hzFreq),
    )  # Set frequency attribute in Hz
    dwf.FDwfAnalogOutNodeAmplitudeSet(
        hdwf, channel1, AnalogOutNodeCarrier, c_double(amp)
    )  # Set amplitude attribute in Volts
    dwf.FDwfAnalogOutNodeOffsetSet(
        hdwf, channel1, AnalogOutNodeCarrier, c_double(0)
    )

    dwf.FDwfAnalogOutRunSet(
        hdwf, channel1, c_double(1 / hzFreq)
    )  # run for 1 periods
    dwf.FDwfAnalogOutWaitSet(
        hdwf, channel1, c_double(1 / hzFreq)
    )  # wait one pulse time
    dwf.FDwfAnalogOutRepeatSet(
        hdwf, channel1, c_int(1)
    )  # repeat 1 times

    # set up acquisition
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(20000000.0))
    dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(4096))
    dwf.FDwfAnalogInChannelEnableSet(
        hdwf, c_int(0), c_bool(True)
    )
    dwf.FDwfAnalogInChannelRangeSet(
        hdwf, c_int(0), c_double(10)
    )
    dwf.FDwfAnalogInChannelEnableSet(
        hdwf, c_int(1), c_bool(True)
    )
    dwf.FDwfAnalogInChannelRangeSet(
        hdwf, c_int(1), c_double(10)
    )

    # start analog-in (Scope)
    for iDevice in range(len(rghdwf)):
        hdwf.value = rghdwf[iDevice]
        dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))
    print("   waiting to finish")
    time.sleep(1)

    list_reflection = []
    list_steps = []
    list_voltage = []

    j = 1
    print_count = 0

    # __________________________________________________

    # initialize one pulse to remove voltage spike
    hdwf.value = rghdwf[0]

    dwf.FDwfAnalogOutConfigure(
        hdwf, channel1, c_bool(True)
    )  # starts the waveform
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value:
            break
        time.sleep(0.001)
    dwf.FDwfAnalogInStatusData(
        hdwf, 0, rgdSamples1, 4096
    )  # get channel 1 data
    dwf.FDwfAnalogInStatusData(
        hdwf, 1, rgdSamples2, 4096
    )  # get channel 2 data

    hdwf.value = rghdwf[1]
    while True:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if sts.value == DwfStateDone.value:
            break
        time.sleep(0.001)
    time.sleep(0.1)
    print("Acquisition finished")

    dwf.FDwfAnalogInStatusData(
        hdwf, 0, rgdSamples3, 4096
    )  # get channel 1 data
    dwf.FDwfAnalogInStatusData(
        hdwf, 1, rgdSamples4, 4096
    )  # get channel 2 data
    #################################
    time.sleep(0.1)
    while j < pulses + 1:
        try:
            print(j)
            hdwf.value = rghdwf[0]
            dwf.FDwfAnalogOutConfigure(
                hdwf, channel1, c_bool(True)
            )  # starts the waveform

            # begin acquisition
            time.sleep(0.5)

            while True:
                dwf.FDwfAnalogInStatus(
                    hdwf, c_int(1), byref(sts)
                )
                if sts.value == DwfStateDone.value:
                    break
                time.sleep(0.001)
            time.sleep(0.1)
            print("Acquisition finished")

            dwf.FDwfAnalogInStatusData(
                hdwf, 0, rgdSamples1, 4096
            )  # get channel 1 data
            dwf.FDwfAnalogInStatusData(
                hdwf, 1, rgdSamples2, 4096
            )  # get channel 2 data

            hdwf.value = rghdwf[1]
            while True:
                dwf.FDwfAnalogInStatus(
                    hdwf, c_int(1), byref(sts)
                )
                if sts.value == DwfStateDone.value:
                    break
                time.sleep(0.001)
            time.sleep(0.1)
            print("Acquisition finished")

            dwf.FDwfAnalogInStatusData(
                hdwf, 0, rgdSamples3, 4096
            )  # get channel 1 data
            dwf.FDwfAnalogInStatusData(
                hdwf, 1, rgdSamples4, 4096
            )  # get channel 2 data

            dc1 = sum(rgdSamples1) / len(rgdSamples1)
            print("DC1: " + str(dc1) + "V")

            dc2 = sum(rgdSamples2) / len(rgdSamples2)
            print("DC2: " + str(dc2) + "V")

            dc3 = sum(rgdSamples3) / len(rgdSamples3)
            print("DC3: " + str(dc3) + "V")

            dc4 = sum(rgdSamples4) / len(rgdSamples4)
            print("DC4: " + str(dc4) + "V")

            rgpy1 = [0.0] * len(rgdSamples1)
            for i in range(0, len(rgpy1)):
                rgpy1[i] = rgdSamples1[i]
            rgpy2 = [0.0] * len(rgdSamples2)
            for i in range(0, len(rgpy2)):
                rgpy2[i] = rgdSamples2[i]
            rgpy3 = [0.0] * len(rgdSamples3)
            for i in range(0, len(rgpy2)):
                rgpy3[i] = rgdSamples3[i]
            rgpy4 = [0.0] * len(rgdSamples4)
            for i in range(0, len(rgpy4)):
                rgpy4[i] = rgdSamples4[i]
            list_reflection.append([j, dc1, dc2, dc3, dc4])

            df_reflection = pd.DataFrame(
                list_reflection,
                columns=[
                    'steps',
                    'dc1',
                    'dc2',
                    'dc3',
                    'dc4',
                ],
            )

            if print_count == 100:
                print('data dumped to csv')
                df_reflection.to_csv(
                    path
                    + '/'
                    + timestr
                    + '_detector_signal.csv',
                    columns=[
                        'steps',
                        'dc1',
                        'dc2',
                        'dc3',
                        'dc4',
                    ],
                    mode='w',
                )
                print_count = 0
            j = j + 1
            print_count = print_count + 1
        except KeyboardInterrupt:
            break
    df_reflection = pd.DataFrame(
        list_reflection,
        columns=['steps', 'dc1', 'dc2', 'dc3', 'dc4'],
    )

    df_reflection.to_csv(
        path + '/' + timestr + '_detector_signal.csv',
        columns=['steps', 'dc1', 'dc2', 'dc3', 'dc4'],
        mode='w',
    )

    df_plot = df_reflection.loc[
        :, df_reflection.columns != 'steps'
    ]
    df_plot.plot(
        subplots=True, figsize=(6, 6), title=timestr
    )
    plt.savefig(path + '/' + timestr + 'plot.png')

    plt.show()
    print("done.")
    dwf.FDwfDeviceCloseAll()
    
    # section to rename and save template file called 'do_not_rename.py'
    
    if save_data == 'n':
        exit
    else:
        src_dir = os.getcwd() # get current directory
        dest_dir = src_dir+"/data"+"/"+timestr # define destination directory
        src_file = os.path.join(src_dir,'do_not_rename.py') # tell python what the template file is
        shutil.copy(src_file,dest_dir) # copy the template file into the destination directory
        dst_file = os.path.join(dest_dir,'do_not_rename.py') # access the destination file
        new_dst_file_name = os.path.join(dest_dir,timestr + '_detector_signal.py') # define new name
        os.rename(dst_file, new_dst_file_name) # actually rename

'''
if __name__ == '__main__':
    fire.Fire(walk)
'''