#!/bin/bash
set -e

#
# Script:
#   prep_shifting_ag.sh
#
# Source:
#   Curtis et al. 2018 Science (https://science.sciencemag.org/content/361/6407/1108)
#   Data: https://gfw2-data.s3.amazonaws.com/forest_change/tsc/Goode_FinalClassification_19_05pcnt_prj.zip
#   Info: http://data.globalforestwatch.org/datasets/tree-cover-loss-by-dominant-driver

# Class codes:
#   0 = Zero or minor loss
#   1 = Commodity driven deforestation
#   2 = Shifting agriculture
#   3 = Forestry
#   4 = Wildfire
#   5 = Urbanization
#   -1.69999999999999994e+308 = NoData

# convert from float to binary mask of shifting agricultural forest loss (i.e., 0 = not shifting ag, 1 = shifting ag)
FLT_WGS_10KM=/mnt/data3/biomass/sgorelik/misc/curtis/Goode_FinalClassification_19_05pcnt_prj.tif
MSK_WGS_10KM=/mnt/data3/biomass/sgorelik/misc/curtis/curtis_shifting_ag_mask.tif
gdal_calc.py \
    -A $FLT_WGS_10KM \
    --outfile=$MSK_WGS_10KM \
    --calc='A == 2' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0 \
    --overwrite

# downsample/reproject raster from ~10km/WGS84 to 500m/sinusoidal
Rscript \
    /mnt/data3/sgorelik/repos/biomass_team/unrealized/1_mapping/warp2sin.R \
    $MSK_WGS_10KM \
    -o /mnt/data3/biomass/sgorelik/misc/curtis/curtis_shifting_ag_mask_500m.tif \
    -s -v

# cleanup temporary file
gdalmanage delete $MSK_WGS_10KM