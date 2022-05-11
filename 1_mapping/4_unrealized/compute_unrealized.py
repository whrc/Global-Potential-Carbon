#!/usr/bin/env python3
# 
# usage:
# ./compute_unrealized.py <input_current_biomass.tif> <input_potential_biomass.tif> [options]
#

from optparse import OptionParser
from raspy import *

def calc_unr(cur_arr, cur_nd, pot_arr, pot_nd, unr_nd):
	"""Compute unrealized potential biomass image array from current and potential bimass image arrays"""
	unr_arr = pot_arr - cur_arr # compute unrealized potential array
	unr_arr[(cur_arr == cur_nd) | (pot_arr == pot_nd)] = unr_nd # address NoData cells
	return unr_arr

def main():
	
	# tool parameters
	parser = OptionParser(usage = 'usage: %prog <input_current_biomass.tif> <input_potential_biomass.tif> [options]', description = __doc__)
	parser.add_option('-n', '--nodata', dest = 'nodata', action = 'store', type = 'int', metavar = 'INT', default = -32768, help = 'output NoData value (default is %default)')
	parser.add_option('-o', '--outfile', dest = 'outfile', action = 'store', type = 'string', metavar = 'FILE', default = 'unrealized_potential.tif', help = 'unrealized potential biomass raster output path (default is \"%default\")')
	
	# parse options and arguments
	(opts, args) = parser.parse_args()
	if len(args) != 2:
		parser.error('\nIncorrect number of arguments.')
	else:
		cur_tif, pot_tif = args
		unr_tif = opts.outfile
		unr_nd = opts.nodata
		
		# ----------------------------------------------------------------------------------------------
		print('1/4: Reading inputs ...', flush = True)
		# ----------------------------------------------------------------------------------------------
		
		# read in current and potential rasters
		cur_arr = raster(cur_tif)
		pot_arr = raster(pot_tif)
		
		# check NoData values of input rasters
		cur_nd = get_nodata(cur_tif)
		pot_nd = get_nodata(pot_tif)

		# check CRS info from inputs for outputs
		gt, sr = get_gt_sr(cur_tif)
		
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		print('2/4: Computing unrealized potential biomass raster ...', flush = True)
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		
		unr_arr = calc_unr(cur_arr, cur_nd, pot_arr, pot_nd, unr_nd)
		
		print('Writing {} ...'.format(unr_tif), flush = True)
		write_gtiff(unr_arr, unr_tif, dtype = 'Int16', gt = gt, sr = sr, nodata = unr_nd)

		# free up memory
		del unr_arr
		
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		print('3/4: Computing adjusted potential biomass raster ...', flush = True)
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		
		# index pixels where current is greater than potential (do not include NoData cells)
		cur_gt_pot_ind = (cur_arr > pot_arr) & (cur_arr != cur_nd) & (pot_arr != pot_nd)
		
		# if current is greater than potential, then set potential to current
		pot_arr[cur_gt_pot_ind] = cur_arr[cur_gt_pot_ind]

		del cur_gt_pot_ind
		
		adj_pot_tif = pot_tif.replace('.tif', '_adj.tif')
		print('Writing {} ...'.format(adj_pot_tif), flush = True)
		write_gtiff(pot_arr, adj_pot_tif, dtype = 'Int16', gt = gt, sr = sr, nodata = pot_nd)
		
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		print('4/4: Computing adjusted unrealized potential biomass raster ...', flush = True)
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		
		adj_unr_arr = calc_unr(cur_arr, cur_nd, pot_arr, pot_nd, unr_nd)
		
		del cur_arr, pot_arr
		
		adj_unr_tif = unr_tif.replace('.tif', '_adj.tif')
		print('Writing {} ...'.format(adj_unr_tif), flush = True)
		write_gtiff(adj_unr_arr, adj_unr_tif, dtype = 'Int16', gt = gt, sr = sr, nodata = unr_nd)
		
if __name__ == '__main__':
	main()

