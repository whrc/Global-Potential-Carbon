#!/usr/bin/env python3

# identify portion of cropland (30m native) that falls within shifting agriculture (10km native)

from raspy import *

# GFSAD cropland mask (0 = nodata/not cropland, 1 = cropland)
crop = raster('GFSAD_crop_mask_500m.tif', verbose = True)

# Curtis et al. shifting ag mask (0 = not shifting ag, 1 = shifting ag)
shag = raster('curtis_shift_ag_mask_500m.tif', verbose = True)

# if cropland and shifting ag, then shifting ag
crop[(crop == 1) & (shag == 1)] = 2

# therefore:
#   0 = not cropland (nodata)
#   1 = cropland (not shifting ag)
#   2 = cropland (shifting ag)

gt, sr = get_gt_sr('GFSAD_crop_mask_500m.tif')
write_gtiff(crop, out_tif = 'gfsad_crop_mask_500m_with_shift_ag.tif', dtype = 'Byte', gt = gt, sr = sr, nodata = 0, msg = True, stats = True)
