#!/usr/bin/env python3

# combine_crop_and_shifting_ag.py

import sys
sys.path.append('/mnt/data3/sgorelik/repos/biomass_team/unrealized')
from rasters import *

# GFSAD mask of cropland (i.e., 0 = not cropland, 1 = cropland)
crop = r2n('/mnt/data3/biomass/sgorelik/misc/gfsad/GFSAD_500m_global_cropland_mask.tif')

# Curtis et al. mask of forest loss driven by shifting ag (i.e., 0 = not shifting ag, 1 = shifting ag)
shag = r2n('/mnt/data3/biomass/sgorelik/misc/curtis/curtis_shifting_ag_mask_500m.tif')

# if cropland and shifting ag, then shifting ag
crop[(crop == 1) & (shag == 1)] = 2

# therefore:
#   0 = not cropland
#   1 = cropland (not shifting ag)
#   2 = cropland (shifting ag)

# write output
gt, sr = get_gt_sr('/mnt/data3/biomass/sgorelik/misc/gfsad/GFSAD_500m_global_cropland_mask.tif')
write_gtiff(crop, out_tif = '/mnt/data3/biomass/sgorelik/misc/gfsad/GFSAD_500m_global_cropland_with_shifting_ag.tif', dtype = 'Byte', gt = gt, sr = sr, nodata = 0)

# compute shifting ag. portion of cropland
crop_cnt = crop[crop == 1].size
shag_cnt = crop[crop == 2].size
prc_shag = (shag_cnt / (shag_cnt + crop_cnt)) * 100
print('Percent of cropland considered shifting ag: {0:.2f}%'.format(prc_shag))
