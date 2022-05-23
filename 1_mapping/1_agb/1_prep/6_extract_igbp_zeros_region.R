#!/usr/bin/R
# Extract IGBP Zero-Pixel coordinates from eroded MCD12 raster
# Takes a subsample of 200K per region to reduce overhead
# Saves into MODIS tile CSVs

library(raster)

set.seed(4322)

# Parse Args ------------------------------------------------------------------
args <- commandArgs(trailingOnly = TRUE)
raw_MCD12_dir <- args[1]
eroded_MCD12_dir <-  args[2]
region_shapefile <- args[3]
out_csv_dir <- args[4]

dir.create(out_csv_dir, recursive=TRUE, showWarnings=TRUE)

# Read Regiion Shapefile ------------------------------------------------------
region_mtiles <- shapefile(region_shapefile)

hv_list <- paste0("h", sprintf("%02d", region_mtiles$h),
                  "v", sprintf("%02d", region_mtiles$v))

# Make VRTs out of full region -------------------------------------------------
eroded_tifs <- Sys.glob(paste0(eroded_MCD12_dir, "/*", hv_list, "*.tif"))
temp_eroded_vrt <- paste0(tempdir(), "/eroded.vrt")
system(paste("gdalbuildvrt", "-tap", "-tr", "463.31271653", "463.31271653",
             temp_eroded_vrt, paste(eroded_tifs, collapse=" ")))
eroded_raster <- raster(temp_eroded_vrt)

raw_tifs <- Sys.glob(paste0(raw_MCD12_dir, "/*", hv_list, "*.tif"))
temp_raw_vrt <- paste0(tempdir(), "/raw.vrt")
system(paste("gdalbuildvrt", "-tap", "-tr", "463.31271653", "463.31271653",
             temp_raw_vrt, paste(raw_tifs, collapse=" ")))
raw_raster <- raster(temp_raw_vrt)

# Extract 400,000 zero-biomass pixels (will reduce to 200k later) -------------
NAvalue(eroded_raster) <- 0
blocks = blockSize(eroded_raster)
total_igbp_zeros <- sum(sapply(1:length(blocks$row), function(i) sum(!is.na(getValuesBlock(eroded_raster, row=blocks$row[i], nrow = blocks$nrows[i])))))
sample_fraction <- 400000/total_igbp_zeros
sample_fraction <- min(sample_fraction, 1) # Don't want a sample fraction greater than 1!
raster_points <- rasterToPoints(eroded_raster, spatial = TRUE, progress="text",
                                fun=function(x) {runif(0, 1, n=length(x)) < sample_fraction})


 # Extract vars and reduce to 200k --------------------------------------------
points_mtiles <- over(raster_points, region_mtiles)
raster_points$h_tile <- points_mtiles$h
raster_points$v_tile <- points_mtiles$v
raster_points <- raster_points[!is.na(raster_points$h_tile),]
raster_points$index <- 1:nrow(raster_points)
raster_points <- raster_points[sample(raster_points$index, min(nrow(raster_points), 200000) ,replace = F),]
raster_points$igbp <- extract(raw_raster, raster_points, progress='text')

coords <- coordinates(raster_points)
raster_points$modis_x <- coords[,'x']
raster_points$modis_y <- coords[,'y']
raster_points$hv <- paste0("h", sprintf("%02d", raster_points$h_tile),
                           "v", sprintf("%02d", raster_points$v_tile))
raster_points$glasBM <- 0

# Write out to tiled csvs -----------------------------------------------------

for(hv in hv_list) {
  hv_raster_points <- raster_points[raster_points$hv==hv,]
  if(nrow(hv_raster_points)>0) {
    hv_raster_df <- data.frame(hv_raster_points)
    hv_raster_df <- hv_raster_df[c('h_tile', 'v_tile', 'modis_x', 'modis_y', 'igbp', 'glasBM')]
    out_path <- paste0(out_csv_dir, "/igbp_zero_pixels_", hv, ".csv")
    write.csv(hv_raster_df, out_path, row.names = FALSE)
  }
}


