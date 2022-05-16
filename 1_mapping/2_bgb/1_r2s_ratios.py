#!/usr/bin/env python3
# Creates a 500m raster of woody root:shoot ratios by Dinerstein et al. biome and ecoregion

import sys
import pandas as pd
from progressbar import *
from raspy import *

# ---------------------------------------------------------------------------------------------
# Input data
# ---------------------------------------------------------------------------------------------

# current ca. 2016 aboveground biomass (Mg/ha)
cur_agb_tif = 'Current_AGB_MgCha_500m.tif'
cur_agb_img = raster(cur_agb_tif, verbose = True)
cur_agb_nd = get_nodata(cur_agb_tif)
cur_agb_img[cur_agb_img == cur_agb_nd] = 0

# rasterized Dinerstein et al. ecoregions
eco_img = raster('ecoregions_500m.tif', verbose = True)
eco_df = pd.read_csv('eco_r2s_ratios.csv')

# rasterized Dinerstein et al. biomes
biome_img = raster('biomes_500m.tif', verbose = True)

#  biome_code                                       biome_name
#  0                                                Rock & Ice
#  1            Tropical & Subtropical Moist Broadleaf Forests
#  2              Tropical & Subtropical Dry Broadleaf Forests
#  3                 Tropical & Subtropical Coniferous Forests
#  4                       Temperate Broadleaf & Mixed Forests
#  5                                 Temperate Conifer Forests
#  6                                      Boreal Forests/Taiga
#  7  Tropical & Subtropical Grasslands, Savannas & Shrublands
#  8               Temperate Grasslands, Savannas & Shrublands
#  9                             Flooded Grasslands & Savannas
#  10                          Montane Grasslands & Shrublands
#  11                                                   Tundra
#  12                 Mediterranean Forests, Woodlands & Scrub
#  13                               Deserts & Xeric Shrublands
#  14                                                Mangroves
#  15                                                   NoData

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('Building empty root:shoot raster ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# fill with zeros
r2s_flt_img = np.full(biome_img.shape, fill_value = 0, dtype = np.float32)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('1. Boreal forests or taiga ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[(biome_img == 6) & (cur_agb_img <= 37.5)] = 0.392
r2s_flt_img[(biome_img == 6) & (cur_agb_img  > 37.5)] = 0.239

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('2. Mangroves ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[biome_img == 14] = 0.39 # Hutchison et al. 2014

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('3. Mediterranean forests, woodlands, and scrub ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[biome_img == 12] = 0.371

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('4. Temperate broadleaf and mixed forests ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

widgets = [FormatLabel('Processing'), Bar(marker = '.', left = ' ', right = '', fill =' '), ' ', Percentage(), ' | ', ETA(), '    ']
pbar = ProgressBar(widgets = widgets).start()

for index, row in eco_df.iterrows():
    if row['biome_code'] == 4:
        eco_code = row['eco_code']
        mokany_biome = row['mokany_biome']

        # Mokany: Temperate oak forest
        if mokany_biome == 'tof':
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img > 35)] = 0.295

        # Mokany: Temperate eucalypt forest/plantation
        if mokany_biome == 'tef':
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img < 25)] = 0.437
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img >= 25) & (cur_agb_img <= 75)] = 0.275
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img > 75)] = 0.2

        # Mokany: Other temperate broadleaf forest/plantation
        if mokany_biome == 'otbf':
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img < 37.5)] = 0.456
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img >= 37.5) & (cur_agb_img <= 75)] = 0.226
            r2s_flt_img[(biome_img == 4) & (eco_img == eco_code) & (cur_agb_img > 75)] = 0.241

    pbar.update(index)
pbar.finish()

del eco_img

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('5. Temperate conifer forests ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[(biome_img == 5) & (cur_agb_img < 25)] = 0.403
r2s_flt_img[(biome_img == 5) & (cur_agb_img >= 25) & (cur_agb_img <= 75)] = 0.292
r2s_flt_img[(biome_img == 5) & (cur_agb_img > 75)] = 0.201

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('6. Tropical and subtropical coniferous forests ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[(biome_img == 3) & (cur_agb_img < 25)] = 0.403
r2s_flt_img[(biome_img == 3) & (cur_agb_img >= 25) & (cur_agb_img <= 75)] = 0.292
r2s_flt_img[(biome_img == 3) & (cur_agb_img > 75)] = 0.201

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('7. Tropical and subtropical dry broadleaf forests ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[(biome_img == 2) & (cur_agb_img <= 10)] = 0.563
r2s_flt_img[(biome_img == 2) & (cur_agb_img  > 10)] = 0.275

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('8. Tropical and subtropical moist broadleaf forests ...', flush = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

r2s_flt_img[(biome_img == 1) & (cur_agb_img <= 62.5)] = 0.205
r2s_flt_img[(biome_img == 1) & (cur_agb_img  > 62.5)] = 0.235

# ---------------------------------------------------------------------------------------------
# Write root:shoot ratio numpy array to raster
# ---------------------------------------------------------------------------------------------

del cur_agb_img
del biome_img

# multiply ratios by scaling factor to save raster as integer rather than float
r2s_int_img = np.copy(r2s_flt_img) * 1e3
del r2s_flt_img
r2s_int_img = r2s_int_img.astype(np.int16)

gt, sr = get_gt_sr(cur_agb_tif)
write_gtiff(r2s_int_img, 'Root2Shoot_Ratios_Scaled1e3_500m.tif', dtype = 'UInt16', nodata = 0, gt = gt, sr = sr, stats = True, msg = True)
