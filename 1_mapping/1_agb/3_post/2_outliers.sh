#!/bin/bash
set -e

# Clips both current and potential biomass outliers to the global
# 	99.99th percentile of potential biomass (749 Mg/ha).

# current
gdal_calc.py \
	-A global_actual_biomass_2016_v6_blend_a95_f03_w75.tif \
	--outfile=global_actual_biomass_2016_v6_blend_a95_f03_w75_clp.tif \
	--calc="(A*(A <= 749)) + (749*(A > 749))" \
	--NoDataValue=-32768 \
	--format='GTiff' \
	--type='Int16' \
	--co='COMPRESS=LZW'

# potential
gdal_calc.py \
	-A global_potential_biomass_v6_blend_ndm.tif \
	--outfile=global_potential_biomass_v6_blend_ndm_clp.tif \
	--calc="(A*(A <= 749)) + (749*(A > 749))" \
	--NoDataValue=-32768 \
	--format='GTiff' \
	--type='Int16' \
	--co='COMPRESS=LZW'
