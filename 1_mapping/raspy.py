#!/usr/bin/env python3

# functions for working with raster data
# https://github.com/srgorelik/raspy

from osgeo import gdal, osr
import numpy as np
import subprocess as sp
import os

def get_nodata(raster_file, band = 1):
	"""Get raster nodata value"""
	file = gdal.Open(raster_file)
	nodata = file.GetRasterBand(band).GetNoDataValue()
	file = None
	return nodata

def get_gt_sr(raster_file):
	"""Get geotransform"""
	file = gdal.Open(raster_file)
	gt = file.GetGeoTransform()
	sr = file.GetProjection()
	file = None
	return [gt, sr]

def get_proj4str(raster_file):
	"""Get proj4 string"""
	file = gdal.Open(raster_file)
	proj = osr.SpatialReference(wkt = file.GetProjection()).ExportToProj4().rstrip()
	file = None
	return proj

def get_nbands(raster_file):
	"""Get number of bands"""
	file = gdal.Open(raster_file)
	num_bands = file.RasterCount
	file = None
	return num_bands

def get_dims(raster_file):
	"""Get dimensions of raster file, without loading it into memory"""
	file = gdal.Open(raster_file)
	num_cols = file.RasterXSize
	num_rows = file.RasterYSize
	num_bands = file.RasterCount
	file = None
	return [num_cols, num_rows, num_bands]

def get_xy_res(raster_file):
	"""Get X and Y resolution of raster file, without loading it into memory"""
	file = gdal.Open(raster_file)
	gt = file.GetGeoTransform()
	file = None
	x_res = gt[1]
	y_res = -gt[5]
	return [x_res, y_res]

def get_prj_units(raster_file):
	"""Get units of raster file CRS, without loading it into memory"""
	prj4_str = get_proj4str(raster_file)
	prj4_str_list = prj4_str.split('+')
	units_str = list(filter(lambda x: 'units' in x, prj4_str_list))[0]
	units_str = units_str.strip().split('=')[1]
	return units_str

def get_cell_area_ha(raster_file):
	"""Get grid cell area (ha) of raster file, without loading it into memory"""
	units = get_prj_units(raster_file)
	if units == 'm':
		x_res, y_res = get_xy_res(raster_file)
		area_ha = x_res * y_res * 1e-4
		return area_ha
	else:
		print('Error: CRS units are {} (must be meters).'.format(units), flush = True)
		return

def get_dtype(raster_file, band = 1):
	"""Get raster data type"""
	file = gdal.Open(raster_file)
	dtype_int = file.GetRasterBand(band).DataType
	dtype_str = gdal.GetDataTypeName(dtype_int)
	file = None
	return dtype_str

def dtype_gdal(dtype_str):
	"""Translate data type from string to GDAL data type (integer)"""
	dtype_switcher = {
		"Unknown" : gdal.GDT_Unknown,   # Unknown or unspecified type
		"Byte" : gdal.GDT_Byte,         # Eight bit unsigned integer
		"UInt16" : gdal.GDT_UInt16,     # Sixteen bit unsigned integer
		"Int16" : gdal.GDT_Int16,       # Sixteen bit signed integer
		"UInt32" : gdal.GDT_UInt32,     # Thirty two bit unsigned integer
		"Int32" : gdal.GDT_Int32,       # Thirty two bit signed integer
		"Float32" : gdal.GDT_Float32,   # Thirty two bit floating point
		"Float64" : gdal.GDT_Float64,   # Sixty four bit floating point
		"CInt16" : gdal.GDT_CInt16,     # Complex Int16
		"CInt32" : gdal.GDT_CInt32,     # Complex Int32
		"CFloat32" : gdal.GDT_CFloat32, # Complex Float32
		"CFloat64" : gdal.GDT_CFloat64  # Complex Float64
	}
	dtype_int = dtype_switcher.get(dtype_str, 0)
	return dtype_int

def dtype_bit_depth(dtype_str):
	"""Get pixel bit depth from raster data type"""
	bit_depth_switcher = {
		"Byte" : 8,
		"UInt16" : 16,
		"Int16" : 16,
		"UInt32" : 32,
		"Int32" : 32,
		"Float32" : 32,
		"Float64" : 64,
		"CInt16" : 16,
		"CInt32" : 32,
		"CFloat32" : 32,
		"CFloat64" : 64
	}
	bit_depth = bit_depth_switcher.get(dtype_str, 0)
	return bit_depth

def raster(raster_file, bands = None, verbose = False):
	"""Load single- or multi-band raster from disk into a 2- or 3-dimensional numpy array in memory.\nNote, bands must be INTEGER or LIST of integers, e.g., [1, 3, 6] = Bands 1, 3 and 6. There is no Band 0."""
	if verbose: print('Reading {} ...'.format(raster_file), flush = True)
	file = gdal.Open(raster_file)
	tot_band_cnt = file.RasterCount
	if bands == None:
		if (verbose) & (tot_band_cnt == 1): print('Raster has 1 band ...', flush = True)
		if (verbose) & (tot_band_cnt > 1): print('Reading all {} bands ...'.format(tot_band_cnt), flush = True)
		arr = file.ReadAsArray()
	elif type(bands) == int: # in this case, "bands" refers to only one band
		if verbose: print('Reading band {} of {} ...'.format(bands, tot_band_cnt), flush = True)
		arr = file.GetRasterBand(bands).ReadAsArray()
	elif type(bands) == list:
		arr_list = []
		for band in bands:
			if verbose: print('Reading band {} ...'.format(band), flush = True)
			tmp_arr = file.GetRasterBand(band).ReadAsArray()
			arr_list.append(tmp_arr)
		arr = np.stack(arr_list, axis = 0)
	else:
		print('Error: bands argument must be type INTEGER or LIST (of integers), e.g., [1, 3, 6] = Bands 1, 3 and 6. There is no Band 0.', flush = True)
		return
	file = None
	return arr
	
def write_gtiff(img_arr, out_tif, dtype, gt, sr, nodata = None, stats = True, msg = False):
	"""Write a 2D numpy image array to a GeoTIFF raster file on disk"""
	
	# check that output is a numpy array
	if type(img_arr) != np.ndarray:
		print('Error: numpy array invalid', flush = True)
		return
	
	# check gdal data type
	dtype_int = dtype_gdal(dtype)
	if dtype_int == 0:
		print('Error: output data type invalid', flush = True)
		return
	
	if msg: print('Writing {} ...'.format(out_tif), flush = True)
	ndim = img_arr.ndim
	nband = 1
	nrow = img_arr.shape[0]
	ncol = img_arr.shape[1]
	driver = gdal.GetDriverByName('GTiff')
	out_dataset = driver.Create(out_tif, ncol, nrow, nband, dtype_int, options = [ 'COMPRESS=LZW' ])
	out_dataset.SetGeoTransform(gt)
	out_dataset.SetProjection(sr)
	out_dataset.GetRasterBand(1).WriteArray(img_arr)
	if (nodata != None) and (type(nodata) != str):
		out_dataset.GetRasterBand(1).SetNoDataValue(nodata)
	out_dataset = None
	if stats: cmd_chk = sp.run(['gdal_edit.py', '-stats', out_tif])
	return

def stats(input, nodata = None):
	"""Get descriptive statistics for either a raster on disk (input = filepath) or a numpy array stored in memory"""
	if (type(input) != str) and (type(input) != np.ndarray):
		print("Error: input must be either filepath to raster or numpy image array.", flush = True)
		return
	elif type(input) == str:
		file = gdal.Open(input)
		img = np.array(file.GetRasterBand(1).ReadAsArray())
		nodata = file.GetRasterBand(1).GetNoDataValue()
		img_data = img[img != nodata]
		del img
		img_min = np.min(img_data)
		img_max = np.max(img_data)
		img_mean = np.mean(img_data)
		img_std = np.std(img_data)
		file = None
	else: # type(input) == np.ndarray
		if nodata != None: input = input[input != nodata]
		img_min = np.min(input)
		img_max = np.max(input)
		img_mean = np.mean(input)
		img_std = np.std(input)
	if nodata == None:
		print("Min.\tMax.\tMean\tStd.", flush = True)
		print("%2.2f\t%2.2f\t%2.2f\t%2.2f" % (img_min, img_max, img_mean, img_std), flush = True)
		return
	else:
		print("Min.\tMax.\tMean\tStd.\tNoData", flush = True)
		print("%2.2f\t%2.2f\t%2.2f\t%2.2f\t%i" % (img_min, img_max, img_mean, img_std, nodata), flush = True)
		return


