#!/bin/bash
set -e

#
# Script:
#   prep_henderson_pastureland.sh
#
# Source:
#   Henderson et al. 2015: https://doi.org/10.1016/j.agee.2015.03.029
#   Data (mitkgco2eqha1.img) acquired from TNC (Susan/Peter, June 2019)
#

# convert from IMG to GeoTIFF
SRC_IMG=/mnt/data3/biomass/sgorelik/misc/henderson_2015/mitkgco2eqha1.img
DST_TIF=/mnt/data3/biomass/sgorelik/misc/henderson_2015/proc/mitkgco2eqha1.tif
gdal_translate -of GTiff -ot Float32 -co COMPRESS=LZW -a_nodata -9999 $SRC_IMG $DST_TIF

# create mask of pastureland (i.e., 0 = not pastureland, 1 = pastureland)
MSK_TIF=/mnt/data3/biomass/sgorelik/misc/henderson_2015/proc/henderson_pastureland_mask.tif
gdal_calc.py \
    -A $DST_TIF \
    --outfile=$MSK_TIF \
    --calc='A != -9999' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0 \
    --overwrite

# downsample/reproject raster from ~1km/WGS84 to 500m/sinusoidal
Rscript \
    /mnt/data3/sgorelik/repos/biomass_team/unrealized/1_mapping/warp2sin.R \
    $MSK_TIF \
    -o /mnt/data3/biomass/sgorelik/misc/henderson_2015/proc/henderson_pastureland_mask_sin500m.tif \
    -s -v

# cleanup temporary file
gdalmanage delete $MSK_TIF
