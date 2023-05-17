# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 13:24:18 2023

@author: remelgado
"""

#----------------------------------------------------------------------------#
# load arguments / modules
#----------------------------------------------------------------------------#

from statsmodels.nonparametric.smoothers_lowess import lowess
from argparse import ArgumentParser
from rasterio.mask import mask
from progress.bar import Bar
from os.path import join
import rasterio as rt
import pandas as pd
import numpy as np
import fiona as fn
import glob2 as g
import sys

parser = ArgumentParser(description = 'Pre-classification of water bodies')
parser.add_argument("smoothing", help = "logical argument indicating if \
    smoothing should be applied", action=argparse.BooleanOptionalAction)
parser.add_argument("boundaries", help = "shapefile with country boundaries")
parser.add_argument("path_a", help = "path to dependent variable")
parser.add_argument("path_b", help = "path to independent variable")


options = parser.parse_args()
smoothing = options.smoothing
boundaries = int(options.boundaries)
path_a = int(options.path_a)
path_b = int(options.path_b)

#----------------------------------------------------------------------------#
# load data
#----------------------------------------------------------------------------#

# list files on (in)dependent variable
files_a = sorted(g.glob(join(path_a, '*.tif')))
files_b = sorted(g.glob(join(path_b, '*.tif')))
n = len(files_a)

# bounding box of the region of interest (ROI)
bbox = [fn.open(boundaries)['geometry']]

#----------------------------------------------------------------------------#
# load images with (in)depent variable(s) over the ROI
#----------------------------------------------------------------------------#

a = [mask(rt.open(f), bbox, crop=True, 
          all_touched=True, indexes=1, nodata=0)[0] for f in files_a]

a = np.stack(a, axis=2)

b = [mask(rt.open(f), bbox, crop=True, 
          all_touched=True, indexes=1, nodata=0)[0] for f in files_b]

b = np.stack(b, axis=2)

#----------------------------------------------------------------------------#
# find suitable pixels and extract samples
#----------------------------------------------------------------------------#

# locate suitable pixels
px = np.where((np.max(a, axis=2) > 0) & (np.min(b, axis=2) == 0))

# control variable specifying the indentity of time steps (needed for lowess)
x = np.array(range(1,n+1))

if len(px[0]) == 0:
    sys.exit()

#----------------------------------------------------------------------------#
# extract samples
#----------------------------------------------------------------------------#

bar = Bar('processing data for ', max=len(px[0]))

samples = []

for p in range(0,len(px[0])):
    
    # read data for (in)dependent data
    a = a[px[0][p],px[1][p],:]
    b = b[px[0][p],px[1][p],:]
    
    # apply smoothing
    if smoothing:
        a = lowess(a, x, frac=0.4, return_sorted=False)
        b = lowess(b, x, frac=0.4, return_sorted=False)
    
    # record samples, where A/B is the difference between a/b and its smoothed curve
    samples.append(pd.DataFrame({'a':a, 'b':b}))
    
    # add empty, nodata row (needed by CCM implementation)
    samples.append(pd.DataFrame({'a':[np.nan], 'b':[np.nan]}))
    
    bar.next()

bar.finish()

#----------------------------------------------------------------------------#
# export
#----------------------------------------------------------------------------#

samples = pd.concat(samples)
samples.to_csv("samples.csv", index=False)
