#!/usr/bin/env python3

from raspy import *

stores = ['Current', 'Potential', 'Unrealized']
nd = -32768

for store in stores:
	
	f_agb = '{}_AGB_MgCha_500m.tif'.format(store)
	agb = raster(f_agb, verbose = True)
	ha = get_cell_area_ha(f_agb)
	gt, sr = get_gt_sr(f_agb)
	
	bgb = raster('{}_BGB_MgCha_500m.tif'.format(store), verbose = True)
	soc = raster('{}_SOC_MgCha_500m.tif'.format(store), verbose = True)
	
	ind = np.logical_or.reduce((agb == nd, bgb == nd, soc == nd))
	agb[ind] = 0
	bgb[ind] = 0
	soc[ind] = 0
	
	# AGB+BGB only
	bio = agb + bgb
	print(round(np.sum(bio[bio > 0]*ha)/1e9, 1))
	bio[ind] = nd
	write_gtiff(bio, '{}_AGB_BGB_MgCha_500m.tif'.format(store), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
	del bio
	
	# AGB+BGB+SOC
	tot = agb + bgb + soc
	print(round(np.sum(tot[tot > 0]*ha)/1e9, 1))
	tot[ind] = nd
	write_gtiff(tot, '{}_AGB_BGB_SOC_MgCha_500m.tif'.format(store), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
	del tot
