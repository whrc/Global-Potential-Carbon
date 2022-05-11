#!/bin/bash

#
# Script:
#   prep_ramankutty_pastureland.sh
#
# Source data (login needed):
#   https://sedac.ciesin.columbia.edu/downloads/data/aglands/aglands-pastures-2000/gl-pastures-geotif.zip
#

# multiply input raster by 100 to convert from floats ranging from 0-1 to integer ranging from 0-100% pasture per pixel
RAT_WGS_10KM=/mnt/data3/biomass/sgorelik/misc/SEDAC/pasture/pasture.tif
INT_WGS_10KM=/mnt/data3/biomass/sgorelik/misc/SEDAC/pasture/pasture_byte.tif
gdal_calc.py \
    -A $RAT_WGS_10KM \
    --outfile=$INT_WGS_10KM \
    --calc='(A > 0) * A * 100' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --overwrite \
    --NoDataValue=0

# downsample/reproject raster from ~10km/WGS84 to 500m/sinusoidal
INT_SIN_500M=/mnt/data3/biomass/sgorelik/misc/SEDAC/pasture/pasture_byte_500m.tif
Rscript ../warp2sin.R $INT_WGS_10KM -o $INT_SIN_500M -s

# convert from proportion of land area used as pasture (grazing) per pixel to mask of pasture land (i.e., 0 = non-pasture, 1 = pasture)
MSK_SIN_500M=/mnt/data3/biomass/sgorelik/misc/SEDAC/pasture/SEDAC_500m_global_pasture_mask.tif
gdal_calc.py \
    -A $INT_SIN_500M \
    --outfile=$MSK_SIN_500M \
    --calc='(A > 50) * 1' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --overwrite \
    --NoDataValue=0

rm $INT_WGS_10KM $INT_SIN_500M