#!/usr/bin/env python3

# replaces SOC nodata value (-32767) with biomass nodata value (-32768) for consistency 

# source:
#  Sanderman, J., Hengl, T., and Fiske, G. 2017. The soil carbon debt of 12,000 years 
#  of human land use. PNAS 114(36): 9575–9580. doi:10.1073/pnas.1706103114.
# 
# downloaded from:
#  https://github.com/whrc/Soil-Carbon-Debt
#
# input soc rasters:
# - top 2 m of soil
# - units: MgC/ha
# - res: 10 km
# - values ≥ 0
# - nodata = -32767

from raspy import *

def proc_soc(f_in, f_out):
	
	# read input layer
	soc = raster(f_in, verbose = True)
	nd = get_nodata(f_in) # -32767
	
	# replace nodata cells with -32768
	soc[soc == nd] = -32768
	
	# write to disk
	gt, sr = get_gt_sr(f_in)
	write_gtiff(soc, f_out, dtype = 'Int16', gt = gt, sr = sr, nodata = -32768, stats = True, msg = True)
	return

# current ca. 2010
proc_soc(f_in = 'SOCS_0_200cm_year_2010AD_10km.tif', f_out = 'Current_SOC_MgCha_10km.tif')

# potential
proc_soc(f_in = 'SOCS_0_200cm_year_NoLU_10km.tif', f_out = 'Potential_SOC_MgCha_10km.tif')
