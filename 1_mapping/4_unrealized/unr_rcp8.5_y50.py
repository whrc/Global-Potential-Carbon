#!/usr/bin/env python3

from raspy import *

nd = -32768
pools = ['AGB', 'BGB']
mdls = ['bc', 'cc', 'gs', 'hd', 'he', 'ip', 'mc', 'mg', 'mi', 'mr', 'no', 'mean'] # 11 earth system models and pixel-based mean

for pool in pools:
	cur = raster('Base_Cur_{}_MgCha_500m.tif'.format(pool), verbose = True)
	for mdl in mdls:
		
		f_pot = 'RCP85y50{}_Pot_{}_MgCha_500m.tif'.format(mdl, pool)
		pot = raster(f_pot, verbose = True)
	
		ind = np.logical_or(cur == nd, pot == nd)
		cur[ind] = 0
		pot[ind] = 0
		unr = pot - cur
		unr[ind] = nd
		
		gt, sr = get_gt_sr(f_pot)
		write_gtiff(unr, 'RCP85y50{}_Unr_{}_MgCha_500m.tif'.format(mdl, pool), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
