#!/usr/bin/env python3

# =======================================================================================================
#
# Title:
# 	6_mask_with_carbon.py
#
# Purpose:
#	Mask out pixels in the NCS raster without unrealized carbon.
#
# =======================================================================================================

import sys
sys.path.append('/mnt/data3/sgorelik/repos/biomass_team/unrealized')
from rasters import *

# NCS zones (with an avoided loss threshold of 0.9)
ncs_tif = '/home/sgorelik/data/ncs/v4/global_500m_ncs_zones_a90.tif'
print('Reading {} ...'.format(ncs_tif), flush = True)
ncs_img = r2n(ncs_tif)
ncs_nd = get_nodata(ncs_tif)
gt, sr = get_gt_sr(ncs_tif)

# unrealized potential combined (AGB+BGB+SOC) biomass density (Mg/ha)
unr_tif = '/home/sgorelik/data/combined/all/global_unrealized_total_AGB_BGB_SOC_Mgha.tif'
print('Reading {} ...'.format(unr_tif), flush = True)
unr_img = r2n(unr_tif)
unr_nd = get_nodata(unr_tif)

# mask out pixels with no unrealized potential carbon
ncs_img[(unr_img == unr_nd) & (unr_img == 0)] = ncs_nd

# write raster
out_tif = ncs_tif.replace('.tif', '_cm.tif')
print('Writing {} ...'.format(out_tif), flush = True)
write_gtiff(ncs_img, out_tif = out_tif, gt = gt, sr = sr, dtype = 'Byte', nodata = 0)

print('Done!', flush = True)

