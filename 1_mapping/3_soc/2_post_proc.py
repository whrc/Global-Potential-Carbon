#!/usr/bin/env python3

from raspy import *

# -----------------------------------------------------------------
# inputs
# -----------------------------------------------------------------

f_cur = 'SOCS_0_200cm_year_2010AD_500m.tif'
f_pot = 'SOCS_0_200cm_year_NoLU_500m.tif'

cur = raster(f_cur, verbose = True)
pot = raster(f_pot, verbose = True)

nd_i = -32767
nd_o = -32768

# -----------------------------------------------------------------
# update nodata cells
# -----------------------------------------------------------------

cur[np.logical_or(cur == nd_i, pot == nd_i)] = nd_o
pot[np.logical_or(cur == nd_i, pot == nd_i)] = nd_o

# -----------------------------------------------------------------
# adjust potential
# -----------------------------------------------------------------

# if current > potential, then set potential to current
# there is no unrealized potential C in these places

pot[cur > pot] = cur[cur > pot]

# -----------------------------------------------------------------
# mask water
# -----------------------------------------------------------------

# igbp land/water probability (0-75 = prob water; 76-100 = prob land; 255 = fill)
lwp = raster('water_prob.tif')

cur[cur == nd_o] = 0
pot[pot == nd_o] = 0

cur[np.logical_or(lwp <= 75, lwp == 255)] = nd_o
pot[np.logical_or(lwp <= 75, lwp == 255)] = nd_o

# -----------------------------------------------------------------
# outputs
# -----------------------------------------------------------------

gt, sr = get_gt_sr(f_cur)
write_gtiff(cur, 'Base_Cur_SOC_MgCha_500m.tif', dtype = 'Int16', gt = gt, sr = sr, nodata = nd_o, stats = True, msg = True)

gt, sr = get_gt_sr(f_pot)
write_gtiff(pot, 'Base_Pot_SOC_MgCha_500m.tif', dtype = 'Int16', gt = gt, sr = sr, nodata = nd_o, stats = True, msg = True)
