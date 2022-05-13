#!/bin/bash
set -e

# source:
#   Curtis et al. (2018) Science: https://science.sciencemag.org/content/361/6407/1108
#   data: https://gfw2-data.s3.amazonaws.com/forest_change/tsc/Goode_FinalClassification_19_05pcnt_prj.zip
#   info: http://data.globalforestwatch.org/datasets/tree-cover-loss-by-dominant-driver

# class codes:
#   0 = Zero or minor loss
#   1 = Commodity driven deforestation
#   2 = Shifting agriculture
#   3 = Forestry
#   4 = Wildfire
#   5 = Urbanization
#   -1.69999999999999994e+308 = NoData

# convert from float to mask (0 = nodata/not shifting ag, 1 = shifting ag)
gdal_calc.py \
    -A Goode_FinalClassification_19_05pcnt_prj.tif \
    --outfile=curtis_shift_ag_mask.tif \
    --calc='A == 2' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0

# downsample/reproject raster from ~10km/WGS84 to 500m/sinusoidal
Rscript ../warp2sin.R curtis_shift_ag_mask.tif -o curtis_shift_ag_mask_500m.tif -s -v

rm Goode_FinalClassification_19_05pcnt_prj.tif curtis_shift_ag_mask.tif
