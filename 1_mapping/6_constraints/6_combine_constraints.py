#!/usr/bin/env python3

from raspy import *
import pandas as pd

# cropland and shifting ag:
#  0 = not cropland (nodata)
#  1 = cropland (not shifting ag)
#  2 = cropland (shifting ag)
crop = raster('gfsad_crop_mask_500m_with_shift_ag.tif', verbose = True)

# pasture (0 = not pasture/nodata, 1 = pasture)
past = raster('ramankutty_pasture_mask_500m.tif', verbose = True)

# urban (0 = not urban/nodata, 1 = urban)
urbn = raster('ghsl_urban_mask_500m.tif', verbose = True)

# combine constraints into one mutually exclusive layer (note order matters for giving priority)
cons = np.zeros(crop.shape, np.uint8)
cons[urbn == 1] = 4 # urban
cons[past == 1] = 3 # pasture
cons[crop == 2] = 2 # cropland (shifting ag)
cons[crop == 1] = 1 # cropland (not shifting ag)

# therefore:
#  0 = no constraint (nodata)
#  1 = cropland (not shifting ag)
#  2 = cropland (shifting ag)
#  3 = pasture
#  4 = urban

gt, sr = get_gt_sr('gfsad_crop_mask_500m_with_shift_ag.tif')
write_gtiff(cons, out_tif = 'global_constraints_500m.tif', dtype = 'Byte', gt = gt, sr = sr, nodata = 0, msg = True, stats = True)

# write table of class codes and names to CSV file
dct = {'cons_code': [1, 2, 3, 4], 'cons_name': ['cropland (not shifting ag)', 'cropland (shifting ag)', 'pasture', 'urban']}
df = pd.DataFrame.from_dict(dct)
df.to_csv('constraint_codes_names.csv', index = False)
