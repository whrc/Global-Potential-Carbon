#!/usr/bin/env python3

from raspy import *

nd = -32768

for store in ['Cur', 'Pot', 'Unr']:
	
	f_agb = 'Base_{}_AGB_MgCha_500m.tif'.format(store)
	agb = raster(f_agb, verbose = True)
	gt, sr = get_gt_sr(f_agb)
	
	bgb = raster('Base_{}_BGB_MgCha_500m.tif'.format(store), verbose = True)
	soc = raster('Base_{}_SOC_MgCha_500m.tif'.format(store), verbose = True)
	
	ind = np.logical_or.reduce((agb == nd, bgb == nd, soc == nd))
	agb[ind] = 0
	bgb[ind] = 0
	soc[ind] = 0
	
	# AGB+BGB only
	bio = agb + bgb
	bio[ind] = nd
	write_gtiff(bio, 'Base_{}_AGB_BGB_MgCha_500m.tif'.format(store), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
	del bio
	
	# AGB+BGB+SOC
	tot = agb + bgb + soc
	tot[ind] = nd
	write_gtiff(tot, 'Base_{}_AGB_BGB_SOC_MgCha_500m.tif'.format(store), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
	del tot
