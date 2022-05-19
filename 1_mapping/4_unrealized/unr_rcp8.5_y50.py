#!/usr/bin/env python3

from raspy import *

cur = raster('Base_Cur_AGB_MgCha_500m.tif', verbose = True)
nd = -32768

# earth system models
mdls = ['bc', 'cc', 'gs', 'hd', 'he', 'ip', 'mc', 'mg', 'mi', 'mr', 'no']
for mdl in mdls:
	
	f_pot = 'RCP85y50{}_Pot_AGB_MgCha_500m.tif'.format(mdl)
	pot = raster(f_pot, verbose = True)

	ind = np.logical_or(cur == nd, pot == nd)
	cur[ind] = 0
	pot[ind] = 0
	unr = pot - cur
	unr[ind] = nd
	
	gt, sr = get_gt_sr(f_pot)
	write_gtiff(unr, 'RCP85y50{}_Unr_AGB_MgCha_500m.tif'.format(mdl), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
