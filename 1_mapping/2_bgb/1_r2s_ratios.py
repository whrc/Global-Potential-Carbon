#!/usr/bin/env python3

import pandas as pd
from progressbar import *
from raspy import *

# current aboveground biomass density (Mg/ha)
f_cur = 'Current_AGB_Mgha_500m.tif'
agb = raster(f_cur, verbose = True)
agb_nd = get_nodata(f_cur)
agb[agb == agb_nd] = 0

# rasterized Dinerstein et al. ecoregions
ecos = raster('ecoregions_500m.tif', verbose = True)
eco_df = pd.read_csv('eco_r2s_ratios.csv')

# rasterized Dinerstein et al. biomes
biomes = raster('biomes_500m.tif', verbose = True)

# initialize root:shoot array
r2s_flt = np.full(agb.shape, fill_value = 0, dtype = np.float32)

print('1. Boreal forests or taiga ...', flush = True)
r2s_flt[(biomes == 6) & (agb <= 75)] = 0.392
r2s_flt[(biomes == 6) & (agb  > 75)] = 0.239

print('2. Mangroves ...', flush = True)
r2s_flt[biomes == 14] = 0.39 # from Hutchison et al. 2014

print('3. Mediterranean forests, woodlands, and scrub ...', flush = True)
r2s_flt[biomes == 12] = 0.371

print('4. Temperate broadleaf and mixed forests ...', flush = True)
widgets = [FormatLabel('Processing'), Bar(marker = '.', left = ' ', right = '', fill =' '), ' ', Percentage(), ' | ', ETA(), '    ']
pbar = ProgressBar(widgets = widgets).start()
nrows = len(eco_df.index)
for index, row in eco_df.iterrows():
	if row['biome_code'] == 4:
		eco_code = row['eco_code']
		mokany_biome = row['mokany_biome']
		# mokany temperate oak forest
		if mokany_biome == 'tof':
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb > 70)] = 0.295
		# mokany temperate eucalypt forest/plantation
		if mokany_biome == 'tef':
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb < 50)] = 0.437
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb >= 50) & (agb <= 150)] = 0.275
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb > 150)] = 0.2
		# mokany other temperate broadleaf forest/plantation
		if mokany_biome == 'otbf':
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb < 75)] = 0.456
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb >= 75) & (agb <= 150)] = 0.226
			r2s_flt[(biomes == 4) & (ecos == eco_code) & (agb > 150)] = 0.241
	pbar.update((index+1)/nrows*100)
pbar.finish()
del ecos

print('5. Temperate conifer forests ...', flush = True)
r2s_flt[(biomes == 5) & (agb < 50)] = 0.403
r2s_flt[(biomes == 5) & (agb >= 50) & (agb <= 150)] = 0.292
r2s_flt[(biomes == 5) & (agb > 150)] = 0.201

print('6. Tropical and subtropical coniferous forests ...', flush = True)
r2s_flt[(biomes == 3) & (agb < 50)] = 0.403
r2s_flt[(biomes == 3) & (agb >= 50) & (agb <= 150)] = 0.292
r2s_flt[(biomes == 3) & (agb > 150)] = 0.201

print('7. Tropical and subtropical dry broadleaf forests ...', flush = True)
r2s_flt[(biomes == 2) & (agb <= 20)] = 0.563
r2s_flt[(biomes == 2) & (agb  > 20)] = 0.275

print('8. Tropical and subtropical moist broadleaf forests ...', flush = True)
r2s_flt[(biomes == 1) & (agb <= 125)] = 0.205
r2s_flt[(biomes == 1) & (agb  > 125)] = 0.235

# free mem
del agb
del biomes

# apply scaling factor to ratios to save as integer on disk to save space
r2s_int = np.rint(r2s_flt*1e3).astype(np.int16)
del r2s_flt

gt, sr = get_gt_sr(f_cur)
write_gtiff(r2s_int, 'Root2Shoot_Ratios_Scaled1e3_500m.tif', dtype = 'UInt16', nodata = 0, gt = gt, sr = sr, stats = True, msg = True)
