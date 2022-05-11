#!/usr/bin/env Rscript
# splits data into training and test set

library(dplyr, quiet=T)
library(data.table, quiet=T)
library(argparser, quiet=T)

# Parse args-------------------------------------------------------------------
p <- arg_parser("Split csv into training/test sets, with option of adding extra 0 BM pixels.")

p <- add_argument(p, "glas_csv_dir",
                  help="Input GLAS csv directory. Will merge all csvs in this dir",
                  type="character")
p <- add_argument(p, "igbp_zeros_csv_dir",
                  help="csv directory containing extra IGBP zero tiled-csvs. Will merge all csvs in this dir",
                  type="character")
p <- add_argument(p, "out_dir", help="Output directory.", type="character")
p <- add_argument(p, "region",
                  help="Region name. Used for output file path",
                  type="character")
p <- add_argument(p, "model_type", help="Model type: 'actual' or 'potential'", type="character")


# Parse the command line arguments
argv <- parse_args(p)

# Define test
test_frac <- 0.2

if (argv$model_type == "actual") {
  include_spectral <- TRUE
} else if (argv$model_type == "potential") {
  include_spectral <- FALSE
} else {
  stop("Argument 5 must be potential or actual")
}

# Prep file paths -------------------------------------------------------------
dir.create(argv$out_dir,recursive=TRUE,showWarnings=FALSE)
test_out <- paste0(argv$out_dir,"/",argv$region, "_", argv$model_type, "_test.csv")
training_out <- paste0(argv$out_dir,"/",argv$region, "_", argv$model_type, "_train.csv")


# Data Prep -------------------------------------------------------------------
ReadAllCSVsFromDir <- function(csv_dir) {
  csv_paths <- Sys.glob(paste0(csv_dir, '/*.csv'))
  datalist = lapply(csv_paths, function(x){read.csv(file=x,header=T)})
  return(Reduce(function(x,y) rbind(x,y), datalist))
}


ElimCols <- function(df) {
    # Eliminate extra columns that aren't needed any more
    col_elims <- c("ECO_ID","HEIGHT1","HEIGHT2","HEIGHT3","NPEAKS","lc_center","treecover.mean","treecover_1x1",
                  "lossyear","gain","roads2k","roads3k","roads4k","roads5k","roads10k","igbp","BIOME","ECO_AREA",
                  "flag7","flag8","flag9","flag10","flag11","ELEV","SRTM_ELEV","dem.mean","slope.mean","treecover2000_max",
                  "hansen_dmask","srtmFlag","county_fip")
    return(df[ , -which(names(df) %in% col_elims)])
}

CleanDF <- function(df, byte_cols, include_spectral=FALSE) {

  if (include_spectral) {
    c6_band_exclude <- c(67)
    c6_pred_list <- paste0('c6_b',(1:67)[!(1:67 %in% c6_band_exclude)])
  } else {
    c6_pred_list <- c()
  }


  pred_list <- c(c6_pred_list,
                 'elev','slope',
                 "SLTPPT_M_sl4_250m_ll",   "PHIKCL_M_sl4_250m_ll",   "CECSOL_M_sl4_250m_ll",   "TEXMHT_M_sl5_250m_ll",
                 "AWCtS_M_sl7_250m_ll",    "ORCDRC_M_sl5_250m_ll",   "OCSTHA_M_100cm_250m_ll", "BLDFIE_M_sl2_250m_ll",
                 "OCSTHA_M_sd3_250m_ll",   "SNDPPT_M_sl1_250m_ll",   "CLYPPT_M_sl4_250m_ll",   "PHIHOX_M_sl5_250m_ll",
                 "ORCDRC_M_sl2_250m_ll",   "OCDENS_M_sl7_250m_ll",   "TEXMHT_M_sl2_250m_ll",   "CECSOL_M_sl3_250m_ll",
                 "AWCh2_M_sl7_250m_ll",    "SLTPPT_M_sl3_250m_ll",   "PHIKCL_M_sl3_250m_ll",   "BDTICM_M_250m_ll",
                 "AWCh3_M_sl7_250m_ll",    "AWCh1_M_sl7_250m_ll",    "PHIHOX_M_sl2_250m_ll",   "WWP_M_sl7_250m_ll",
                 "SNDPPT_M_sl6_250m_ll",   "CLYPPT_M_sl3_250m_ll",   "OCSTHA_M_sd4_250m_ll",   "CRFVOL_M_sl7_250m_ll",
                 "BLDFIE_M_sl5_250m_ll",   "OCSTHA_M_200cm_250m_ll", "AWCh3_M_sl2_250m_ll",    "PHIKCL_M_sl6_250m_ll",
                 "SLTPPT_M_sl6_250m_ll",   "AWCtS_M_sl5_250m_ll",    "AWCh2_M_sl2_250m_ll",    "TEXMHT_M_sl7_250m_ll",
                 "CECSOL_M_sl6_250m_ll",   "OCDENS_M_sl2_250m_ll",   "ORCDRC_M_sl7_250m_ll",   "CRFVOL_M_sl2_250m_ll",
                 "OCSTHA_M_sd1_250m_ll",   "CLYPPT_M_sl6_250m_ll",   "WWP_M_sl2_250m_ll",      "SNDPPT_M_sl3_250m_ll",
                 "AWCh1_M_sl2_250m_ll",    "PHIHOX_M_sl7_250m_ll",   "OCDENS_M_sl5_250m_ll",   "AWCh2_M_sl5_250m_ll",
                 "AWCtS_M_sl2_250m_ll",    "CECSOL_M_sl1_250m_ll",   "AWCh3_M_sl5_250m_ll",    "PHIKCL_M_sl1_250m_ll",
                 "SLTPPT_M_sl1_250m_ll",   "AWCh1_M_sl5_250m_ll",    "CLYPPT_M_sl1_250m_ll",   "SNDPPT_M_sl4_250m_ll",
                 "WWP_M_sl5_250m_ll",      "OCSTHA_M_sd6_250m_ll",   "BLDFIE_M_sl7_250m_ll",   "BDRLOG_M_250m_ll",
                 "CRFVOL_M_sl5_250m_ll",   "AWCh3_M_sl4_250m_ll",    "OCDENS_M_sl4_250m_ll",   "ORCDRC_M_sl1_250m_ll",
                 "AWCtS_M_sl3_250m_ll",    "AWCh2_M_sl4_250m_ll",    "TEXMHT_M_sl1_250m_ll",   "SLGWRB_250m_ll",
                 "BLDFIE_M_sl6_250m_ll",   "CRFVOL_M_sl4_250m_ll",   "PHIHOX_M_sl1_250m_ll",   "AWCh1_M_sl4_250m_ll",
                 "WWP_M_sl4_250m_ll",      "SNDPPT_M_sl5_250m_ll",   "AWCh2_M_sl3_250m_ll",    "AWCtS_M_sl4_250m_ll",
                 "TEXMHT_M_sl6_250m_ll",   "CECSOL_M_sl7_250m_ll",   "OCDENS_M_sl3_250m_ll",   "ORCDRC_M_sl6_250m_ll",
                 "OCSTHA_M_30cm_250m_ll",  "AWCh3_M_sl3_250m_ll",    "PHIKCL_M_sl7_250m_ll",   "SLTPPT_M_sl7_250m_ll",
                 "CLYPPT_M_sl7_250m_ll",   "SNDPPT_M_sl2_250m_ll",   "WWP_M_sl3_250m_ll",      "AWCh1_M_sl3_250m_ll",
                 "PHIHOX_M_sl6_250m_ll",   "BLDFIE_M_sl1_250m_ll",   "CRFVOL_M_sl3_250m_ll",   "SLTPPT_M_sl2_250m_ll",
                 "PHIKCL_M_sl2_250m_ll",   "AWCh3_M_sl6_250m_ll",    "ACDWRB_M_ss_250m_ll",    "ORCDRC_M_sl3_250m_ll",
                 "OCDENS_M_sl6_250m_ll",   "TEXMHT_M_sl3_250m_ll",   "CECSOL_M_sl2_250m_ll",   "AWCh2_M_sl6_250m_ll",
                 "AWCtS_M_sl1_250m_ll",    "OCSTHA_M_sd5_250m_ll",   "CRFVOL_M_sl6_250m_ll",   "BLDFIE_M_sl4_250m_ll",
                 "HISTPR_250m_ll",         "AWCh1_M_sl6_250m_ll",    "PHIHOX_M_sl3_250m_ll",   "SNDPPT_M_sl7_250m_ll",
                 "WWP_M_sl6_250m_ll",      "CLYPPT_M_sl2_250m_ll",   "CECSOL_M_sl5_250m_ll",   "TEXMHT_M_sl4_250m_ll",
                 "AWCtS_M_sl6_250m_ll",    "AWCh2_M_sl1_250m_ll",    "ORCDRC_M_sl4_250m_ll",   "OCDENS_M_sl1_250m_ll",
                 "SLTPPT_M_sl5_250m_ll",   "PHIKCL_M_sl5_250m_ll",   "AWCh3_M_sl1_250m_ll",    "WWP_M_sl1_250m_ll",
                 "BDRICM_M_250m_ll",       "CLYPPT_M_sl5_250m_ll",   "PHIHOX_M_sl4_250m_ll",   "AWCh1_M_sl1_250m_ll",
                 "CRFVOL_M_sl1_250m_ll",   "BLDFIE_M_sl3_250m_ll",   "OCSTHA_M_sd2_250m_ll",
                 'prec_1','prec_2','prec_3','prec_4','prec_5','prec_6','prec_7','prec_8','prec_9','prec_10','prec_11','prec_12',
                 'tmax_1','tmax_2','tmax_3','tmax_4','tmax_5','tmax_6','tmax_7','tmax_8','tmax_9','tmax_10','tmax_11','tmax_12',
                 'tmean_1','tmean_2','tmean_3','tmean_4','tmean_5','tmean_6','tmean_7','tmean_8','tmean_9','tmean_10','tmean_11','tmean_12_v2',
                 'tmin_1','tmin_2','tmin_3','tmin_4','tmin_5','tmin_6','tmin_7','tmin_8','tmin_9','tmin_10','tmin_11','tmin_12',
                 'bio_1','bio_2','bio_3','bio_4','bio_5','bio_6','bio_7','bio_8','bio_9','bio_10','bio_11','bio_12','bio_13',
                 'bio_14','bio_15','bio_16','bio_17','bio_18','bio_19')

  df[df==32767] <- NA
  df[df==-32768] <- NA
  if(length(byte_cols > 0)) {
    df[byte_cols][df[byte_cols]==255] <- NA
  }
  # Remove rows where there is an NA predictor
  pred_list <- pred_list[pred_list %in% colnames(df)]
  df <- df[complete.cases(df[,pred_list]),]
  return(df)
}

#Read in pixel csv:
mod_pix <- ReadAllCSVsFromDir(argv$glas_csv_dir)
print("Starting Dims:")
print(dim(mod_pix))

# Eliminate extra columns
mod_pix <- ElimCols(mod_pix)

# Filter out nodata values. -32678 for all, plus 255 for soil vars with maxvals == 255 exactly.
colmaxes <- sapply(mod_pix, max, na.rm = TRUE)
colmins <- sapply(mod_pix, min, na.rm = TRUE)
nodat_255_cols <- grep("250m",names(colmaxes[colmaxes==255 & colmins>=(0)]),value=TRUE)

mod_pix <- CleanDF(mod_pix,nodat_255_cols, include_spectral=include_spectral)

# Add IGBP Zero BM Pixels -----------------------------------------------------

AddIGBP <- function(mod_pix, igbp_csv_dir, byte_cols,
                    include_spectral=FALSE) {
  #' Add Zero biomass pixels based on IGBP land cover classes

  #Set seed for random sample:
  set.seed(3351)

  # How many to add
  igbp_add_count = round(sum(mod_pix['glasBM']==0) * 0.25)

  # Raed all csvs
  igbp_df = ReadAllCSVsFromDir(igbp_csv_dir)

  # Remove nas
  igbp_df = CleanDF(igbp_df, byte_cols, include_spectral = include_spectral)

  # Match columns
  igbp_df = igbp_df[,colnames(igbp_df)[(colnames(igbp_df) %in% colnames(mod_pix))]]
  igbp_df[,colnames(mod_pix)[!(colnames(mod_pix) %in% colnames(igbp_df))]] = NA

  # Select random sample
  igbp_samplerows = sample(1:nrow(igbp_df), min(nrow(igbp_df), igbp_add_count) ,replace = F)
  igbp_subset = igbp_df[igbp_samplerows, ]

  if (include_spectral==TRUE) {
    # Double the amount of croplands that were selected
    igbp_remainder = igbp_df[!(1:nrow(igbp_df) %in% igbp_samplerows),]
    igbp_remainder_croplands = igbp_remainder[igbp_remainder$igbp_class==12,]
    igbp_subset_cropland_count = sum(igbp_subset$igbp_class==12)
    cropland_additions = sample(1:nrow(igbp_remainder_croplands), igbp_subset_cropland_count, replace = F)
    igbp_subset = rbind(igbp_subset, igbp_remainder_croplands[cropland_additions,])
  }

  # Add column saying whether it is from IGBP
  igbp_subset$igbp_addition <- 1
  mod_pix$igbp_addition <- 0

  # Add to mod_pix
  mod_pix = rbind(mod_pix,igbp_subset[ , !(names(igbp_subset) %in% c('myIndex'))])

  return(mod_pix)
}

mod_pix <- AddIGBP(mod_pix, argv$igbp_zeros_csv_dir, nodat_255_cols,
                   include_spectral)
print("Final Dims:")
print(dim(mod_pix))

# Split -----------------------------------------------------------------------

# Add an index column:
mod_pix$myIndex <- 1:nrow(mod_pix)

# Take out a random sample of 20%, which we'll set aside as independent testing data:
test_id <- sample(mod_pix$myIndex, floor(nrow(mod_pix) * test_frac) ,replace = F)
test <- mod_pix[is.element(mod_pix$myIndex,test_id),]

# Get all the pixels _not_ in the 20%, which we'll use for training:
training <- mod_pix[!is.element(mod_pix$myIndex,test_id),]

# Write out
write.csv(training,training_out,row.names = FALSE)
write.csv(test,test_out,row.names = FALSE)

