#!/bin/bash

# source: https://sedac.ciesin.columbia.edu/downloads/data/aglands/aglands-pastures-2000/gl-pastures-geotif.zip
# info: https://sedac.ciesin.columbia.edu/data/set/aglands-pastures-2000/data-download

# convert input from float to integer, replacing nodata value with zero
gdal_calc.py \
    -A pasture.tif \
    --outfile=pasture_byte.tif \
    --calc='(A > 0) * A * 100' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --overwrite \
    --NoDataValue=0

# downsample/reproject raster from ~10km/WGS84 to 500m/sinusoidal
Rscript ../warp2sin.R pasture_byte.tif -o pasture_byte_500m.tif -s

# convert from continuous variable to mask (0 = not pasture/nodata, 1 = pasture)
gdal_calc.py \
    -A pasture_byte_500m.tif \
    --outfile=ramankutty_pasture_mask_500m.tif \
    --calc='(A > 50) * 1' \
    --format='GTiff' \
    --type='Byte' \
    --co='COMPRESS=LZW' \
    --NoDataValue=0

rm pasture_byte.tif pasture_byte_500m.tif
