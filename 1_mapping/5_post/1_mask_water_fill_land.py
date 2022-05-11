#!/usr/bin/env python3

# apply land/water mask so all previous nodata pixels on land remain zero and all water pixels become nodata

import sys, os
sys.path.append('/mnt/data3/sgorelik/repos/raspy')
from raspy import *

# water/land probability (0-75 = water; 76-100 = land; 255 = fill)
wp = raster('/mnt/data3/biomass/raw/watermask2/water_prob.tif')

# layers to fix
f_list = [
	'/mnt/data3/biomass/sgorelik/agbs/tiffs/v6/global_potential_biomass_v6_blend_ndm_clp.tif'
]

for f in f_list:
	
	print('Processing {} ...'.format(f), flush = True)
	
	# read inputs
	r = raster(f)
	nd = get_nodata(f) # -32768
	dt = get_dtype(f) # Int16
	gt, sr = get_gt_sr(f)
	
	# convert all nodata (-32768) to zero
	r[r == nd] = 0
	
	# mask out water/fill as nodata (-32768)
	r[(wp <= 75) | (wp > 100)] = nd
	
	# write to disk
	write_gtiff(r, out_tif = f.replace('.tif', '_wm.tif'), dtype = dt, gt = gt, sr = sr, nodata = nd)

