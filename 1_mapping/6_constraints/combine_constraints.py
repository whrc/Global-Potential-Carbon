#!/usr/bin/env python3

# combine_constraints.py

import sys
sys.path.append('/mnt/data3/sgorelik/repos/biomass_team/unrealized')
from rasters import *
import pandas as pd

# cropland/shifting agriculture (already mutually exclusive classes):
#  0 = nodata
#  1 = cropland (not shifting ag)
#  2 = cropland (shifting ag)
crop = r2n('/mnt/data3/biomass/sgorelik/misc/gfsad/GFSAD_500m_global_cropland_with_shifting_ag.tif')

# pastureland/rangeland (already mutually exclusive classes):
#  0 = nodata
#  1 = rangeland
#  2 = pasture
prld = r2n('/mnt/data3/biomass/sgorelik/misc/rangeland/global_rangeland_500m.tif')

# urban (0 = nodata, 1 = urban)
urbn = r2n('/mnt/data3/biomass/sgorelik/misc/ghsl/ghsl_urban_mask_500m.tif')

# combine constraints into one mutually exclusive layer
cons = np.zeros(crop.shape, np.uint8)
cons[urbn == 1] = 5 # urban
cons[prld == 2] = 4 # pasture
cons[prld == 1] = 3 # rangeland
cons[crop == 2] = 2 # cropland (shifting ag)
cons[crop == 1] = 1 # cropland (not shifting ag)

# thus, output classes are:
#  0 = no constraint
#  1 = cropland (not shifting ag)
#  2 = cropland (shifting ag)
#  3 = rangeland
#  4 = pasture
#  5 = urban

# write output to raster
gt, sr = get_gt_sr('/mnt/data3/biomass/sgorelik/ncs3/global_500m_ncs_zones_a90.tif')
write_gtiff(cons, out_tif = '/mnt/data3/biomass/sgorelik/constraints/global_constraints_500m.tif', dtype = 'Byte', gt = gt, sr = sr, nodata = 0)

# write table of class codes and names to CSV file
dct = {'cons_code': [1, 2, 3, 4, 5], 'cons_name': ['cropland (not shifting ag)', 'cropland (shifting ag)', 'rangeland', 'pasture', 'urban']}
df = pd.DataFrame.from_dict(dct)
df.to_csv('/mnt/data3/biomass/sgorelik/constraints/constraint_codes_names.csv', index = False)
