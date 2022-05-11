#!/usr/bin/env python3

# =======================================================================================================
#
# Title:
# 	5_create_NCS_raster.py
#
# Purpose:
#	Build a global raster of the NCS opportunity categories
#
# Notes:
#	This scripts needs ~75 GB of memory to run.
#
# =======================================================================================================

import sys, os
from raspy import *

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Set threshold parameters (Mg/ha in biomass not carbon!)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# biophysical thresholds
brl_bt = 10 # = 5 MgC/ha
tmp_bt = 10 # = 5 MgC/ha
trp_bt = 40 # = 20 MgC/ha

# commercial thresholds
brl_ct = 100 # = 50 MgC/ha
tmp_ct = 150 # = 75 MgC/ha
trp_ct = 220 # = 110 MgC/ha

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Input rasters
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# bioclimate zones (1 = polar; 2 = subtropics; 3 = temperate; 4 = tropics; 5 = boreal)
gez_tif = '/home/sgorelik/data/fao/gez_2010_sin500m_LW.tif'
print('Reading {} ...'.format(gez_tif), flush = True)
gez_img = raster(gez_tif)
gez_nd = get_nodata(gez_tif)

# current AGB+BGB
cur_tif = '/home/sgorelik/data/combined/woody/global_current_total_AGB_BGB_Mgha.tif'
print('Reading {} ...'.format(cur_tif), flush = True)
cur_img = raster(cur_tif)
cur_nd = get_nodata(cur_tif) # NoData = 0
gt, sr = get_gt_sr(cur_tif)

# potential AGB+BGB
pot_tif = '/home/sgorelik/data/combined/woody/global_potential_total_AGB_BGB_Mgha.tif'
print('Reading {} ...'.format(pot_tif), flush = True)
pot_img = raster(pot_tif)
pot_nd = get_nodata(pot_tif) # NoData = 0

# potential SOC
soc_tif = '/home/sgorelik/data/soc/sin500m/wm/SOCS_0_200cm_year_NoLU_500m_Mgha_wm_adj.tif'
print('Reading {} ...'.format(soc_tif), flush = True)
soc_img = raster(soc_tif)
soc_nd = get_nodata(soc_tif) # NoData = -32768

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Prepare data
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

print('Compute ratio of current to potential biomass ...', flush = True)

# divide rasters and ignore division by zero warnings
with np.errstate(invalid = 'ignore', divide = 'ignore'):
	rat_img = cur_img/pot_img

del cur_img

# replace NaN and Inf with 0
rat_img[(np.isinf(rat_img) | np.isnan(rat_img))] = 0

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Build raster
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# create global raster filled with zeros
ncs_img = np.full(pot_img.shape, 0)

print('Building boreal/polar NCS zones ...', flush = True)
ncs_img[((gez_img == 1) | (gez_img == 5)) & ( ((pot_img != pot_nd) & (pot_img <= brl_bt)) | ((pot_img == pot_nd) & (soc_img > 0)) )] = 1
ncs_img[((gez_img == 1) | (gez_img == 5)) & ((pot_img != pot_nd) & (pot_img > brl_bt) & (pot_img <= brl_ct)) & (rat_img <= 0.25)] = 2
ncs_img[((gez_img == 1) | (gez_img == 5)) & ((pot_img != pot_nd) & (pot_img > brl_bt) & (pot_img <= brl_ct)) & (rat_img > 0.25) & (rat_img <= 0.90)] = 3
ncs_img[((gez_img == 1) | (gez_img == 5)) & ((pot_img != pot_nd) & (pot_img > brl_bt) & (pot_img <= brl_ct)) & (rat_img > 0.90)] = 4
ncs_img[((gez_img == 1) | (gez_img == 5)) & ((pot_img != pot_nd) & (pot_img > brl_ct)) & (rat_img <= 0.25)] = 5
ncs_img[((gez_img == 1) | (gez_img == 5)) & ((pot_img != pot_nd) & (pot_img > brl_ct)) & (rat_img > 0.25) & (rat_img <= 0.90)] = 6
ncs_img[((gez_img == 1) | (gez_img == 5)) & ((pot_img != pot_nd) & (pot_img > brl_ct)) & (rat_img > 0.90)] = 7

print('Building temperate NCS zones ...', flush = True)
ncs_img[(gez_img == 3) & ( ((pot_img != pot_nd) & (pot_img <= tmp_bt)) | ((pot_img == pot_nd) & (soc_img > 0)) )] = 8
ncs_img[(gez_img == 3) & ((pot_img != pot_nd) & (pot_img > tmp_bt) & (pot_img <= tmp_ct)) & (rat_img <= 0.25)] = 9
ncs_img[(gez_img == 3) & ((pot_img != pot_nd) & (pot_img > tmp_bt) & (pot_img <= tmp_ct)) & (rat_img > 0.25) & (rat_img <= 0.90)] = 10
ncs_img[(gez_img == 3) & ((pot_img != pot_nd) & (pot_img > tmp_bt) & (pot_img <= tmp_ct)) & (rat_img > 0.90)] = 11
ncs_img[(gez_img == 3) & ((pot_img != pot_nd) & (pot_img > tmp_ct)) & (rat_img <= 0.25)] = 12
ncs_img[(gez_img == 3) & ((pot_img != pot_nd) & (pot_img > tmp_ct)) & (rat_img > 0.25) & (rat_img <= 0.90)] = 13
ncs_img[(gez_img == 3) & ((pot_img != pot_nd) & (pot_img > tmp_ct)) & (rat_img > 0.90)] = 14

print('Building tropical/subtropical NCS zones ...', flush = True)
ncs_img[((gez_img == 2) | (gez_img == 4)) & ( ((pot_img != pot_nd) & (pot_img <= trp_bt)) | ((pot_img == pot_nd) & (soc_img > 0)) )] = 15
ncs_img[((gez_img == 2) | (gez_img == 4)) & ((pot_img != pot_nd) & (pot_img > trp_bt) & (pot_img <= trp_ct)) & (rat_img <= 0.25)] = 16
ncs_img[((gez_img == 2) | (gez_img == 4)) & ((pot_img != pot_nd) & (pot_img > trp_bt) & (pot_img <= trp_ct)) & (rat_img > 0.25) & (rat_img <= 0.90)] = 17
ncs_img[((gez_img == 2) | (gez_img == 4)) & ((pot_img != pot_nd) & (pot_img > trp_bt) & (pot_img <= trp_ct)) & (rat_img > 0.90)] = 18
ncs_img[((gez_img == 2) | (gez_img == 4)) & ((pot_img != pot_nd) & (pot_img > trp_ct)) & (rat_img <= 0.25)] = 19
ncs_img[((gez_img == 2) | (gez_img == 4)) & ((pot_img != pot_nd) & (pot_img > trp_ct)) & (rat_img > 0.25) & (rat_img <= 0.90)] = 20
ncs_img[((gez_img == 2) | (gez_img == 4)) & ((pot_img != pot_nd) & (pot_img > trp_ct)) & (rat_img > 0.90)] = 21

del gez_img, pot_img, soc_img, rat_img

write_gtiff(ncs_img, out_tif = '/home/sgorelik/data/ncs/v5/global_500m_ncs_zones.tif', gt = gt, sr = sr, dtype = 'Byte', nodata = 0, stats = True, msg = True)
