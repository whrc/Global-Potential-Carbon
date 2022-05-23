#!/usr/bin/env Rscript

library(sp)
library(raster)
library(maptools)
library(rgdal)

args <- commandArgs(trailingOnly = TRUE)
tileid = args[1]
csv_in_path = args[2]
outdir = args[3]

temp_dir = tempdir()

# Some hardcoded stuff. These are the dirs that ../stage_files.sh downloads to.
road_layer = "./stage/roads/groads_with_pakistan.shp"
hansen_dir = "./stage/Hansen/"
ifl_layer = "./stage/ifl/ifl_2013.shp"
igbp_raster = "./stage/igbp/Global_MCD12Q1_2007_v0051.tif"
outcsv = paste0(outdir,tileid,"_out.csv")
county_layer = "./stage/counties/counties_with_WHRCMapV3_and_NBCD_stats.shp"

#------------------------------------------------------------------------------
# Run extract for Hansen (in python)
#------------------------------------------------------------------------------
# Call python extraction code
system(paste("python3 ",
             "1_glas_prefilter_extract_prox.py",
              tileid,
              road_layer,
              csv_in_path,
              outcsv,
              hansen_dir,
              temp_dir))
print("Done with Hansen and roads")

#------------------------------------------------------------------------------
# IGBP class (integer from 0 to 17)
#------------------------------------------------------------------------------
results = read.csv(outcsv)
spatial.points=SpatialPoints(data.frame(results$LON,results$LAT))
proj4string = CRS("+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0")
projection(spatial.points) = proj4string
igbp = raster(igbp_raster)
#IGBP raster in sinusoidal projection
glas.pts.sinu = spTransform( spatial.points, CRSobj = CRS(projection(igbp)))
extract.igbp = extract(igbp,glas.pts.sinu,progress='text',nl=1,df=T,weights=F)
results$igbp = extract.igbp$world_mcd12q1_2001
print("Done with IGBP")

#------------------------------------------------------------------------------
#Intact forest layer
#------------------------------------------------------------------------------

IFL = readShapePoly(ifl_layer)
projection(IFL) = projection(spatial.points)
extract.ifl = over(spatial.points,IFL)
ifl.bin = as.numeric(!is.na(extract.ifl$IFL))  #A value of 1 means intact forest, 0 means not intact
results$IFL13 = ifl.bin
print("Done with intact forest layer")

#------------------------------------------------------------------------------
# Extract counties
#------------------------------------------------------------------------------
counties = readShapePoly(county_layer)
projection(counties) = CRS('+proj=longlat +datum=WGS84 +no_defs')
extract.counties = over(spatial.points,counties)
results$county_fip = extract.counties$FIPS

#------------------------------------------------------------------------------
# Write output
#------------------------------------------------------------------------------
write.csv(results,outcsv)
unlink(temp_dir)




