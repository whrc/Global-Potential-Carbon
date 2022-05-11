#!/bin/bash
set -e

# AGB
python3 ./compute_unrealized.py \
	global_actual_biomass_2016_v6_blend_a95_f03_w75_clp.tif \
	global_potential_biomass_v6_blend_ndm_clp.tif \
	-o global_unrealized_2016_AGB_Mgha.tif

# BGB
python3 ./compute_unrealized.py \
	Current_BGB_MgCha_500m.tif \
	Potential_BGB_MgCha_500m.tif \
	-o Unrealized_BGB_MgCha_500m.tif

# SOC
python3 ./compute_unrealized.py \
	Current_SOC_MgCha_500m.tif \
	Potential_SOC_MgCha_500m.tif \
	-o Unrealized_SOC_MgCha_500m.tif

