#!/usr/bin/env Rscript
# ------------------------------------------------------------------------------------------
#
# warp2sin.R
#
# Purpose:
# 	Reprojects a raster to the ~500m MODIS sinusoidal grid via nearest neighbor resampling.
#
# Usage:
# 	./warp2sin.R <input.tif> [options]
#
# Notes:
# 	Gdalwarp will print warnings/errors, but after much testing, it has been determined that
# 	the result is achieved most accurately using the following combination of gdalwarp and
# 	gdal_translate. Thus, ignore warning/error messages. For more info on the underlying
# 	gdalwarp problem with projecting global rasters from WGS84 to sinusoidal, see:
# 	https://gis.stackexchange.com/q/119603/109281.
#
# ------------------------------------------------------------------------------------------

suppressPackageStartupMessages(library(optparse))

file.ext <- function(x) {
	pos <- regexpr("\\.([[:alnum:]]+)$", x)
	ifelse(pos > -1L, substring(x, pos + 1L), "")
}

opt.list <- list(
	make_option(c('-o','--outfile'), type = 'character', default = NULL, metavar = 'FILE',
				help = 'Path for output GeoTIFF (default is to append \"_sin\" to input path)'),
	make_option(c('-r','--resampling-method'), type = 'character', default = 'near', metavar = 'STRING', dest = 'method',
				help = 'Resampling method to use (default is \"%default\"; for list of available gdalwarp\n\t\toptions, see https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-r)'),
	make_option(c('-s','--stats'), action = 'store_true', default = F,
				help = 'Compute statistics of output'),
	make_option(c('-v','--verbose'), action = 'store_true', default = F,
				help = 'Prints progress and information messages')
)

opt.parser <- OptionParser(option_list = opt.list,
						   usage = 'usage: %prog <input.tif> [options]\n',
						   description = paste0('Reprojects a raster to match the CRS, resolution, and extent\n',
						   					 'of WHRC\'s MODIS-based global biomass products.\n\n',
						   					 'Arguments:\n', '\t<input.tif>\n', '\t\tRaster (GeoTIFF or VRT) to reproject'))

inputs <- try(parse_args(opt.parser, positional_arguments = 1), silent = T)

if (inherits(inputs, 'try-error')) {
	print_help(opt.parser)
	stop('must provide input GeoTIFF.')
}

pos.args <- inputs$args
opt.args <- inputs$options

inpfile <- pos.args[1]
outfile <- opt.args$outfile
method <- opt.args$method
verbose <- opt.args$verbose
stats.flag <- opt.args$stats

methods <- c('near','bilinear','cubic','cubicspline','lanczos','average','mode','max','min','med','q1','q3')
if (!method %in% methods) stop(paste('resampling method must be one of', paste(methods, collapse = ', ')))

ext <- file.ext(inpfile)
if ((ext != 'tif') & (ext != 'vrt')) stop('input file must be a GeoTIFF or VRT.')
if (verbose) cat(paste('Input:', inpfile), fill = T)
if (verbose) cat(paste('Resampling method:', method), fill = T)
if (is.null(outfile)) {
	outfile <- paste0(dirname(inpfile), '/', gsub(paste0('.', ext, '$'), paste0('_sin.', ext), basename(inpfile)))
} else {
	if (file.ext(outfile) != 'tif') stop('output file must be a GeoTIFF.')
}
if (file.exists(outfile)) stop(paste(outfile, 'already exists.'))
tmpfile <- paste0(dirname(outfile), '/', gsub('.tif$', '_tmp.tif', basename(outfile)))

res <- 463.312716525001520 # or 463.312716529999989 ???

if (verbose) cat('\n1. Reprojecting to modis 500m sinusoidal grid ...', fill = T)
warp.cmd <- paste('gdalwarp',
	'-of GTiff',
	'-co "COMPRESS=LZW"',
	'-tap',
	'-tr', res, res,
	'-r near',
	"-t_srs '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs'",
	'-multi',
	'-overwrite',
	inpfile,
	tmpfile)
warp.catch <- system(warp.cmd, ignore.stderr = (!verbose), intern = (!verbose))

if (!file.exists(tmpfile)) stop('reprojection not successful.')

if (verbose) cat('\n2. Correcting extent ...', fill = T)
trns.cmd <- paste('gdal_translate',
	'-projwin -20015109.354 10007554.677 20015109.354 -6671703.118',
	'-tr', res, res,
	'-of GTiff',
	'-co "COMPRESS=LZW"',
	tmpfile,
	outfile)
trns.catch <- system(trns.cmd, ignore.stderr = (!verbose), intern = (!verbose))

if (verbose) cat('\n3. Cleaning up ...', fill = T)
unlink(tmpfile)

if (stats.flag) {
	if (verbose) cat('\n4. Computing stats ...', fill = T)
	edit.cmd <- paste('gdal_edit.py -stats', outfile)
	edit.catch <- system(edit.cmd, ignore.stderr = (!verbose), intern = (!verbose))
}

