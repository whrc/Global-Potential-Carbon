#!/bin/bash
set -e

# Source:
#   Global Human Settlement Layer (GHSL), v1.0
#   Pesaresi and Freirie 2016: http://data.jrc.ec.europa.eu/dataset/jrc-ghsl-ghs_smod_pop_globe_r2016a
#   Data: http://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_SMOD_POP_GLOBE_R2016A/GHS_SMOD_POP2015_GLOBE_R2016A_54009_1k/V1-0/GHS_SMOD_POP2015_GLOBE_R2016A_54009_1k_v1_0.zip
#   Info: https://ghsl.jrc.ec.europa.eu/ghs_smod.php
#
#   GHSL is generated by integration of built-up areas produced from
#   Landsat image and population data derived from the CIESIN GPW v4.
#
#   Classes:
#   0 = NoData
#   1 = Rural
#   2 = Urban clusters
#   3 = Urban centers

# create mask (0 = not urban, 1 = urban) (ca. 1km)
gdal_calc.py \
    -A GHS_SMOD_POP2015_GLOBE_R2016A_54009_1k_v1_0.tif \
    --outfile=ghsl_urban_mask.tif \
    --calc='(A == 2) + (A == 3)' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0

# downsample and reproject from ~1km/WGS84 to 500m/sinusoidal
Rscript ../warp2sin.R ghsl_urban_mask.tif -o ghsl_urban_mask_500m.tif -s -v

rm ghsl_urban_mask.tif
