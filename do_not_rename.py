#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 14:47:43 2021

@author: lt-afm
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

df = pd.read_csv(file_name+".csv",names=column_names)

df.plot(
        subplots=True, figsize=(6, 6), title=str(file_name)
    )

plt.show()


