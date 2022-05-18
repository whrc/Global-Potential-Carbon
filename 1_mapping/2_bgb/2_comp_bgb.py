#!/usr/bin/env python3

from raspy import *

# root:shoot ratios
f_r2s = 'Root2Shoot_Ratios_Scaled1e3_500m.tif'
r2s = raster(f_r2s, verbose = True)

# apply scaling factor
scale_factor = 1000
r2s = r2s / scale_factor

def comp_bgb(r2s, f_agb, f_bgb):
	
	agb = raster(f_agb, verbose = True)
	nd = get_nodata(f_agb)
	gt, sr = get_gt_sr(f_agb)
	
	# multiply aboveground by root:shoot ratios
	bgb_flt = agb * r2s
	
	# apply mokany et al.'s (2006) eq. 1 to pixels with no r:s ratio
	eq1_ind = (agb != nd) & (agb > 0) & (r2s == 0)
	bgb_flt[eq1_ind] = np.power(agb[eq1_ind], 0.89) * 0.489
	del eq1_ind
	
	bgb_int = np.rint(bgb_flt).astype(np.int16)
	del bgb_flt
	
	bgb_int[agb == nd] = nd
	del agb
	
	write_gtiff(bgb_int, f_bgb, dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = True)
	return

def main():
	
	# aboveground inputs
	f_agb_lst = ['Base_Cur_AGB_Mgha_500m.tif', 'Base_Pot_AGB_Mgha_500m.tif']
	
	# compute belowground
	for f_agb in f_agb_lst:
		f_bgb = f_agb.replace('AGB', 'BGB')
		comp_bgb(r2s, f_agb, f_bgb)

if __name__ == '__main__':
	main()
