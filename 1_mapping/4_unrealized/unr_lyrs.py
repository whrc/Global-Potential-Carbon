#!/usr/bin/env python3
#!/usr/bin/env python3

from raspy import *

def comp_unr(f_cur_i, f_pot_i, f_unr_o, nd = -32768, verbose = True):
	cur = raster(f_cur_i, verbose = verbose)
	pot = raster(f_pot_i, verbose = verbose)
	ind = np.logical_or(cur == nd, pot == nd)
	cur[ind] = 0
	pot[ind] = 0
	unr = pot - cur
	unr[ind] = nd
	gt, sr = get_gt_sr(f_cur_i)
	write_gtiff(unr, f_unr_o, dtype = 'Int16', gt = gt, sr = sr, nodata = nd, stats = True, msg = verbose)
	return

def main():
	pools = ['AGB', 'BGB', 'SOC']
	for pool in pools:
		comp_unr(
			f_cur_i = 'Current_{}_MgCha_500m.tif'.format(pool), 
			f_pot_i = 'Potential_{}_MgCha_500m.tif'.format(pool), 
			f_unr_o = 'Unrealized_{}_MgCha_500m.tif'.format(pool)
		)

if __name__ == '__main__':
	main()
