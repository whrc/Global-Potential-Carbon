#!/usr/bin/env Rscript
# --------------------------------------------------------------------------------------------------
#
# make_zonal_stats_table.R
#
# Command-line tool to compute zonal stats of global carbon density layers
#
# Usage:
#   ./make_zonal_stats_table.R <inputs.csv> <carbon_summary.csv> [options]
#
# --------------------------------------------------------------------------------------------------

suppressPackageStartupMessages(library(optparse))
suppressPackageStartupMessages(library(foreach))
suppressPackageStartupMessages(library(parallel))
suppressPackageStartupMessages(library(doMC))
suppressPackageStartupMessages(library(data.table))
suppressPackageStartupMessages(library(raster))
suppressPackageStartupMessages(library(dplyr))

rasterOptions(tmpdir = '~/tmp/r')

# ---------------------------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------------------------

# - - - - - - - - - - - -
# Define user parameters
# - - - - - - - - - - - -

opt.list <- list(
  make_option(c('-s', '--split'), type = 'integer', default = 100, help = 'Division applied to each side of the input rasters (e.g.,\n\t\ts = 4 gives 16 tiles) (default is %default)'),
  make_option(c('--overwrite'), action = 'store_true', default = FALSE, help = 'Overwite ouput CSV file if it exists? (default is no)')
)

opt.parser <- OptionParser(option_list = opt.list,
                           usage = 'usage: %prog <input_parameters.csv> <carbon_summary.csv> [options]\n',
                           description = paste0('Computes a zonal summary of global carbon rasters.\n\n',
                                                'Arguments:\n',
                                                '\t<inputs.csv>\n',
                                                '\t\tCSV file containing paths to input raster files\n\n',
                                                '\t<carbon_summary.csv>\n',
                                                '\t\tCSV file to save output carbon summary'))

# - - - - - - - - - - - -
# Parse user parameters
# - - - - - - - - - - - -

arguments <- parse_args(opt.parser, positional_arguments = 2)
pos.args <- arguments$args
opt <- arguments$options

csv.in <- pos.args[1]
csv.out <- pos.args[2]
s <- opt$split
overwrite.flag <- opt$overwrite

if (is.null(csv.in)) stop('input CSV required.') else cat(paste('Input:', csv.in), fill = T)

if (is.null(csv.out)) {
  stop('output CSV path required.')
} else if (!file.exists(csv.out)) {
  cat(paste('Output:', csv.out), fill = T)
} else if (file.exists(csv.out) & isTRUE(overwrite.flag)) {
  cat(paste('Output:', csv.out, 'will be overwritten.'), fill = T)
} else if (file.exists(csv.out) & !isTRUE(overwrite.flag)) {
  stop(paste('output CSV file exists. Must set --overwrite flag to overwrite', csv.out))
}

# - - - - - - - - - - - -
# Check input rasters
# - - - - - - - - - - - -

df.in <- read.csv(csv.in, header = T, stringsAsFactors = F)

# check that necessary CSV columns exist
col.hdrs <- c('variable','zonal','file','pixel_values','code_file','code_col','name_col')
for (v in col.hdrs) if(!v %in% colnames(df.in)) { stop(paste0('column named \"', v, '\" not found in ', csv.in)) }

# check that input raster files exist
df.in$file_exists <- file.exists(df.in$file)
if (!all(df.in$file_exists)) {
  df.in.na <- df.in %>%
    filter(file_exists == F) %>%
    dplyr::select(variable, file)
  stop('could not find:', paste0('\n  ', sprintf("% 2s", 1:nrow(df.in.na)), '. ', sprintf("%-18s", df.in.na$variable), ' ', df.in.na$file))
}

# check that input class code name files exist
df.test <- df.in %>% filter(pixel_values == 'codes') %>% select(variable, code_file)
df.test$code_file_exists <- file.exists(df.test$code_file)
if (!all(df.test$code_file_exists)) {
  df.in.na <- df.test %>%
    filter(code_file_exists == F) %>%
    dplyr::select(variable, code_file)
  stop('could not find:', paste0('\n  ', sprintf("% 2s", 1:nrow(df.in.na)), '. ', sprintf("%-18s", df.in.na$variable), ' ', df.in.na$code_file))
}

# get list of input rasters
tifs <- df.in$file

# and their shorthand names
vars <- df.in$variable

# get biomass density varaible names
bio.vars <- df.in$variable[df.in$zonal == 0]

# get zonal variable names
zone.vars <- df.in$variable[df.in$zonal == 1]

# get list of input zonal rasters
zone.tifs <- df.in$file[df.in$zonal == 1]

# stack rasters (note, this does not read them into memory)
r <- stack(tifs)
names(r) <- vars

# get X and Y dimensions of stack
x <- ncol(r)
y <- nrow(r)
z <- nlayers(r)

# get pixel resolution to convert units from Mg/ha to Mg
xres.m <- xres(r)
yres.m <- yres(r)
px.ha <- (xres.m * yres.m) / 1e4

# ---------------------------------------------------------------------------------------------
# Build table
# ---------------------------------------------------------------------------------------------

# create tile index
df.tiles <- expand.grid(i = 0:(s-1), j = 0:(s-1))
num.tiles <- nrow(df.tiles)

# process tiles in parallel
num.cores <- parallel::detectCores()
num.cores <- ifelse(num.cores > 1, num.cores - 1, num.cores)
registerDoMC(num.cores)
cat(paste('Processing', z, 'raster layers into', format(num.tiles, big.mark = ','), 'tiles using', num.cores, 'CPU(s) ...'), fill = T)

chunk <- function(x, n) { split(x, cut(seq_along(x), n, labels = F)) }
num.chunks <- 100
tile.chunks <- chunk(1:nrow(df.tiles), n = num.chunks)

df.all <- data.frame()
pb <- txtProgressBar(min = 0, max = num.chunks, initial = 0, style = 3)
for (c in 1:num.chunks) {
  tile.chunk <- tile.chunks[[c]]
  df.chunk <- foreach(t = tile.chunk, .combine = rbind) %dopar% {

    # extract only subwindow of global rasters
    i <- df.tiles$i[t]
    j <- df.tiles$j[t]
    df.tile.values <- as.data.frame(getValuesBlock(r, row = (j * y/s), nrows = (y/s), col = (i * x/s), ncols = (x/s)))

    # summarize biomass by zones and calculate SOC inside and outside of AGB (call new columns "forest" and "other", respectively)
    df.tile.sum <- df.tile.values %>%
        mutate_at(vars(one_of(bio.vars)), .funs = function(x) { ifelse(is.na(x), 0, x) }) %>%
        mutate_at(vars(one_of(bio.vars)), .funs = function(x) { x * px.ha }) %>%
        mutate(forest_soc_act = ifelse(!is.na(agb_act) & agb_act > 0, soc_act, NA),
               forest_soc_pot = ifelse(!is.na(agb_pot) & agb_pot > 0, soc_pot, NA),
               forest_soc_pot_adj = ifelse(!is.na(agb_pot_adj) & agb_pot_adj > 0, soc_pot_adj, NA),
               forest_soc_unr = ifelse(!is.na(agb_unr) & agb_unr > 0, soc_unr, NA),
               forest_soc_unr_adj = ifelse(!is.na(agb_unr_adj) & agb_unr_adj > 0, soc_unr_adj, NA),
               other_soc_act = ifelse(is.na(agb_act) | agb_act == 0, soc_act, NA),
               other_soc_pot = ifelse(is.na(agb_pot) | agb_pot == 0, soc_pot, NA),
               other_soc_pot_adj = ifelse(is.na(agb_pot_adj) | agb_pot_adj == 0, soc_pot_adj, NA),
               other_soc_unr = ifelse(is.na(agb_unr) | agb_unr == 0, soc_unr, NA),
               other_soc_unr_adj = ifelse(is.na(agb_unr_adj) | agb_unr_adj == 0, soc_unr_adj, NA)) %>%
        group_by_at(vars(one_of(zone.vars))) %>%
        summarize_all(sum, na.rm = T) %>%
        as.data.frame()

    return(df.tile.sum)
  }
  df.all <- rbind(df.all, df.chunk)
  setTxtProgressBar(pb, c)
}

# summarize all foreach results again by zonal groups
df.sum <- df.all %>%
  group_by_at(vars(one_of(zone.vars))) %>%
  summarize_all(sum, na.rm = T) %>%
  as.data.frame()

# ---------------------------------------------------------------------------------------------
# Add class names
# ---------------------------------------------------------------------------------------------

cat('\nAdding class names ...', fill = T)

df.codes <- df.in %>%
  dplyr::filter(pixel_values == 'codes') %>%
  dplyr::select(variable, code_file, code_col, name_col)

for (row in 1:nrow(df.codes)) {
  code.row <- df.codes[row,]
  zone.var <- code.row$variable
  code.csv <- code.row$code_file
  code.col <- code.row$code_col
  name.col <- code.row$name_col
  df.zones <- read.csv(code.csv, header = T) %>% dplyr::select(one_of(code.col, name.col)) %>% as.data.frame()
  df.sum <- merge(df.zones, df.sum, by.x = code.col, by.y = zone.var, all = T)
}

# ---------------------------------------------------------------------------------------------
# Write table to CSV file
# ---------------------------------------------------------------------------------------------

# for zones added that do not have any biomass, change their biomass value from NA to 0 Mg
df.sum <- mutate_at(df.sum, vars(matches('agb|agc|bgb|bgc|soc')), .funs = function(x) { ifelse(is.na(x), 0, x) })

cat(paste('Writing', csv.out, '...'), fill = T)
fwrite(df.sum, file = csv.out, na = 'NA', row.names = F)

unlink('~/tmp/r/*')