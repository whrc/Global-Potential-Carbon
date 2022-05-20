#!/usr/bin/env python3

from raspy import *

# -----------------------------------------------------------------
# inputs
# -----------------------------------------------------------------

f_cur = 'Base_Cur_AGB_MgCha_500m.tif'
f_pot = 'Base_Pot_AGB_MgCha_500m.tif'

f_cur_lwr = 'global_actual_v5_quant_reg_q2_5_MgCha.tif'
f_cur_upr = 'global_actual_v5_quant_reg_q97_5_MgCha.tif'
f_pot_lwr = 'global_potential_v5_quant_reg_q2_5_MgCha.tif'
f_pot_upr = 'global_potential_v5_quant_reg_q97_5_MgCha.tif'

cur = raster(f_cur, verbose = True)
cur_lwr = raster(f_cur_lwr, verbose = True)
cur_upr = raster(f_cur_upr, verbose = True)

pot = raster(f_pot, verbose = True)
pot_lwr = raster(f_pot_lwr, verbose = True)
pot_upr = raster(f_pot_upr, verbose = True)

nd = -32768

# -----------------------------------------------------------------
# match nodata/water cells
# -----------------------------------------------------------------

ind = np.logical_or.reduce((cur == nd, cur_lwr == nd, cur_upr == nd, pot_lwr == nd, pot_upr == nd)) # cur and pot have same nodata/water cells

cur_lwr[ind] = nd
cur_upr[ind] = nd

pot_lwr[ind] = nd
pot_upr[ind] = nd

# -----------------------------------------------------------------
# cap outliers
# -----------------------------------------------------------------

# lower limit layers
lwr_pot_pct = np.percentile(pot_lwr[pot_lwr > 0], 99.99)
cur_lwr[cur_lwr > lwr_pot_pct] = lwr_pot_pct
pot_lwr[pot_lwr > lwr_pot_pct] = lwr_pot_pct

# upper limit layers
upr_pot_pct = np.percentile(pot_upr[pot_upr > 0], 99.99)
cur_upr[cur_upr > upr_pot_pct] = upr_pot_pct
pot_upr[pot_upr > upr_pot_pct] = upr_pot_pct

# -----------------------------------------------------------------
# adjust potential
# -----------------------------------------------------------------

# lower limit layers
pot_lwr[cur_lwr > pot_lwr] = cur_lwr[cur_lwr > pot_lwr]

# upper limit layers
pot_upr[cur_upr > pot_upr] = cur_upr[cur_upr > pot_upr]

# -----------------------------------------------------------------
# compute uncertainty index
# -----------------------------------------------------------------

def unc_ind(bio, lwr, upr):
	
	# index valid data cells
	vld = np.logical_and.reduce((bio != nd, lwr != nd, upr != nd))
	
	# save memory
	vbio = bio[vld]; del bio
	vlwr = lwr[vld]; del lwr
	vupr = upr[vld]; del upr
	
	# initialize output array
	unc = np.full(vld.shape, dtype = np.int16, fill_value = nd)
	
	# compute numerator for uncertainty index
	vnum = vupr - vlwr
	del vupr, vlwr
	
	# divide by bio and convert from float to integer,
	# supress/hide the warnings issued by zero division
	with np.errstate(all = 'ignore'):
		unc[vld] = np.rint(np.true_divide(vnum, vbio)).astype(np.int16)
	del vnum, vbio, vld
	unc[np.logical_or(np.isinf(unc), np.isnan(unc))] = 0
	return unc

cur_unc = unc_ind(bio = cur, lwr = cur_lwr, upr = cur_upr)
pot_unc = unc_ind(bio = pot, lwr = pot_lwr, upr = pot_upr)

# -----------------------------------------------------------------
# outputs
# -----------------------------------------------------------------

gt, sr = get_gt_sr(f_cur)

write_gtiff(cur_unc, 'Base_Cur_UI_500m.tif', dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
write_gtiff(pot_unc, 'Base_Pot_UI_500m.tif', dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
