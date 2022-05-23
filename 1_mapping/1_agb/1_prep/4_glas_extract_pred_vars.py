#! /usr/bin/env python3
"""Extract 500m predictor variables for actual or potential modeling.

Usage:
    python3 4_extract_preds.py --help

    To include spectral variables for actual modeling, be sure to use --include_spectral
"""


import numpy as np
import gdal
import pandas as pd
import glob
import argparse
import os
import tempfile
import subprocess as sp
import shutil


def argparse_init():
    """Prepare ArgumentParser for command line inputs."""
    p = argparse.ArgumentParser(
        description='Extract predictor variables at GLAS shot locations.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('input_csv',
                   help='Path to input csv.',
                   type=str)
    p.add_argument('output_csv',
                   help='Path to output csv.',
                   type=str)
    p.add_argument('gs_pattern_listing',
                   help='Text file containing GC Storage dirs for predictors.',
                   type=str)
    p.add_argument('--include_spectral',
                   help='Extract spectral variables for actual modeling.',
                   dest='include_spectral',
                   default=False,
                   action='store_true')

    return(p)


def get_indices(coords, geotrans):
    """Get raster indices for set of coords given raster geotransformation."""
    x_indices, y_indices = (((coords[:,0]-geotrans[0])/geotrans[1]).astype(int),
                            ((coords[:,1]-geotrans[3])/geotrans[5]).astype(int))

    return x_indices, y_indices


def stage_rasters(mtile, gs_pattern_list):
    """Stage rasters from Google Cloud Storage."""
    tmpdir = tempfile.mkdtemp()

    for gs_pattern in gs_pattern_list:
        sp.call(['gsutil', '-q', 'cp', '{}{}.*'.format(gs_pattern, mtile),
                 tmpdir])

    return tmpdir


def extract_spectral(df, pred_dir):
    """Extract spectral variables and add to dataframe

    Notes:
        Relies on spectral raster ending in *.bip. Not a good idea.

    """
    coords = df.as_matrix(['modis_x', 'modis_y'])

    # Get raster indices
    r_path = glob.glob('{}/*.bip'.format(pred_dir))[0]
    geotrans = gdal.Open(r_path).GetGeoTransform()
    x_indices, y_indices = get_indices(coords, geotrans)

    fh = gdal.Open(r_path)
    band_nums = fh.RasterCount
    for band in range(1,band_nums+1):
        var_name = 'c6_b{}'.format(str(band))
        var_array = fh.GetRasterBand(band).ReadAsArray()
        var_vals = var_array[y_indices,x_indices]
        df.loc[:, var_name] = var_vals

    return df


def extract_nonspectral(df, pred_dir, mtile):
    """Extract all nonspectral variables (soil, climate, elevation, slope."""
    coords = df.as_matrix(['modis_x', 'modis_y'])

    # Get list of raster paths
    r_path_list = glob.glob('{}/*{}*.tif'.format(pred_dir, mtile))

    # Get raster indices using first raster geotransform
    geotrans = gdal.Open(r_path_list[0]).GetGeoTransform()
    x_indices, y_indices = get_indices(coords, geotrans)

    for r_path in r_path_list:
        var_name = os.path.basename(r_path).split(mtile)[0][:-1]
        fh = gdal.Open(r_path)
        var_array = fh.GetRasterBand(1).ReadAsArray()
        var_vals = var_array[y_indices, x_indices]
        df.loc[:, var_name] = var_vals

    return df


def extract_all_vars(input_csv, output_csv, gs_pattern_list_file,
                     include_spectral=False):
    """Extract all variables"""

    # Read csv
    glas_df = pd.read_csv(input_csv)

    # Find MODIS tile
    mtile_string = 'h{}v{}'.format(str(int(glas_df.loc[0, 'h_tile'])).zfill(2),
                                   str(int(glas_df.loc[0, 'v_tile'])).zfill(2))

    # Get GS directory listing
    with open(gs_pattern_list_file) as src:
        gs_pattern_list = src.read().splitlines()

    # Stage rasters into temporary directory
    tmpdir = stage_rasters(mtile_string, gs_pattern_list)

    # Extract variables
    glas_df = extract_nonspectral(glas_df, tmpdir, mtile_string)
    if include_spectral:
        glas_df = extract_spectral(glas_df, tmpdir)

    # Write output df
    glas_df.to_csv(output_csv, header=True, mode='w', index=False)

    shutil.rmtree(tmpdir)

    return


def main():
    # Get args
    parser = argparse_init()
    args = parser.parse_args()

    extract_all_vars(args.input_csv, args.output_csv, args.gs_pattern_listing,
                     args.include_spectral)

    return

if __name__ == '__main__':
    main()
