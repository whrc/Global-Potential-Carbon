#!/bin/bash
set -e

#
# Script:
#   prep_gpw_urban.sh
#
# Source:
#   Gridded Population of the World (GPW), Population Density ca. 2015, v4.11
#   Data: https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-population-density-rev11/gpw-v4-population-density-rev11_2015_30_sec_tif.zip (login required)
#   Info: https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11
#

# create mask of urban areas (i.e., 0 = not urban, 1 = urban) ca. 1km
SRC_TIF=/mnt/data3/biomass/sgorelik/misc/SEDAC/population/gpw_v4_population_density_rev11_2015_30_sec.tif
DST_TIF=/mnt/data3/biomass/sgorelik/misc/SEDAC/population/gpw_gt100_urban_mask.tif
gdal_calc.py \
    -A $SRC_TIF \
    --outfile=$DST_TIF \
    --calc='A > 100' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0 \
    --overwrite

# downsample/reproject raster from ~1km/WGS84 to 500m/sinusoidal
Rscript \
    /mnt/data3/sgorelik/repos/biomass_team/unrealized/1_mapping/warp2sin.R \
    $DST_TIF \
    -o /mnt/data3/biomass/sgorelik/misc/SEDAC/population/gpw_gt100_urban_mask_500m.tif \
    -s -v

# cleanup temporary file
gdalmanage delete $DST_TIF
