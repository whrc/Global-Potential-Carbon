#!/bin/bash
set -e

# Soil organic carbon (SOC) rasters:
# - top 2 m of soil
# - units: MgC/ha
# - res: 10 km
# - values ≥ 0
# - nodata = -32767

# Source:
# Sanderman, J., Hengl, T., and Fiske, G. 2017. The soil carbon debt of 12,000 years of human land use.
# PNAS 114(36): 9575–9580. doi:10.1073/pnas.1706103114.

# current ca. 2010
wget \
	https://github.com/whrc/Soil-Carbon-Debt/blob/master/SOCS/SOCS_0_200cm_year_2010AD_10km.tif?raw=true \
	-O SOCS_0_200cm_year_2010AD_10km.tif

# potential
wget \
	https://github.com/whrc/Soil-Carbon-Debt/blob/master/SOCS/SOCS_0_200cm_year_NoLU_10km.tif?raw=true \
	-O SOCS_0_200cm_year_NoLU_10km.tif

# compute stats
gdal_edit.py -stats SOCS_0_200cm_year_2010AD_10km.tif
gdal_edit.py -stats SOCS_0_200cm_year_NoLU_10km.tif
