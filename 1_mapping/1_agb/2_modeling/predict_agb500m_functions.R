#!/usr/bin/R

library(raster)
library(gdalUtils)

#------------------------------------------------------------------------------
### Define functions

LoadObj <- function(f) {
  # Loads a single object stored in a .RData file.
  # Lets you name it however you please, rather than having to use original
  # naming from when .RData file was created.
  env <- new.env()
  nm <- load(f, env)[1]
  env[[nm]]
}

CategorizeVariables <- function(pred.names) {
  # Categorizes variables. Useful for getting exact paths for
  # copying to cloud storage.
  #
  # Args:
  #   pred.names: List of predictor variables from model.
  #
  # Returns:
  #   List, pred.names categorized as "soil", "climate", "terrain", "spectral"
  #
  # Notes:
  #   This is crazy rigid, will need to be updated in the future.

  categorized.preds <- list()

  # Preds that start with bio, tmin, tmax, tmean, prec are climate
  categorized.preds[["climate"]] <- pred.names[grep(paste(c(
    "^bio", "^tmin", "^tmax", "^prec", "^tmean"
  ), collapse = "|"),
  pred.names)]

  # Terrain variables start with elev or slope
  categorized.preds[["terrain"]] <- pred.names[grep(paste(c("^slope", "^elev"), collapse =
                                                            "|"), pred.names)]

  # Soil variables all end with 250m_ll
  categorized.preds[["soil"]] <- pred.names[grep("250m_ll$", pred.names)]

  # Spectral variables start with c6_b
  categorized.preds[["spectral"]] <- pred.names[grep("^c6_b", pred.names)]

  # Delete empty list elements
  categorized.preds <- categorized.preds[sapply(categorized.preds, function(x)
    length(x) != 0)]

  return(categorized.preds)

}

ClimateResampleAndAverage <- function(worldclim.preds, tile.id, shared.dir, work.dir) {
  # Extract resampled MODIS tile from WorldClim data
  #
  # Args:
  #   worldclim.preds: Names of climate predictor variables.
  #   tile.id: MODIS tile ID (h##v##)
  #   shared.dir: Shared directory on cluster NFS.
  #   work.dir: Temporary working directory
  #
  # Returns:
  #   Null

  # Get tile.id bounding coordinates from  a reference tile
  reference.file <- Sys.glob(paste0(work.dir, "/*", tile.id, "*.tif"))[1]
  reference.raster <- raster(reference.file)
  tile.extent <- extent(reference.raster)
  tile.bbox <- c(tile.extent@xmin, tile.extent@ymin,
                 tile.extent@xmax, tile.extent@ymax)

  # Resample all variables EXCEPT mean (doesn't exist yet)
  worldclim.preds.nonmean <- worldclim.preds[!grepl("tmean", worldclim.preds)]
  for (pred in worldclim.preds.nonmean) {
    global.src.raster <- paste0(shared.dir, "/", pred, ".tif")
    # First make sure that it exists
    for (try in 1:100) {
      if (file.exists(global.src.raster)) {
        break
      } else {
        print(paste("Waiting for global climate rasters, try:", try))
        Sys.sleep(10)
      }
    }
    output.tile.raster <- paste0(work.dir, "/", pred, "_", tile.id, ".tif")
    gdalwarp(srcfile = global.src.raster,
             dstfile = output.tile.raster,
             s_srs="+proj=longlat +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +no_defs",
             t_srs="+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs",
             tr=c(463.3127,463.3127),
             te=tile.bbox,
             r="near",
             co=c("COMPRESS=LZW"),
             of="GTiff",
             overwrite=TRUE)
  }

  # Calculate tmean from tmax's and tmin's
  worldclim.preds.meanonly <- worldclim.preds[grepl("tmean", worldclim.preds)]
  for (pred in worldclim.preds.meanonly) {
    mean.output.raster <- paste0(work.dir, "/", pred, "_", tile.id, ".tif")
    min.input.raster <- sub("tmean", "tmin", mean.output.raster)
    max.input.raster <- sub("tmean", "tmax", mean.output.raster)
    system(paste0("gdal_calc.py -A ", min.input.raster, " -B", max.input.raster,
                  " --calc=",
                  "'-32768*logical_or(A==-32768, B==-32768) + (A!=-32768)*(B!=-32768)*((A+B)/2)'",
                  " --outfile=", mean.output.raster, " --type='Int16' --co='COMPRESS=LZW'"))
  }
  return()
}

StageFiles <- function(tile.id,
                       gs.input.dirs,
                       categorized.preds,
                       actual.year,
                       shared.dir,
                       work.dir) {
  # Prepare simple text file with list of files to copy from GCS
  #
  # Args:
  #   tile.id: MODIS tile ID (h##v##)
  #   gs.input.dirs: List/hash of categorized GCS directories containing
  #                  raster predictors.
  #   categorized.preds: List of preds by category.
  #   actual.year: Year of prediction for actual.
  #   shared.dir: Shared directory on cluster NFS.
  #   work.dir: Temporary working directory
  #
  # Returns:
  #   Null
  file.list.path <- paste0(work.dir, "/gs_preds_tocopy.txt")

  gs.patterns <- c()
  for (cat in names(categorized.preds)) {
    preds = categorized.preds[[cat]]
    # Spectral data is special case
    if (cat == "spectral") {
      gs.patterns <- c(
        gs.patterns,
        paste0(
          gs.input.dirs[[cat]],
          "/MCD*A",
          actual.year,
          "*",
          tile.id,
          "*.bip"
        )
      )
    # Climate is also a special case. Download is handled by other process.
    } else if (cat != "climate") {
      gs.patterns <- c(gs.patterns,
                       paste0(gs.input.dirs[[cat]],
                              "/", preds, "_", tile.id, ".tif"))
    }
  }
  writeLines(gs.patterns, file.list.path)

  # Copy files
  system(paste("cat", file.list.path, "|", "gsutil -q cp -I", work.dir),
         wait = TRUE)

  ClimateResampleAndAverage(categorized.preds[["climate"]], tile.id, shared.dir, work.dir)
  return()

}


LoadPredictorStack <- function(tile.id,
                               work.dir,
                               spectral.bands.exclude = c(67)) {
  # Load raster stack of predictors
  #
  # Args:
  #    tile.id: MODIS tile ID (h##v##)
  #    work.dir: Temporary working directory
  #    spectral.bands.exclude: Band numbers to exclude for spectral data.
  #                            Default: c(67) (Snow band in Ale's tifs)
  #
  # Returns:
  #   Raster Stack of predictor tifs.

  pred.stack <- stack(Sys.glob(paste0(work.dir, "/*", tile.id, "*.tif")))

  # Remove tile id from names
  names(pred.stack) <-
    gsub(paste0("_", tile.id), "", names(pred.stack))

  actual.files <- Sys.glob(paste0(work.dir, "/*", tile.id, "*.bip"))
  if (length(actual.files) > 0) {
    spec.stack <- stack(actual.files)
    names(spec.stack) <- paste0("c6_b", (1:67))
    pred.stack <- stack(pred.stack, spec.stack)
  }

  return(pred.stack)

}


#------------------------------------------------------------------------------
### Master function
AGBPredictTile <- function(region,
                           tile.id,
                           predict.function,
                           gs.input.dirs,
                           gs.out.file,
                           gs.model.dir,
                           shared.dir,
                           actual.year = 2007) {
  # Run biomass prediction for one tile.
  #
  # Args:
  #   region: Region for prediction, e.g. "tropical_america"
  #   tile.id: MODIS tile ID (h##v##).
  #   predict.function: Function for raster library to use for prediction.
  #                     Tested with randomForest and ranger.
  #                     See https://www.rdocumentation.org/packages/raster/versions/2.6-7/topics/predict.
  #   gs.input.dirs: List/hash for variable types and their GCS directories.
  #                  Note that the "climate" dir contains global, non-resampled
  #                  files. Will be resampled on the fly.
  #   gs.out.file: Output path
  #   gs.model.dir: Cloud storage path to model file (.RData).
  #   shared.dir: Directory on file share ($HOME on elasticluster) for sharing
  #               files between slurm jobs.
  #   actual.year: Year for actual prediction. 2001-2016 for MODIS.
  #                Default = 2007.
  #
  # Returns:
  #   Path to predicted output file on Google Cloud Storage.

  print(paste("Start,", gs.out.file))
  # Strip trailing slashes from GCS directories and local.
  gs.model.dir <- sub("/$", "", gs.model.dir)
  gs.input.dirs <- lapply(gs.input.dirs, function(x) sub("/$", "", x))
  shared.dir <- sub("/$", "", shared.dir)

  # Create working directory
  work.dir <- paste0(tempdir(), "/working")
  dir.create(work.dir)

  # Load model
  system(paste0("gsutil -q cp ", gs.model.dir, "/", region, "*.RData ", work.dir))
  local.model.path <- Sys.glob(paste0(work.dir, "/*.RData"))
  set.rm <- LoadObj(local.model.path)

  # Change tmean_12_v2 predictor name to just tmean_12. Fix for an old problem.
  set.rm$forest$independent.variable.names <- gsub(
    "tmean_12_v2", "tmean_12", set.rm$forest$independent.variable.names)

  # Get predictor names
  pred.names <- set.rm$forest$independent.variable.names
  categorized.preds <- CategorizeVariables(pred.names)

  # Copy files from Google Cloud Storage
  StageFiles(tile.id, gs.input.dirs, categorized.preds, actual.year, shared.dir, work.dir)

  # Create predictor stack
  pred.stack <- LoadPredictorStack(tile.id, work.dir)

  # Order predictors by model's variable names
  pred.stack <- pred.stack[[pred.names]]

  # Predict
  tmp.out.file <- paste0(work.dir,
                         "/", region, "_biomass_", tile.id, "_raw.tif")
  predict.function(preds=pred.stack, model=set.rm, filename=tmp.out.file)

  # Copy output to cloud storage
  system(paste("gsutil -q cp -Z", tmp.out.file, gs.out.file))

  print("Done")

  return(gs.out.file)

}
