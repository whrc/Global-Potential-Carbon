# 5_constraints

Directory description place holder.

## Scripts

+ [prep_cropland_GEE.js](./prep_cropland_GEE.js) - description place holder.
+ [prep_pastureland.sh](./prep_pastureland.sh) - description place holder.
+ [script.R](./script.R) - description place holder.

## Notes

If you export a global raster from GEE with the CRS set to [SR-ORG:6974](https://spatialreference.org/ref/sr-org/modis-sinusoidal-3/) (the corrected MODIS projection required by GEE) and the output is a set of tiles rather than a single raster, then builidng a global mosaic without converting the CRS will lead to errors, e.g.:
```
$ gdalbuildvrt global.vrt *.tif
$ gdalinfo global.vrt
```
```
ERROR 1: tolerance condition error
```
Note, those errors are mixed in with the normal `gdalinfo` output. Also,
```
$ gdalsrsinfo -o proj4 global.vrt
```
will return:
```
'+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs '
```
which is the proj4 of SRS-ORG:6974, whereas our global 500m biomass rasters use [SRS-ORG:6842](https://spatialreference.org/ref/sr-org/modis-sinusoidal/), the original MODIS sinusoidal projection. To build the global mosaic of the exported GEE tiles in the original MODIS sinusoidal projection:
```
$ gdal_translate \
>   -a_srs '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs' \
>   global.vrt global.tif
```
After that, run 
```
$ gdalsrsinfo -o proj4 global.tif
```
And you should see
```
'+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs '
```
which is the proj4 of SR-ORG:6842 (the original MODIS projection).
