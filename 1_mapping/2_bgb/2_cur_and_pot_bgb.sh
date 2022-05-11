#!/bin/bash
set -e

# run current
python3 ./compute_belowground.py -v \
	--agb global_actual_biomass_2016_v6_blend_a95_f03_w75_clp.tif \
	--r2s Root2Shoot_Ratios_Scaled1e3.tif -s 1000 \
	--out Current_BGB_MgCha_500m.tif

# run potential
python3 ./compute_belowground.py -v \
	--agb global_potential_biomass_v6_blend_ndm_clp.tif \
	--r2s Root2Shoot_Ratios_Scaled1e3.tif -s 1000 \
	--out Potential_BGB_MgCha_500m.tif
