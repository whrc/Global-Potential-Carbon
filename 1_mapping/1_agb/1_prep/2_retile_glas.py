#!/usr/bin/env python3

# given glas shots csv, script finds modis tiles for each coordinate and extracts the pixel id from that tile

import numpy as np
import sys
import gdal
import pandas as pd
import subprocess
import math
from pyproj import Proj
import os
import filelock

in_csv_path = sys.argv[1]
out_csv_dir = sys.argv[2]
modis_dir = sys.argv[3]

# Set which columns to keep in csv
keep_columns = ['ShotID','LAT','LON','h_tile','v_tile','modis_x','modis_y',
                'ECO_ID','YEAR','HEIGHT1','HEIGHT2','HEIGHT3','NPEAKS',
		'flag7','flag8','flag9','flag10','flag11','ELEV','SRTM_ELEV',
                'dem.mean','slope.mean','treecover2000_max','lossyear','gain',
		'lossyear_pyunique','gain_pymax','datamask_pyunique','roads2k','roads3k',
                'roads4k','roads5k','igbp','IFL','glasBM']

# Given modis coords, find modis tile
def find_modis_tiles(coord,tileref_array):
    h = 9999
    v = 9999
    h_match = np.logical_and(coord[0] >= tileref_array[:,2],coord[0] <= tileref_array[:,3])
    v_match = np.logical_and(coord[1] >= tileref_array[:,4],coord[1] <= tileref_array[:,5])
    both_match = np.logical_and(h_match,v_match)
    match_index = both_match.nonzero()[0][0]
    h,v = (tileref_array[match_index][0],tileref_array[match_index][1])
    return(int(h),int(v))

# Get indices for extraction
def get_indices(coords,geotrans):
    x_indices,y_indices = (((coords[:,0]-geotrans[0])/geotrans[1]).astype(int),
                           ((coords[:,1]-geotrans[3])/geotrans[5]).astype(int))
    return(y_indices,x_indices)

def extract_pixids(df,mod_pixid_tif):
    # Get glas_coords
    glas_coords = df.as_matrix(['modis_x','modis_y'])
    # Get pixel ids with those coords
    fh = gdal.Open(mod_pixid_tif)
    geotrans = fh.GetGeoTransform()
    pixid_array = fh.GetRasterBand(1).ReadAsArray()
    y_indices, x_indices = get_indices(glas_coords,geotrans)
    # find any inices that are out of bounds (oob) and drop them
    oob_obs = np.where((y_indices < 0) | (y_indices >= fh.RasterYSize) |
                       (x_indices < 0) | (x_indices >= fh.RasterXSize))[0]
    del_mask = np.ones(len(y_indices), dtype=bool)
    del_mask[oob_obs] = False

    # Now delete oob_obs from variables
    df = df.drop(df.index[oob_obs])
    y_indices = y_indices[del_mask]
    x_indices = x_indices[del_mask]
    glas_coords = glas_coords[del_mask,]
    # Extract pixel ids
    pixids = pixid_array[y_indices, x_indices]
    df['pixel_id'] = pixids
    return(df)

def main():
    ### Initialize
    subprocess.call(['mkdir','-p',out_csv_dir])
    tileref = np.genfromtxt('../2_modeling/mod_tileref_sinu.csv',delimiter=',')
    glas_df = pd.read_csv(in_csv_path)

    ### Finding modis tiles/coordinates
    # Get coords and reproject
    glas_coords = glas_df.as_matrix(['LON','LAT'])
    myProj = Proj("+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs")
    glas_coords_sinu_x,glas_coords_sinu_y = myProj(glas_coords[:,0],glas_coords[:,1])
    glas_coords_sinu = np.column_stack([glas_coords_sinu_x,glas_coords_sinu_y])
    glas_df['modis_y'] = glas_coords_sinu_y
    glas_df['modis_x'] = glas_coords_sinu_x
    mod_tiles = np.apply_along_axis(find_modis_tiles,1,glas_coords_sinu,tileref)
    glas_df['h_tile'] = mod_tiles[:,0]
    glas_df['v_tile'] = mod_tiles[:,1]

    # Find unique modis tiles (hv sets)
    unique_mod_tiles = np.unique(mod_tiles,axis=0)
    print(unique_mod_tiles)

    ### A couple cleanup steps
    # If slope column does not exist, change meanSlope column name to slope
    if not 'slope.mean' in glas_df.columns:
        if 'slope_mean' in glas_df.columns:
            old_slope_name = 'slope_mean'
        elif 'slope_hl' in glas_df.columns:
            old_slope_name = 'slope_hl'
        elif 'meanSlope' in glas_df.columns:
            old_slope_name = 'meanSlope'
        else:
            print('No valid slope column')
        glas_df = glas_df.rename(index=str,columns={old_slope_name:'slope.mean'})
    # If dem.mean column does not exist, change elev_mean column name to dem.mean
    if not 'dem.mean' in glas_df.columns:
        if 'elev_mean' in glas_df.columns:
            old_elev_name = 'elev_mean'
        elif 'Elev_hl' in glas_df.columns:
            old_elev_name = 'Elev_hl'
        else:
            print('No valid elev column')
	glas_df = glas_df.rename(index=str,columns={old_elev_name:'dem.mean'})
    # If ECO_ID column does not exist, delete that from keep_column list
    if not 'ECO_ID' in glas_df.columns:
        glas_df['ECO_ID'] = 0

    # Update df to only keep filtering columns as well as glasBM
    glas_df = glas_df[keep_columns]

    ### Write outputs to modis tiled csvs
    # For each of unique modis tile, check if csv exists. If not, create. Then write to csv
    for i in range(0,unique_mod_tiles.shape[0]):
        h = unique_mod_tiles[i,0]
        v = unique_mod_tiles[i,1]
        print(('h=' + str(h) + ',v=' + str(v)))
        temp_df = glas_df.loc[(glas_df['h_tile'] == h) & (glas_df['v_tile'] == v)]

        # Get pixel_ids
        mod_tile = 'h' + str(h).zfill(2) + 'v' + str(v).zfill(2)
        modis_pixid_tif_path = str(modis_dir) + 'modis_500m_pixid_' + mod_tile + ".tif"
        temp_df = extract_pixids(temp_df,modis_pixid_tif_path)

        # Write out
        out_csv_temp = out_csv_dir + mod_tile + "_glas_modistile.csv"
        out_csv_flock = out_csv_temp + '_.flock'
        lock = filelock.FileLock(out_csv_flock)
        with lock.acquire(): # No timeout
            if not os.path.isfile(out_csv_temp):
                temp_df.to_csv(out_csv_temp,header=True,mode='w',index=False)
            else:
                temp_df.to_csv(out_csv_temp,header=False,mode='a',index=False)
            lock.release()
    return()

if __name__ == '__main__':
    main()

