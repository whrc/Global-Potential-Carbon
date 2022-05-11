#!/bin/bash
set -e

#
# Script:
#   prep_ellis_rangeland.sh
#
# Source:
#   Ellis et al. 2010: https://doi.org/10.1111/j.1466-8238.2010.00540.x
#   Data: http://ecotope.org/files/anthromes/v2/data/anthromes/anthromes_2_GeoTIFF.zip
#   Info: http://ecotope.org/anthromes/v2/data/
#

# Rangeland classes/pixel values:
#  41 = Residential rangelands
#  42 = Populated rangelands
#  43 = Remote rangelands

# create mask of rangeland (i.e., 0 = not rangeland, 1 = rangeland) ca. 10km
SRC_TIF=/mnt/data3/biomass/sgorelik/misc/anthromes/2000/anthro2_a2000.tif
DST_TIF=/mnt/data3/biomass/sgorelik/misc/anthromes/2000/ellis_rangeland_mask.tif
gdal_calc.py \
    -A $SRC_TIF \
    --outfile=$DST_TIF \
    --calc='(A == 41) + (A == 42) + (A == 43)' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0 \
    --overwrite

# downsample/reproject raster from ~1km/WGS84 to 500m/sinusoidal
Rscript \
    /mnt/data3/sgorelik/repos/biomass_team/unrealized/1_mapping/warp2sin.R \
    $DST_TIF \
    -o /mnt/data3/biomass/sgorelik/misc/anthromes/2000/ellis_rangeland_mask_500m.tif \
    -s -v

# cleanup temporary file
gdalmanage delete $DST_TIF
