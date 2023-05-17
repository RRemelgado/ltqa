# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 14:39:01 2022

@author: rr70wedu
"""

#----------------------------------------------------------------------------#
# read modules and command line arguments
#----------------------------------------------------------------------------#

from argparse import ArgumentParser
import rasterio as rt
import numpy as np

parser = ArgumentParser(description = 'map last data year')

parser.add_argument("wdir", help="working directory")

parser.add_argument(
    "-y", "--year",
    help = "target year",
    dest = "year",
    required = True,
    metavar = 4,
    type = str,
)

parser.add_argument(
    "-t", "--time",
    help = "acquisition time (day or night)",
    dest = "time",
    required = True,
    metavar = 4,
    type = str,
)

parser.add_argument(
    "-r", "--reference",
    help = "image with reference extent and resolution",
    dest = "reference",
    required = True,
    metavar = 4,
    type = str,
)

options = parser.parse_args()
reference = options.reference
wdir = options.wdir
time = options.time
target = options.year

#----------------------------------------------------------------------------#
# associate tile geometries to their respective ID's
#----------------------------------------------------------------------------#

minYear = 1982

reference = rt.open(reference)

ids = rt.open('f{wdir}LTQA-{time}_imageFrequency_{target}0000_1km.tif')

p = reference.meta.copy()
p.update(dtype='int16', compress='deflate', predict=2, zlevel=9)

ods = rt.open(f'{wdir}LTQA-{time}-lastYear_{target}0000_1km.tif', 'w', **p)

nr = ids.height
nc = ids.width

ind = np.array_split(np.asarray(range(0,nr)), 20) # window indices

for i in range(0, 20):
    
    # define processing window
    ro = np.min(ind[i]) # row ofset
    ne = np.max(ind[i])-np.min(ind[i])+1 # nr. of rows
    w = rt.windows.Window(0, ro, nc, ne) # window (input)
    
    ia = ids.read(1, window=w)
    ra = reference.read(1, window=w)
    
    oa = np.zeros((ne,nc), dtype='int16')
    oa[np.where((ra == 1) & (ia > 0))] = int(target)
    
    px = np.where((ra == 1) & (ia == 0))
    
    year = int(target)-1
    
    while (len(px[0]) > 0) & (year >= minYear):
        ta = rt.open(f'{wdir}LTQA-{time}_imageFrequency_{year}0000_1km.tif').read(1, window=w)
        ta[ta == 255] = 0
        oa[np.where((ra == 1) & (ta > 0) & (oa == 0))] = year
        px = np.where((ra == 1) & (oa == 0))
        year = year-1
    
    ods.write(oa, window=w, indexes=1)
    
    print(i)

ods.close()
