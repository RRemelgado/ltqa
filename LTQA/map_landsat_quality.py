# -*- coding: utf-8 -*-
"""
Created on Sat Jul 31 01:35:16 2021

@author: rr70wedu
"""

#----------------------------------------------------------------------------#
# read modules and command line arguments
#----------------------------------------------------------------------------#

from argparse import ArgumentParser
from rasterio.mask import mask
from os.path import join
import rasterio as rt
import pandas as pd
import fiona as fn
import numpy as np

parser = ArgumentParser(description = 'map yearly landsat quality')

parser.add_argument("output", help = "path to output directory")

parser.add_argument(
    "-m", "--metadata",
    help = "path to csv with metadata",
    dest = "meta",
    required = True,
    metavar = 4,
    type = str,
)

parser.add_argument(
    "-s", "--tiles",
    help = "path to shp with wrs tiling system",
    dest = "tiles",
    required = True,
    metavar = 4,
    type = str,
)

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
odir = options.output
tiles = options.tiles
time = options.time
year = options.year
meta = options.meta

# read metadata on acquisition quality
meta = pd.read_csv(meta, dtype={'tile_id':str, 'year':str})

#----------------------------------------------------------------------------#
# associate tile geometries to their respective ID's
#----------------------------------------------------------------------------#

wrs = {}

wrs['shp'] = fn.open(tiles)
wrs['tid'] = ['{0:03d}'.format(s['properties']['PATH']) + \
                    '{0:03d}'.format(s['properties']['ROW']) for \
                        s in wrs['shp']]

#----------------------------------------------------------------------------#
# read reference layer and build output image profiles
#----------------------------------------------------------------------------#

reference = rt.open(reference)
nr = reference.height
nc = reference.width
p1 = reference.meta.copy()
p1.update(dtype='float32', compress='deflate', predict=2, zlevel=9, nodata=0)
p2 = reference.meta.copy()
p2.update(dtype='uint8', compress='deflate', predict=2, zlevel=9, nodata=0)
p3 = reference.meta.copy()
p3.update(dtype='float32', compress='deflate', predict=2, zlevel=9, nodata=None)
p4 = reference.meta.copy()
p4.update(dtype='uint16', compress='deflate', predict=2, zlevel=9, nodata=0)

#----------------------------------------------------------------------------#
# build initial layers
#----------------------------------------------------------------------------#

oname = join(odir, f'LTQA-{time}_nrTiles_{year}0000_1km.tif')
nt_ds = rt.open(oname, 'w+', **p2)

oname = join(odir, f'LTQA-{time}_totalQuality_{year}0000_1km.tif')
iq_ds = rt.open(oname, 'w+', **p1)

oname = join(odir, f'LTQA-{time}_imageFrequency_{year}0000_1km.tif')
yc_ds = rt.open(oname, 'w+', **p4)

oname = join(odir, f'LTQA-{time}_monthFrequency_{year}0000_1km.tif')
mc_ds = rt.open(oname, 'w+', **p2)

oname = join(odir, f'LTQA-{time}_distributionQuality_{year}0000_1km.tif')
dq_ds = rt.open(oname, 'w+', **p3)

oname = join(odir, f'LTQA-{time}_distributionBalance_{year}0000_1km.tif')
dq_db = rt.open(oname, 'w+', **p3)

oname = join(odir, f'LTQA-{time}_maxQuality_{year}0000_1km.tif')
mx_ds = rt.open(oname, 'w+', **p3)

#----------------------------------------------------------------------------#
# find relevant tiles
#----------------------------------------------------------------------------#

# access metadata for target year
ind = np.where((meta['year'] == year) & (meta['dayOrNight'] == time))[0]

#----------------------------------------------------------------------------#
# build quality layers
#----------------------------------------------------------------------------#

for i in range(0, len(ind)):
    
    try:
        
        # target bounding box
        rid = meta['tile_id'].values[ind[i]]
        
        # extraxt bounding box geometry
        f = wrs['shp'][wrs['tid'].index(rid)]['geometry']
        
        # make mask of tile over reference array
        ia = mask(reference, [f], all_touched=True, pad=True, \
                    pad_width=1, crop=True, indexes=1, nodata=255)
                   
        px = reference.index(ia[1].c, ia[1].f)
        w = rt.windows.Window(px[1], px[0], ia[0].shape[1], ia[0].shape[0])
        ia = (ia[0] < 255).astype('uint8')
        
        #====================================================================#
        # update quality layers
        #====================================================================#
        
        oa = nt_ds.read(1, window=w) + ia
        nt_ds.write(oa.astype('uint8'), window=w, indexes=1)
        
        oa = iq_ds.read(1, window=w) + \
            meta['total_quality'].values[ind[i]] * ia
        iq_ds.write(oa.astype('float32'), window=w, indexes=1)
        
        oa = yc_ds.read(1, window=w) + \
            meta['image_count'].values[ind[i]] * ia
        yc_ds.write(oa.astype('uint16'), window=w, indexes=1)
        
        oa = mc_ds.read(1, window=w) + \
            meta['month_count'].values[ind[i]] * ia
        mc_ds.write(oa.astype('uint8'), window=w, indexes=1)
        
        oa = dq_ds.read(1, window=w) + \
            meta['distribution_quality'].values[ind[i]] * ia
        dq_ds.write(oa.astype('float32'), window=w, indexes=1)
        
        oa = dq_db.read(1, window=w) + \
            meta['distribution_balance'].values[ind[i]] * ia
        dq_db.write(oa.astype('float32'), window=w, indexes=1)
        
        oa = mx_ds.read(1, window=w) + \
            meta['max_quality'].values[ind[i]] * ia
        mx_ds.write(oa.astype('float32'), window=w, indexes=1)
        
        del oa
    
    except:
        
        print(rid + ' not in tile system (likely polar; wrong time assined')
    
    print(i)

#----------------------------------------------------------------------------#
# close dataset access
#----------------------------------------------------------------------------#

nt_ds.close()
iq_ds.close()
yc_ds.close()
mc_ds.close()
dq_ds.close()
dq_db.close()
mx_ds.close()

#----------------------------------------------------------------------------#
# update data within tile overlaps
#----------------------------------------------------------------------------#

nt_ds = rt.open(join(odir, 'LTQA-{time}_nrTiles_{year}0000_1km.tif'))

a0 = nt_ds.read(1)

mc_ds = rt.open(join(odir, 'LTQA-{time}_monthFrequency_{year}0000_1km.tif'), 'r+')
oa = mc_ds.read(1).astype('float32')
px = np.where(oa > 0)
oa[px] = oa[px] / a0[px]
mc_ds.write(oa.astype('uint8'), indexes=1)
mc_ds.close()

del oa

dq_ds = rt.open(join(odir, 'LTQA-{time}_distributionQuality_{year}0000_1km.tif'), 'r+')
oa = dq_ds.read(1)
px = np.where(oa > 0)
oa[px] = oa[px] / a0[px]
dq_ds.write(oa, indexes=1)
dq_ds.close()

del oa

dq_db = rt.open(join(odir, 'LTQA-{time}_distributionBalance_{year}0000_1km.tif'), 'r+')
oa = dq_db.read(1)
px = np.where((oa < 0) | (oa > 0))
oa[px] = oa[px] / a0[px]
dq_db.write(oa, indexes=1)
dq_db.close()

del oa

mx_ds = rt.open(join(odir, 'LTQA-{time}_maxQuality_{year}0000_1km.tif'), 'r+')
oa = mx_ds.read(1)
px = np.where(oa > 0)
oa[px] = oa[px] / a0[px]
mx_ds.write(oa, indexes=1)
mx_ds.close()

# print('---------------------------------------------------------------------')
# print(year)
# print('---------------------------------------------------------------------')
