#!/usr/bin/env python3

# create_rangeland.py

# Create rangeland layer from combining Henderson et al. and Ramankutty et al. pasture layers.

import sys
sys.path.append('/mnt/data3/sgorelik/repos/biomass_team/unrealized')
from rasters import *

# Ramankutty et al. mask of pastureland (i.e., 0 = not pasture, 1 = pasture)
rama = r2n('/mnt/data3/biomass/sgorelik/misc/SEDAC/pasture/SEDAC_500m_global_pasture_mask.tif')

# Henderson et al. mask of pastureland (i.e., 0 = not pasture, 1 = pasture)
hend = r2n('/mnt/data3/biomass/sgorelik/misc/henderson_2015/proc/henderson_pastureland_mask_sin500m.tif')

# if pasture in both Ramankutty & Henderson, keep as pasture, but if pasture in Ramankutty only, then its rangeland
rama[(rama == 1) & (hend == 1)] = 2

# therefore, result is:
#   0 = no data
#   1 = rangeland
#   2 = pasture

# write output
gt, sr = get_gt_sr('/mnt/data3/biomass/sgorelik/misc/SEDAC/pasture/SEDAC_500m_global_pasture_mask.tif')
write_gtiff(rama, out_tif = '/mnt/data3/biomass/sgorelik/misc/rangeland/global_rangeland_500m.tif', dtype = 'Byte', gt = gt, sr = sr, nodata = 0)

# compute portion of pixels within each class
rang_cnt = rama[rama == 1].size
past_cnt = rama[rama == 2].size
prc_rang = (rang_cnt / (rang_cnt + past_cnt)) * 100
prc_past = (past_cnt / (rang_cnt + past_cnt)) * 100
print('Rangeland: {0:.2f}%'.format(prc_rang))
print('Pastureland: {0:.2f}%'.format(prc_past))
