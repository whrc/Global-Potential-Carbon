#!/usr/bin/env python3

# Matches the nodata cells in the current and potential layers.
# Note, in output filename, "ndm" = nodata match.

import sys
from raspy import *

f_cur = 'global_actual_biomass_2016_v6_blend_a95_f03_w75.tif'
f_pot = 'global_potential_biomass_v6_blend.tif'

cur = raster(f_cur, verbose = True)
pot = raster(f_pot, verbose = True)

nd = -32768

ind = np.logical_or(cur == nd, pot == nd)

cur[ind] = nd
pot[ind] = nd

gt, sr = get_gt_sr(f_cur)
write_gtiff(cur, f_cur.replace('.tif', '_ndm.tif'), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)

gt, sr = get_gt_sr(f_pot)
write_gtiff(pot, f_pot.replace('.tif', '_ndm.tif'), dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
