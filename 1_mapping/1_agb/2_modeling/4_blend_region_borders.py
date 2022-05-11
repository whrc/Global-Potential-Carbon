#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Blend region borders for 500m AGB biomass map

Usage:
    python3 4_blend_region_borders.py --help
    
"""


from __future__ import print_function
import subprocess as sp
import os
import sys
import argparse
import shutil
import glob
import re
import tempfile
import shutil
import itertools
import pandas as pd


# Border pairs to exclude. Used in case when tile in both regions, but
# borders not actually touching. Should be list of sets.
BORDERS_EXCLUDE = [{'tropical_asia', 'tropical_africa'}]


def argparse_init():
    """Prepare ArgumentPjarser for inputs"""

    p = argparse.ArgumentParser(
        description="Blend region borders for 500m AGB biomass map.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('srcdir',
                   help = 'Path to raw tile directory',
                   type = str)
    p.add_argument('dstfile',
                   help = 'Path to output raster file, GTiff format',
                   type = str)
    p.add_argument('--shapefile_dir',
                   help = 'Directory containing region shapefiles',
                   default = '/mnt/a/mfarina/biomass_shapefiles/with_mtiles/',
                   type = str)
    p.add_argument('--save_tiles',
                   help = 'Save blended tiles along border in this dir.',
                   default = None,
                   type = str)

    return(p)


def populate_tile_dict(srcdir, region_list,
                       tile_id_regex = r'h[0-9]{2}v[0-9]{2}'):
    """Creates dictionary of every tile in every region.

    Args:
        srcdir (str): Path to raw tile dir.
        region_list (list): List of region names.
        tile_id_regex (str): Regex pattern to match tile id. Defaults to
            MODIS style. Lat/Long would be: r'[0-9]{2}[N|S]_[0-9]{3}[E|W]'

    Returns:
        dict: Dictionary of tiles by region.

    """

    tile_dict = {}
    r = re.compile(tile_id_regex)

    for reg in region_list:
        reg_files = glob.glob('{}/*{}*.tif'.format(srcdir, reg))
        reg_tile_ids = [r.search(f).group(0) for f  in reg_files]
        tile_dict[reg] = reg_tile_ids

    return(tile_dict)


def prep_borders(target_reg, other_reg, srcdir, border_tiles, tmpdir,
        shapefile_dir):
    """Prepares masks and proximity calculation tifs for blending.

    Args:
        target_reg (str): Region for proximity calculations.
        other_reg (str): Border region.
        srcdir (str): Directory containing raw input tiles.
        border_tiles (list): Tiles contained in both target_reg and other_reg.
        tmpdir (str): Temporary working directory. Tifs will be saved here.
        shapefile_dir (str): Directory containing region boundary shapefiles.

    Returns:
        Tuple containing:
        (str: Path to raw mosaic tif,
         str: Path to prox tif)

    """
    # Step 1: Define temporary file paths
    raw_vrt = '{}/{}_{}_raw_mosaic.vrt'.format(tmpdir, target_reg, other_reg)
    raw_tif = os.path.splitext(raw_vrt)[0] + '.tif'
    mask_tif = '{}/{}_{}_mask.tif'.format(tmpdir, target_reg, other_reg)
    prox_tif = '{}/{}_{}_prox.tif'.format(tmpdir, target_reg, other_reg)

    # Step 2: Build mosaics of raw tiles
    sp.call((['gdalbuildvrt',
              '-tap', '-tr', '463.31271653', '463.31271653',
              raw_vrt] +
              [glob.glob('{}/{}*{}*.tif'.format(
                  srcdir, target_reg, t))[0] for t in border_tiles]))

    sp.call(['gdal_translate', '-co', 'COMPRESS=LZW',
             raw_vrt, raw_tif])

    # Step 3: Create clipped mask
    shapefile_path = glob.glob('{}/*{}*.shp'.format(shapefile_dir, target_reg))
    if not len(shapefile_path) == 1:
        print('Error: Not exactly 1 shapefile for {}'.format(target_reg))
        exit
    else:
        shapefile_path = shapefile_path[0]
    # Make mask of zeros
    sp.call(['gdal_calc.py', '-A', raw_tif, '--calc=0',
              '--outfile={}'.format(mask_tif)])
    # Rasterize
    sp.call(['gdal_rasterize', '-b', '1', '-burn', '1',
             '-l', os.path.splitext(os.path.basename(shapefile_path))[0],
             shapefile_path, mask_tif])

    # Step 4: Proximity calculation
    sp.call(['gdal_proximity.py', '-values', '1', '-co', 'COMPRESS=LZW',
             '-ot','Float32', mask_tif, prox_tif])

    return(raw_tif, prox_tif)


def blend_regions(reg1, reg2, srcdir, border_tiles, tmpdir,
        shapefile_dir):
    """Creates blended border mosaic of reg1, reg2.

    Args:
        reg1 (str): Name of first region
        reg2 (str): Name of second region
        srcdir (str): Directory containing raw input tiles
        border_tiles (list): List of tiles at border for blending
        tmpdir (str): Temporary working directory
        shapefile_dir (str): Directory containing region shapefiles

    Returns:
        str: Path to output tif blended border of reg1, reg2.

    """
    # Define filepaths for blended border tifs
    blend_float_tif = '{}/{}_{}_border.tif'.format(tmpdir, reg1, reg2)
    blend_int_tif = '{}/{}_{}_border_int.tif'.format(tmpdir, reg1, reg2)

    # Prepare files for blending
    r1_raw_path, r1_prox_path = prep_borders(
        reg1, reg2, srcdir, border_tiles, tmpdir,shapefile_dir)
    r2_raw_path, r2_prox_path = prep_borders(
        reg2, reg1, srcdir, border_tiles, tmpdir,shapefile_dir)

    # Blend calculation. Using hard-coded distance of 250 pixels.
    sp.call(['gdal_calc.py',
             '-A', r1_raw_path, '-B', r1_prox_path,
             '-C', r2_raw_path, '-D', r2_prox_path,
             ('--calc=(-32768*logical_and(A==-32768,C==-32768))+(A*((B<250)*(1-(B/250)))+(C*((D<250)*(1-(D/250)))))'
             '/(((D<250)*(1-(D/250))+(B<250)*(1-(B/250)))+(1*logical_and(B>=250,D>=250)))'),
             '--outfile={}/{}_{}_border.tif'.format(tmpdir, reg1, reg2),
             '--type=Float32', '--creation-option=COMPRESS=LZW',
             '--NoDataValue=-32768', '--overwrite'])

    # Translate from float to int:
    sp.call(['gdal_translate', '-a_nodata', '-32768', '-co', 'COMPRESS=LZW',
             '-ot', 'Int16', blend_float_tif, blend_int_tif])

    return(blend_int_tif)


def clip_to_modis_tile(input_raster, modis_tile_ref, modis_h, modis_v,
                       output_raster):
    """Clip global or regional raster to a single MODIS tile."""

    target_corners = modis_tile_ref[(modis_tile_ref.h == modis_h) \
        & (modis_tile_ref.v == modis_v)]

    # Use gdal_translate to clip raster
    sp.call(['gdal_translate', '-co', 'COMPRESS=LZW',
        '-projwin', str(target_corners.minx.values[0]), str(target_corners.maxy.values[0]),
        str(target_corners.maxx.values[0]), str(target_corners.miny.values[0]),
        input_raster, output_raster])

    return


def blend_world(srcdir, dstfile, shapefile_dir, region_list, save_tiles):
    """Blend and create global mosaic

    Args:
        srcdir (str): Directory containing raw input tiles
        dstfile (str): Path to destination file
        shapefile_dir (str): Directory containing region shapefiles
        region_list (list): List of region names

    Returns:
        str: Path to final destination file

    """
    # Create temporary directory
    tmpdir = tempfile.mkdtemp()

    # Get dictionary of tiles in each region
    tile_dict = populate_tile_dict(srcdir, region_list)

    # Run blending for each region combination
    blended_border_tifs = []
    region_combos = list(itertools.combinations(region_list,2))
    for reg1, reg2 in region_combos:
        exclude_pair = {reg1, reg2} in BORDERS_EXCLUDE
        border_tiles = list(set(tile_dict[reg1]).intersection(
                                set(tile_dict[reg2])))

        if not exclude_pair and len(border_tiles)>0:
            print('{}-{} START'.format(reg1, reg2))
            blended_border_tifs.append(
                blend_regions(reg1, reg2, srcdir, border_tiles, tmpdir,
                              shapefile_dir))
            print('{}-{} DONE'.format(reg1, reg2))

        # If specified, save border tiles to dir
        if save_tiles is not None:
            sp.call(['mkdir', '-p', save_tiles])
            modis_tile_ref = pd.read_csv('./mod_tileref_sinu.csv')
            full_border = '{}/{}_{}_border_int.tif'.format(tmpdir, reg1, reg2)
            for hv in border_tiles:
                h = int(hv[1:3])
                v = int(hv[4:6])
                output_path = '{}/border_{}.tif'.format(save_tiles, hv)
                clip_to_modis_tile(full_border, modis_tile_ref, h, v,
                                   output_path)


    print('All Borders Ready')

    # Buildvrt
    sp.call((['gdalbuildvrt', '-tap', '-tr', '463.31271653', '463.31271653',
             '{}/global_blend.vrt'.format(tmpdir)] +
             glob.glob('{}/*.tif'.format(srcdir)) +
             [border_tif for border_tif in blended_border_tifs]))

    sp.call(['gdal_translate', '-co', 'COMPRESS=LZW',
             '{}/global_blend.vrt'.format(tmpdir), dstfile])

    # Remove temporary directory
    shutil.rmtree(tmpdir)

    return(dstfile)


def main():

    # Define region_list
    region_list = ['tropical_america', 'tropical_africa', 'tropical_asia',
                   'palearctic', 'australia', 'nearctic']

    parser = argparse_init()
    args = parser.parse_args()

    blend_world(args.srcdir, args.dstfile, args.shapefile_dir, region_list,
                args.save_tiles)

    return()


if __name__ == '__main__':
    main()
