#!/bin/bash
set -e

# current
python3 ./compute_belowground.py -v -s 1000 \
	--agb /home/sgorelik/data/pnas/Current_AGB_MgCha_500m.tif \
	--r2s /home/sgorelik/data/pnas/Root2Shoot_Ratios_Scaled1e3.tif \
	--out /home/sgorelik/data/pnas/Current_BGB_MgCha_500m.tif

# potential
python3 ./compute_belowground.py -v -s 1000 \
	--agb /home/sgorelik/data/pnas/Potential_AGB_MgCha_500m.tif \
	--r2s /home/sgorelik/data/pnas/Root2Shoot_Ratios_Scaled1e3.tif \
	--out /home/sgorelik/data/pnas/Potential_BGB_MgCha_500m.tif
