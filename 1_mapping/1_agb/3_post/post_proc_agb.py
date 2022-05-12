#!/usr/bin/env python3

from raspy import *

# -----------------------------------------------------------------
# inputs
# -----------------------------------------------------------------

f_cur = 'global_actual_biomass_2016_v6_blend_a95_f03_w75.tif'
f_pot = 'global_potential_biomass_v6_blend.tif'

cur = raster(f_cur, verbose = True)
pot = raster(f_pot, verbose = True)

nd = -32768

# -----------------------------------------------------------------
# match nodata cells in the current and potential layers
# -----------------------------------------------------------------

cur[np.logical_or(cur == nd, pot == nd)] = nd
pot[np.logical_or(cur == nd, pot == nd)] = nd

# -----------------------------------------------------------------
# cap outliers
# -----------------------------------------------------------------

# cap both current and potential biomass outliers to the global
# 99.99th percentile of potential biomass

pot_pct = np.percentile(pot[pot > 0], 99.99)

cur[cur > pot_pct] = pot_pct
pot[pot > pot_pct] = pot_pct

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

cur[cur == nd] = 0
pot[pot == nd] = 0

cur[np.logical_or(lwp <= 75, lwp == 255)] = nd
pot[np.logical_or(lwp <= 75, lwp == 255)] = nd

# -----------------------------------------------------------------
# convert units from biomass (Mg/ha) to carbon (MgC/ha)
# -----------------------------------------------------------------

cur[cur > 0] = np.rint(np.true_divide(cur[cur > 0], 2)).astype(np.int16)
pot[pot > 0] = np.rint(np.true_divide(pot[pot > 0], 2)).astype(np.int16)

# -----------------------------------------------------------------
# outputs
# -----------------------------------------------------------------

gt, sr = get_gt_sr(f_cur)
write_gtiff(cur, 'Current_AGB_MgCha_500m.tif', dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)

gt, sr = get_gt_sr(f_pot)
write_gtiff(pot, 'Potential_AGB_MgCha_500m.tif', dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
