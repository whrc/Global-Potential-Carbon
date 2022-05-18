#!/usr/bin/env python3

from raspy import *

f_cons = 'Societal_Constraints_500m.tif'
cons = raster(f_cons, verbose = True)
gt, sr = get_gt_sr(f_cons)

#  0 = no constraint (nodata)
#  1 = cropland (not shifting ag)
#  2 = cropland (shifting ag)
#  3 = pasture
#  4 = urban

for pool in ['AGB', 'BGB', 'AGB_BGB', 'SOC', 'AGB_BGB_SOC']:
	unr = raster('Base_Unr_{}_MgCha_500m.tif'.format(pool), verbose = True)
	unr[cons > 0] = -32768
	write_gtiff(unr, 'Base_Con_Unr_{}_MgCha_500m.tif'.format(pool), dtype = 'Int16', gt = gt, sr = sr, nodata = -32768, stats = True, msg = True)
