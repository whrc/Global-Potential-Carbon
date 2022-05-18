#!/usr/bin/env python3

from raspy import *
import pandas as pd

# -----------------------------------------------------------------
# inputs
# -----------------------------------------------------------------

# biophysical thresholds
brl_bt = 5
tmp_bt = 5
trp_bt = 20

# commercial thresholds
brl_ct = 50
tmp_ct = 75
trp_ct = 110

# bioclimate zones (1 = polar; 2 = subtropics; 3 = temperate; 4 = tropics; 5 = boreal; 15 = nodata)
f_bcz = 'Bioclimate_Zones_500m.tif'
bcz = raster(f_bcz, verbose = True)
gt, sr = get_gt_sr(f_bcz)

# current AGB+BGB
cur = raster('Base_Cur_AGB_BGB_MgCha_500m.tif', verbose = True)

# potential AGB+BGB
pot = raster('Base_Pot_AGB_BGB_MgCha_500m.tif', verbose = True)

# potential SOC
soc = raster('Base_Pot_SOC_MgCha_500m.tif', verbose = True)

# unrealized AGB+BGB+SOC
unr = raster('Base_Unr_AGB_BGB_SOC_MgCha_500m.tif', verbose = True)

# societal constraints (0 = no constraint, 1-4 = constraint)
con = raster('Societal_Constraints_500m.tif', verbose = True)

# -----------------------------------------------------------------
# ratio of current to potential
# -----------------------------------------------------------------

cur[cur == -32768] = 0
pot[pot == -32768] = 0

with np.errstate(invalid = 'ignore', divide = 'ignore'):
	c2p = np.true_divide(cur, pot)

del cur

c2p[np.logical_or(np.isinf(c2p), np.isnan(c2p))] = 0

# -----------------------------------------------------------------
# map ncs opportunity space
# -----------------------------------------------------------------

ncs = np.zeros(bcz.shape, dtype = np.int16)

# boreal/polar
ncs[((bcz == 1) | (bcz == 5)) & ( ((pot > 0) & (pot <= brl_bt)) | ((pot == 0) & (soc > 0)) )] = 1
ncs[((bcz == 1) | (bcz == 5)) & ((pot > 0) & (pot > brl_bt) & (pot <= brl_ct)) & (c2p <= 0.25)] = 2
ncs[((bcz == 1) | (bcz == 5)) & ((pot > 0) & (pot > brl_bt) & (pot <= brl_ct)) & (c2p > 0.25) & (c2p <= 0.90)] = 3
ncs[((bcz == 1) | (bcz == 5)) & ((pot > 0) & (pot > brl_bt) & (pot <= brl_ct)) & (c2p > 0.90)] = 4
ncs[((bcz == 1) | (bcz == 5)) & ((pot > 0) & (pot > brl_ct)) & (c2p <= 0.25)] = 5
ncs[((bcz == 1) | (bcz == 5)) & ((pot > 0) & (pot > brl_ct)) & (c2p > 0.25) & (c2p <= 0.90)] = 6
ncs[((bcz == 1) | (bcz == 5)) & ((pot > 0) & (pot > brl_ct)) & (c2p > 0.90)] = 7

# temperate
ncs[(bcz == 3) & ( ((pot > 0) & (pot <= tmp_bt)) | ((pot == 0) & (soc > 0)) )] = 1
ncs[(bcz == 3) & ((pot > 0) & (pot > tmp_bt) & (pot <= tmp_ct)) & (c2p <= 0.25)] = 2
ncs[(bcz == 3) & ((pot > 0) & (pot > tmp_bt) & (pot <= tmp_ct)) & (c2p > 0.25) & (c2p <= 0.90)] = 3
ncs[(bcz == 3) & ((pot > 0) & (pot > tmp_bt) & (pot <= tmp_ct)) & (c2p > 0.90)] = 4
ncs[(bcz == 3) & ((pot > 0) & (pot > tmp_ct)) & (c2p <= 0.25)] = 5
ncs[(bcz == 3) & ((pot > 0) & (pot > tmp_ct)) & (c2p > 0.25) & (c2p <= 0.90)] = 6
ncs[(bcz == 3) & ((pot > 0) & (pot > tmp_ct)) & (c2p > 0.90)] = 7

# tropical/subtropical
ncs[((bcz == 2) | (bcz == 4)) & ( ((pot > 0) & (pot <= trp_bt)) | ((pot == 0) & (soc > 0)) )] = 1
ncs[((bcz == 2) | (bcz == 4)) & ((pot > 0) & (pot > trp_bt) & (pot <= trp_ct)) & (c2p <= 0.25)] = 2
ncs[((bcz == 2) | (bcz == 4)) & ((pot > 0) & (pot > trp_bt) & (pot <= trp_ct)) & (c2p > 0.25) & (c2p <= 0.90)] = 3
ncs[((bcz == 2) | (bcz == 4)) & ((pot > 0) & (pot > trp_bt) & (pot <= trp_ct)) & (c2p > 0.90)] = 4
ncs[((bcz == 2) | (bcz == 4)) & ((pot > 0) & (pot > trp_ct)) & (c2p <= 0.25)] = 5
ncs[((bcz == 2) | (bcz == 4)) & ((pot > 0) & (pot > trp_ct)) & (c2p > 0.25) & (c2p <= 0.90)] = 6
ncs[((bcz == 2) | (bcz == 4)) & ((pot > 0) & (pot > trp_ct)) & (c2p > 0.90)] = 7

del bcz, pot, soc, c2p

# mask out pixels with no unrealized potential carbon
ncs[np.logical_or(unr == -32768, unr == 0)] = 0

# apply societal constraints
ncs[con > 0] = 0

# -----------------------------------------------------------------
# outputs
# -----------------------------------------------------------------

write_gtiff(ncs, out_tif = 'NCS_Opportunity_Categories_500m.tif', gt = gt, sr = sr, dtype = 'Byte', nodata = 0, stats = True, msg = True)

dct = {'ncs_code': range(1, 8), 'ncs_name': ['Nonwoody', 'R/L', 'MM/L', 'M/L', 'R/H', 'MM/H', 'M/H']}
df = pd.DataFrame.from_dict(dct)
df.to_csv('ncs_opp_space.csv', index = False)
