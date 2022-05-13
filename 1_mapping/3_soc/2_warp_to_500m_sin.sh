#!/bin/bash
set -e

# resample SOC layers from 10km to 500m (modis sinusoidal)

# current
Rscript ../warp2sin.R Current_SOC_MgCha_10km.tif -o Current_SOC_MgCha_500m.tif -s -v

# potential
Rscript ../warp2sin.R Potential_SOC_MgCha_10km.tif -o Potential_SOC_MgCha_500m.tif -s -v
