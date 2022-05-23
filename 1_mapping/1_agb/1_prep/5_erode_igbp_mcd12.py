#!/usr/bin/env python3
"""Erode target igbp classes by 2 pixels

Erodes target landcover class by specified # of pixels.

Usage:
    python3 5_erode_igbp_mcd12.py [in-tif] [out-tif] [mode]

"""
import skimage.morphology as skmorph
import gdal
import sys
import numpy as np
import re
import os
import subprocess
import glob
import tempfile
import shutil

in_tif = sys.argv[1]
out_tif = sys.argv[2]
mode = sys.argv[3] # actual or potential

if mode == 'actual':
    lc_targets = np.array([10,12,13,15,16])
elif mode == 'potential':
    lc_targets = np.array([16])
else:
    raise('Error: arg 3 must be actual or potential')

padding = 927 # ~ 2 x 463m

def apply_erosion(array):
    nbhood = np.array([[0,0,1,0,0],
                       [0,1,1,1,0],
                       [1,1,1,1,1],
                       [0,1,1,1,0],
                       [0,0,1,0,0]])
    return(skmorph.binary_erosion(array,nbhood))

def glob_tif(target_path):
    globd = glob.glob(target_path)
    if len(globd) > 0:
        return(globd[0])
    else:
        return('')
def build_3x3_vrt(in_path,pad, tmpdir):
    fh = gdal.Open(in_path)
    ulx, xres, xskew, uly, yskew, yres  = fh.GetGeoTransform()
    lrx = ulx + (fh.RasterXSize * xres)
    lry = uly + (fh.RasterYSize * yres)
    hv = re.search("(h\d+v\d+)",in_path).group(0)

    combined_vrt = tmpdir + '/morph_' + hv + '.vrt'
    h = int(hv[1:3])
    v = int(hv[4:6])
    all_h = np.array([-1,0,1]) + h
    all_v = np.array([-1,0,1]) + v
    new_hvs = ['h' + str(x).zfill(2) + 'v' + str(y).zfill(2) for x in all_h for y in all_v]
    full_paths_list = [glob_tif(os.path.dirname(in_path) + '/*' + z + '*.tif') for z in new_hvs]
    subprocess.call(['gdalbuildvrt','-te',str(ulx-pad),str(lry-pad),str(lrx+pad),str(uly+pad),
                     combined_vrt] + full_paths_list)
    return(combined_vrt)

def write_image(im,inpath,outpath,gdal_dtype):
    # Input
    source_ds = gdal.Open(inpath)

    # Destination
    dst_filename = outpath
    y_pixels, x_pixels = im.shape  # number of pixels in x
    driver = gdal.GetDriverByName('GTiff')
    outds = driver.Create(dst_filename,x_pixels, y_pixels, 1,gdal_dtype,options = [ 'COMPRESS=LZW' ])
    outds.GetRasterBand(1).WriteArray(im)

    # Add GeoTranform and Projection
    geotrans=source_ds.GetGeoTransform()  #get GeoTranform from existed 'data0'
    proj=source_ds.GetProjection() #you can get from a exsited tif or import
    outds.SetGeoTransform(geotrans)
    outds.SetProjection(proj)
    outds.FlushCache()
    outds=None
    return()

def main():
    tmpdir = tempfile.mkdtemp()
    in_vrt = build_3x3_vrt(in_tif,padding, tmpdir)
    fh = gdal.Open(in_vrt)
    in_array = fh.GetRasterBand(1).ReadAsArray()

    binary_array = np.zeros(in_array.shape)
    binary_array[np.isin(in_array,lc_targets)] = 1

    out_array = apply_erosion(binary_array)
    print((out_array.shape))
    write_image(out_array[2:2403,2:2403],in_tif,out_tif,gdal.GDT_Byte)
    shutil.rmtree(tmpdir)
    return()

if __name__ == "__main__":
    main()
