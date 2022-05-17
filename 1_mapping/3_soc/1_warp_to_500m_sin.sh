#!/bin/bash
set -e

# resample SOC layers from 10km to 500m (modis sinusoidal)

# input source:
#  Sanderman, J., Hengl, T., and Fiske, G. 2017. The soil carbon debt of 12,000 years
#  of human land use. PNAS 114(36): 9575–9580. doi:10.1073/pnas.1706103114.
#
# downloaded from:
#  https://github.com/whrc/Soil-Carbon-Debt
#
# input soc rasters:
# - top 2 m of soil
# - units: MgC/ha
# - res: 10 km
# - values ≥ 0
# - nodata = -32767

# current
Rscript ../warp2sin.R SOCS_0_200cm_year_2010AD_10km.tif -o SOCS_0_200cm_year_2010AD_500m.tif -s -v

# potential
Rscript ../warp2sin.R SOCS_0_200cm_year_NoLU_10km.tif -o SOCS_0_200cm_year_NoLU_500m.tif -s -v
