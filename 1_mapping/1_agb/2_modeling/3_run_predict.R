#!/usr/bin/R
# Example:
#   Rscript run_predict.R "example_params.R" "tropical_asia" "h24v05"

start.time <- Sys.time()

library(ranger)
source("./predict_agb500m_functions.R")

#------------------------------------------------------------------------------
### Command line arguments define param file, region, tile.id, and actual.year
args = commandArgs(trailingOnly=TRUE)
param.file = args[1]
region = args[2]
tile.id = args[3]
if (length(args) > 3) {
  actual.year = as.integer(args[4])
} else {
  actual.year = 2000 # Default. Will be ignored by potential.
}

#------------------------------------------------------------------------------
### Load params
source(param.file)

#------------------------------------------------------------------------------
### Define prediction function.

# Set up for ranger, can be tweaked to work with randomForest and more.
# Function used for prediction. Must take preds, model, and outputfilename.
predict.function <- function(preds, model, filename) {
  out <- raster(preds[[1]])
  out <- writeStart(out, filename, overwrite=TRUE,progress="text", format="GTiff", datatype="INT2S",
                    options=c("COMPRESS=LZW"), NAflag=-32768)
  bs <- blockSize(out, minblocks=32)
  for (i in 1:bs$n) {
    predrows <- getValues(preds, row=bs$row[i], nrows=bs$nrows[i])
    valid.indices <- complete.cases(predrows)
    v.complete <- rep(NA, nrow(predrows))
    num.valid <- sum(valid.indices)
    if (num.valid > 0) {
      print(paste("Num Obs in Block =", num.valid))
      if (num.valid == 1) {
        # If there is only one valid index, prediction matrix
        # must be transposed. Otherwise creates Nx1 instead of 1xN matrix.
        predrows.valid <- as.matrix(t(predrows[valid.indices,]))
      } else {
        predrows.valid <- predrows[valid.indices,]
      }
      v <- predict(model, predrows.valid, num.threads=1,type='response')$predictions
      v.complete[valid.indices] <- round(v)
    }
    v.complete[(v.complete<0) & (v.complete != -32768)] = 0
    out <- writeValues(out, v.complete, bs$row[i])
    print(paste("Block", i, "Done"))
  }
  out <- writeStop(out)
  return()
}


#------------------------------------------------------------------------------
### Check if output already exists. If not, run prediction.
params$gs.out.dir <- sub("/$", "", params$gs.out.dir) # Remove trailing /
gs.out.file <- paste0(params$gs.out.dir, '/', region, "_biomass_", actual.year, "_", tile.id, "_raw.tif")
check.exists <- system(paste('gsutil -q ls', gs.out.file))

if (check.exists != 0) {
  tryCatch(
    AGBPredictTile(region = region,
                   tile.id = tile.id,
                   actual.year = actual.year,
                   gs.out.file = gs.out.file,
                   predict.function = predict.function,
                   shared.dir = params$shared.stage.dir,
                   gs.model.dir = params$gs.model.dir,
                   gs.input.dirs = params$gs.input.dirs)
  , finally = unlink(tempdir(), recursive = TRUE))
} else {
  print("Not Run: Output Already Exists")
}

# Delete temporary directory
unlink(tempdir(), recursive = TRUE)
