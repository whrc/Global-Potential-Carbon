#!/usr/bin/env python3

"""Computes a BGB layer using layers of AGB and R:S ratios."""

# usage:
#   ./compute_belowground.py --agb <input_aboveground_biomass.tif> --r2s <input_r2s_ratios.tif> \
#     --out <output_belowground_biomass.tif> [options]

class ScaleFactorError(Exception):
    pass

class DimsError(Exception):
	pass

from optparse import OptionParser
from raspy import *

def compute_belowground(agb_img, r2s_img, agb_nd, r2s_nd, opts):

	if opts.verbose: print('Converting NoData values in the R:S ratios array to 0 ...'.format(r2s_nd), flush = True)
	r2s_img[r2s_img == r2s_nd] = 0

	if opts.verbose: print('Multiplying AGB and R:S ratios to compute a BGB array ...', flush = True)
	bgb_flt_img = agb_img * r2s_img

	if opts.verbose: print('Applying Mokany et al.\'s (2006) Eq. 1 to pixels with missing BGB ...', flush = True)
	index_eq1 = (agb_img != agb_nd) & (agb_img > 0) & (bgb_flt_img == 0) & (r2s_img == 0)
	del r2s_img
	bgb_flt_img[index_eq1] = np.power(agb_img[index_eq1], 0.89) * 0.489
	del index_eq1

	if opts.verbose: print('Converting BGB from type float to integer ...', flush = True)
	bgb_int_img = np.rint(bgb_flt_img).astype(np.int16)
	del bgb_flt_img

	if opts.verbose: print('Replacing BGB NoData value ...'.format(agb_nd), flush = True)
	bgb_int_img[agb_img == agb_nd] = agb_nd
	del agb_img

	return bgb_int_img

def main():

	# tool parameters
	usage = "usage: %prog --agb <input_aboveground_biomass.tif> \\\n\t--r2s <input_r2s_ratios.tif> --out <output_belowground_biomass.tif> [options]"
	parser = OptionParser(usage = usage, description = __doc__)
	parser.add_option('-a', '--agb', dest = "agb", action = "store", default = None, metavar = "FILE", help = "REQUIRED; path to raster of aboveground biomass")
	parser.add_option('-r', '--r2s', dest = "r2s", action = "store", default = None, metavar = "FILE", help = "REQUIRED; path to raster of root:shoot ratios")
	parser.add_option('-o', '--out', dest = "bgb", action = "store", default = None, metavar = "FILE", help = "REQUIRED; path for output raster")
	parser.add_option('-s', '--scaling-factor', dest = "scale", action = "store", type = "int", default = 1, metavar = "INT", help = "scaling factor to divide root:shoot ratios by if the raster is stored as integers rather than floats")
	parser.add_option('--overwrite', dest = "overwrite", action = "store_true", default = False, help = "overwrite output raster")
	parser.add_option('-d', '--dry-run', dest = "dry_run", action = "store_true", default = False, help = "perform a dry run (do not save result to disk)")
	parser.add_option('-v', '--verbose', dest = "verbose", action = "store_true", default = False, help = "print progress information")

	# parse options and arguments
	(opts, args) = parser.parse_args()
	agb_tif = opts.agb
	r2s_tif = opts.r2s
	bgb_tif = opts.bgb

	# ----------------------------------------------------------------------------------------------
	# Process raster data
	# ----------------------------------------------------------------------------------------------

	try:

		if agb_tif is None: parser.error('--agb must be set.')
		if r2s_tif is None: parser.error('--r2s must be set.')
		if bgb_tif is None: parser.error('--out must be set.')
		if not os.path.isfile(agb_tif): parser.error('\n{} does not exist.'.format(agb_tif))
		if not os.path.isfile(r2s_tif): parser.error('\n{} does not exist.'.format(r2s_tif))
		if os.path.isfile(bgb_tif) and not opts.overwrite: parser.error('\nThe output raster {} already exists.\nSet --overwrite flag to overwrite existing raster.'.format(bgb_tif))
		if opts.dry_run: print('*** This is only a dry-run. No outputs will be saved. ***', flush = True)

		# check data type of scaling factor
		scale_factor = opts.scale
		if type(scale_factor) is not int:
			raise ScaleFactorError

		# check dimension of input rasters
		agb_dims = get_dims(agb_tif)
		r2s_dims = get_dims(r2s_tif)
		if agb_dims != r2s_dims:
			raise DimsError

		# get CRS info from AGB for BGB output
		gt, sr = get_gt_sr(agb_tif)

		# load input rasters into memory
		if opts.verbose: print('Reading AGB input: {} ...'.format(agb_tif), flush = True)
		agb_img = raster(agb_tif)

		if opts.verbose: print('Reading R:S input: {} ...'.format(r2s_tif), flush = True)
		r2s_img = raster(r2s_tif)

		# apply scaling factor (default is 1)
		if scale_factor > 1:
			print('Dividing R:S ratios by scaling factor of {} ...'.format(scale_factor), flush = True)
			r2s_img = r2s_img / scale_factor

		# get NoData values of input rasters
		agb_nd = get_nodata(agb_tif)
		r2s_nd = get_nodata(r2s_tif)

		# - - - - - - - - - - - - - - - - - - - - - - - - - -
		# Compute belowground biomass
		# - - - - - - - - - - - - - - - - - - - - - - - - - -

		bgb_img = compute_belowground(agb_img, r2s_img, agb_nd, r2s_nd, opts)
		del agb_img
		del r2s_img

		if not opts.dry_run:
			if opts.verbose: print('Writing {} ...'.format(bgb_tif), flush = True)
			write_gtiff(bgb_img, bgb_tif, dtype = 'Int16', gt = gt, sr = sr, nodata = agb_nd, stats = True)

	# ----------------------------------------------------------------------------------------------
	# Exceptions
	# ----------------------------------------------------------------------------------------------

	except MemoryError:
		print('Error: ran out of memory.', flush = True)

	except DimsError:
		print('Error: input rasters must have the same dimensions.', flush = True)

	except ScaleFactorError:
		print('Error: scaling factor must be integer.', flush = True)

if __name__ == "__main__":
	main()
