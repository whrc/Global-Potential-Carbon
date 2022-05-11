#!/usr/bin/env Rscript

library(ranger)

set.seed(1231)

# Parse Args ------------------------------------------------------------------
args <- commandArgs(trailingOnly = TRUE)
in_csv <- args[1] # Input data csv
out_model_path <- args[2] # Path to save model
model_type <- args[3] # "current" or "potential"
pred_list_rfile <- args[4] # .R file containing pred_names variable (list of predictor variables)
n_thread <- as.integer(args[5]) # Number of threads to runin parallel

# Set Variable Importance metric
# "none", "impurity", "impurity_corrected", or "permutation"
var_imp_metric <- "permutation"

# Load data -------------------------------------------------------------------
# Get pred_names from files and assign caseweighting
if (model_type == "current") {
  weight_95th <- 4 # Top 5% of biomass pixels will have 4x weight
  weight_90th <- 2 # Top 10%-5% of biomass pixels will have double weight
  weight_80th <- 1 # Second 10% weight
  weight_zero <- 4 # Pixels with 0 biomass will have 4x weight

} else if (model_type == "potential") {
  weight_95th <- 10
  weight_90th <- 5
  weight_80th <- 1
  weight_zero <- 1

} else {
  stop("model_type (arg 3) must be 'current' or 'potential'")
}

# Get pred_names
source(pred_list_rfile)

# Read input data frame
print("Loading CSV")
mod_pix = read.csv(in_csv)

# Assign case weights ---------------------------------------------------------
bm_80th <- quantile(mod_pix$glasBM, 0.8)
bm_90th <- quantile(mod_pix$glasBM, 0.9)
bm_95th <- quantile(mod_pix$glasBM, 0.95)
mod_pix[,"case_weight"] <- 1
mod_pix[mod_pix$glasBM == 0, "case_weight"] <- weight_zero
mod_pix[mod_pix$glasBM > bm_80th, "case_weight"] <- weight_80th
mod_pix[mod_pix$glasBM > bm_90th, "case_weight"] <- weight_90th
mod_pix[mod_pix$glasBM > bm_95th, "case_weight"] <- weight_95th

# Calculate sample fraction ---------------------------------------------------
# Current set up:
# Get sample size up to 100K
# If more than 100K pixels available, set sample frac to limit to 100K
sample_frac <- 1
if (nrow(mod_pix) > 100000) {
  sample_frac <- 100000/nrow(mod_pix)
}

# Train Random Forest ---------------------------------------------------------
Xy <- mod_pix[,c(pred_names,'glasBM')]
case_weights <- mod_pix$case_weight
print("Start training...")
rf_model <- ranger(data = Xy, dependent.variable.name = 'glasBM',
                min.node.size = 5, mtry = floor(length(pred_names)/3),
                importance = var_imp_metric, case.weights = case_weights,
                num.threads = n_thread, sample.fraction = sample_frac,
                scale.permutation.importance = TRUE)

print("Training done.")
print(rf_model)

# Save to file
save(rf_model, file = out_model_path)
